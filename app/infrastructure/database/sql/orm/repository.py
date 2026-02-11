from typing import Any, Optional, List, Type
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ..exceptions import DatabaseError
from .declarative import ElementalSQLBase
from app.elemental.exceptions import DuplicateError, ConflictError


class ElementalRepository:
    def __init__(self, model: Type[ElementalSQLBase], session: AsyncSession):
        self.model = model
        self.session = session

    async def _check_uniqueness(self, existing_id: Optional[Any], field: str, value: Any) -> bool:
        """Checks if a unique field value already exists for another record."""
        column = getattr(self.model, field)
        conditions = [column == value]

        if existing_id is not None:
            conditions.append(self.model.id != existing_id) # noqa

        stmt = select(self.model).where(and_(*conditions)).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is None

    async def _select_one(self, **query) -> Optional[ElementalSQLBase]:
        """Generic filter_by one record."""
        stmt = select(self.model).filter_by(**query)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def _get_by_id(self, object_id: Any) -> Optional[ElementalSQLBase]:
        """Get record by primary key."""
        return await self.session.get(self.model, object_id)

    # app/infrastructure/database/sql/models/repository.py

    async def _create(self, instance: ElementalSQLBase) -> ElementalSQLBase:
        """Add and commit a new record."""
        try:
            self.session.add(instance)
            await self._commit()

            # We try to refresh to get DB-generated fields (like ID or timestamps)
            # If it fails due to closed transaction, we catch it and continue
            try:
                await self.session.refresh(instance)
            except Exception:
                # Session closed, or transaction completed; instance
                # still holds the data from the commit.
                pass

            return instance
        except IntegrityError as e:
            # Handle unique constraints
            field_ = str(e.orig)
            raise DuplicateError(
                resource=self.model.__name__,
                field=field_,
                value="Value already exists"
            ) from e
        except SQLAlchemyError as e:
            # This is where your 502 was coming from
            raise DatabaseError(
                message="Error saving new instance",
                details={"orig": str(e)}
            ) from e

    async def _update(self, instance: ElementalSQLBase) -> ElementalSQLBase:
        """Commit changes to an existing record safely."""
        try:
            # Re-attach the instance to the current session if it was detached
            instance = await self.session.merge(instance)

            await self._commit()

            # Refresh to get any DB-side changes (triggers, defaults)
            try:
                await self.session.refresh(instance)
            except Exception:
                # If refresh fails after commit, we at least have the instance
                pass

            return instance
        except SQLAlchemyError as e:
            # Rollback is usually handled by your commit/session logic
            raise DatabaseError(
                message="Error updating instance",
                details={"orig": str(e)}
            ) from e

    async def _delete(self, instance: ElementalSQLBase) -> None:
        """Delete and commit."""
        try:
            # Check if an instance is detached or not persisted
            if instance not in self.session:
                instance = await self.session.merge(instance)

            await self.session.delete(instance)
            await self._commit()
        except SQLAlchemyError as e:
            # Avoid raising ExternalServiceError (502)
            # Use ConflictError (409) or a custom DatabaseError (500)
            raise ConflictError(
                message="Could not delete: instance is not in a valid state",
                details={"orig": str(e)}
            ) from e

    async def _get_all(self, page: int = 1, page_size: int = 10) -> List[ElementalSQLBase]:
        """Paginated fetch."""
        if page < 1 or page_size < 1:
            # Note: This is more of a ValidationError than a DatabaseError
            raise DatabaseError(message="Pagination parameters must be >= 1")

        offset = (page - 1) * page_size
        stmt = select(self.model).offset(offset).limit(page_size)

        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise DatabaseError(message="Error fetching records", details={"orig": str(e)}) from e

    async def _commit(self):
        """Standardized commit with automatic rollback on failure."""
        try:
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            # We re-raise to let the caller methods (_create, _update) handle it
            raise e