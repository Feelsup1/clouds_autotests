# file: pages/dashboard_page.py
import os
from typing import Dict
import allure

from pages.base_page import BasePage
from utils.yaml_loader import load_yaml


class DashboardPage(BasePage):
    """
    Page Object для дашборда после успешного логина.
    """

    URL_FRAGMENT = "/dashboard"
    LOCATORS_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "locators",
        "dashboard_page.yaml",
    )

    def __init__(self, driver, base_url: str):
        super().__init__(driver, base_url)
        self.locators: Dict[str, dict] = load_yaml(self.LOCATORS_PATH)

    @allure.step("Убедиться, что открыт дашборд")
    def ensure_opened(self) -> None:
        """
        Проверяет, что пользователь находится на странице дашборда:
          - URL содержит /dashboard;
          - видны ключевые элементы (меню пользователя, сайдбар, баланс и т.п.).
        """
        self.wait_url_contains(self.URL_FRAGMENT, timeout=30)
        self.ensure_locators_present(
            "user_menu_button",
            "sidebar_menu",
            timeout=30,
        )
