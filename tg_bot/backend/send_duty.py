from ..config import send_duty
from db.methods.get import get_students_with_duty_notification


async def send_user_ns_duty():
    ids = get_students_with_duty_notification()
    for z in ids:
        await send_duty(z)
