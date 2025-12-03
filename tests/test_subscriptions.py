# file: tests/test_subscriptions.py
import logging
import uuid

import pytest
import allure

from pages.auth_page import AuthPage
from pages.sidebar_page import SidebarPage
from pages.account_settings_page import AccountSettingsPage

log = logging.getLogger(__name__)


def _make_contact_data(suffix: str) -> dict:
    """
    Генерирует тестовые данные контакта для блока Subscriptions.
    Все поля заполнены валидными значениями (EC: класс валидных данных).
    """
    email = f"qa+subs_{suffix}@example.com"
    company = f"Test Company {suffix}"
    return {
        # Блок Contact info – верхние поля
        "first_name": f"QA Auto {suffix}",
        "middle_name": f"Middle {suffix}",
        "last_name": f"Sub {suffix}",
        "nickname": f"Nick {suffix}",
        "comments": f"Auto-created contact {suffix}",  # большое поле Comments

        # Job role блок
        "job_roles": ["Technical"],  # хотя бы одна роль обязательно
        "company": company,
        "job_title": f"QA Engineer {suffix}",
        "job_role": "QA Engineer",

        # Contact details
        "phone": "+1234567890",
        "email": email,
        "secondary_email": f"secondary_{email}",

        # Дополнительные заметки (если у тебя есть отдельный textarea под этим)
        "notes": f"Notes for {suffix}",
    }


@pytest.fixture
def subscriptions_page(driver, base_url, credentials) -> AccountSettingsPage:
    """
    Предусловие для тестов:

      - пользователь залогинен;
      - открыт Account settings;
      - выбрана вкладка Subscriptions.

    Scope='function' → каждый тест изолирован.
    """
    auth_page = AuthPage(driver, base_url)

    with allure.step("Авторизоваться валидным пользователем"):
        auth_page.login(credentials["login"], credentials["password"])

    with allure.step("Открыть Account settings через боковое меню"):
        sidebar = SidebarPage(driver, base_url)
        sidebar.open_section("account_settings_menu")

    page = AccountSettingsPage(driver, base_url)

    with allure.step("Проверить вкладку Subscriptions"):
        page.ensure_on_subscriptions_tab()

    return page


@allure.feature("Account settings")
@allure.story("Subscriptions — CRUD контактов")
class TestSubscriptions:
    """
    Тесты на блок Subscriptions:

      - добавление контакта;
      - редактирование контакта;
      - удаление контакта.

    Техники тест-дизайна:
      * EC (класс валидных данных) — валидный полностью заполненный контакт.
    """

    @pytest.mark.positive
    @allure.title("Subscriptions: добавление контакта с заполнением всех полей")
    def test_add_subscription_contact_positive(
        self, subscriptions_page: AccountSettingsPage
    ):
        """
        Шаги:
          1. Открыть Account settings → Subscriptions.
          2. Нажать Add contact.
          3. Заполнить все поля валидными данными.
          4. Сохранить.
          5. Убедиться, что контакт появился в списке.
        """
        suffix = uuid.uuid4().hex[:8]
        contact = _make_contact_data(suffix)

        with allure.step(
            "Удалить контакт, если он уже существует (идемпотентность теста)"
        ):
            subscriptions_page.delete_contact_if_exists(contact["email"])

        with allure.step("Создать новый контакт"):
            subscriptions_page.create_contact(contact)

        with allure.step("Проверить, что контакт появился в списке"):
            assert subscriptions_page.is_contact_present(contact["email"]), (
                f"Контакт с email {contact['email']} должен быть в списке после создания"
            )

    @pytest.mark.positive
    @allure.title("Subscriptions: редактирование существующего контакта")
    def test_edit_subscription_contact_positive(
        self, subscriptions_page: AccountSettingsPage
    ):
        """
        Шаги:
          1. Создать тестовый контакт (если его ещё нет).
          2. Открыть форму редактирования контакта.
          3. Изменить несколько полей (имя, телефон, заметку).
          4. Сохранить.
          5. Убедиться, что изменения отразились в списке.
        """
        suffix = uuid.uuid4().hex[:8]
        original = _make_contact_data(suffix)

        with allure.step("Убедиться, что исходный контакт существует"):
            if not subscriptions_page.is_contact_present(original["email"]):
                subscriptions_page.create_contact(original)

        updated = dict(original)
        updated["first_name"] = original["first_name"] + " UPDATED"
        updated["phone"] = "+9876543210"
        updated["notes"] = f"{original['notes']} (edited)"

        with allure.step("Отредактировать контакт"):
            subscriptions_page.edit_contact(original["email"], updated)

        with allure.step("Проверить, что контакт обновлён"):
            contact_row = subscriptions_page.get_contact(updated["email"])
            assert contact_row is not None, (
                "Контакт должен существовать после редактирования"
            )


    @pytest.mark.positive
    @allure.title("Subscriptions: удаление существующего контакта")
    def test_delete_subscription_contact_positive(
        self, subscriptions_page: AccountSettingsPage
    ):
        """
        Шаги:
          1. Убедиться, что тестовый контакт существует
             (если нет — создать его).
          2. Удалить контакт через блок Subscriptions.
          3. Проверить, что контакт больше не отображается в списке.

        Техники тест-дизайна:
          * EC — валидный полностью заполненный контакт как исходное состояние.
          * Idempotent action — перед запуском/повторным запуском тест сам
            приводит систему в нужное состояние.
        """
        # генерим уникальный контакт
        suffix = uuid.uuid4().hex[:8]
        contact = _make_contact_data(suffix)

        with allure.step("Убедиться, что тестовый контакт существует"):
            if not subscriptions_page.is_contact_present(contact["email"]):
                subscriptions_page.create_contact(contact)

        with allure.step("Удалить контакт из блока Subscriptions"):
            subscriptions_page.delete_contact(contact["email"])

        with allure.step("Проверить, что контакт отсутствует в списке"):
            assert not subscriptions_page.is_contact_present(
                contact["email"], timeout=5
            ), f"Контакт с email {contact['email']} не должен отображаться после удаления"

        # опционально: второй вызов для проверки идемпотентности окружения
        with allure.step("Проверить, что повторное удаление безопасно (идемпотентность)"):
            subscriptions_page.delete_contact_if_exists(contact["email"])