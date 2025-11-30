# file: pages/account_settings_page.py
import os
import logging
from typing import Dict

import allure

from utils.yaml_loader import load_yaml
from pages.base_page import BasePage


log = logging.getLogger(__name__)


class AccountSettingsPage(BasePage):
    """
    Page Object для Account Settings -> Subscriptions.
    """

    LOCATORS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locators", "account_settings.yaml")

    def __init__(self, driver, base_url: str):
        """
        :param driver: Экземпляр WebDriver.
        :param base_url: Базовый URL портала.
        """
        super().__init__(driver, base_url)
        self.locators: Dict[str, dict] = load_yaml(self.LOCATORS_PATH)

    @allure.step("Открыть страницу Account Settings / Subscriptions")
    def open_subscriptions(self) -> None:
        """
        Открывает страницу Subscriptions.

        Предполагается, что пользователь уже залогинен.
        """
        # путь примерный, подправь по реальному URL
        self.open("account/settings/subscriptions")

    @allure.step("Добавить контакт с заполнением всех полей")
    def add_contact(self, name: str, email: str, phone: str) -> None:
        """
        Добавляет новый контакт в блоке Subscriptions.

        :param name: Имя контакта.
        :param email: Email контакта.
        :param phone: Телефон контакта.
        """
        self.click(self.locators["add_contact_button"])
        self.type(self.locators["contact_name_input"], name)
        self.type(self.locators["contact_email_input"], email)
        self.type(self.locators["contact_phone_input"], phone)
        self.click(self.locators["contact_save_button"])

    @allure.step("Отредактировать первый контакт")
    def edit_first_contact(self, new_name: str) -> None:
        """
        Редактирует первый контакт в таблице.

        :param new_name: Новое имя контакта.
        """
        self.click(self.locators["contact_edit_button"])
        self.type(self.locators["contact_name_input"], new_name)
        self.click(self.locators["contact_save_button"])

    @allure.step("Удалить первый контакт")
    def delete_first_contact(self) -> None:
        """
        Удаляет первый контакт в списке.
        """
        self.click(self.locators["contact_delete_button"])

    def has_any_contact(self) -> bool:
        """
        Проверяет, что в таблице есть хотя бы один контакт.

        :return: True, если контакт есть; False иначе.
        """
        try:
            self.find(self.locators["contact_row"], timeout=5)
            log.info("Контакт найден в таблице")
            return True
        except Exception:
            log.info("Контактов в таблице не найдено")
            return False
