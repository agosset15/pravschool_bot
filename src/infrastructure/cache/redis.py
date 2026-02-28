import inspect
from functools import wraps
from typing import (
    Any,
    Callable,
    Coroutine,
    Optional,
    ParamSpec,
    TypeVar,
    Union,
    cast,
    get_type_hints,
)

from adaptix import Retort
from loguru import logger
from redis.asyncio import Redis
from redis.typing import ExpiryT

from src.core.constants import TIME_1M
from src.core.utils import json

from .key_builder import StorageKey

T = TypeVar("T", bound=Any)
P = ParamSpec("P")


def _extract_args(func: Callable, args: tuple, kwargs: dict) -> dict[str, Any]:
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    result = dict(bound_args.arguments)
    result.pop("self", None)
    return result


def provide_cache(  # noqa: C901
    prefix: Optional[str] = None,
    ttl: ExpiryT = TIME_1M,
    key_builder: Optional[Union[Callable[..., Any], type[StorageKey]]] = None,
) -> Callable[[Callable[P, Coroutine[Any, Any, T]]], Callable[P, Coroutine[Any, Any, T]]]:
    def decorator(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:
        return_type = get_type_hints(func).get("return", Any)

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            self: Any = args[0]
            retort: Retort = self.retort
            redis: Redis = self.redis

            if isinstance(key_builder, type) and issubclass(key_builder, StorageKey):
                func_args = _extract_args(func, args, kwargs)
                try:
                    key_obj = key_builder(**func_args)
                    key = retort.dump(key_obj)
                except Exception:
                    key = "unknown_key"
                    for arg_val in func_args.values():
                        try:
                            key_obj = key_builder.from_obj(arg_val)
                            key = retort.dump(key_obj)
                            break
                        except Exception:
                            continue
            elif key_builder:
                suffix = str(key_builder(*args, **kwargs))
                key = f"cache:{prefix or func.__name__}:{suffix}"
            else:
                key_parts = ["cache", prefix or func.__name__]
                key_parts.extend(map(str, args[1:]))
                key_parts.extend(map(str, kwargs.values()))
                key = ":".join(key_parts)

            try:
                cached_data = await redis.get(key)
                if cached_data is not None:
                    logger.debug(f"Cache hit for key '{key}'")
                    raw_json = json.decode(cached_data)
                    return cast(T, retort.load(raw_json, return_type))
            except Exception as e:
                logger.warning(f"Cache read failed for key '{key}' error '{e}'")

            logger.debug(f"Cache miss for key '{key}', executing function")
            result = await func(*args, **kwargs)

            try:
                serialized_data = retort.dump(result, return_type)
                await redis.setex(name=key, time=ttl, value=json.encode(serialized_data))
                logger.debug(f"Result cached for key '{key}' with ttl '{ttl}'")
            except Exception as e:
                logger.warning(f"Cache write failed for key '{key}' error '{e}'")

            return result

        return wrapper

    return decorator


def invalidate_cache(  # noqa: C901
    key_builder: Union[str, list[str], type[StorageKey]],
) -> Callable[[Callable[P, Coroutine[Any, Any, T]]], Callable[P, Coroutine[Any, Any, T]]]:
    def decorator(func: Callable[P, Coroutine[Any, Any, T]]) -> Callable[P, Coroutine[Any, Any, T]]:  # noqa: C901
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:  # noqa: C901
            result = await func(*args, **kwargs)
            self: Any = args[0]
            redis: Redis = self.redis
            retort: Retort = self.retort

            try:
                if isinstance(key_builder, type) and issubclass(key_builder, StorageKey):
                    func_args = _extract_args(func, args, kwargs)

                    key = None
                    try:
                        key_obj = key_builder(**func_args)
                        key = retort.dump(key_obj)
                    except Exception:
                        for val in func_args.values():
                            try:
                                key_obj = key_builder.from_obj(val)
                                key = retort.dump(key_obj)
                                break
                            except Exception:
                                continue

                    if key:
                        await redis.delete(key)
                        logger.debug(f"Invalidated specific cache key '{key}'")

                elif isinstance(key_builder, (str, list)):
                    prefixes = [key_builder] if isinstance(key_builder, str) else key_builder
                    for p in prefixes:
                        pattern = f"cache:{p}*"
                        keys = []

                        async for k in redis.scan_iter(match=pattern):
                            keys.append(k)

                        if keys:
                            await redis.delete(*keys)
                            logger.debug(f"Invalidated cache for prefix '{p}', count '{len(keys)}'")
                        else:
                            logger.debug(
                                f"No cache keys found to invalidate for pattern '{pattern}'"
                            )
            except Exception as e:
                logger.warning(f"Cache invalidation failed for '{key_builder}' error '{e}'")

            return result

        return wrapper

    return decorator