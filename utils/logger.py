# file: utils/logger.py
import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """
    Конфигурирует глобальное логирование.

    :param level: Уровень логирования (по умолчанию INFO).
    """
    root = logging.getLogger()
    if root.handlers:
        # Уже настроено
        return

    root.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
