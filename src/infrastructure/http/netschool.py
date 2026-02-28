from datetime import date, timedelta
from hashlib import md5
from io import BytesIO
from typing import Any, Dict, List, Optional

import httpx
from httpx import AsyncClient, HTTPStatusError, Response
from loguru import logger
from orjson import JSONDecodeError
from pydantic import TypeAdapter

from src.core.exceptions import AuthError, NetSchoolAPIError, SchoolNotFoundError
from src.core.utils import json
from src.core.utils.converters import dashes_to_dots_date
from src.core.utils.time import date_now

__all__ = ["NetSchoolAPI"]

from .base import AsyncClientWrapper, Requester
from .schemas import (
    Announcement,
    Assignment,
    AssignmentInfo,
    Attachment,
    Diary,
    School,
    ShortSchool,
    Student,
)

announcements_schema = TypeAdapter(list[Announcement])
assignments_schema = TypeAdapter(list[Assignment])
attachments_schema = TypeAdapter(list[Attachment])
schools_schema = TypeAdapter(list[ShortSchool])
students_schema = TypeAdapter(list[Student])


class NetSchoolAPI:
    def __init__(self,
                 url: str,
                 username: str,
                 password: bytes,
                 student_id: int,
                 school_id: int,
                 default_requests_timeout: Optional[int] = None
                 ):
        url = url.rstrip("/")
        self._wrapped_client = AsyncClientWrapper(
            async_client=AsyncClient(
                base_url=f"{url}/webapi",
                headers={"user-agent": "NetSchoolAPI/5.0.3", "referer": url},
                event_hooks={"response": [self._die_on_bad_status]},
                verify=False
            ),
            default_requests_timeout=default_requests_timeout,
        )

        self._student_id = student_id
        self._students: List[Student] = []
        self._year_id = -1
        self._school_id = school_id
        self._version = -1

        self.username: str = username
        self.password: bytes = password

        self._assignment_types: Dict[int, str] = {}
        self.access_token = None

    async def __aenter__(self) -> "NetSchoolAPI":
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb):
        await self.logout()

    def get_session_data(self) -> Dict[str, str]:
        data = dict(self._wrapped_client.client.cookies)
        data["at"] = self.access_token
        return data

    async def set_session_data(self, session_data: Dict[str, str]) -> None:
        self._wrapped_client.client.cookies = session_data
        self.access_token = session_data.get("at", "0")
        self._wrapped_client.client.headers["at"] = self.access_token
        try:
            await self.init(10)
        except HTTPStatusError:
            await self.login(20)

    async def login(self, requests_timeout: Optional[int] = None) -> None:
        requester = self._wrapped_client.make_requester(requests_timeout)
        # Getting the `NSSESSIONID` cookie for `auth/getdata`
        await requester(self._wrapped_client.client.build_request(
            method="GET", url="logindata"
        ))

        # Getting the `NSSESSIONID` cookie for `login`
        response = await requester(self._wrapped_client.client.build_request(
            method="POST", url="auth/getdata"
        ))
        login_meta = response.json()
        salt = login_meta.pop("salt")
        self._version = login_meta["ver"]
        pw2 = md5(salt.encode() + self.password).hexdigest()
        pw = pw2[: len(self.password)]
        try:
            response = await requester(
                self._wrapped_client.client.build_request(
                    method="POST",
                    url="login",
                    data={
                        "loginType": 1,
                        "scid": self._school_id,
                        "un": self.username,
                        "pw": pw,
                        "pw2": pw2,
                        **login_meta,
                    },
                )
            )
        except HTTPStatusError as http_status_error:
            if http_status_error.response.status_code == httpx.codes.CONFLICT:
                try:
                    response_json = http_status_error.response.json()
                except httpx.ResponseNotRead:
                    pass
                else:
                    if "message" in response_json:
                        raise AuthError(
                            http_status_error.response.json()["message"]
                        )
                raise AuthError()
            else:
                raise http_status_error
        auth_result = response.json()

        if "at" not in auth_result:
            raise AuthError(auth_result["message"])

        self.access_token = auth_result["at"]
        self._wrapped_client.client.headers["at"] = auth_result["at"]
        await self.init(requests_timeout)

    async def init(self, requests_timeout: Optional[int] = None) -> None:
        requester = self._wrapped_client.make_requester(requests_timeout)
        response = await requester(self._wrapped_client.client.build_request(
            method="GET", url="student/diary/init",
        ))
        diary_info = response.json()
        self._students = students_schema.validate_python(diary_info["students"])
        self._student_id = diary_info["currentStudentId"]

        for i, student in enumerate(self._students):
            data = {"filterId": "SID",
                    "filterValue": f"{student.id}",
                    "filterText": f"{student.name}"}
            clid = await self._request_with_optional_relogin(requests_timeout,
                                                             self._wrapped_client.client.build_request(
                                                                 method="POST",
                                                                 url="reports/studenttotal/initfilters",
                                                                 json={"params": None,
                                                                       "selectedData": [data]}))
            resp = clid.json()
            self._students[i].class_id = int(resp[0]["items"][0]["value"])
            self._students[i].class_name = str(resp[0]["items"][0]["title"])

        response = await requester(self._wrapped_client.client.build_request(
            method="GET", url="years/current"
        ))
        year_reference = response.json()
        self._year_id = year_reference["id"]

        response = await requester(self._wrapped_client.client.build_request(
            method="GET", url="grade/assignment/types", params={"all": False},
        ))
        assignment_reference = response.json()
        self._assignment_types = {
            assignment["id"]: assignment["name"]
            for assignment in assignment_reference
        }

    async def diary(
            self,
            start: Optional[date] = None,
            end: Optional[date] = None,
            student_id: Optional[int] = None,
            requests_timeout: Optional[int] = None,
    ) -> Diary:
        if not start:
            start = date_now() - timedelta(days=date_now().weekday())
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
                    "vers": 1769362161360,
                    "studentId": self._student_id,
                    "yearId": self._year_id,
                    "weekStart": start.isoformat(),
                    "weekEnd": end.isoformat(),
                },
            )
        )
        diary = Diary.model_validate(response.json(),
                                             context={"assignment_types": self._assignment_types})
        return diary

    async def overdue(
            self,
            start: Optional[date] = None,
            end: Optional[date] = None,
            student_id: Optional[int] = None,
            requests_timeout: Optional[int] = None,
    ) -> List[Assignment]:
        if not start:
            monday = date_now() - timedelta(days=date_now().weekday())
            start = monday
        if not end:
            end = start + timedelta(days=5)
        if student_id:
            self._student_id = student_id

        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="student/diary/pastMandatory",
                params={
                    "studentId": self._student_id,
                    "yearId": self._year_id,
                    "weekStart": start.isoformat(),
                    "weekEnd": end.isoformat(),
                },
            )
        )
        assignments = assignments_schema.validate_python(
            response.json(),
            context={"assignment_types": self._assignment_types}
        )
        return assignments

    async def assignment_info(
            self,
            assignment_id: int,
            student_id: Optional[int] = None,
            requests_timeout: Optional[int] = None,
    ) -> AssignmentInfo:
        if not student_id:
            student_id = self._student_id

        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url=f"student/diary/assigns/{assignment_id}",
                params={
                    "studentId": student_id,
                },
            )
        )
        assignment = AssignmentInfo.model_validate(
            response.json(),
            context={"assignment_types": self._assignment_types}
        )
        return assignment

    async def announcements(
            self, take: Optional[int] = -1,
            requests_timeout: Optional[int] = None) -> List[Announcement]:
        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="announcements",
                params={"take": take},
            )
        )
        announcements = announcements_schema.validate_python(response.json())
        return announcements

    async def attachments(
            self, assignment_id: int, student_id: Optional[int] = None,
            requests_timeout: Optional[int] = None) -> List[Attachment]:
        if not student_id:
            student_id = self._student_id

        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="POST",
                url="student/diary/get-attachments",
                params={"studentId": student_id},
                json={"assignId": [assignment_id]},
            ),
        )
        response = response.json()
        if not response:
            return []
        attachments_json = response[0]["attachments"]
        attachments = attachments_schema.validate_python(attachments_json)
        return attachments

    async def download_attachment(
            self, attachment_id: int, assignment_id: int, student_id: Optional[int] = None,
            requests_timeout: Optional[int] = None) -> bytes:
        await self.attachments(assignment_id, student_id)
        return ((
                    await self._request_with_optional_relogin(
                        requests_timeout,
                        self._wrapped_client.client.build_request(
                            method="GET", url=f"attachments/{attachment_id}"))
                ).content)

    async def init_reports(self, requests_timeout: Optional[int] = None) -> Dict[str, Any]:
        requester = self._wrapped_client.make_requester(requests_timeout)

        try:
            response = await self._fetch_reports_data(requester)
        except NetSchoolAPIError:
            raise

        response_data = response.json()

        general_group = response_data[0]
        common_group = response_data[1]

        general_reports = await self._process_report_group(requester, general_group)
        common_reports = await self._process_report_group(requester, common_group)

        return {
            "general_title": general_group["title"],
            "general": general_reports,
            "common_title": common_group["title"],
            "common": common_reports
        }

    async def report(self, report_id: str, student_id: Optional[int] = None,
                     filters: Optional[List[Dict[str, str]]] = None,
                     requests_timeout: Optional[int] = None) -> str:
        """Generates a report, handles SignalR negotiation, and returns the file content."""

        student = self._resolve_student_context(student_id, filters)

        payload = await self._build_report_payload(report_id, student, filters, requests_timeout)

        # 3. Execute Report via SignalR
        return await self._execute_signalr_session(report_id, payload, requests_timeout)

    async def school(self, requests_timeout: Optional[int] = None) -> School:
        response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET",
                url="schools/{0}/card".format(self._school_id),
            )
        )
        school = School.model_validate(response.json())
        return school

    async def logout(self, requests_timeout: Optional[int] = None):
        try:
            await self._wrapped_client.request(
                requests_timeout,
                self._wrapped_client.client.build_request(
                    method="POST",
                    url="auth/logout",
                )
            )
        except httpx.HTTPStatusError as http_status_error:
            if (
                    http_status_error.response.status_code
                    == httpx.codes.UNAUTHORIZED
            ):
                pass
            else:
                raise http_status_error

    async def full_logout(self, requests_timeout: Optional[int] = None):
        await self.logout(requests_timeout)
        await self._wrapped_client.client.aclose()

    async def schools(
            self, requests_timeout: Optional[int] = None) -> List[ShortSchool]:
        resp = await self._wrapped_client.request(
            requests_timeout,
            self._wrapped_client.client.build_request(
                method="GET", url="schools/search",
            )
        )
        schools = schools_schema.validate_python(resp.json())
        return schools

    async def download_profile_picture(
            self, user_id: int, buffer: BytesIO,
            requests_timeout: Optional[int] = None):
        buffer.write((
                         await self._request_with_optional_relogin(
                             requests_timeout,
                             self._wrapped_client.client.build_request(
                                 method="GET",
                                 url="users/photo",
                                 params={"at": self.access_token, "userId": user_id},
                             ),
                             follow_redirects=True,
                         )
                     ).content)

    @property
    def students(self) -> Optional[List[Student]]:
        return self._students if self._students != [] else None

    @property
    def current_student(self) -> int:
        if self._student_id == -1:
            raise NetSchoolAPIError("Not logged in!")
        return self._student_id

    #

    @staticmethod
    async def _die_on_bad_status(response: Response):
        if not response.is_redirect:
            response.raise_for_status()

    async def _request_with_optional_relogin(
            self, requests_timeout: Optional[int], request: httpx.Request,
            follow_redirects=False):
        if not requests_timeout:
            requests_timeout = 120
        try:
            response = await self._wrapped_client.request(
                requests_timeout, request, follow_redirects
            )
        except httpx.HTTPStatusError as http_status_error:
            logger.debug(http_status_error)
            if (http_status_error.response.status_code == httpx.codes.UNAUTHORIZED or
                    http_status_error.response.status_code == httpx.codes.INTERNAL_SERVER_ERROR):
                await self.login()
                return await self._request_with_optional_relogin(
                    requests_timeout, request, follow_redirects
                )
            else:
                raise http_status_error
        else:
            return response

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
                self._school_id = school["id"]
                return school["id"]
        raise SchoolNotFoundError(school_name)

    async def _fetch_reports_data(self, requester) -> httpx.Response:
        """Fetches the reports list with 401 retry logic."""
        request = self._wrapped_client.client.build_request(method="GET", url="reports")

        try:
            return await requester(request)
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 401:
                await self.login()
                try:
                    return await requester(request)
                except httpx.HTTPStatusError:
                    raise NetSchoolAPIError("Ошибка получения отчетов")
            raise

    async def _process_report_group(self, requester, group_data: dict) -> List[dict]:
        """Processes a list of reports from a specific group (general or common)."""
        processed_reports = []
        for report in group_data["reports"]:
            report_id = report["id"]
            filters = await self._parse_report_filters(requester, report_id)

            processed_reports.append({
                "id": report_id,
                "path": report_id.casefold(),
                "title": report["title"],
                "filters": filters
            })
        return processed_reports

    async def _parse_report_filters(self, requester, report_id: str) -> List[dict]:
        """Fetches and parses filters for a specific report ID."""
        # TODO: !!! student_id for filters
        url = f"reports/{report_id.casefold()}"
        request = self._wrapped_client.client.build_request(method="GET", url=url)

        response = await requester(request)
        data = response.json()

        filter_sources = data.get("filterSources", [])
        report_filters = []

        # Configuration constants
        special_filters = ("period", "StartDate", "EndDate", "PCLID")
        exclude_filters = ("PCLID",)

        for filter_item in filter_sources:
            f_id = filter_item["filterId"]
            default_val = filter_item["defaultValue"]

            # Skip excluded filters or those without default values
            if f_id in exclude_filters or default_val is None:
                continue

            # Handle 'period' specifically
            if f_id == "period":
                report_filters.append(self._build_period_filter(filter_item))
                continue

            # Handle standard filters with items
            if f_id not in special_filters:
                report_filters.append({
                    "id": f_id,
                    "default": default_val,
                    "items": filter_item["items"]
                })
            else:
                # Handle other special filters without items
                report_filters.append({
                    "id": f_id,
                    "default": default_val
                })

        return report_filters

    @staticmethod
    def _build_period_filter(filter_item: dict) -> dict:
        """Constructs the specific structure for the 'period' filter."""
        raw_value = filter_item["defaultValue"]
        # Normalize timestamp format
        normalized_value = raw_value.replace("0000000", "000Z")

        # Parse dates for title formatting
        try:
            date_part, time_part = raw_value.split("T")
            end_date_str = time_part.split(" - ")[1]

            start_date = dashes_to_dots_date(date_part)
            end_date = dashes_to_dots_date(end_date_str)
            title = f"{start_date} - {end_date}"
        except (ValueError, IndexError):
            # Fallback if date parsing fails, preserving original logic flow
            title = normalized_value

        return {
            "id": filter_item["filterId"],
            "default": normalized_value,
            "items": [{"title": title, "value": normalized_value}]
        }

    def _resolve_student_context(self, arg_id: Optional[int],
                                 filters: Optional[List[Dict]]) -> Student:
        """Determines the correct student ID and retrieves the student object."""
        # Priority: 1. Filters SID, 2. Argument ID, 3. Instance Default
        if filters:
            sid_filter = self._find_by_key(key_name="id", key="SID", data=filters)
            if sid_filter:
                arg_id = int(sid_filter["value"])

        if not arg_id:
            arg_id = self._student_id

        student_id = int(arg_id)
        student: Optional[Student] = next((s for s in self._students if s.id == student_id), None)

        if not student:
            raise NetSchoolAPIError("Student not found")

        return student

    async def _build_report_payload(
            self,
            report_id: str,
            student: Student,
            filters: Optional[List],
            requests_timeout: Optional[int]
    ) -> Dict:
        """Constructs the JSON payload required for the report task."""
        payload = {
            "selectedData": [],
            "params": [
                {"name": "SCHOOLYEARID", "value": str(self._year_id)},
                {"name": "SERVERTIMEZONE", "value": str(3)},
                {"name": "FULLSCHOOLNAME", "value": 'АНО СОШ "Димитриевская" \n '
                                                    'создано в @pravschool_bot'},
                {"name": "DATEFORMAT", "value": """d\\u0001mm\\u0001yy\\u0001."""}
            ]
        }

        if not filters:
            # Fetch report definition to get default SID title and Period
            response = await self._request_with_optional_relogin(
                requests_timeout,
                self._wrapped_client.client.build_request(method="GET", url=f"reports/{report_id}")
            )
            data = response.json()
            filter_sources = data["filterSources"]

            # Find Student ID Title
            sid_item = self._find_by_key("value", str(student.id), filter_sources[0]["items"])
            sid_title = sid_item["title"] if sid_item else str(student.id)

            # Find Period Default (Search by ID for robustness, originally index 2)
            period_source = self._find_by_key("filterId", "period", filter_sources)
            period_raw = period_source["defaultValue"] if period_source else ""

            payload["selectedData"].append({
                "filterId": "SID",
                "filterValue": str(student.id),
                "filterText": sid_title
            })
            payload["selectedData"].append({
                "filterId": "period",
                "filterValue": period_raw.replace("0000000", "000Z"),
                "filterText": self._format_period_string(period_raw)
            })
        else:
            for f in filters:
                payload["selectedData"].append({
                    "filterId": f["id"],
                    "filterValue": f["value"],
                    "filterText": f["text"]
                })

        # Insert PCLID at specific index 1
        payload["selectedData"].insert(1, {
            "filterId": "PCLID",
            "filterValue": str(student.class_id),
            "filterText": student.class_name
        })

        return payload

    @staticmethod
    def _format_period_string(raw_value: str) -> str:
        """Formats the period date string consistently (DD.MM.YYYY - DD.MM.YYYY)."""
        if not raw_value:
            return ""
        try:
            date_part, time_part = raw_value.split("T")
            end_date_str = time_part.split(" - ")[1]
            start = dashes_to_dots_date(date_part)  # noqa: DTZ007
            end = dashes_to_dots_date(end_date_str)
            return f"{start} - {end}"
        except (ValueError, IndexError):
            return raw_value

    async def _execute_signalr_session(self, report_id: str, payload: Dict,
                                       requests_timeout: Optional[int]) -> str:
        """Handles SignalR negotiation, connection, task queuing, and file retrieval."""
        requester = self._wrapped_client.make_requester(requests_timeout)

        # 1. Negotiate Connection
        neg_response = await self._request_with_optional_relogin(
            requests_timeout,
            self._wrapped_client.client.build_request(
                "GET", "/signalr/negotiate",
                params={
                    "_": self._version,
                    "at": self.access_token,
                    "clientProtocol": "1.5",
                    "connectionData": '[{"name":"queuehub"}]'
                }
            )
        )
        neg_data = neg_response.json()
        connect_token = neg_data["ConnectionToken"]
        connection_id_prefix = neg_data["ConnectionId"][0]

        # 2. Prepare SignalR Query Params
        query = {
            "transport": "serverSentEvents",
            "clientProtocol": "1.5",
            "at": self.access_token,
            "connectionToken": connect_token,
            "connectionData": '[{"name":"queuehub"}]',
            "tid": connection_id_prefix,
            "_": self._version,
        }

        # 3. Connect and Listen for Task Completion
        async with self._wrapped_client.client.stream(
                "GET", "signalr/connect", timeout=30, params=query
        ) as r:
            async for chunk in r.aiter_text():
                if "initialized" in chunk:
                    # Connection Established: Start Task
                    await requester(self._wrapped_client.client.build_request(
                        "GET", "signalr/start", params=query
                    ))
                    task_response = await requester(self._wrapped_client.client.build_request(
                        "POST", f"reports/{report_id}/queue", json=payload
                    ))
                    if task_response.status_code == 500:
                        logger.error(task_response.reason_phrase)

                    task_id = task_response.json()["taskId"]

                    await requester(self._wrapped_client.client.build_request(
                        "POST", "signalr/send", params=query,
                        data={"data": {"H": "queuehub", "M": "StartTask", "A": [task_id], "I": 0}}
                    ))
                else:
                    # Check for Completion Message
                    try:
                        content = chunk.replace("data: ", "")
                        if not content:
                            continue
                        message = json.decode(content)

                        if message.get("M") and message["M"][0]["M"] == "complete":
                            # Task Complete: Abort and Download
                            await requester(
                                self._wrapped_client.client.build_request(
                                    "POST", "signalr/abort", params=query
                                ))

                            file_id = message["M"][0]["A"][0]["Data"]
                            file = await requester(self._wrapped_client.client.build_request(
                                "GET", f"files/{file_id}"
                            ))
                            return file.text
                    except JSONDecodeError:
                        continue

        raise NetSchoolAPIError("Report generation failed or timed out")

    @staticmethod
    def _find_by_key(
            key_name: str, key: str, data: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        for item in data:
            if item[key_name] == key:
                return item
        return None