import logging
from typing import Dict


class _ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        record.levelname = f"{color}{levelname}{self.RESET}"
        return super().format(record)


class _JSONFormatter(logging.Formatter):
    def format(self, record):
        import json
        from datetime import datetime

        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry)


elemental_log_formatters: Dict[str, logging.Formatter] = {
    "standard": logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ),
    "detailed": logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] [%(module)s:%(funcName)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ),
    "colored": _ColoredFormatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ),
    "json": _JSONFormatter(),
    "simple": logging.Formatter("%(levelname)s: %(message)s"),
}


def get_formatter(name: str = "standard") -> logging.Formatter:
    return elemental_log_formatters.get(name, elemental_log_formatters["standard"])


def add_custom_formatter(name: str, formatter: logging.Formatter) -> None:
    elemental_log_formatters[name] = formatter
