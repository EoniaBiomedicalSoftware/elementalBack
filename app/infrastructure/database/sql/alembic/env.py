from alembic import context
from sqlalchemy import pool
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy.ext.asyncio import AsyncEngine

from app.elemental.settings import get_settings
from app.infrastructure.database.sql.models.declarative import ElementalSQLBase
from app.infrastructure.database.sql.exceptions import DatabaseError

base = ElementalSQLBase()

from app.src.shared import *

settings = get_settings()
config = context.config
 
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
 
target_metadata = base.metadata

if not hasattr(settings, "database"):
    raise DatabaseError(
        message="Database is not configured"
    )

db_settings = settings.database

db_driver = db_settings.driver

if db_driver == 'sqlite' or db_driver == 'sqlite+aiosqlite':
    _db_url: str = f'{db_driver}:///{db_settings.name}'
else:
    _db_url: str = (
        f'{db_driver}://'
        f'{db_settings.user}:{db_settings.password.get_secret_value()}'
        f'@{db_settings.host}:{db_settings.port}/{db_settings.name}'
    )


config.set_main_option(
    'sqlalchemy.url',
    _db_url
)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
 
    with context.begin_transaction():
        context.run_migrations()
 

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
 
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
