# file: pages/sidebar_page.py
import os
import logging
from typing import Dict, Iterable, List

import allure

from pages.base_page import BasePage
from utils.yaml_loader import load_yaml

log = logging.getLogger(__name__)


class SidebarPage(BasePage):
    """
    Page Object для левого бокового меню.

    Это компонент, который используется на страницах после логина
    (Dashboard, Cloud Storage и т.п.). Предполагается, что пользователь
    уже авторизован, а нужная страница открыта.
    """

    LOCATORS_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "locators",
        "sidebar.yaml",
    )

    def __init__(self, driver, base_url: str):
        """
        :param driver: Экземпляр WebDriver.
        :param base_url: Базовый URL портала.
        """
        super().__init__(driver, base_url)
        self.locators: Dict[str, dict] = load_yaml(self.LOCATORS_PATH)

    @allure.step("Открыть раздел через боковое меню: {menu_key}")
    def open_section(self, menu_key: str) -> None:
        """
        Открывает раздел, кликнув по пункту бокового меню.

        :param menu_key: Ключ локатора в sidebar.yaml
                         (например, 'billing_menu', 'ssl_certificates_menu').
        """
        locator = self.locators[menu_key]
        log.info("Клик по пункту бокового меню '%s': %s", menu_key, locator)
        self.click(locator, timeout=60)

    @allure.step("Последовательно кликнуть по пунктам бокового меню")
    def click_through_sidebar_items(self, menu_keys: Iterable[str]) -> None:
        """
        Последовательно кликает по переданным пунктам меню.
        Удобно использовать в smoke-тестах.

        :param menu_keys: Итерируемая коллекция ключей локаторов меню.
        """
        for key in menu_keys:
            self.open_section(key)

    @allure.step("Проверить, что пункт бокового меню '{menu_key}' активен")
    def is_item_active(self, menu_key: str, timeout: int = 5) -> bool:
        """
        Проверяет, что пункт бокового меню помечен как активный.

        Ожидаем, что у элемента есть CSS-класс вроде 'active' / 'selected' /
        'current'. При необходимости список токенов можно расширить.

        :param menu_key: Ключ локатора в sidebar.yaml.
        :param timeout: Таймаут ожидания появления элемента.
        :return: True, если пункт активен, иначе False.
        """
        locator = self.locators[menu_key]
        element = self.find(locator, timeout=timeout)
        classes = (element.get_attribute("class") or "").lower()
        return any(token in classes for token in ("active", "selected", "current"))

    @allure.step("Получить список отображаемых пунктов бокового меню")
    def get_visible_items(self) -> List[str]:
        """
        Возвращает список ключей локаторов, которые сейчас отображаются
        в боковом меню (есть в DOM и не падают по таймауту).

        :return: Список имён локаторов (ключей из sidebar.yaml).
        """
        visible: List[str] = []
        for key, locator in self.locators.items():
            if self.is_element_present(locator, timeout=1):
                visible.append(key)
        log.info("Видимые пункты бокового меню: %s", visible)
        return visible
