# file: utils/wait.py
from typing import Callable, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait


def wait_for(driver: WebDriver, condition: Callable[[WebDriver], Any], timeout: int = 10):
    """
    Обертка над WebDriverWait.

    :param driver: Экземпляр WebDriver.
    :param condition: Callable условие (обычно expected_conditions.*).
    :param timeout: Таймаут ожидания в секундах.
    :return: Результат condition.
    """
    return WebDriverWait(driver, timeout).until(condition)
