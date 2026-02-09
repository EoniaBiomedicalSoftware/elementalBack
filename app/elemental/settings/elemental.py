import os
from pathlib import Path
from pydantic import Field
from typing import Annotated, Literal, Optional
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import PydanticBaseSettingsSource
from pydantic_settings import TomlConfigSettingsSource

from ..common.schemas import ElementalSchema


class _ApplicationSettings(ElementalSchema):
    app_name: str = "My App"
    app_env: str = "development"
    app_description: str = "My App Description"
    app_version: str = '0.0.0'
    debug: bool = False
    host: str = 'localhost'
    port: int = 8000
    api_version: str = 'v1'
    api_prefix: str = "/api"
    frontend_host_url: Optional[str] = None


class CliApplication(_ApplicationSettings):
    app_type: Literal["cli"] = "cli"


class _CorsSettings(ElementalSchema):
    origins: list[str] = ['*']
    allow_credentials: bool = True
    allow_methods: list[str] = ['*']
    allow_headers: list[str] = ['*']
    max_age: int = 3600


class WebApplication(_ApplicationSettings):
    app_type: Literal["web"] = "web"
    ssl_enabled: bool = False
    cors: _CorsSettings = _CorsSettings()


class ElementalSettings(PydanticBaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='elementalback_',
        env_nested_delimiter='__',
        env_file=None,
        extra='ignore'
    )

    application: Annotated[
        WebApplication | CliApplication,
        Field(discriminator="app_type")
    ]
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[PydanticBaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:

        app_env:str = os.environ.get('elementalback_application__app_env')

        if app_env:
            return (
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )

        return (
            TomlConfigSettingsSource(
                settings_cls, toml_file=Path('settings.dev.toml')
            ),
        )
