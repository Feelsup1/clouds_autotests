# file: tests/test_auth.py
import logging

import pytest
import allure

from pages.auth_page import AuthPage
from pages.dashboard_page import DashboardPage

log = logging.getLogger(__name__)

# Наборы данных для негативных кейсов авторизации
#
# Техники тест-дизайна:
#   - EC (Equivalence Classes): пустые значения, неверный формат email, валидный логин + пустой пароль.
#   - BVA (Boundary Value Analysis): слишком длинный логин.
NEGATIVE_AUTH_CASES = [
    # 1) Оба поля пустые — EC + BVA (граница 0 символов)
    pytest.param(
        "",  # login_input
        "",  # password_input
        {
            "title": "Негатив: пустые логин и пароль (BVA: длина = 0)",
            "email_warn": True,
            "password_warn": True,
        },
        id="empty_email_and_password",
    ),
    # 2) Слишком длинный логин + валидный пароль — BVA (верхняя граница длины)
    pytest.param(
        "x" * 129,  # login_input (слишком длинный логин / email)
        None,  # password_input = None → взять валидный из credentials
        {
            "title": "Негатив: слишком длинный логин (BVA: длина > допустимой)",
            "email_warn": True,
            "password_warn": False,
        },
        id="long_email_valid_password",
    ),
    # 3) Неверный формат email + валидный пароль — EC (класс «неправильный формат»)
    pytest.param(
        "not-an-email",  # login_input (нет @ и домена)
        None,  # валидный пароль из credentials
        {
            "title": "Негатив: неверный формат email (EC: неправильный формат)",
            "email_warn": True,
            "password_warn": False,
        },
        id="invalid_email_format_valid_password",
    ),
    # 4) Валидный email + пустой пароль — EC/BVA для пароля
    pytest.param(
        None,  # login_input = None → валидный логин из credentials
        "",  # пустой пароль
        {
            "title": "Негатив: валидный email и пустой пароль (BVA: длина пароля = 0)",
            "email_warn": False,
            "password_warn": True,
        },
        id="valid_email_empty_password",
    ),
]


@allure.feature("Авторизация")
class TestAuth:
    @pytest.mark.positive
    @allure.story("Невалидная авторизация")
    def test_login_logout_positive(self, driver, base_url, credentials):
        page = AuthPage(driver, base_url)

        with allure.step("Авторизоваться валидным пользователем"):
            page.login(credentials["login"], credentials["password"])

        with allure.step("Убедиться, что дашборд открыт"):
            dashboard = DashboardPage(driver, base_url)
            dashboard.ensure_opened()

        with allure.step("Выполнить логаут"):
            page.logout()

        with allure.step("Проверить, что снова открыта страница авторизации"):
            page.ensure_opened()

    @pytest.mark.negative
    @allure.story("Невалидная авторизация")
    @pytest.mark.parametrize("login_input,password_input,expect", NEGATIVE_AUTH_CASES)
    def test_login_negative(
        self, driver, base_url, credentials, login_input, password_input, expect
    ):
        """
        Параметризированный негативный тест авторизации.

        Наборы:
          - пустые логин/пароль (EC + BVA: нижняя граница 0 символов);
          - слишком длинный логин + валидный пароль (BVA: верхняя граница);
          - неверный формат email + валидный пароль (EC: неправильный формат);
          - валидный email + пустой пароль (EC/BVA для пароля).
        """
        page = AuthPage(driver, base_url)

        allure.dynamic.title(expect["title"])

        login, password = page.resolve_credentials(
            login_input=login_input,
            password_input=password_input,
            credentials=credentials,
        )

        with allure.step(
            f"Открыть страницу логина и ввести login='{login}' / password (маскируется)"
        ):
            page.open_login_page()
            page.fill_credentials(login, password)
            page.submit_login()

        with allure.step("Проверить варнинги у полей логина"):
            errors = page.get_login_errors()
            assert errors["email"] == expect["email_warn"], (
                f"Ожидание по Email: {expect['email_warn']}, "
                f"фактически: {errors['email']}"
            )
            assert errors["password"] == expect["password_warn"], (
                f"Ожидание по Password: {expect['password_warn']}, "
                f"фактически: {errors['password']}"
            )

        with allure.step("Проверить, что пользователь не залогинен"):
            assert not page.is_element_present(
                page.locators["user_menu_button"], timeout=2
            ), "Меню пользователя не должно быть доступно при неуспешной авторизации"

        with allure.step("Проверить, что остаёмся на /login"):
            assert "/login" in driver.current_url, (
                "Не должны уходить с /login при неуспешной авторизации"
            )
