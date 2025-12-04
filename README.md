# UI автотесты для https://portal.servers.com/

Репозиторий содержит небольшую, но «живую» UI-автоматизацию под тестовое задание от **servers.com**:

> Написать базовые автотесты (любой язык/фреймворк):
>
> - Login / Logout;
> - Account settings → блок **Subscriptions**: добавление, редактирование и удаление контакта с заполнением всех полей;
> - Проверка работоспособности бокового меню;
> - Приложить команды для запуска тестов.

Реализация сделана на **Python + pytest + Selenium + Allure**, с использованием **Page Object Model** и вынесением локаторов в отдельные **YAML**-файлы.

---

## Технологии

- **Python 3.10+**
- **pytest** — фреймворк для тестов
- **Selenium WebDriver** — UI-автоматизация (Chrome)
- **webdriver-manager** — автозагрузка драйвера
- **Allure** — шаги и отчёты
- **PyYAML** — загрузка локаторов из `*.yaml`
- Логирование через стандартный `logging`

---

## Основная функциональность тестов

### 1. Login / Logout

Файл: `tests/test_auth.py`  
Page Object: `pages/auth_page.py`

Сценарии:

- Позитивный вход с валидными логином/паролем и последующий logout.
- Негативные сценарии авторизации:
  - пустые поля;
  - неверный пароль;
  - некорректный email и т.д.
- Используются техники тест-дизайна:
  - **EC (Equivalence Classes)** — классы валидных/невалидных данных;
  - **BVA (Boundary Value Analysis)** — пустые строки как нижняя граница.

После логина проверяется наличие меню пользователя, после logout — возврат на страницу `/login`.

---

### 2. Боковое меню (Sidebar)

Файл: `tests/test_sidebar.py`  
Page Object: `pages/sidebar_page.py`  
Локаторы: `locators/sidebar.yaml` (или в `dashboard/account`, в зависимости от структуры)

Сценарии:

- Переход по основным пунктам левого бокового меню (например: SSL, Account settings, Requests).
- Для каждого пункта:
  - кликаем по соответствующему элементу;
  - проверяем, что `current_url` содержит ожидаемый фрагмент (`/ssl`, `/account`, `/requests` и т.д.).

Тест параметризован, каждый пункт меню — отдельный **класс эквивалентности**.  
Первый и последний элементы панели дополнительно рассматриваются как **границы** (BVA).

---

### 3. Account settings → Subscriptions (CRUD контактов)

Файл: `tests/test_subscriptions.py`  
Page Object: `pages/account_settings_page.py`  
Локаторы: `locators/account_settings.yaml`

Реализованы сценарии:

1. **Добавление контакта** с заполнением всех полей:
   - Contact info (first/middle/last name, nickname, comments);
   - Job role (company, job title, job role, чекбоксы ролей: Primary / Technical / Billing / Abuse / Emergency);
   - Contact details (phone, email, secondary email);
   - Notes / Comments.
   - После создания — проверка, что контакт появился в таблице (по email).

2. **Редактирование контакта**:
   - При необходимости контакт создаётся заранее.
   - Меняются несколько полей (например, имя, телефон, заметки).
   - После сохранения проверяется, что обновлённые данные отразились в списке.

3. **Удаление контакта**:
   - При необходимости контакт предварительно создаётся.
   - Удаление происходит строго по email (выбор нужной строки и её кнопки-корзины).
   - Проверяется, что контакт больше не отображается.

Все операции обёрнуты в Allure-шаги, используются вспомогательные методы:

- `create_contact(contact)`
- `edit_contact(email, new_contact)`
- `delete_contact(email)`
- `is_contact_present(email)`
- `delete_contact_if_exists(email)`

Генерация тестовых данных вынесена в `_make_contact_data`, чтобы не дублировать строки в тестах.

---

## Структура проекта

```text
servers_autotests/
├── pages/
│   ├── base_page.py            # Общий базовый Page Object (open, click, type, find, waits, логирование)
│   ├── auth_page.py            # Страница логина/логаута
│   ├── sidebar_page.py         # Боковое меню
│   └── account_settings_page.py# Account settings / Subscriptions
│
├── locators/
│   ├── auth_page.yaml          # Локаторы для логина/логаута и cookie-баннера
│   ├── sidebar.yaml            # Локаторы пунктов бокового меню
│   └── account_settings.yaml   # Локаторы для блока Subscriptions
│
├── tests/
│   ├── test_auth.py            # Login / Logout + негативные сценарии авторизации
│   ├── test_sidebar.py         # Проверка навигации по боковому меню
│   └── test_subscriptions.py   # Add / Edit / Delete контактов в Subscriptions
│
├── utils/
│   ├── wait.py                 # Обёртка над WebDriverWait (wait_for)
│   ├── yaml_loader.py          # Загрузка YAML локаторов
│   └── logger.py               # Настройка логирования
│
├── conftest.py                 # Pytest-фикстуры (driver, base_url, credentials, и т.д.)
├── requirements.txt            # Зависимости проекта
└── README.md                   # Этот файл


---

## Быстрый старт (как запустить тесты)

```bash
git clone https://github.com/Feelsup1/servers_autotests.git
cd servers_autotests
git checkout tests                  # тестовое находится в ветке tests

python -m venv venv
venv\Scripts\activate               # Windows PowerShell/cmd
pip install -r requirements.txt

# задать учётные данные через переменные окружения
set PORTAL_LOGIN=day+test2@servers.com
set PORTAL_PASSWORD=pef2cxp8dqj_tcq_XTW

# прогнать все тесты
pytest -v --alluredir=allure-results

# Просмотр отчёта Allure (если установлен allure CLI):
allure serve allure-results
