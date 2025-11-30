# file: pages/auth_page.py
import os
import logging
from typing import Dict

import allure

from utils.yaml_loader import load_yaml
from pages.base_page import BasePage

log = logging.getLogger(__name__)


class AuthPage(BasePage):
    """
    Page Object для страницы авторизации и логаута.
    """

    LOCATORS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locators", "auth_page.yaml")

    def __init__(self, driver, base_url: str):
        """
        :param driver: Экземпляр WebDriver.
        :param base_url: Базовый URL портала.
        """
        super().__init__(driver, base_url)
        self.locators: Dict[str, dict] = load_yaml(self.LOCATORS_PATH)

    @allure.step("Открыть страницу авторизации")
    def open_login_page(self) -> None:
        """
        Открывает страницу логина и, если нужно, принимает cookies.

        Проверки:
          - страница загрузилась;
          - поле ввода логина (email) стало доступно.
        """
        self.open("login")

        # Сначала пытаемся закрыть баннер cookies (если он есть)
        self.accept_cookies_if_present()

        # ✅ Критично: даём странице больше времени дорисовать форму логина.
        # На портале login-форма подгружается не мгновенно, поэтому ставим,
        # например, 30 секунд.
        self.find(self.locators["username_input"], timeout=30)

    @allure.step("Принять cookies, если баннер отображается")
    def accept_cookies_if_present(self) -> None:
        """
        Принимает cookies, если баннер с кнопкой согласия отображается.
        Локатор берётся из auth_page.yaml (cookies_accept_button).
        """
        locator = self.locators.get("cookies_accept_button")
        if not locator:
            log.info("Локатор cookies_accept_button не задан, ничего не делаем")
            return

        self.click_if_present(locator, timeout=5)

    @allure.step("Ввести логин и пароль")
    def fill_credentials(self, login: str, password: str) -> None:
        """
        Заполняет поля логина и пароля.

        :param login: Имя пользователя.
        :param password: Пароль пользователя.
        """
        self.type(self.locators["username_input"], login)
        self.type(self.locators["password_input"], password)

    @allure.step("Нажать кнопку Login")
    def submit_login(self) -> None:
        """
        Нажимает на кнопку логина.
        """
        self.click(self.locators["login_button"])

    @allure.step("Авторизоваться с валидными кредами")
    def login(self, login: str, password: str) -> None:
        """
        Полный сценарий логина с валидными данными.

        :param login: Имя пользователя.
        :param password: Пароль.
        """
        self.open_login_page()
        self.fill_credentials(login, password)
        self.submit_login()

    @allure.step("Открыть меню пользователя")
    def open_user_menu(self) -> None:
        self.click(self.locators["user_menu_button"])
        assert self.find(self.locators["logout_button"])

    @allure.step("Выйти из аккаунта")
    def logout(self) -> None:
        """
        Выполняет логаут через меню пользователя.
        """
        self.open_user_menu()
        self.click(self.locators["logout_button"])

    def has_email_warning(self, timeout: int = 2) -> bool:
        """
        Проверяет, есть ли варнинг у поля Email.

        :param timeout: Таймаут ожидания иконки ошибки.
        :return: True, если иконка отображается, иначе False.
        """
        return self.is_element_present(self.locators["email_error_icon"], timeout=timeout)

    def has_password_warning(self, timeout: int = 2) -> bool:
        """
        Проверяет, есть ли варнинг у поля Password.

        :param timeout: Таймаут ожидания иконки ошибки.
        :return: True, если иконка отображается, иначе False.
        """
        return self.is_element_present(self.locators["password_error_icon"], timeout=timeout)

    def get_login_errors(self) -> dict:
        """
        Возвращает информацию о наличии варнингов по полям логина.

        :return: dict вида:
                 {
                   "email": True/False,
                   "password": True/False,
                 }
        """
        return {
            "email": self.has_email_warning(),
            "password": self.has_password_warning(),
        }

    def resolve_credentials(
        self,
        login_input: str | None,
        password_input: str | None,
        credentials: dict,
    ) -> tuple[str, str]:
        """
        Строит реальные логин/пароль для теста.

        Если login_input/password_input = None — берём валидные значения из credentials.
        Иначе используем переданное значение (негативные кейсы).

        :param login_input: Логин из набора данных или None (использовать валидный).
        :param password_input: Пароль из набора данных или None (использовать валидный).
        :param credentials: Фикстура с валидными кредами.
        :return: (login, password)
        """
        login = credentials["login"] if login_input is None else login_input
        password = credentials["password"] if password_input is None else password_input
        return login, password


