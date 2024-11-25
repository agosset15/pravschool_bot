from tg_bot.models import Schedule


def find_free_rooms(rooms: list[Schedule]) -> list[list[list[str]]]:
    r = [[[] for _1 in range(10)] for _ in range(6)]
    for room in rooms:
        for day_number, day in enumerate(room.days):
            for lesson_number, lesson in enumerate(day.lessons):
                if lesson.name is None:
                    r[day_number][lesson_number].append(lesson.room)
    return r
