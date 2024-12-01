import json
from datetime import date, timedelta, datetime
from hashlib import md5
from io import BytesIO
from typing import Optional, Dict, List, Union, Any

import httpx
from httpx import AsyncClient, Response

from netschoolapi import errors, schemas

__all__ = ['NetSchoolAPI']

from netschoolapi.async_client_wrapper import AsyncClientWrapper, Requester


async def _die_on_bad_status(response: Response):
    if not response.is_redirect:
        response.raise_for_status()


class NetSchoolAPI:
    def __init__(self, url: str, default_requests_timeout: int = None):
        url = url.rstrip('/')
        self._wrapped_client = AsyncClientWrapper(
            async_client=AsyncClient(
                base_url=f'{url}/webapi',
                headers={'user-agent': 'NetSchoolAPI/5.0.3', 'referer': url},
                event_hooks={'response': [_die_on_bad_status]},
                verify=False
            ),
            default_requests_timeout=default_requests_timeout,
        )

        self._student_id = -1
        self._students = []  # [{'studentId': int, 'nickName': str, 'className': str, 'classId': str(int), 'iupGrade': 0}]
        self._year_id = -1
        self._school_id = -1
        self._version = -1

        self._assignment_types: Dict[int, str] = {}
        self._login_data = ()
        self._access_token = None

    async def __aenter__(self) -> 'NetSchoolAPI':
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        await self.logout()

    async def login(
            self, user_name: str, password: bytes | str,
            school_name_or_id: Union[int, str],
            requests_timeout: int = None, password_encode: bool = False) -> str:
        requester = self._wrapped_client.make_requester(requests_timeout)
        # Getting the `NSSESSIONID` cookie for `auth/getdata`
        await requester(self._wrapped_client.client.build_request(
            method="GET", url="logindata"
        ))

        # Getting the `NSSESSIONID` cookie for `login`
        response = await requester(self._wrapped_client.client.build_request(
            method="POST", url='auth/getdata'
        ))
        login_meta = response.json()
        salt = login_meta.pop('salt')
        self._version = login_meta["ver"]
        encoded_password = password
        if password_encode:
            encoded_password = md5(
                password.encode('windows-1251')
            ).hexdigest().encode()
        pw2 = md5(salt.encode() + encoded_password).hexdigest()
        pw = pw2[: len(password)]
        try:
            response = await requester(
                self._wrapped_client.client.build_request(
                    method="POST",
                    url='login',
                    data={
                        'loginType': 1,
                        'scid': (
                            (await self._get_school_id(
                                school_name_or_id, requester,
                            ))
                            if isinstance(school_name_or_id, str) else
                            school_name_or_id
                        ),
                        'un': user_name,
                        'pw': pw,
                        'pw2': pw2,
                        **login_meta,
                    },
                )
            )
        except httpx.HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == httpx.codes.CONFLICT:
                try:
                    response_json = http_status_error.response.json()
                except httpx.ResponseNotRead:
                    pass
                else:
                    if 'message' in response_json:
                        raise errors.AuthError(
                            http_status_error.response.json()['message']
                        )
                raise errors.AuthError()
            else:
                raise http_status_error
        auth_result = response.json()

        if 'at' not in auth_result:
            raise errors.AuthError(auth_result['message'])

        self._access_token = auth_result["at"]
        self._wrapped_client.client.headers['AT'] = auth_result['at']

        response = await requester(self._wrapped_client.client.build_request(
            method="GET", url='student/diary/init',
        ))
        diary_info = response.json()
        self._students = diary_info['students']
        student = diary_info['students'][diary_info['currentStudentId']]
        self._student_id = student['studentId']

        for i, student in enumerate(self._students):
            clid = await self._request_with_optional_relogin(requests_timeout,
                                                             self._wrapped_client.client.build_request(
                                                                 method="POST", url=f"reports/studenttotal/initfilters",
                                                                 json={"params": None,
                                                                       "selectedData": [{"filterId": "SID",
                                                                                         "filterValue": f"{student['studentId']}",
                                                                                         "filterText": f"{student['nickName']}"}]}))
            resp = clid.json()
            self._students[i]['classId'] = resp[0]['items'][0]['value']
            self._students[i]['className'] = resp[0]['items'][0]['title']

        response = await requester(self._wrapped_client.client.build_request(
            method="GET", url='years/current'
        ))
        year_reference = response.json()
        self._year_id = year_reference['id']

        response = await requester(self._wrapped_client.client.build_request(
            method="GET", url="grade/assignment/types", params={"all": False},
        ))
        assignment_reference = response.json()
        self._assignment_types = {
            assignment['id']: assignment['name']
            for assignment in assignment_reference
        }
        self._login_data = (user_name, encoded_password, school_name_or_id)
        return encoded_password

    async def _request_with_optional_relogin(
            self, requests_timeout: Optional[int], request: httpx.Request,
            follow_redirects=False):
        try:
            response = await self._wrapped_client.request(
                requests_timeout, request, follow_redirects
            )
        except httpx.HTTPStatusError as http_status_error:
            if (http_status_error.response.status_code == httpx.codes.UNAUTHORIZED or
                    http_status_error.response.status_code == httpx.codes.INTERNAL_SERVER_ERROR):
                if self._login_data:
                    await self.login(*self._login_data)
                    return await self._request_with_optional_relogin(
                        requests_timeout, request, follow_redirects
                    )
                else:
                    raise errors.AuthError(
                        ".login() before making requests that need "
                        "authorization"
                    )
            else:
                raise http_status_error
        else:
            return response

    async def diary(
            self,
            start: Optional[date] = None,
            end: Optional[date] = None,
            student_id: Optional[int] = None,
            requests_timeout: int = None,
    ) -> schemas.Diary:
        if not start:
            monday = date.today() - timedelta(days=date.today().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)
        if student_id:
            self._student_id = student_id

        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="student/diary",
                params={
                    'studentId': self._student_id,
                    'yearId': self._year_id,
                    'weekStart': start.isoformat(),
                    'weekEnd': end.isoformat(),
                },
            )
        )
        diary_schema = schemas.DiarySchema()
        diary_schema.context['assignment_types'] = self._assignment_types
        diary = diary_schema.load(response.json())
        return diary  # type: ignore

    async def overdue(
            self,
            start: Optional[date] = None,
            end: Optional[date] = None,
            student_id: Optional[int] = None,
            requests_timeout: int = None,
    ) -> List[schemas.Assignment]:
        if not start:
            monday = date.today() - timedelta(days=date.today().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)
        if student_id:
            self._student_id = student_id

        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url='student/diary/pastMandatory',
                params={
                    'studentId': self._student_id,
                    'yearId': self._year_id,
                    'weekStart': start.isoformat(),
                    'weekEnd': end.isoformat(),
                },
            )
        )
        assignments_schema = schemas.AssignmentSchema()
        assignments_schema.context['assignment_types'] = self._assignment_types
        assignments = assignments_schema.load(response.json(), many=True)
        return assignments  # type: ignore

    async def assignment_info(
            self,
            assignment_id: int,
            student_id: Optional[int] = None,
            requests_timeout: int = None,
    ) -> schemas.AssignmentInfo:
        if not student_id:
            student_id = self._student_id

        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url=f"student/diary/assigns/{assignment_id}",
                params={
                    'studentId': student_id,
                },
            )
        )
        assignments_schema = schemas.AssignmentInfoSchema()
        assignments_schema.context['assignment_types'] = self._assignment_types
        assignments = assignments_schema.load(response.json())
        return assignments  # type: ignore

    async def announcements(
            self, take: Optional[int] = -1,
            requests_timeout: int = None) -> List[schemas.Announcement]:
        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="announcements",
                params={"take": take},
            )
        )
        announcements = schemas.AnnouncementSchema().load(response.json(), many=True)
        return announcements  # type: ignore

    async def attachments(
            self, assignment_id: int, student_id: Optional[int] = None,
            requests_timeout: int = None) -> List[schemas.Attachment]:
        if not student_id:
            student_id = self._student_id

        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="POST",
                url='student/diary/get-attachments',
                params={'studentId': student_id},
                json={'assignId': [assignment_id]},
            ),
        )
        response = response.json()
        if not response:
            return []
        attachments_json = response[0]['attachments']
        attachments = schemas.AttachmentSchema().load(attachments_json, many=True)
        return attachments  # type: ignore

    async def download_attachment(
            self, attachment_id: int, assignment_id: int, student_id: Optional[int] = None,
            requests_timeout: int = None):
        await self.attachments(assignment_id, student_id)
        return ((
                    await self._request_with_optional_relogin(
                        requests_timeout,
                        self._wrapped_client.client.build_request(
                            method="GET", url=f"attachments/{attachment_id}"))
                ).content)

    async def init_reports(self, requests_timeout: int = None):
        requester = self._wrapped_client.make_requester(requests_timeout)

        async def parse_filters(report_id: str) -> list[dict[str, str | list[dict[str, str]]]]:
            filters = (await requester(self._wrapped_client.client.build_request(
                method="GET", url="reports/" + report_id.casefold()),)).json()
            filters = filters["filterSources"]
            report_filters = []
            special_filters = ("period", "StartDate", "EndDate", "PCLID")
            exclude_filters = ("PCLID", )
            for filter_ in filters:
                if filter_["filterId"] not in special_filters and filter_["defaultValue"] is not None:
                    report_filters.append({"id": filter_["filterId"], "default": filter_["defaultValue"],
                                           "items": filter_["items"]})
                elif filter_["defaultValue"] is None or filter_["filterId"] in exclude_filters:
                    pass
                elif filter_['filterId'] == 'period':
                    report_filters.append({'id': filter_['filterId'],
                                           'default': filter_['defaultValue'].replace('0000000', '000Z'),
                                           'items': [{'title': f"{datetime.strptime(filter_['defaultValue'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y') + ' - ' + datetime.strptime(filter_['defaultValue'].split('T')[1].split(' - ')[1], '%Y-%m-%d').strftime('%d.%m.%Y')}",
                                                      'value': filter_['defaultValue'].replace('0000000', '000Z')}]})
                else:
                    report_filters.append({"id": filter_["filterId"], "default": filter_["defaultValue"]})
            return report_filters

        response = await requester(self._wrapped_client.client.build_request(method="GET", url="reports"), )
        if response.status_code == 401:
            await self.login(*self._login_data)
            response = await requester(self._wrapped_client.client.build_request(method="GET", url="reports"), )
            if response.status_code == 401:
                raise errors.NetSchoolAPIError("Ошибка получения отчетов")
        response = response.json()
        general_reports = []
        for report in response[0]["reports"]:
            general_reports.append({"id": report["id"], "path": report["id"].casefold(), "title": report["title"],
                                    "filters": await parse_filters(report["id"])})
        common_reports = []
        for report in response[1]["reports"]:
            common_reports.append({"id": report["id"], "path": report["id"].casefold(), "title": report["title"],
                                   "filters": await parse_filters(report["id"])})

        return {"general_title": response[0]["title"], "general": general_reports, "common_title": response[1]["title"],
                "common": common_reports}

    async def report(self, report_url: str, student_id: Optional[int] = None,
                     filters: list[dict[str, str]] = None,
                     requests_timeout: int = None):
        if filters:
            student_id = next((x['value'] for x in filters if x['id'] == 'SID'), None)
        if not student_id:
            student_id = self._student_id
        student = next((x for x in self._students if x['studentId'] == student_id), None)
        payload = {"selectedData": [],
                   "params": [{"name": "SCHOOLYEARID", "value": self._year_id}, {"name": "SERVERTIMEZONE", "value": 3},
                              {"name": "FULLSCHOOLNAME",
                               "value": "АНО СОШ \"Димитриевская\" \n создано в @pravschool_bot"},
                              {"name": "DATEFORMAT", "value": "d\u0001mm\u0001yy\u0001."}]}
        if not filters:
            response = await self._request_with_optional_relogin(requests_timeout,
                                                                 self._wrapped_client.client.build_request(
                                                                     method="GET", url=report_url), )
            response = response.json()
            sid = None
            for item in response['filterSources'][0]['items']:
                if int(item['value']) == int(student_id):
                    sid = item['title']
            payload['selectedData'].append({"filterId": "SID", "filterValue": f"{student_id}",
                                            "filterText": f"{sid}"})
            payload['selectedData'].append({"filterId": "period",
                                            "filterValue": f"{response['filterSources'][2]['defaultValue'].replace('0000000', '000Z')}",
                                            "filterText": f"{datetime.strptime(response['filterSources'][2]['defaultValue'].split('T')[0], '%Y-%m-%d').strftime('%d.%m.%Y') + ' - ' + datetime.strptime(response['filterSources'][2]['defaultValue'].split('T')[1].split(' - ')[1], '%Y-%m-%d').strftime('%d.%m.%Y')}"})
        else:
            for filter_ in filters:
                payload['selectedData'].append({"filterId": filter_['id'], "filterValue": filter_['value'],
                                                "filterText": filter_['text']})
        payload['selectedData'].insert(1, {"filterId": "PCLID", "filterValue": f"{student['classId']}",
                                           "filterText": f"{student['className']}"})
        response = await self._request_with_optional_relogin(requests_timeout,
                                                             self._wrapped_client.client.build_request(
                                                                 "GET", "/signalr/negotiate",
                                                                 params={
                                                                     '_': self._version,
                                                                     'at': self._access_token,
                                                                     'clientProtocol': '1.5',
                                                                     'connectionData': '[{"name":"queuehub"}]', }))
        response = response.json()
        connect_token = response['ConnectionToken']
        try_id = response['ConnectionId'][0]
        query = {'transport': 'serverSentEvents', 'clientProtocol': '1.5', 'at': self._access_token,
                 'connectionToken': connect_token, 'connectionData': '[{"name":"queuehub"}]', 'tid': try_id,
                 '_': self._version, }

        async with self._wrapped_client.client.stream('GET', 'signalr/connect', timeout=20, params=query) as r:
            async for chunk in r.aiter_text():
                if 'initialized' in chunk:
                    await self._wrapped_client.request(requests_timeout, self._wrapped_client.client.build_request(
                        "GET", "signalr/start", params=query))
                    response = await self._wrapped_client.request(requests_timeout,
                                                                  self._wrapped_client.client.build_request(
                                                                      "POST", f"{report_url}/queue",
                                                                      json=payload))
                    task_id = response.json()['taskId']
                    await self._wrapped_client.request(requests_timeout, self._wrapped_client.client.build_request(
                        "POST", "signalr/send", params=query, data={
                            'data': {"H": "queuehub", "M": "StartTask", "A": [task_id], "I": 0}}))
                else:
                    chunk = json.loads(chunk.replace('data: ', ''))
                    if chunk:
                        if chunk['M'] and chunk['M'][0]['M'] == 'complete':
                            await self._wrapped_client.request(requests_timeout,
                                                               self._wrapped_client.client.build_request(
                                                                   "POST", "signalr/abort", params=query))
                            file = await self._wrapped_client.request(requests_timeout,
                                                                      self._wrapped_client.client.build_request(
                                                                          "GET",
                                                                          f"files/{chunk['M'][0]['A'][0]['Data']}"))
                            return file.text

    async def school(self, requests_timeout: int = None) -> schemas.School:
        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url='schools/{0}/card'.format(self._school_id),
            )
        )
        school = schemas.SchoolSchema().load(response.json())
        return school  # type: ignore

    async def logout(self, requests_timeout: int = None):
        try:
            await self._wrapped_client.request(
                requests_timeout,
                self._wrapped_client.client.build_request(
                    method="POST",
                    url='auth/logout',
                )
            )
        except httpx.HTTPStatusError as http_status_error:
            if (
                    http_status_error.response.status_code
                    == httpx.codes.UNAUTHORIZED
            ):
                # Session is dead => we are logged out already
                # OR
                # We are logged out already
                pass
            else:
                raise http_status_error

    async def full_logout(self, requests_timeout: int = None):
        await self.logout(requests_timeout)
        await self._wrapped_client.client.aclose()

    async def schools(
            self, requests_timeout: int = None) -> List[schemas.ShortSchool]:
        resp = await self._wrapped_client.request(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET", url="schools/search",
            )
        )
        schools = schemas.ShortSchoolSchema().load(resp.json(), many=True)
        return schools  # type: ignore

    async def _get_school_id(
            self, school_name: str,
            requester: Requester) -> Dict[str, int]:
        schools = (await requester(
            self._wrapped_client.client.build_request(
                method="GET",
                url="schools/search",
            )
        )).json()

        for school in schools:
            if school["shortName"] == school_name:
                self._school_id = school['id']
                return school["id"]
        raise errors.SchoolNotFoundError(school_name)

    async def download_profile_picture(
            self, user_id: int, buffer: BytesIO,
            requests_timeout: int = None):
        buffer.write((
                         await self._request_with_optional_relogin(
                             requests_timeout,
                             self._wrapped_client.client.build_request(
                                 method="GET",
                                 url="users/photo",
                                 params={"at": self._access_token, "userId": user_id},
                             ),
                             follow_redirects=True,
                         )
                     ).content)

    @property
    def students(self) -> List[Any]:
        return self._students if self._students != [] else None

    @property
    def current_student(self):
        return self._student_id if self._student_id != -1 else None

    @property
    def is_logged(self) -> bool:
        return self._login_data != ()
