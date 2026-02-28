from adaptix import Retort
from dishka import AnyOf, Provider, Scope, provide
from fluentogram import TranslatorHub, TranslatorRunner
from fluentogram.storage import FileStorage
from loguru import logger

from src.core.config import AppConfig
from src.core.i18n import TranslatorHubImpl, TranslatorRunnerImpl


class I18nProvider(Provider):
    scope = Scope.APP

    @provide(source=TranslatorHubImpl, provides=TranslatorHub)
    def get_translator_hub(
        self,
        config: AppConfig,
        retort: Retort,
    ) -> AnyOf[TranslatorHubImpl, TranslatorHub]:
        storage = FileStorage(path=config.translations_dir / "{locale}")
        locales_map: dict[str, tuple[str, ...]] = {}

        for locale_code in config.locales:
            fallback_chain: list[str] = [locale_code]
            if config.default_locale != locale_code:
                fallback_chain.append(config.default_locale)
            locales_map[locale_code] = tuple(fallback_chain)

        if config.default_locale not in locales_map:
            locales_map[config.default_locale] = (config.default_locale,)

        logger.debug(
            f"Loaded TranslatorHub with locales: "
            f"{[locale.value for locale in locales_map.keys()]}, "  # type: ignore[attr-defined]
            f"default={config.default_locale.value}"
        )

        return TranslatorHubImpl(
            locales_map,
            root_locale=config.default_locale,
            storage=storage,
            retort=retort,
        )

    @provide(scope=Scope.REQUEST, source=TranslatorRunnerImpl, provides=TranslatorRunner)
    def get_translator(
        self,
        config: AppConfig,
        translator_hub: TranslatorHub,
    ) -> TranslatorRunner:
        locale = config.default_locale

        logger.debug(f"Translator for user with default locale '{locale}'")

        return translator_hub.get_translator_by_locale(locale=locale)