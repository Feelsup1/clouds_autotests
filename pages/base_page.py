# file: pages/base_page.py
import os
import logging
from typing import Tuple

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC

from utils.wait import wait_for


log = logging.getLogger(__name__)


class BasePage:
    """
    Базовый класс для всех Page Object'ов.

    Содержит общие методы взаимодействия с элементами, ожиданий, логирования
    и добавления скриншотов в Allure.
    """

    def __init__(self, driver: WebDriver, base_url: str):
        """
        :param driver: Экземпляр WebDriver.
        :param base_url: Базовый URL тестируемого приложения.
        """
        self.driver = driver
        self.base_url = base_url.rstrip("/") + "/"

    def open(self, path: str = "") -> None:
        """
        Открывает страницу по относительному пути.

        :param path: Относительный путь (например, 'login' или 'account/settings').
        """
        url = self.base_url + path.lstrip("/")
        log.info(f"Открытие URL: {url}")
        with allure.step(f"Открыть страницу: {url}"):
            self.driver.get(url)

    @staticmethod
    def _to_by(locator: dict) -> Tuple[str, str]:
        """
        Преобразует словарь локатора из YAML к нужному формату Selenium.

        :param locator: Словарь вида {'by': 'css selector', 'value': '...'}.
        :return: Кортеж (By, selector).
        """
        by_str = locator["by"]
        value = locator["value"]
        by_map = {
            "id": By.ID,
            "name": By.NAME,
            "xpath": By.XPATH,
            "css selector": By.CSS_SELECTOR,
            "class name": By.CLASS_NAME,
            "link text": By.LINK_TEXT,
            "partial link text": By.PARTIAL_LINK_TEXT,
            "tag name": By.TAG_NAME,
        }
        return by_map[by_str], value

    def is_element_present(self, locator: dict, timeout: int = 20) -> bool:
        """
        Проверяет, что элемент присутствует на странице.

        :param locator: Словарь локатора из YAML.
        :param timeout: Таймаут ожидания.
        :return: True, если элемент найден, иначе False.
        """
        try:
            self.find(locator, timeout)
            return True
        except TimeoutException:
            return False

    def find(self, locator: dict, timeout: int = 20):
        """
        Находит элемент с явным ожиданием.

        :param locator: Словарь локатора из YAML.
        :param timeout: Таймаут ожидания.
        :return: WebElement.
        """
        by, value = self._to_by(locator)
        log.debug(f"Ожидание элемента: by={by}, value={value}")
        try:
            return wait_for(self.driver, EC.visibility_of_element_located((by, value)), timeout)
        except TimeoutException:
            self._attach_screenshot("element_not_found")
            raise

    def find_all(self, locator: dict, timeout: int = 10):
        """
        Находит все элементы с явным ожиданием наличия хотя бы одного.

        :param locator: Словарь локатора из YAML.
        :param timeout: Таймаут ожидания.
        :return: Список WebElement.
        """
        by, value = self._to_by(locator)
        log.debug(f"Ожидание списка элементов: by={by}, value={value}")
        try:
            return wait_for(self.driver, EC.presence_of_all_elements_located((by, value)), timeout)
        except TimeoutException:
            self._attach_screenshot("elements_not_found")
            raise

    def click(self, locator: dict, timeout: int = 10) -> None:
        """
        Кликает по элементу с ожиданием кликабельности.

        :param locator: Словарь локатора из YAML.
        :param timeout: Таймаут ожидания.
        """
        by, value = self._to_by(locator)
        with allure.step(f"Клик по элементу: {by}={value}"):
            log.info(f"Клик по элементу: by={by}, value={value}")
            try:
                element = wait_for(self.driver, EC.element_to_be_clickable((by, value)), timeout)
                element.click()
            except (TimeoutException, WebDriverException):
                self._attach_screenshot("click_error")
                raise

    def type(self, locator: dict, text: str, timeout: int = 10, clear: bool = True) -> None:
        """
        Вводит текст в поле ввода.

        :param locator: Словарь локатора из YAML.
        :param text: Вводимый текст.
        :param timeout: Таймаут ожидания.
        :param clear: Нужно ли предварительно очистить поле.
        """
        by, value = self._to_by(locator)
        with allure.step(f"Ввод текста '{text}' в поле: {by}={value}"):
            log.info(f"Ввод текста в элемент: by={by}, value={value}, text={text}")
            try:
                element = wait_for(self.driver, EC.visibility_of_element_located((by, value)), timeout)
                if clear:
                    element.clear()
                element.send_keys(text)
            except (TimeoutException, WebDriverException):
                self._attach_screenshot("type_error")
                raise

    def get_text(self, locator: dict, timeout: int = 10) -> str:
        """
        Возвращает текст элемента.

        :param locator: Словарь локатора из YAML.
        :param timeout: Таймаут ожидания.
        :return: Текст элемента.
        """
        element = self.find(locator, timeout)
        text = element.text
        log.info(f"Текст элемента: '{text}'")
        return text

    def _attach_screenshot(self, name: str) -> None:
        """
        Создает скриншот и прикрепляет его к Allure-отчету.

        :param name: Имя скриншота.
        """
        try:
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
        except WebDriverException as e:
            log.error(f"Не удалось сделать скриншот: {e}")

    def click_if_present(self, locator: dict, timeout: int = 3) -> bool:
        """
        Пытается кликнуть по элементу, если он появился в течение timeout.
        Если элемент не появился — молча продолжает тест.

        :param locator: Словарь локатора из YAML.
        :param timeout: Таймаут ожидания элемента.
        :return: True, если кликнули; False, если элемент не появился.
        """
        by, value = self._to_by(locator)
        with allure.step(f"Клик по элементу (если есть): {by}={value}"):
            log.info(f"Пробуем кликнуть (если есть) по элементу: by={by}, value={value}")
            try:
                element = wait_for(self.driver, EC.element_to_be_clickable((by, value)), timeout)
                element.click()
                log.info("Элемент найден и нажат")
                return True
            except TimeoutException:
                log.info("Элемент не появился, продолжаем без клика")
                return False
            except WebDriverException:
                self._attach_screenshot("click_if_present_error")
                raise
