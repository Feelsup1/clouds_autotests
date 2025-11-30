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

    url_fragment = "/dashboard"
    required_locators = ("user_menu_button", "sidebar_menu", "current_balance")
    LOCATORS_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "locators",
        "dashboard_page.yaml",
    )

    def __init__(self, driver, base_url: str):
        super().__init__(driver, base_url)
        self.locators: Dict[str, dict] = load_yaml(self.LOCATORS_PATH)
