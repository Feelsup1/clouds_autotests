# file: pages/sidebar.py
import os
import logging
from typing import Dict, List

import allure

from utils.yaml_loader import load_yaml
from pages.base_page import BasePage


log = logging.getLogger(__name__)


class Sidebar(BasePage):
    """
    Page Object для бокового меню.
    """

    LOCATORS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locators", "sidebar.yaml")

    def __init__(self, driver, base_url: str):
        """
        :param driver: Экземпляр WebDriver.
        :param base_url: Базовый URL портала.
        """
        super().__init__(driver, base_url)
        self.locators: Dict[str, dict] = load_yaml(self.LOCATORS_PATH)

    @allure.step("Получить список пунктов бокового меню")
    def get_sidebar_items(self) -> List[str]:
        """
        Возвращает список текстов пунктов бокового меню.

        :return: Список названий пунктов.
        """
        elements = self.find_all(self.locators["sidebar_links"])
        texts = [el.text for el in elements]
        log.info(f"Пункты бокового меню: {texts}")
        return texts

    @allure.step("Проверить кликабельность пунктов бокового меню")
    def click_through_sidebar_items(self) -> None:
        """
        Последовательно кликает по пунктам меню (BVA/EC здесь — по одному
        элементу из каждого 'класса' пунктов меню).
        """
        elements = self.find_all(self.locators["sidebar_links"])
        for el in elements:
            text = el.text
            with allure.step(f"Клик по пункту меню '{text}'"):
                log.info(f"Клик по пункту меню '{text}'")
                el.click()
                # тут можно добавить проверку URL или заголовка страницы
