from typing import Any

from taskiq import AsyncResultBackend, SmartRetryMiddleware
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from src.core.config import AppConfig
from src.infrastructure.taskiq.middlewares import ErrorMiddleware


def create_broker(config: AppConfig) -> RedisStreamBroker:
    result_backend: AsyncResultBackend[Any] = RedisAsyncResultBackend(
        redis_url=config.redis.dsn,
        keep_results=False,
        result_ex_time=3600,
    )

    stream_broker = RedisStreamBroker(
        url=config.redis.dsn,
        maxlen=1000,
    ).with_result_backend(result_backend)

    return stream_broker


broker = create_broker(config=AppConfig.get())

broker.with_middlewares(
    *(
        ErrorMiddleware(),
        SmartRetryMiddleware(
            default_retry_count=5,
            default_delay=15,
            use_jitter=True,
            use_delay_exponent=True,
            max_delay_exponent=120,
        ),
    )
)