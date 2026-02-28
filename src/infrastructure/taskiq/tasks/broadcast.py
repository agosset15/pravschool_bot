import asyncio
from typing import Optional, cast

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from dishka.integrations.taskiq import FromDishka, inject
from loguru import logger

from src.core.constants import BATCH_DELAY, BATCH_SIZE_20
from src.core.dto import BroadcastDto
from src.core.enums import BroadcastMessageStatus, BroadcastStatus
from src.infrastructure.taskiq.broker import broker


@broker.task
@inject(patch_module=True)
async def send_broadcast_task(
    broadcast: BroadcastDto,
    plan_id: Optional[int],
    broadcast_dao: FromDishka[BroadcastDao],
    get_broadcast_audience_users: FromDishka[GetBroadcastAudienceUsers],
    initialize_broadcast_messages: FromDishka[InitializeBroadcastMessages],
    update_broadcast_message_status: FromDishka[UpdateBroadcastMessageStatus],
    finish_broadcast: FromDishka[FinishBroadcast],
    notifier: FromDishka[Notifier],
) -> None:
    task_id = broadcast.task_id

    users = await get_broadcast_audience_users.system(
        GetBroadcastAudienceUsersDto(broadcast.audience, plan_id)
    )
    users = users * 5
    if not users:
        logger.warning(f"No users found for broadcast '{task_id}'")
        await finish_broadcast.system(FinishBroadcastDto(task_id, BroadcastStatus.COMPLETED))
        return

    messages = [
        BroadcastMessageDto(
            user_telegram_id=user.telegram_id,
            status=BroadcastMessageStatus.PENDING,
        )
        for user in users
    ]

    messages = await initialize_broadcast_messages.system(
        InitializeBroadcastMessagesDto(task_id, messages)
    )

    total_users = len(users)
    loop = asyncio.get_running_loop()
    start_time = loop.time()
    total_retry_time = 0.0
    semaphore = asyncio.Semaphore(BATCH_SIZE_20)

    logger.info(f"Started sending broadcast '{task_id}', total users: {total_users}")

    async def send_one(user: UserDto) -> tuple:
        nonlocal total_retry_time
        status = BroadcastMessageStatus.FAILED
        msg_id = None
        retry_time_for_user = 0.0

        while True:
            try:
                async with semaphore:
                    tg_message = await notifier.notify_user(user, payload=broadcast.payload)

                if tg_message:
                    status = BroadcastMessageStatus.SENT
                    msg_id = tg_message.message_id

                return user.telegram_id, status, msg_id, retry_time_for_user

            except TelegramRetryAfter as error:
                wait_time = error.retry_after + BATCH_DELAY
                logger.warning(f"Flood wait {error.retry_after}s for user '{user.telegram_id}'")
                await asyncio.sleep(wait_time)
                retry_time_for_user += wait_time
                total_retry_time += wait_time
            except Exception:
                logger.exception(f"Failed to send to '{user.telegram_id}'")
                return user.telegram_id, status, msg_id, retry_time_for_user

    for i, batch in enumerate(chunked(users, BATCH_SIZE_20), start=1):
        if i % 5 == 0:
            current = await broadcast_dao.get_by_task_id(task_id)
            if not current or current.status == BroadcastStatus.CANCELED:
                logger.info(f"Broadcast '{task_id}' was canceled")
                break

        tasks = [asyncio.create_task(send_one(user)) for user in batch]
        results = await asyncio.gather(*tasks)

        updates = UpdateBroadcastMessageStatusDto(
            task_id=task_id,
            messages=[
                BroadcastMessageDto(
                    id=next(m.id for m in messages if m.user_telegram_id == tg_id),
                    user_telegram_id=tg_id,
                    status=status,
                    message_id=msg_id,
                )
                for tg_id, status, msg_id, _ in results
            ],
        )

        await update_broadcast_message_status.system(updates)

        sent_count = sum(1 for _, status, _, _ in results if status == BroadcastMessageStatus.SENT)
        failed_count = len(results) - sent_count
        batch_retry_time = sum(r[3] for r in results)

        logger.info(
            f"Batch {i}: sent={sent_count}, failed={failed_count}, "
            f"retry_time={batch_retry_time:.2f}s"
        )

    total_elapsed = loop.time() - start_time
    await finish_broadcast.system(FinishBroadcastDto(task_id, BroadcastStatus.COMPLETED))
    logger.success(
        f"Broadcast '{task_id}' finished in {total_elapsed:.2f}s "
        f"with total retry time {total_retry_time:.2f}s"
    )


@broker.task
@inject(patch_module=True)
async def delete_broadcast_task(
    broadcast: BroadcastDto,
    bot: FromDishka[Bot],
    bulk_update_broadcast_messages: FromDishka[BulkUpdateBroadcastMessages],
) -> tuple[int, int, int]:
    broadcast_id = cast(int, broadcast.id)

    if not broadcast.messages:
        logger.error(f"Messages list is empty for broadcast '{broadcast_id}', aborting")
        raise ValueError(f"Broadcast '{broadcast_id}' messages is empty")

    logger.info(f"Started deleting messages for broadcast '{broadcast_id}'")

    deleted_count = 0
    total_messages = len(broadcast.messages)
    total_retry_time = 0.0

    loop = asyncio.get_running_loop()
    start_time = loop.time()
    semaphore = asyncio.Semaphore(BATCH_SIZE_20)

    async def delete_one(message: BroadcastMessageDto) -> tuple[BroadcastMessageDto, float]:
        nonlocal total_retry_time
        retry_time_for_msg = 0.0

        if (
            message.status not in (BroadcastMessageStatus.SENT, BroadcastMessageStatus.EDITED)
            or not message.message_id
        ):
            return message, retry_time_for_msg

        while True:
            try:
                async with semaphore:
                    if await bot.delete_message(
                        chat_id=message.user_telegram_id, message_id=message.message_id
                    ):
                        message.status = BroadcastMessageStatus.DELETED

                return message, retry_time_for_msg

            except TelegramRetryAfter as error:
                wait_time = error.retry_after + BATCH_DELAY
                logger.warning(
                    f"Flood wait {error.retry_after}s for user '{message.user_telegram_id}'"
                )
                await asyncio.sleep(wait_time)
                retry_time_for_msg += wait_time
                total_retry_time += wait_time

            except Exception:
                logger.exception(
                    f"Exception deleting message for user '{message.user_telegram_id}'"
                )
                return message, retry_time_for_msg

    for i, batch in enumerate(chunked(broadcast.messages, BATCH_SIZE_20), start=1):
        tasks = [asyncio.create_task(delete_one(m)) for m in batch]
        results = await asyncio.gather(*tasks)

        updated_messages = [r[0] for r in results]
        batch_retry_time = sum(r[1] for r in results)

        await bulk_update_broadcast_messages.system(updated_messages)

        batch_deleted = sum(
            1 for m in updated_messages if m.status == BroadcastMessageStatus.DELETED
        )
        deleted_count += batch_deleted

        logger.info(f"Batch {i}: deleted={batch_deleted}, retry_time={batch_retry_time:.2f}s")

        if batch_retry_time == 0:
            await asyncio.sleep(BATCH_DELAY)

    total_elapsed = loop.time() - start_time
    logger.success(
        f"Deletion finished for broadcast '{broadcast_id}' "
        f"Total: {total_messages}, Deleted: {deleted_count}, "
        f"Time: {total_elapsed:.2f}s, Retry time: {total_retry_time:.2f}s"
    )

    return total_messages, deleted_count, total_messages - deleted_count


@broker.task(schedule=[{"cron": "0 0 */7 * *"}])
@inject(patch_module=True)
async def delete_broadcasts_task(clear_old_broadcasts: FromDishka[ClearOldBroadcasts]) -> None:
    await clear_old_broadcasts.system()