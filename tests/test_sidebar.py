# file: tests/test_sidebar.py
import logging

import pytest
import allure

from pages.auth_page import AuthPage
from pages.sidebar_page import SidebarPage

log = logging.getLogger(__name__)

# Тестовые данные для пунктов бокового меню.
# Здесь мы показываем:
#   * EC (Equivalence Classes) — каждый пункт меню как отдельный класс.
#
# menu_key          — ключ локатора в locators/sidebar.yaml
# url_fragment      — фрагмент URL, который должен появиться после перехода
SIDEBAR_ITEMS = [
    pytest.param("ssl_certificates_menu", "/ssl", id="SSL certificates"),
    pytest.param("account_settings_menu", "/account", id="Account settings"),
    pytest.param("requests_menu", "/requests", id="Requests"),
]


@allure.feature("Боковое меню")
class TestSidebar:
    """
    Тесты на работоспособность левого бокового меню.

    Техники тест-дизайна:
      * EC (классы эквивалентности): каждый пункт меню как отдельный класс.
    """

    @pytest.mark.positive
    @allure.story("Навигация по каждому пункту бокового меню (EC)")
    @pytest.mark.parametrize("menu_key,url_fragment", SIDEBAR_ITEMS)
    def test_sidebar_navigation(
        self,
        driver,
        base_url,
        credentials,
        menu_key,
        url_fragment,
    ):
        """
        Позитивный параметризованный тест (EC):

        Шаги:
          1. Авторизоваться валидным пользователем.
          2. Кликнуть по пункту бокового меню.
          3. Проверить, что:
             - текущий URL содержит ожидаемый фрагмент;
        """
        auth_page = AuthPage(driver, base_url)

        with allure.step("Авторизоваться валидным пользователем"):
            auth_page.login(credentials["login"], credentials["password"])

        sidebar = SidebarPage(driver, base_url)

        with allure.step(f"Открыть раздел через боковое меню: {menu_key}"):
            sidebar.open_section(menu_key)

        with allure.step("Проверить, что URL содержит ожидаемый фрагмент"):
            current_url = driver.current_url
            assert url_fragment in current_url, (
                f"Ожидалось, что URL будет содержать '{url_fragment}', "
                f"фактический URL: {current_url}"
            )
