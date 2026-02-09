import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, DateTime, String


class ElementalModelMixin:
    """
    Model utilities mixin - Migrado exacto de tu mixins.py
    """
    
    @classmethod
    def get_fields(cls) -> List[str]:
        """Get all field names defined in the model."""
        return list(cls.__mapper__.c.keys())
    
    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name for the model."""
        return cls.__tablename__
    
    def model_dump(self) -> Dict[str, Any]:
        """
        Dump model to dictionary
        """
        return {
            field: getattr(self, field)
            for field in self.get_fields()
        }

    def update(self, **kwargs) -> None:
        """
        Update model fields
        """
        for field, value in kwargs.items():
            if hasattr(self, field):
                setattr(self, field, value)


class ElementalUUIDMixin:
    """
    Mixin para primary key UUID
    """
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4().hex),
    )
    
    @classmethod
    async def ensure_unique_id(cls, session: AsyncSession, id: str) -> str:
        """
        Ensures that the given UUID is unique by checking the database.
        If the ID already exists, generates a new UUID.
        
        Args:
            session: The SQLAlchemy session.
            id: The UUID to check for uniqueness.
        
        Returns:
            A unique UUID.
        """
        while await session.get(cls, id):  # Check if ID exists in DB
            id = str(uuid.uuid4().hex)  # Generate a new UUID
        return id


class ElementalTimestampMixin:
    """
    Mixin para timestamps automáticos
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class ElementalSoftDeleteMixin:
    """
    Mixin para soft delete
    """
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    def soft_delete(self) -> None:
        """
        Soft delete record
        """
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        """
        Restore soft deleted record
        """
        self.deleted_at = None


class ElementalAuditMixin:
    """
    Mixin para auditoría (quién creó/modificó)
    """
    created_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    def set_created_by(self, user_id: str):
        """Set creator"""
        self.created_by = user_id
    
    def set_updated_by(self, user_id: str):
        """Set updater"""
        self.updated_by = user_id


class ElementalReadOnlyMixin:
    """
    Mixin para modelos de solo lectura
    """
    def save(self):
        raise NotImplementedError("This model is read-only")
    
    def delete(self):
        raise NotImplementedError("This model is read-only")

