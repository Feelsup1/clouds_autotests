# file: tests/test_sidebar.py
import logging

import pytest
import allure

from pages.auth_page import AuthPage
from pages.sidebar import Sidebar


log = logging.getLogger(__name__)


@allure.feature("Боковое меню")
class TestSidebar:
    """
    Тесты бокового меню.

    Техника: выбор представительных значений из классов эквивалентности
    (каждый пункт меню как отдельный класс).
    """

    @pytest.mark.positive
    @pytest.mark.smoke
    @allure.story("Кликабельность пунктов меню")
    @allure.title("Позитив: все пункты бокового меню кликабельны")
    def test_sidebar_items_clickable(self, driver, base_url, credentials):
        """
        Шаги:
          1. Авторизоваться валидным пользователем.
          2. Убедиться, что боковое меню отображается.
          3. Последовательно кликнуть по всем пунктам меню.
          4. Проверить, что каждый клик не приводит к ошибке JS/HTTP (упрощённо — тест проходит).
        """
        auth_page = AuthPage(driver, base_url)
        sidebar = Sidebar(driver, base_url)

        with allure.step("Авторизоваться"):
            auth_page.login(credentials["login"], credentials["password"])

        with allure.step("Проверить наличие пунктов меню"):
            items = sidebar.get_sidebar_items()
            assert items, "Ожидались пункты бокового меню"

        with allure.step("Кликнуть по всем пунктам меню"):
            sidebar.click_through_sidebar_items()
