from ..config import ns, bot
from db.methods.get import get_students_with_duty_notification, get_student_by_telegram_id


async def send_user_ns_duty():
    ids = get_students_with_duty_notification()
    for z in ids:
        login_data = get_student_by_telegram_id(z.id)
        await ns.login(login_data.login, login_data.password, 'Свято-Димитриевская школа')
        ass = await ns.overdue()
        await ns.logout()
        await ns.logout()
        await ns.logout()
        if ass is not None:
            arr = []
            for i in ass:
                date = i.deadline
                await ns.login(login_data.login, login_data.password, 'Свято-Димитриевская школа')
                diary = await ns.diary(start=date)
                await ns.logout()
                await ns.logout()
                await ns.logout()
                day = diary.schedule[0]
                lesson = day.lessons
                for less in lesson:
                    assig = less.assignments
                    if assig:
                        for qw in assig:
                            if qw.id == i.id:
                                arr.append(f'Долг -- {qw.type} по предмету {less.subject}:\n{qw.content}')

            text = "\n\n".join(arr)
            await bot.send_message(ids[z][0], f"Вот ваши долги на данное время:\n\n{text}")
        else:
            await bot.send_message(ids[z][0], "На данный момент просроченных заданий нет!")
        await ns.logout()
        await ns.logout()
