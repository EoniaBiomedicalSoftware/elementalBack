from .declarative import ElementalSQLBase
from .mixins import (
    ElementalModelMixin,
    ElementalUUIDMixin,
    ElementalTimestampMixin,
    ElementalSoftDeleteMixin,
    ElementalAuditMixin
)

class ElementalTable(ElementalSQLBase, ElementalModelMixin):
    __abstract__ = True
    

class ElementalUUIDTable(
    ElementalTable,
    ElementalUUIDMixin,
):
    """Tabla con UUID solo."""
    __abstract__ = True


class ElementalTimestampTable(
    ElementalTable,
    ElementalTimestampMixin,
):
    """Tabla con timestamps solo."""
    __abstract__ = True


class ElementalSoftDeleteTable(
    ElementalTable,
    ElementalSoftDeleteMixin,
):
    """Tabla con soft delete solo."""
    __abstract__ = True


class ElementalFullAuditTable(
    ElementalTable,
    ElementalUUIDMixin,
    ElementalTimestampMixin,
    ElementalSoftDeleteMixin,
    ElementalAuditMixin,
):
    """Tabla con UUID, timestamps, soft delete y auditoría."""
    __abstract__ = True