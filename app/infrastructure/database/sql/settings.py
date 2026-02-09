from pydantic import Field, SecretStr
from app.elemental.common import ElementalSchema


class DatabaseSettings(ElementalSchema):
    driver: str = Field(
        default="postgresql+asyncpg",
        description="Database dialect and driver (e.g., postgresql+asyncpg)",
        repr=False
    )
    host: str = Field(description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(description="Database name")
    user: str = Field(description="Database user", repr=False)
    password: SecretStr = Field(description="Database password", repr=False)
    pool_size: int = Field(default=5, description="Connection pool size")
    max_overflow: int = Field(default=10, description="Max overflow connections")
    echo: bool = Field(default=False, description="Log SQL statements")
