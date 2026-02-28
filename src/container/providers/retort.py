from datetime import datetime
from typing import Any

from adaptix import (
    ExtraSkip,
    Retort,
    as_is_dumper,
    as_is_loader,
    dumper,
    loader,
    name_mapping,
)
from adaptix._internal.provider.loc_stack_filtering import OriginSubclassLSC
from adaptix.conversion import ConversionRetort
from dishka import Provider, Scope, provide
from pydantic import SecretStr

from src.infrastructure.cache.key_builder import StorageKey, serialize_storage_key


class RetortProvider(Provider):
    scope = Scope.APP

    @provide
    def get_retort(self) -> Retort:
        def secret_dumper(value: Any) -> Any:
            if isinstance(value, SecretStr):
                return value.get_secret_value()
            return value

        retort = Retort(
            recipe=[
                as_is_loader(datetime),
                as_is_dumper(datetime),
                name_mapping(extra_in=ExtraSkip()),
                #
                dumper(OriginSubclassLSC(StorageKey), serialize_storage_key),
                #
                loader(SecretStr, SecretStr),
                dumper(SecretStr, lambda v: v.get_secret_value()),
                dumper(Any, secret_dumper),
            ],
        )

        return retort

    @provide
    def get_conversion_retort(self) -> ConversionRetort:
        conversion_retort = ConversionRetort(
            recipe=[
                dumper(SecretStr, lambda v: v.get_secret_value()),
            ]
        )
        return conversion_retort