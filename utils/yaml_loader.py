# file: utils/yaml_loader.py
import os
import yaml
from typing import Any, Dict


def load_yaml(file_path: str) -> Dict[str, Any]:
    """
    Загружает YAML-файл с локаторами.

    :param file_path: Путь до YAML файла.
    :return: Словарь с локаторами.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"YAML-файл не найден: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
