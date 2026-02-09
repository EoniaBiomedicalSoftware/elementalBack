from sqlalchemy.orm import configure_mappers

from .registry.relations_registry import register_all_relationships

register_all_relationships()
configure_mappers()
