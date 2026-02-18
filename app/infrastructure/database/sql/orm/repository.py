from typing import Any, Optional, List, Type
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from ..exceptions import DatabaseError
from .declarative import ElementalSQLBase
from app.elemental.exceptions import DuplicateError, ConflictError, ValidationError


class ElementalRepository:
    def __init__(self, model: Type[ElementalSQLBase], session: AsyncSession):
        self.model = model
        self.session = session

    async def _check_uniqueness(self, existing_id: Optional[Any], field: str, value: Any) -> bool:
        """Checks if a unique field value already exists for another record."""
        column = getattr(self.model, field)
        conditions = [column == value]

        if existing_id is not None:
            conditions.append(self.model.id != existing_id)

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

    async def _create(self, instance: ElementalSQLBase) -> ElementalSQLBase:
        """Add and commit a new record."""
        try:
            self.session.add(instance)
            await self._commit()

            try:
                await self.session.refresh(instance)
            except Exception:
                pass

            return instance
        except IntegrityError as e:
            error_msg = str(e.orig).lower()

            if "not null" in error_msg:
                raise ValidationError(
                    message="A required field is missing.",
                    details={"error_type": "missing_required_field"}
                )

            if "unique" in error_msg or "duplicate" in error_msg:
                raise DuplicateError(
                    message="A record with this information already exists.",
                    details={"error_type": "unique_violation"}
                )

            raise ValidationError(
                message="Data integrity violation.",
                details={"error_type": "integrity_error"}
            )

        except SQLAlchemyError:
            raise DatabaseError(
                message="Error saving new instance",
                details={"error_type": "internal_db_error"}
            )

    async def _update(self, instance: ElementalSQLBase) -> ElementalSQLBase:
        """Commit changes to an existing record safely."""
        try:
            instance = await self.session.merge(instance)
            await self._commit()

            try:
                await self.session.refresh(instance)
            except Exception:
                pass

            return instance
        except IntegrityError as e:
            # Handle integrity errors during update (e.g., changing email to an existing one)
            error_msg = str(e.orig).lower()
            if "unique" in error_msg or "duplicate" in error_msg:
                raise DuplicateError(message="Conflict with existing data.", details={"error_type": "unique_violation"})
            raise ValidationError(message="Update failed due to integrity violation.")

        except SQLAlchemyError:
            raise DatabaseError(
                message="Error updating instance",
                details={"error_type": "internal_db_error"}
            )

    async def _delete(self, instance: ElementalSQLBase) -> None:
        """Delete and commit."""
        try:
            if instance not in self.session:
                instance = await self.session.merge(instance)

            await self.session.delete(instance)
            await self._commit()
        except SQLAlchemyError:
            raise ConflictError(
                message="Could not delete: instance is in use or invalid state",
                details={"error_type": "delete_conflict"}
            )

    async def _get_all(self, page: int = 1, page_size: int = 10) -> List[ElementalSQLBase]:
        """Paginated fetch."""
        if page < 1 or page_size < 1:
            raise ValidationError(message="Pagination parameters must be >= 1")

        offset = (page - 1) * page_size
        stmt = select(self.model).offset(offset).limit(page_size)

        try:
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError:
            raise DatabaseError(
                message="Error fetching records",
                details={"error_type": "fetch_error"}
            )

    async def _commit(self):
        """Standardized commit with automatic rollback on failure."""
        try:
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e