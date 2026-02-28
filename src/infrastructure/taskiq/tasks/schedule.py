from pathlib import Path
from typing import Optional

from dishka.integrations.taskiq import FromDishka, inject
from loguru import logger

from src.core.dto import MessagePayloadDto
from src.core.enums import SystemNotificationType
from src.infrastructure.parsers.schedule import ExcelParser
from src.infrastructure.taskiq.broker import broker
from src.services.notification import NotificationService
from src.services.schedule import ScheduleService


@broker.task()
@inject
async def parse_schedule(
    excel_file_path: Path,
    positional_data: Optional[str],
    notification_service: FromDishka[NotificationService],
    schedule_service: FromDishka[ScheduleService],
) -> None:
    logger.info(f"Starting parse_schedule task with excel_file_path={excel_file_path}")

    parser = ExcelParser(excel_file_path)
    try:
        await schedule_service.delete_all()
        await schedule_service.create_recursive(
            await parser.parse_all()
        )
    except Exception as e:
        logger.error(f"Error parsing schedule: {e}")
        await notification_service.system_notify(
            MessagePayloadDto(
                i18n_key="ntf-error.parsing",
                i18n_kwargs={"error": str(e)}),
            SystemNotificationType.ERROR
        )
        return
    await notification_service.system_notify(
        MessagePayloadDto(i18n_key="ntf-success.parsing"),
        SystemNotificationType.TASK_SUCCEED
    )
