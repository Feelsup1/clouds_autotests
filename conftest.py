# file: conftest.py
import os
import logging
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import allure

from utils.logger import configure_logging


log = logging.getLogger(__name__)


def pytest_configure(config):
    """Глобальная настройка логирования для всего раннера."""
    configure_logging()
    log.info("Pytest configuration initialized")


@pytest.fixture(scope="session")
def base_url() -> str:
    """
    Базовый URL портала.

    :return: Базовый URL.
    """
    return "https://portal.servers.com/"


@pytest.fixture(scope="session")
def credentials() -> dict:
    """
    Фикстура с кредами, скрытыми через переменные окружения.

    Ожидаемые переменные:
        PORTAL_LOGIN
        PORTAL_PASSWORD
    """
    login = os.getenv("PORTAL_LOGIN")
    password = os.getenv("PORTAL_PASSWORD")

    if not login or not password:
        raise RuntimeError(
            "Не заданы переменные окружения PORTAL_LOGIN / PORTAL_PASSWORD"
        )

    return {"login": login, "password": password}


@pytest.fixture(scope="function")
def driver() -> webdriver.Chrome:
    """
    Фикстура инициализирует WebDriver и закрывает его по завершении сессии.

    :return: Экземпляр Selenium WebDriver.
    """
    options = Options()
    # В реальной жизни тут можно включить headless и пр.
    # options.add_argument("--headless=new")
    options.add_argument("--start-maximized")

    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(5)

    yield drv

    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Хук pytest — если тест упал, прикрепляем скриншот к Allure.
    """
    outcome = yield
    result = outcome.get_result()

    if result.when == "call" and result.failed:
        driver_fixture = item.funcargs.get("driver")
        if driver_fixture:
            try:
                allure.attach(
                    driver_fixture.get_screenshot_as_png(),
                    name=f"screenshot_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception as e:
                log.error(f"Не удалось сделать скриншот: {e}")
