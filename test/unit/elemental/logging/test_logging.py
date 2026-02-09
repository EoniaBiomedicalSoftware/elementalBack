import pytest
import logging
from unittest.mock import MagicMock, patch
from app.elemental.logging.logger import get_logger, setup_elemental_logger, _LOGGER_REGISTRY
from app.elemental.logging.formatters import _ColoredFormatter, get_formatter

@pytest.fixture(autouse=True)
def clean_registry():
    """Clean logger registry before each test."""
    _LOGGER_REGISTRY.clear()
    yield
    _LOGGER_REGISTRY.clear()

@patch("app.elemental.logging.logger.RotatingFileHandler")
@patch("app.elemental.logging.logger.Path")
def test_setup_elemental_logger(mock_path, mock_handler):
    """Must configure console and file handlers."""
    # Mock directory creation
    mock_path.return_value.parent.mkdir.return_value = None
    
    logger = setup_elemental_logger("test_logger")
    
    assert logger.name == "test_logger"
    assert len(logger.handlers) == 2  # Console + File
    assert mock_path.called
    assert mock_handler.called

def test_get_logger_singleton():
    """Must return the same instance for the same name."""
    with patch("app.elemental.logging.logger.RotatingFileHandler"), \
         patch("app.elemental.logging.logger.Path"):
        
        l1 = get_logger("shared")
        l2 = get_logger("shared")
        assert l1 is l2
        
        l3 = get_logger("other")
        assert l1 is not l3

def test_colored_formatter():
    """Must add color codes to the level."""
    formatter = _ColoredFormatter("%(levelname)s: %(message)s")
    record = logging.LogRecord("test", logging.INFO, "path", 1, "msg", (), None)
    
    formatted = formatter.format(record)
    assert "\033[32mINFO\033[0m" in formatted

def test_get_formatter_defaults():
    """Must return the standard formatter by default."""
    fmt = get_formatter("non_existent")
    # Verify that the format matches 'standard'
    assert fmt._fmt == "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"

def test_get_formatter_specific():
    """Must return the requested formatter."""
    fmt = get_formatter("simple")
    assert fmt._fmt == "%(levelname)s: %(message)s"
