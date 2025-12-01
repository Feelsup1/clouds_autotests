# file: pages/account_settings_page.py
import os
import logging
from typing import Dict, Optional

import allure
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.yaml_loader import load_yaml
from utils.wait import wait_for

log = logging.getLogger(__name__)


class AccountSettingsPage(BasePage):
    """
    Page Object для страницы Account settings (вкладка Subscriptions).

    Реализует сценарии:
      - открыть вкладку Subscriptions;
      - создать контакт;
      - отредактировать контакт;
      - удалить контакт;
      - проверить наличие контакта.
    """
    JOB_ROLES = ("Primary", "Technical", "Billing", "Abuse", "Emergency")

    LOCATORS_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "locators",
        "account_settings.yaml",
    )

    def __init__(self, driver, base_url: str):
        """
        :param driver: Экземпляр WebDriver.
        :param base_url: Базовый URL портала.
        """
        super().__init__(driver, base_url)
        self.locators: Dict[str, dict] = load_yaml(self.LOCATORS_PATH)

    # --- Внутренний helper для ожидания URL ---

    def _wait_url_contains(self, fragment: str, timeout: int = 10) -> None:
        """
        Ждёт, пока в текущем URL появится указанный фрагмент.
        """
        wait_for(self.driver, EC.url_contains(fragment), timeout)

    # --- Навигация / проверка вкладки Subscriptions ---

    @allure.step("Открыть вкладку Subscriptions в Account settings")
    def open_subscriptions_tab(self) -> None:
        """
        Открывает вкладку Subscriptions (если ещё не открыта) и ждёт таблицу контактов.
        """
        self.find(self.locators["subscriptions_table"], timeout=15)

    @allure.step("Убедиться, что открыт блок Subscriptions")
    def ensure_on_subscriptions_tab(self) -> None:
        """
        Проверяет, что действительно открыт блок Subscriptions:
          - видна вкладка Subscriptions;
          - видна таблица контактов.
        """
        self.find(self.locators["subscriptions_table"], timeout=30)

    def _make_job_role_checkbox_locator(self, role: str) -> dict:
        """
        Строит локатор для чекбокса роли по тексту лейбла (Primary/Technical/...).
        """
        template = self.locators["job_role_checkbox_by_label"]["value"]
        xpath = template.format(role=role)
        return {"by": "xpath", "value": xpath}

    @allure.step("Заполнить форму контакта")
    def fill_contact_form(self, contact: Dict[str, str]) -> None:
        """
        Заполняет форму контакта всеми полями.

        Ожидаемые ключи в contact:
          - name
          - email
          - phone
          - company
          - role        (текст в поле 'Job role')
          - job_roles   (список чекбоксов ролей: ['Primary', 'Technical', ...])
          - notes       (если хочешь заполнять большую textarea выше)
        """
        # Основные текстовые поля
        self.type(self.locators["contact_name_input"], contact["name"])
        self.type(self.locators["contact_email_input"], '')
        self.type(self.locators["contact_phone_input"], '')
        self.type(self.locators["contact_email_input"], contact["email"])
        self.type(self.locators["contact_phone_input"], contact["phone"])
        self.type(self.locators["contact_company_input"], contact["company"])
        self.type(self.locators["contact_role_input"], contact["role"])

        # Чекбоксы Job role: Primary / Technical / Billing / Abuse / Emergency
        job_roles = contact.get("job_roles") or []
        self._set_job_roles(job_roles)

    def _set_job_roles(self, job_roles: list[str]) -> None:
        """
        Выставляет чекбоксы Job role в нужное состояние.

        :param job_roles: список ролей, которые ДОЛЖНЫ быть выбраны.
                          Например: ["Primary"] или ["Technical", "Billing"].
        """
        desired = set(job_roles)

        for role in self.JOB_ROLES:
            locator = self._make_job_role_checkbox_locator(role)
            try:
                label_el = self.find(locator, timeout=5)
            except TimeoutException:
                log.warning(f"Чекбокс роли '{role}' не найден, пропускаем")
                continue

            # предполагаем структуру <label><input type="checkbox">...</label>
            try:
                input_el = label_el.find_element(By.XPATH, ".//input[@type='checkbox']")
            except Exception as e:
                log.warning(f"Не удалось найти input для роли '{role}': {e}")
                continue

            should_be_checked = role in desired
            is_checked = input_el.is_selected()

            # кликаем только если состояние отличается от желаемого
            if is_checked != should_be_checked:
                label_el.click()


    @allure.step("Создать контакт в Subscriptions")
    def create_contact(self, contact: Dict[str, str]) -> None:
        """
        Создаёт контакт в блоке Subscriptions.

        Фактический поток:
          1. Мы на странице /account в блоке Subscriptions.
          2. Жмём 'Add contact' → редирект на /account/new-contact.
          3. Заполняем форму и жмём Save.
          4. После сохранения нас возвращает обратно на /account,
             и новый контакт появляется в списке.
        """
        # 1. Нажали "Add contact"
        self.click(self.locators["add_contact_button"])

        # 2. Дождались перехода на /account/new-contact
        self._wait_url_contains("/account/new-contact", timeout=10)
        if "new_contact_header" in self.locators:
            self.find(self.locators["new_contact_header"], timeout=10)

        # 3. Заполнили форму и сохранили
        self.fill_contact_form(contact)
        self.click(self.locators["contact_save_button"])

        # 4. Ждём возврата на /account и появления контакта в списке
        self._wait_url_contains("/account/contact", timeout=10)
        self.wait_for_contact(contact["email"])

    # --- Поиск контакта в таблице ---

    def _make_contact_row_locator(self, email: str) -> Dict[str, str]:
        """
        Строит динамический локатор для строки контакта по email.
        """
        template = self.locators["contact_row_by_email"]["value"]
        xpath = template.format(email=email)
        return {"by": "xpath", "value": xpath}

    @allure.step("Ожидать появления контакта с email: {email}")
    def wait_for_contact(self, email: str, timeout: int = 10) -> None:
        """
        Ждёт появления контакта с указанным email в списке.

        :param email: Email контакта.
        :param timeout: Таймаут ожидания.
        """
        row_locator = self._make_contact_row_locator(email)
        self.find(row_locator, timeout=timeout)

    @allure.step("Проверить наличие контакта по email: {email}")
    def is_contact_present(self, email: str, timeout: int = 3) -> bool:
        """
        Проверяет, есть ли контакт с данным email в списке.

        :param email: Email контакта.
        :param timeout: Таймаут ожидания.
        :return: True, если контакт найден, иначе False.
        """
        row_locator = self._make_contact_row_locator(email)
        return self.is_element_present(row_locator, timeout=timeout)

    @allure.step("Получить данные контакта из таблицы по email: {email}")
    def get_contact(self, email: str) -> Optional[Dict[str, str]]:
        """
        Возвращает данные контакта из строки таблицы по email.
        (минимум name/email/phone, если удаётся их извлечь)

        :param email: Email контакта.
        :return: dict или None, если контакт не найден.
        """
        if not self.is_contact_present(email, timeout=3):
            return None

        row_locator = self._make_contact_row_locator(email)
        row = self.find(row_locator, timeout=5)

        cells = row.find_elements("xpath", ".//td")
        texts = [c.text.strip() for c in cells]

        contact: Dict[str, str] = {"email": email}

        if len(texts) >= 1:
            contact["name"] = texts[0]
        if len(texts) >= 2:
            contact["email"] = texts[1]
        if len(texts) >= 3:
            contact["phone"] = texts[2]

        return contact

    def _find_row_and_button(self, email: str, button_locator_key: str):
        """
        Находит строку контакта и кнопку (Edit/Delete) внутри строки.
        """
        row_locator = self._make_contact_row_locator(email)
        row = self.find(row_locator, timeout=5)
        button_locator = self.locators[button_locator_key]
        button = row.find_element(button_locator["by"], button_locator["value"])
        return row, button

    @allure.step("Отредактировать текущий контакт (email: {email})")
    def edit_contact(self, email: str, new_contact: Dict[str, str]) -> None:
        """
        Редактирует контакт, который уже открыт на странице Contact info.

        Ожидаемое состояние перед вызовом:
          - открыта страница /account/contact/<id> с заголовком "Contact info"
          - это карточка контакта с email `email` (используется только для логов)

        :param email: Текущий email контакта (для логов/ожиданий).
        :param new_contact: Новый набор полей (как при create_contact).
        """
        # 1. Нажимаем Edit на странице Contact info
        self.click(self.locators["contact_info_edit_button"])

        # 2. Заполняем форму новыми данными
        self.fill_contact_form(new_contact)

        # 3. Сохраняем
        self.click(self.locators["contact_save_button"])

        # 4. убеждаемся,
        #    что контакт с новым email появился в списке
        self.wait_for_contact(new_contact["email"])

    @allure.step("Убедиться, что открыт блок Subscriptions")
    def ensure_subscriptions_opened(self) -> None:
        """
        Проверяет, что блок Subscriptions действительно отображается.
        По сути — ждём, когда появится регион с заголовком 'Subscriptions'.
        """
        self.find(self.locators["subscriptions_table"], timeout=30)

    @allure.step("Удалить контакт с email: {email}")
    def delete_contact(self, email: str) -> None:
        """
        Удаляет контакт с указанным email через кнопку Delete в строке и подтверждение.

        :param email: Email контакта.
        """
        _, delete_button = self._find_row_and_button(email, "contact_delete_button_in_row")
        delete_button.click()

        # подтверждение в диалоге (если есть)
        try:
            self.click(self.locators["confirm_delete_button"])
        except TimeoutException:
            log.info("Кнопка подтверждения удаления не найдена, возможно, удаление без диалога")

        assert not self.is_contact_present(email, timeout=10), (
            f"Контакт с email {email} не должен отображаться после удаления"
        )

    @allure.step("Удалить контакт, если он существует: {email}")
    def delete_contact_if_exists(self, email: str) -> None:
        """
        Идемпотентно удаляет контакт, если он есть (для подготовки окружения).
        """
        if self.is_contact_present(email, timeout=2):
            self.delete_contact(email)
