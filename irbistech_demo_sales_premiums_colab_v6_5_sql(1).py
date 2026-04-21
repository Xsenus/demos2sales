
# ============================================================
# ИРБИСТЕХ — демонстрации, продажи и премии
# v6.5_sql: PostgreSQL backend, без внешних CRM, товары вручную/через шаблон,
# критерии 3 блоков компактными строками-таблицами, единый Arial-интерфейс,
# совместимость с версиями Gradio в Colab без ошибки LoginButton.
# Google Colab: выполнить одной ячейкой
# ============================================================

import os
import sys
import json
import math
import uuid
import subprocess
import importlib.util
import inspect
from pathlib import Path
from datetime import date, datetime

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value.strip())
    except Exception:
        return default


def install_if_missing(import_name: str, pip_name: str | None = None):
    pip_name = pip_name or import_name
    if importlib.util.find_spec(import_name) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pip_name])

AUTO_INSTALL_PACKAGES = env_bool("DEMO_CALC_AUTO_INSTALL_PACKAGES", True)

if AUTO_INSTALL_PACKAGES:
    for _import, _pip in [
        ("gradio", "gradio"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
        ("xlsxwriter", "xlsxwriter"),
        ("psycopg2", "psycopg2-binary"),
    ]:
        install_if_missing(_import, _pip)

import pandas as pd
import gradio as gr
from demo_calculator_widget import (
    COMPANY_SUPPORT_ARTICLE,
    FIXED_ARTICLES,
    build_demo_calc_html,
    fixed_rows_from_state,
    split_calc_state,
)

# ============================================================
# Совместимость с некоторыми сборками Gradio в Colab
# ============================================================
# Встречается несовпадение пакетов, когда gradio.blocks внутри метода
# expects_oauth обращается к gradio.components.LoginButton, а такого
# класса в gradio.components нет. Тогда приложение падает еще на строке
# with gr.Blocks(...), даже если LoginButton в интерфейсе не используется.
# Ниже два уровня защиты:
# 1) добавляем отсутствующие классы в gradio.components и gradio.blocks.components;
# 2) отключаем OAuth-проверку Blocks.expects_oauth, так как в этом приложении
#    OAuth и LoginButton не используются.
try:
    import gradio.components as _gradio_components
    import gradio.blocks as _gradio_blocks

    class _CompatLoginButton:
        pass

    class _CompatLogoutButton:
        pass

    if not hasattr(_gradio_components, "LoginButton"):
        setattr(_gradio_components, "LoginButton", _CompatLoginButton)
    if not hasattr(_gradio_components, "LogoutButton"):
        setattr(_gradio_components, "LogoutButton", _CompatLogoutButton)

    if hasattr(_gradio_blocks, "components"):
        if not hasattr(_gradio_blocks.components, "LoginButton"):
            setattr(_gradio_blocks.components, "LoginButton", getattr(_gradio_components, "LoginButton", _CompatLoginButton))
        if not hasattr(_gradio_blocks.components, "LogoutButton"):
            setattr(_gradio_blocks.components, "LogoutButton", getattr(_gradio_components, "LogoutButton", _CompatLogoutButton))

    def _irbis_no_oauth(self):
        return False

    try:
        _gradio_blocks.Blocks.expects_oauth = property(_irbis_no_oauth)
    except Exception:
        pass
except Exception:
    pass

import psycopg2
from psycopg2.extras import Json, RealDictCursor, execute_values

try:
    from google.colab import output
    output.enable_custom_widget_manager()
except Exception:
    pass


def dataframe_compat(**kwargs):
    """Gradio Dataframe compatibility: prefer column_count, fallback to col_count."""
    import inspect
    params = inspect.signature(gr.Dataframe).parameters
    if "col_count" in kwargs and "column_count" in params:
        kwargs["column_count"] = kwargs.pop("col_count")
    elif "column_count" in kwargs and "column_count" not in params and "col_count" in params:
        kwargs["col_count"] = kwargs.pop("column_count")
    return gr.Dataframe(**kwargs)

# ============================================================
# 1. НАСТРОЙКИ ПОДКЛЮЧЕНИЯ И КОНСТАНТЫ
# ============================================================

DB_HOST = os.getenv("DEMO_CALC_DB_HOST", "79.174.94.14")
DB_PORT = int(os.getenv("DEMO_CALC_DB_PORT", "5464"))
DB_NAME = os.getenv("DEMO_CALC_DB_NAME", "demo_calc")
DB_USER = os.getenv("DEMO_CALC_DB_USER", "admin")
DB_PASSWORD = os.getenv("DEMO_CALC_DB_PASSWORD", "")
USE_POSTGRES = env_bool("DEMO_CALC_USE_POSTGRES", True)
AUTO_SEED_EMPTY_DATABASE = env_bool("DEMO_CALC_AUTO_SEED_EMPTY_DATABASE", True)

BASE_DIR = Path(os.getenv("DEMO_CALC_BASE_DIR", Path(__file__).resolve().parent))
DATA_DIR = Path(os.getenv("DEMO_CALC_DATA_DIR", BASE_DIR / "data"))
EXPORT_DIR = Path(os.getenv("DEMO_CALC_EXPORT_DIR", DATA_DIR / "exports"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

JSON_BACKUP_PATH = str(Path(os.getenv("DEMO_CALC_JSON_BACKUP_PATH", DATA_DIR / "irbistech_demo_sales_data_backup_v6_5.json")))
EXPORT_XLSX_PATH = str(Path(os.getenv("DEMO_CALC_EXPORT_XLSX_PATH", EXPORT_DIR / "irbistech_demo_sales_export_v6_5.xlsx")))
PRODUCT_TEMPLATE_PATH = str(Path(os.getenv("DEMO_CALC_PRODUCT_TEMPLATE_PATH", EXPORT_DIR / "irbistech_products_template_v6_5.xlsx")))

ACTION_DEMO = "Проведенная демонстрация"
ACTION_SALE = "Проданное оборудование"
ACTION_PREMIUM = "Выплата премии"
SHORT_TYPE = {ACTION_DEMO: "Демо", ACTION_SALE: "Продажа", ACTION_PREMIUM: "Премия"}

USERS = {
    "artur": {"login": "artur", "password": "123", "role": "director", "name": "Артур Гимадеев"},
    "ruslan": {"login": "ruslan", "password": "111", "role": "manager", "name": "Руслан Абдулин"},
    "timur": {"login": "timur", "password": "222", "role": "manager", "name": "Тимур Сафин"},
    "maria": {"login": "maria", "password": "333", "role": "manager", "name": "Мария Иванова"},
    "ildar": {"login": "ildar", "password": "444", "role": "manager", "name": "Ильдар Хасанов"},
}
MANAGER_LOGINS = [k for k, v in USERS.items() if v["role"] == "manager"]
MANAGER_CHOICES = [(USERS[k]["name"], k) for k in MANAGER_LOGINS]
MANAGER_FILTER_CHOICES = [("Все менеджеры", "__all__")] + MANAGER_CHOICES
FONT_CHOICES = ["Arial"]

PRODUCT_COLUMNS = [
    "ID товара", "Артикул", "Наименование ТМЦ", "Цена руб. с НДС",
    "Цена руб. без НДС (A)", "Минимальная цена продажи без НДС (B)",
    "Маржа, руб. без НДС (C)", "% от маржи (D)", "Премия NET (P)", "Комментарий",
]
SALE_COLUMNS = [
    "ID товара", "Артикул", "Наименование оборудования", "Цена руб. с НДС",
    "Цена руб. без НДС", "Кол-во", "ИТОГО с НДС", "ИТОГО без НДС",
    "Сумма НДС", "Минимальная цена продажи без НДС", "Маржа факт на единицу",
    "% от маржи факт", "Премия NET",
]
EXPENSE_COLUMNS = [
    "Статья расхода", "Кол-во", "Ед.изм.", "Цена, руб. без НДС",
    "Цена, руб. с НДС", "Сумма затрат, руб. с НДС", "Комментарий",
]
EXPENSE_SETTINGS_COLUMNS = [
    "Статья расхода", "Ед.изм.", "Кол-во по умолчанию", "Цена без НДС по умолчанию",
    "Цена с НДС по умолчанию", "Кол-во редактирует менеджер", "Цену редактирует менеджер",
    "Тип расчета", "Комментарий",
]
CRITERIA_SETTINGS_COLUMNS = ["Блок", "Код", "Критерий", "Описание", "Уровни JSON"]
UI_SETTINGS_COLUMNS = ["Параметр", "Значение", "Описание"]

# ============================================================
# 2. СПРАВОЧНИКИ МЕТОДИКИ И СМЕТЫ
# ============================================================

DEFAULT_CRITERIA = [
    {"block":"P", "code":"P1", "title":"Покупающий центр подтвержден", "desc":"Кто со стороны клиента участвует в демонстрации и согласовании.", "levels":[["Участники не подтверждены",0],["Только пользователь / мастер",5],["Есть технический инициатор",10],["Есть руководитель / ЛПР и технический инициатор",15]]},
    {"block":"P", "code":"P2", "title":"Объект очистки определен", "desc":"Есть ли конкретный объект, который будут чистить.", "levels":[["Объект не выбран",0],["Объект назван устно",5],["Объект назван и есть фото / видео",10],["Объект назван, есть фото / видео и клиент подтвердил его приоритет",15]]},
    {"block":"P", "code":"P3", "title":"Загрязнение и текущий метод очистки описаны", "desc":"Понятно ли, что удалить и чем клиент чистит сейчас.", "levels":[["Загрязнение не описано",0],["Описано только загрязнение",4],["Описаны загрязнение и текущий метод",7],["Описаны загрязнение, текущий метод и проблемы текущего метода",10]]},
    {"block":"P", "code":"P4", "title":"Воздух и площадка подтверждены", "desc":"Готовность пневмосети и места проведения.", "levels":[["Данные по воздуху отсутствуют",0],["Подтверждено только давление",5],["Подтверждены давление и расход",10],["Подтверждены давление, расход, подключение, доступ и безопасность",15]]},
    {"block":"P", "code":"P5", "title":"Критерии успеха согласованы", "desc":"Договорились ли заранее, что считается успешной демонстрацией.", "levels":[["Критерии не согласованы",0],["Есть устное ожидание результата",5],["Согласованы качество и время очистки",10],["Согласованы качество, время, расход льда и способ фиксации результата",15]]},
    {"block":"P", "code":"P6", "title":"Коммерческий потенциал понятен", "desc":"Есть ли связь между демонстрацией и будущей продажей.", "levels":[["Коммерческий потенциал не понятен",0],["Есть общий интерес",5],["Понятна возможная модель или бюджет",10],["Понятны модель, бюджет, срок и следующий шаг",15]]},
    {"block":"P", "code":"P7", "title":"Логистика и бюджет выезда согласованы", "desc":"Подготовлены ли маршрут, лед, транспорт, люди и бюджет.", "levels":[["Логистика не согласована",0],["Согласованы маршрут и участники",5],["Согласованы маршрут, участники, лед, транспорт и бюджет",10]]},
    {"block":"P", "code":"P8", "title":"Карточка подготовки заполнена", "desc":"Формальный критерий дисциплины. Без карточки нельзя доказать подготовку.", "levels":[["Карточка отсутствует",0],["Карточка заполнена частично",3],["Карточка заполнена полностью",5]]},
    {"block":"R", "code":"R1", "title":"Согласованный технический результат достигнут", "desc":"Достигнута ли цель очистки, согласованная до демонстрации.", "levels":[["Результат не достигнут",0],["Результат достигнут частично",8],["Результат достигнут полностью",15],["Результат достигнут лучше согласованных критериев",20]]},
    {"block":"R", "code":"R2", "title":"Измерения зафиксированы", "desc":"Есть ли цифры: время, расход льда, давление, сопло, площадь / деталь.", "levels":[["Измерений нет",0],["Есть только фото / видео",5],["Есть время или расход льда",10],["Есть время, расход льда, давление, сопло и площадь / деталь",15]]},
    {"block":"R", "code":"R3", "title":"Клиент подтвердил результат", "desc":"Кто со стороны клиента увидел и подтвердил результат.", "levels":[["Подтверждения клиента нет",0],["Подтвердил пользователь / мастер",5],["Подтвердил технический инициатор",10],["Подтвердил руководитель / ЛПР или главный инженер",15]]},
    {"block":"R", "code":"R4", "title":"Следующий шаг после демонстрации получен", "desc":"КП, счет, аренда, договор или повторный тест.", "levels":[["Следующего шага нет",0],["Есть только устный интерес",5],["Назначена дата следующего контакта / встречи",12],["Запрошены КП, счет, аренда, договор или повторный тест",20]]},
    {"block":"R", "code":"R5", "title":"Отчет по демонстрации оформлен", "desc":"Отчет для клиента и контроля ИРБИСТЕХ.", "levels":[["Отчета нет",0],["Есть краткий отчет с фото / видео",5],["Есть отчет с фото / видео, цифрами и выводом",10]]},
    {"block":"R", "code":"R6", "title":"Экономика для клиента посчитана", "desc":"Технический результат переведен в часы, рубли или человеко-часы.", "levels":[["Экономика не обсуждалась",0],["Есть оценка эффекта словами",5],["Есть расчет в часах, рублях или человеко-часах",10]]},
    {"block":"R", "code":"R7", "title":"Причина неуспеха или отказа зафиксирована", "desc":"Если нет продажи, понятно почему и что делать дальше.", "levels":[["Причина не зафиксирована",0],["Причина описана устно",5],["Причина зафиксирована письменно и есть дальнейшее решение",10]]},
    {"block":"M", "code":"M1", "title":"Стратегический статус клиента подтвержден", "desc":"Крупный клиент, отраслевой лидер, повторные продажи, публичный кейс.", "levels":[["Стратегический статус не подтвержден",0],["Статус подтвержден руководителем продаж",8],["Статус подтвержден директором до выезда",15]]},
    {"block":"M", "code":"M2", "title":"Клиент участвует в расходах", "desc":"Оплата или организационное участие клиента подтверждает серьезность намерений.", "levels":[["Клиент не участвует",0],["Клиент предоставляет только площадку / людей",5],["Клиент оплачивает часть расходов",12],["Клиент оплачивает демонстрацию полностью или почти полностью",20]]},
    {"block":"M", "code":"M3", "title":"Выезд заранее согласован внутри ИРБИСТЕХ", "desc":"Кто разрешил тратить деньги на демонстрацию.", "levels":[["Выезд не согласован заранее",0],["Выезд согласован с руководителем продаж",8],["Выезд согласован директором до начала расходов",15]]},
    {"block":"M", "code":"M4", "title":"Логистика выезда оптимизирована", "desc":"Расходы распределяются на несколько задач маршрута.", "levels":[["Отдельный выезд только под одного клиента",0],["Выезд частично совмещен с другой задачей",5],["В маршруте 2+ демонстрации / задачи",10]]},
    {"block":"M", "code":"M5", "title":"Повторная демонстрация обоснована", "desc":"Повтор по запросу клиента отличается от повтора из-за ошибки подготовки.", "levels":[["Повтор из-за ошибки подготовки",0],["Первая демонстрация или повтор не требуется",7],["Повтор по запросу клиента после успешной демонстрации",10]]},
    {"block":"M", "code":"M6", "title":"Демонстрация дала маркетинговую или R&D-ценность", "desc":"Фото, видео, новый кейс, новая отрасль, проверка новой задачи.", "levels":[["Материалы непригодны для повторного использования",0],["Материалы пригодны только внутри компании",7],["Материалы пригодны для кейса / обучения / R&D",15]]},
    {"block":"M", "code":"M7", "title":"Ответственность за отклонения и перерасход", "desc":"Защита от снижения вычета, если перерасход возник по вине менеджера.", "levels":[["Отклонение возникло по вине менеджера",0],["Отклонений не было",10],["Отклонение возникло по подтвержденной причине вне зоны ответственности менеджера",15]]},
]

DEFAULT_EXPENSE_SETTINGS = [
    {"article":"Работа водителя", "unit":"км", "qty_default":1800, "price_net_default":15, "price_vat_default":None, "qty_manager":True, "price_manager":False, "calc_type":"direct", "comment":"Красная цена из настроек, синее количество у менеджера"},
    {"article":"Работа демонстратора", "unit":"часы", "qty_default":16, "price_net_default":1350, "price_vat_default":None, "qty_manager":True, "price_manager":False, "calc_type":"direct", "comment":"Красная цена из настроек"},
    {"article":"Демонстрация криобластера", "unit":"усл", "qty_default":5, "price_net_default":4000, "price_vat_default":None, "qty_manager":True, "price_manager":False, "calc_type":"direct", "comment":"Красная цена из настроек"},
    {"article":"Усложненные условия труда", "unit":"усл", "qty_default":0, "price_net_default":1700, "price_vat_default":None, "qty_manager":True, "price_manager":False, "calc_type":"direct", "comment":"Красная цена из настроек"},
    {"article":"Ручная работа с кабелем и шланга компрессора", "unit":"усл", "qty_default":0, "price_net_default":3500, "price_vat_default":None, "qty_manager":True, "price_manager":False, "calc_type":"direct", "comment":"Красная цена из настроек"},
    {"article":"Использование электрокатушки", "unit":"усл", "qty_default":1, "price_net_default":1500, "price_vat_default":None, "qty_manager":True, "price_manager":True, "calc_type":"direct", "comment":"Синее поле, менеджер может менять количество и цену"},
    {"article":"Выгрузка и загрузка компрессора и электрокатушки", "unit":"усл", "qty_default":0, "price_net_default":1500, "price_vat_default":None, "qty_manager":True, "price_manager":True, "calc_type":"direct", "comment":"Синее поле"},
    {"article":"Налоги на ФОТ", "unit":"усл", "qty_default":0, "price_net_default":0, "price_vat_default":0, "qty_manager":False, "price_manager":False, "calc_type":"payroll_tax", "comment":"Формула: 30% от строк ФОТ и демонстратора"},
    {"article":"Расходы на отель Менеджера", "unit":"день х чел", "qty_default":3, "price_net_default":2800, "price_vat_default":None, "qty_manager":True, "price_manager":True, "calc_type":"direct", "comment":"Синее поле"},
    {"article":"Расходы на отель Водителя", "unit":"день х чел", "qty_default":3, "price_net_default":2800, "price_vat_default":None, "qty_manager":True, "price_manager":True, "calc_type":"direct", "comment":"Синее поле"},
    {"article":"Расходы на переезд менеджера", "unit":"усл", "qty_default":0, "price_net_default":3000, "price_vat_default":None, "qty_manager":True, "price_manager":True, "calc_type":"direct", "comment":"Синее поле"},
    {"article":"Расходы на платную дорогу", "unit":"усл", "qty_default":0, "price_net_default":0, "price_vat_default":0, "qty_manager":True, "price_manager":True, "calc_type":"direct", "comment":"Пользовательское значение"},
    {"article":"Суточные для командировки", "unit":"день х чел", "qty_default":6, "price_net_default":1500, "price_vat_default":None, "qty_manager":False, "price_manager":False, "calc_type":"direct", "comment":"Красное/формульное поле"},
    {"article":"Расходы на дизель (12 л/100км), л", "unit":"литры", "qty_default":0, "price_net_default":0, "price_vat_default":78, "qty_manager":False, "price_manager":False, "calc_type":"diesel", "comment":"Формула: км / 100 × 12 × цена топлива"},
    {"article":"Амортизация Газели", "unit":"км", "qty_default":0, "price_net_default":0, "price_vat_default":10, "qty_manager":False, "price_manager":False, "calc_type":"gazelle_amort", "comment":"Формула: км × ставка амортизации"},
    {"article":"Расходы на закупку сухого льда", "unit":"кг", "qty_default":300, "price_net_default":0, "price_vat_default":90, "qty_manager":True, "price_manager":True, "calc_type":"direct_vat_price", "comment":"Синее поле"},
    {"article":"Расходы на доставку сухого льда в цех", "unit":"усл", "qty_default":0, "price_net_default":1500, "price_vat_default":None, "qty_manager":True, "price_manager":False, "calc_type":"direct", "comment":"Красная цена из настроек"},
]


def default_settings():
    return {
        "vat_rate": 0.22,
        "bonus_rate": 0.65,
        "max_demo_deduction_pct": 1.00,
        "company_support_vat": 30000.0,
        "payroll_tax_rate": 0.30,
        "diesel_l_per_100km": 12.0,
        "p_weight": 0.45,
        "r_weight": 0.35,
        "m_weight": 0.20,
        "k_reduction_factor": 0.80,
        "min_normal_k": 0.20,
        "min_soft_stop_k": 0.80,
        "font_family": "Arial",
        "ui": {
            "action_list_width_pct": 30,
            "font_base_px": 13,
            "font_title_px": 18,
            "card_padding_px": 10,
            "field_gap_px": 8,
            "table_row_height_px": 30,
            "criteria_name_width_pct": 20,
            "criteria_levels_width_pct": 60,
            "criteria_comment_width_pct": 20,
        },
        "criteria": DEFAULT_CRITERIA,
        "expense_settings": DEFAULT_EXPENSE_SETTINGS,
    }


def default_products():
    return [
        {"product_id":"MINI-3.0-P10-F2500", "sku":"MINI-3.0-P10-F2500", "name":"Криобластер MINI 3.0 (P10), 30 кг/ч, 2500 л/мин, MINI-II", "price_vat":203740, "price_net":167000, "min_price_net":130000, "margin_pct":0.65, "comment":"Демо-товар"},
        {"product_id":"BASIC-2.0-P10-PLa-F3500", "sku":"BASIC-2.0-P10-PLa-F3500", "name":"Криобластер BASIC 2.0 (P10/PLa), 0-60 кг/ч, 3500 л/мин", "price_vat":1169980, "price_net":959000, "min_price_net":780000, "margin_pct":0.65, "comment":"Демо-товар"},
        {"product_id":"ONE-2.0-P12-PLa-F3500", "sku":"ONE-2.0-P12-PLa-F3500", "name":"Криобластер ONE 2.0 (P12/PLa), 0-150 кг/ч, 3500 л/мин", "price_vat":1886120, "price_net":1546000, "min_price_net":1250000, "margin_pct":0.65, "comment":"Демо-товар"},
        {"product_id":"TR-2.0-MAX-P12-PLa-F3500-PRO-II", "sku":"TR-2.0-MAX-P12-PLa-F3500-PRO-II", "name":"Криобластер TRANSFORMER 2.0 MAX (P12/PLa), 0-150 кг/ч, 3500 л/мин", "price_vat":2166720, "price_net":1776000, "min_price_net":1430000, "margin_pct":0.65, "comment":"Демо-товар"},
        {"product_id":"NZ-LV-5000", "sku":"NZ-LV-5000", "name":"Сопло агрессивное NZ-LV-5000", "price_vat":92720, "price_net":76000, "min_price_net":55000, "margin_pct":0.65, "comment":"Демо-товар"},
    ]

# ============================================================
# 3. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================


def today_str():
    return date.today().isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def to_float(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        text = str(value).replace("\xa0", " ").replace("руб.", "").replace("%", "").strip()
        text = text.replace(" ", "").replace(",", ".")
        if text == "":
            return default
        return float(text)
    except Exception:
        return default


def pct_to_decimal(value, default=0.0):
    v = to_float(value, default)
    return v / 100.0 if v > 1.0 else v


def decimal_to_pct(value):
    return round(to_float(value, 0) * 100, 4)


def safe_date(text, default=None):
    default = default or today_str()
    try:
        return datetime.fromisoformat(str(text)[:10]).date().isoformat()
    except Exception:
        return default


def date_obj(text):
    try:
        return datetime.fromisoformat(str(text)[:10]).date()
    except Exception:
        return date.min


def money(v):
    return f"{to_float(v):,.2f} руб.".replace(",", " ")


def money0(v):
    return f"{to_float(v):,.0f} руб.".replace(",", " ")


def pct(v, digits=1):
    return f"{to_float(v) * 100:.{digits}f}%".replace(".", ",")


def user_name(login):
    return USERS.get(login, {}).get("name", login or "")


def is_director(user):
    return bool(user and user.get("role") == "director")


def df_from_any(data, columns):
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    elif data is None:
        df = pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(data)
    for c in columns:
        if c not in df.columns:
            df[c] = ""
    return df[columns].copy()


def clean_json(obj):
    if isinstance(obj, dict):
        return {str(k): clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_json(v) for v in obj]
    if isinstance(obj, pd.DataFrame):
        return clean_json(obj.to_dict("records"))
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    try:
        if pd.isna(obj):
            return None
    except Exception:
        pass
    return obj

# ============================================================
# 4. БАЗА ДАННЫХ И СОСТОЯНИЕ
# ============================================================

SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS app_users (
    login TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('director','manager')),
    name TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    settings JSONB NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    sku TEXT NOT NULL,
    name TEXT NOT NULL,
    price_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    price_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    min_price_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    margin_pct NUMERIC(8,6) NOT NULL DEFAULT 0.65,
    comment TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS actions (
    action_id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL,
    manager_login TEXT NOT NULL REFERENCES app_users(login),
    sequence_no INTEGER NOT NULL,
    action_date DATE NOT NULL,
    client TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '',
    task_description TEXT NOT NULL DEFAULT '',
    comment TEXT NOT NULL DEFAULT '',
    is_director_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    confirmed_amount NUMERIC(14,2),
    director_comment TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(manager_login, sequence_no)
);
CREATE TABLE IF NOT EXISTS demo_expenses (
    id BIGSERIAL PRIMARY KEY,
    action_id TEXT NOT NULL REFERENCES actions(action_id) ON DELETE CASCADE,
    row_order INTEGER NOT NULL,
    article TEXT NOT NULL,
    qty NUMERIC(14,4) NOT NULL DEFAULT 0,
    unit TEXT NOT NULL DEFAULT '',
    price_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    price_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    amount_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    calc_type TEXT NOT NULL DEFAULT 'direct',
    is_custom BOOLEAN NOT NULL DEFAULT FALSE,
    comment TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS demo_criterion_values (
    action_id TEXT NOT NULL REFERENCES actions(action_id) ON DELETE CASCADE,
    criterion_code TEXT NOT NULL,
    level_index INTEGER NOT NULL DEFAULT 0,
    manager_comment TEXT NOT NULL DEFAULT '',
    PRIMARY KEY(action_id, criterion_code)
);
CREATE TABLE IF NOT EXISTS sale_rows (
    id BIGSERIAL PRIMARY KEY,
    action_id TEXT NOT NULL REFERENCES actions(action_id) ON DELETE CASCADE,
    row_order INTEGER NOT NULL,
    product_id TEXT NOT NULL REFERENCES products(product_id),
    sku TEXT NOT NULL,
    name TEXT NOT NULL,
    price_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    price_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    qty NUMERIC(14,4) NOT NULL DEFAULT 1,
    total_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    total_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    vat_sum NUMERIC(14,2) NOT NULL DEFAULT 0,
    min_price_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    margin_unit NUMERIC(14,2) NOT NULL DEFAULT 0,
    margin_pct NUMERIC(8,6) NOT NULL DEFAULT 0.65,
    bonus_net NUMERIC(14,2) NOT NULL DEFAULT 0
);
"""


def db_connect():
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)


def ensure_schema():
    if not USE_POSTGRES:
        return False, "PostgreSQL отключен переменной DEMO_CALC_USE_POSTGRES."
    try:
        conn = db_connect()
        conn.autocommit = True
        with conn.cursor() as cur:
            for stmt in [s.strip() for s in SCHEMA_SQL.split(';') if s.strip()]:
                cur.execute(stmt)
        conn.close()
        return True, "Схема БД готова."
    except Exception as e:
        return False, f"База недоступна: {e}"


def create_demo_state():
    settings = default_settings()
    actions = []
    products = [normalize_product(p, settings) for p in default_products()]

    def mk_criteria(level=1):
        values = {}
        for cr in settings["criteria"]:
            max_idx = len(cr["levels"]) - 1
            idx = min(max_idx, level)
            values[cr["code"]] = {"level_index": idx, "manager_comment": "Демо-комментарий"}
        return values

    def product_by_sku(sku):
        return next(p for p in products if p["sku"] == sku)

    def demo_expenses(kind="default"):
        rows = []
        for i, s in enumerate(settings["expense_settings"], start=1):
            qty = s.get("qty_default") or 0
            if s["article"] == "Работа водителя" and kind == "short":
                qty = 300
            elif s["article"] == "Работа водителя" and kind == "medium":
                qty = 900
            elif s["article"] == "Работа водителя":
                qty = 1800
            rows.append({
                "article": s["article"], "qty": qty, "unit": s.get("unit", ""),
                "price_net": s.get("price_net_default") or 0, "price_vat": s.get("price_vat_default") or 0,
                "amount_vat": 0, "calc_type": s.get("calc_type", "direct"), "is_custom": False,
                "comment": s.get("comment", ""), "row_order": i,
            })
        return calc_expenses_rows(rows, settings).to_dict("records")

    clients = {
        "ruslan": ["Центр Транс Техмаш", "Полипластик", "Рязанский завод"],
        "timur": ["Полипластик", "Литейный завод", "Упаковочная фабрика"],
        "maria": ["Кондитерская фабрика", "Пищевик", "Технопласт"],
    }
    sale_skus = ["ONE-2.0-P12-PLa-F3500", "TR-2.0-MAX-P12-PLa-F3500-PRO-II", "MINI-3.0-P10-F2500", "NZ-LV-5000"]
    for mi, manager in enumerate(["ruslan", "timur", "maria"]):
        seqs = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150]
        types = [ACTION_DEMO,ACTION_SALE,ACTION_DEMO,ACTION_SALE,ACTION_SALE,ACTION_PREMIUM,ACTION_DEMO,ACTION_SALE,ACTION_DEMO,ACTION_SALE,ACTION_DEMO,ACTION_SALE,ACTION_DEMO,ACTION_SALE,ACTION_PREMIUM]
        for idx, (seq, tp) in enumerate(zip(seqs, types)):
            d = date(2026, 4, 1) + pd.Timedelta(days=idx*3 + mi)
            action = {
                "id": new_id("ACT"), "type": tp, "manager_login": manager, "sequence_no": seq,
                "date": d.date().isoformat() if hasattr(d, 'date') else d.isoformat(),
                "client": clients[manager][idx % len(clients[manager])], "city": "Казань", "model": "TRANSFORMER 2.0 MAX",
                "task_description": "Демо-задача очистки промышленного оборудования", "comment": "Демо-данные",
                "is_director_confirmed": seq <= 60,
                "confirmed_amount": None,
                "director_comment": "Подтверждено в закрытом периоде" if seq <= 60 else "",
            }
            if tp == ACTION_DEMO:
                action["expenses"] = demo_expenses("short" if manager == "maria" else ("medium" if manager == "timur" else "default"))
                action["criteria"] = mk_criteria(2 if seq <= 60 else (1 if seq in (90,130) else 2))
                calc = calculate_demo(action, settings)
                action["confirmed_amount"] = round(calc["deduction_net"], 2) if action["is_director_confirmed"] else None
            elif tp == ACTION_SALE:
                p = product_by_sku(sale_skus[(idx+mi) % len(sale_skus)])
                row = create_sale_row_from_product(p, 1 if p["sku"] != "NZ-LV-5000" else 2, settings)
                action["rows"] = [row]
                calc = calculate_sale(action, products, settings)
                action["confirmed_amount"] = round(calc["bonus_net"], 2) if action["is_director_confirmed"] else None
            else:
                action["confirmed_amount"] = 0 if action["is_director_confirmed"] else None
            actions.append(action)
    return {"settings": settings, "products": products, "actions": actions}


def load_state_from_db():
    ok, msg = ensure_schema()
    if not ok:
        if Path(JSON_BACKUP_PATH).exists():
            try:
                return json.loads(Path(JSON_BACKUP_PATH).read_text(encoding="utf-8")), msg
            except Exception:
                pass
        return create_demo_state(), msg
    try:
        conn = db_connect()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS n FROM app_users")
            if int(cur.fetchone()["n"] or 0) == 0 and AUTO_SEED_EMPTY_DATABASE:
                conn.close()
                state = create_demo_state()
                persist_state_to_db(state)
                return state, "База была пустой, загружены демо-данные."

            cur.execute("SELECT settings FROM app_settings WHERE id=1")
            row = cur.fetchone()
            settings = row["settings"] if row else default_settings()
            if isinstance(settings, str):
                settings = json.loads(settings)
            settings = merge_settings(settings)

            cur.execute("SELECT * FROM products ORDER BY sku")
            products = [dict(r) for r in cur.fetchall()]
            products = [normalize_product(p, settings) for p in products]

            cur.execute("SELECT * FROM actions ORDER BY manager_login, sequence_no")
            action_rows = [dict(r) for r in cur.fetchall()]
            actions = []
            for a in action_rows:
                action = {
                    "id": a["action_id"], "type": a["action_type"], "manager_login": a["manager_login"],
                    "sequence_no": a["sequence_no"], "date": str(a["action_date"]), "client": a.get("client") or "",
                    "city": a.get("city") or "", "model": a.get("model") or "", "task_description": a.get("task_description") or "",
                    "comment": a.get("comment") or "", "is_director_confirmed": bool(a.get("is_director_confirmed")),
                    "confirmed_amount": float(a["confirmed_amount"]) if a.get("confirmed_amount") is not None else None,
                    "director_comment": a.get("director_comment") or "",
                }
                if action["type"] == ACTION_DEMO:
                    cur.execute("SELECT * FROM demo_expenses WHERE action_id=%s ORDER BY row_order", (action["id"],))
                    action["expenses"] = [dict(r) for r in cur.fetchall()]
                    cur.execute("SELECT * FROM demo_criterion_values WHERE action_id=%s", (action["id"],))
                    action["criteria"] = {r["criterion_code"]: {"level_index": int(r["level_index"]), "manager_comment": r.get("manager_comment") or ""} for r in cur.fetchall()}
                elif action["type"] == ACTION_SALE:
                    cur.execute("SELECT * FROM sale_rows WHERE action_id=%s ORDER BY row_order", (action["id"],))
                    action["rows"] = [dict(r) for r in cur.fetchall()]
                actions.append(action)
        conn.close()
        return {"settings": settings, "products": products, "actions": actions}, "Данные загружены из PostgreSQL."
    except Exception as e:
        if Path(JSON_BACKUP_PATH).exists():
            try:
                return json.loads(Path(JSON_BACKUP_PATH).read_text(encoding="utf-8")), f"Ошибка БД, загружена резервная копия: {e}"
            except Exception:
                pass
        return create_demo_state(), f"Ошибка БД, загружены демо-данные: {e}"


def persist_state_to_db(state):
    Path(JSON_BACKUP_PATH).write_text(json.dumps(clean_json(state), ensure_ascii=False, indent=2), encoding="utf-8")
    if not USE_POSTGRES:
        return "Данные сохранены в JSON-резерве, PostgreSQL отключен."
    ok, msg = ensure_schema()
    if not ok:
        return f"PostgreSQL недоступен. Сохранена JSON-копия: {msg}"
    conn = db_connect()
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("TRUNCATE demo_criterion_values, demo_expenses, sale_rows, actions, products, app_settings, app_users RESTART IDENTITY CASCADE")
            execute_values(cur, "INSERT INTO app_users(login,password,role,name,is_active) VALUES %s", [(u["login"], u["password"], u["role"], u["name"], True) for u in USERS.values()])
            cur.execute("INSERT INTO app_settings(id, settings) VALUES (1, %s)", (Json(clean_json(state.get("settings", default_settings()))),))
            products = [normalize_product(p, state.get("settings", default_settings())) for p in state.get("products", [])]
            execute_values(cur, """INSERT INTO products(product_id, sku, name, price_vat, price_net, min_price_net, margin_pct, comment) VALUES %s""", [
                (p["product_id"], p["sku"], p["name"], p["price_vat"], p["price_net"], p["min_price_net"], p["margin_pct"], p.get("comment", "")) for p in products
            ])
            for a in state.get("actions", []):
                cur.execute("""INSERT INTO actions(action_id, action_type, manager_login, sequence_no, action_date, client, city, model, task_description, comment, is_director_confirmed, confirmed_amount, director_comment)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (a["id"], a["type"], a["manager_login"], int(a.get("sequence_no",0)), safe_date(a.get("date")), a.get("client",""), a.get("city",""), a.get("model",""), a.get("task_description",""), a.get("comment",""), bool(a.get("is_director_confirmed")), a.get("confirmed_amount"), a.get("director_comment","")))
                if a["type"] == ACTION_DEMO:
                    ex_rows = []
                    for i, r in enumerate(a.get("expenses", []), start=1):
                        ex_rows.append((a["id"], i, r.get("article") or r.get("Статья расхода") or "", to_float(r.get("qty", r.get("Кол-во"))), r.get("unit", r.get("Ед.изм.", "")), to_float(r.get("price_net", r.get("Цена, руб. без НДС"))), to_float(r.get("price_vat", r.get("Цена, руб. с НДС"))), to_float(r.get("amount_vat", r.get("Сумма затрат, руб. с НДС"))), r.get("calc_type", "direct"), bool(r.get("is_custom", False)), r.get("comment", r.get("Комментарий", ""))))
                    if ex_rows:
                        execute_values(cur, """INSERT INTO demo_expenses(action_id,row_order,article,qty,unit,price_net,price_vat,amount_vat,calc_type,is_custom,comment) VALUES %s""", ex_rows)
                    cv_rows = []
                    for code, cv in (a.get("criteria") or {}).items():
                        cv_rows.append((a["id"], code, int(cv.get("level_index", 0)), cv.get("manager_comment", "")))
                    if cv_rows:
                        execute_values(cur, "INSERT INTO demo_criterion_values(action_id, criterion_code, level_index, manager_comment) VALUES %s", cv_rows)
                elif a["type"] == ACTION_SALE:
                    sale_rows = []
                    for i, r in enumerate(a.get("rows", []), start=1):
                        sale_rows.append((a["id"], i, r.get("product_id", r.get("ID товара", "")), r.get("sku", r.get("Артикул", "")), r.get("name", r.get("Наименование оборудования", "")), to_float(r.get("price_vat", r.get("Цена руб. с НДС"))), to_float(r.get("price_net", r.get("Цена руб. без НДС"))), to_float(r.get("qty", r.get("Кол-во")),1), to_float(r.get("total_vat", r.get("ИТОГО с НДС"))), to_float(r.get("total_net", r.get("ИТОГО без НДС"))), to_float(r.get("vat_sum", r.get("Сумма НДС"))), to_float(r.get("min_price_net", r.get("Минимальная цена продажи без НДС"))), to_float(r.get("margin_unit", r.get("Маржа факт на единицу"))), pct_to_decimal(r.get("margin_pct", r.get("% от маржи факт")),0.65), to_float(r.get("bonus_net", r.get("Премия NET")))))
                    if sale_rows:
                        execute_values(cur, """INSERT INTO sale_rows(action_id,row_order,product_id,sku,name,price_vat,price_net,qty,total_vat,total_net,vat_sum,min_price_net,margin_unit,margin_pct,bonus_net) VALUES %s""", sale_rows)
        conn.commit()
        conn.close()
        return "Данные сохранены в PostgreSQL."
    except Exception as e:
        conn.rollback()
        conn.close()
        return f"Ошибка сохранения в PostgreSQL. JSON-копия сохранена. Ошибка: {e}"


def merge_settings(s):
    base = default_settings()
    if not isinstance(s, dict):
        return base
    for k, v in s.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k].update(v)
        else:
            base[k] = v
    if "criteria" not in base or not base["criteria"]:
        base["criteria"] = DEFAULT_CRITERIA
    if "expense_settings" not in base or not base["expense_settings"]:
        base["expense_settings"] = DEFAULT_EXPENSE_SETTINGS
    base["font_family"] = "Arial"
    return base

# ============================================================
# 5. ПРОДУКТЫ, СМЕТА, ПРОДАЖИ, ДЕМО, ПРЕМИИ
# ============================================================


def normalize_product(p, settings=None):
    settings = settings or default_settings()
    vat = to_float(settings.get("vat_rate"), 0.22)
    product_id = str(p.get("product_id") or p.get("ID товара") or p.get("sku") or p.get("Артикул") or new_id("PRD"))
    sku = str(p.get("sku") or p.get("Артикул") or product_id)
    name = str(p.get("name") or p.get("Наименование ТМЦ") or p.get("Наименование оборудования") or "")
    price_vat = to_float(p.get("price_vat", p.get("Цена руб. с НДС")), 0)
    price_net = to_float(p.get("price_net", p.get("Цена руб. без НДС (A)", p.get("Цена руб. без НДС"))), 0)
    if price_net <= 0 and price_vat > 0:
        price_net = price_vat / (1+vat)
    if price_vat <= 0 and price_net > 0:
        price_vat = price_net * (1+vat)
    min_price_net = to_float(p.get("min_price_net", p.get("Минимальная цена продажи без НДС (B)", p.get("Минимальная цена продажи без НДС"))), 0)
    margin_pct = pct_to_decimal(p.get("margin_pct", p.get("% от маржи (D)", p.get("% от маржи факт"))), 0.65)
    margin = price_net - min_price_net
    bonus = margin * margin_pct
    return {"product_id": product_id, "sku": sku, "name": name, "price_vat": round(price_vat,2), "price_net": round(price_net,2), "min_price_net": round(min_price_net,2), "margin_pct": round(margin_pct,6), "margin": round(margin,2), "bonus_net": round(bonus,2), "comment": str(p.get("comment", p.get("Комментарий", "")))}


def products_to_df(products, settings=None):
    rows = []
    for p in products or []:
        n = normalize_product(p, settings)
        rows.append({
            "ID товара": n["product_id"], "Артикул": n["sku"], "Наименование ТМЦ": n["name"],
            "Цена руб. с НДС": n["price_vat"], "Цена руб. без НДС (A)": n["price_net"],
            "Минимальная цена продажи без НДС (B)": n["min_price_net"], "Маржа, руб. без НДС (C)": n["margin"],
            "% от маржи (D)": n["margin_pct"], "Премия NET (P)": n["bonus_net"], "Комментарий": n["comment"],
        })
    return pd.DataFrame(rows, columns=PRODUCT_COLUMNS)


def products_from_df(df, settings=None):
    df = df_from_any(df, PRODUCT_COLUMNS)
    products = []
    for _, r in df.iterrows():
        if not str(r.get("Наименование ТМЦ", "")).strip() and not str(r.get("Артикул", "")).strip():
            continue
        products.append(normalize_product(r.to_dict(), settings))
    return products


def product_lookup(products):
    d = {}
    for p in products or []:
        n = normalize_product(p)
        for k in [n["product_id"], n["sku"], n["name"]]:
            if k:
                d[str(k).strip().lower()] = n
    return d


def search_products(query, products):
    query = str(query or "").strip().lower()
    if len(query) < 3:
        return []
    out = []
    for p in products or []:
        n = normalize_product(p)
        hay = f"{n['product_id']} {n['sku']} {n['name']}".lower()
        if query in hay:
            out.append(f"{n['sku']} — {n['name']} | ID:{n['product_id']}")
    return out[:20]


def product_id_from_choice(choice):
    text = str(choice or "")
    return text.split("ID:")[-1].strip() if "ID:" in text else ""


def create_sale_row_from_product(product, qty=1, settings=None):
    p = normalize_product(product, settings)
    qty = max(0.0, to_float(qty, 1))
    total_vat = p["price_vat"] * qty
    total_net = p["price_net"] * qty
    margin_unit = p["price_net"] - p["min_price_net"]
    return {
        "product_id": p["product_id"], "sku": p["sku"], "name": p["name"], "price_vat": p["price_vat"],
        "price_net": p["price_net"], "qty": qty, "total_vat": round(total_vat,2), "total_net": round(total_net,2),
        "vat_sum": round(total_vat-total_net,2), "min_price_net": p["min_price_net"], "margin_unit": round(margin_unit,2),
        "margin_pct": p["margin_pct"], "bonus_net": round(margin_unit * p["margin_pct"] * qty, 2),
    }


def sale_rows_to_df(rows, products, settings):
    lookup = product_lookup(products)
    out = []
    for r in rows or []:
        rid = str(r.get("product_id", r.get("ID товара", ""))).strip()
        sku = str(r.get("sku", r.get("Артикул", ""))).strip()
        found = None
        for key in [rid, sku]:
            if key.lower() in lookup:
                found = lookup[key.lower()]
                break
        if not found:
            continue
        qty = to_float(r.get("qty", r.get("Кол-во", 1)), 1)
        price_vat = to_float(r.get("price_vat", r.get("Цена руб. с НДС")), found["price_vat"])
        price_net = to_float(r.get("price_net", r.get("Цена руб. без НДС")), found["price_net"])
        # locked fields: name, minimum price, bonus percent always from product catalog
        row = create_sale_row_from_product({**found, "price_vat": price_vat, "price_net": price_net}, qty, settings)
        out.append({
            "ID товара": row["product_id"], "Артикул": row["sku"], "Наименование оборудования": row["name"],
            "Цена руб. с НДС": row["price_vat"], "Цена руб. без НДС": row["price_net"], "Кол-во": row["qty"],
            "ИТОГО с НДС": row["total_vat"], "ИТОГО без НДС": row["total_net"], "Сумма НДС": row["vat_sum"],
            "Минимальная цена продажи без НДС": row["min_price_net"], "Маржа факт на единицу": row["margin_unit"],
            "% от маржи факт": row["margin_pct"], "Премия NET": row["bonus_net"],
        })
    return pd.DataFrame(out, columns=SALE_COLUMNS)


def sale_rows_from_df(df, products, settings):
    df = df_from_any(df, SALE_COLUMNS)
    rows = []
    for _, r in sale_rows_to_df(df.to_dict("records"), products, settings).iterrows():
        rows.append({
            "product_id": r["ID товара"], "sku": r["Артикул"], "name": r["Наименование оборудования"],
            "price_vat": to_float(r["Цена руб. с НДС"]), "price_net": to_float(r["Цена руб. без НДС"]),
            "qty": to_float(r["Кол-во"], 1), "total_vat": to_float(r["ИТОГО с НДС"]), "total_net": to_float(r["ИТОГО без НДС"]),
            "vat_sum": to_float(r["Сумма НДС"]), "min_price_net": to_float(r["Минимальная цена продажи без НДС"]),
            "margin_unit": to_float(r["Маржа факт на единицу"]), "margin_pct": pct_to_decimal(r["% от маржи факт"], 0.65),
            "bonus_net": to_float(r["Премия NET"]),
        })
    return rows


def calculate_sale(action, products, settings):
    df = sale_rows_to_df(action.get("rows", []), products, settings)
    bonus = df["Премия NET"].apply(to_float).sum() if not df.empty else 0.0
    return {"rows_df": df, "bonus_net": float(bonus), "total_vat": float(df["ИТОГО с НДС"].apply(to_float).sum()) if not df.empty else 0.0}


def expense_settings_map(settings):
    return {s["article"]: s for s in settings.get("expense_settings", DEFAULT_EXPENSE_SETTINGS)}


def default_expense_rows(settings):
    rows = []
    for i, s in enumerate(settings.get("expense_settings", DEFAULT_EXPENSE_SETTINGS), start=1):
        rows.append({
            "article": s["article"], "qty": s.get("qty_default") or 0, "unit": s.get("unit", ""),
            "price_net": s.get("price_net_default") or 0, "price_vat": s.get("price_vat_default") or 0,
            "amount_vat": 0, "calc_type": s.get("calc_type", "direct"), "is_custom": False, "comment": s.get("comment", ""), "row_order": i,
        })
    return calc_expenses_rows(rows, settings).to_dict("records")


def calc_expenses_rows(rows, settings):
    vat = to_float(settings.get("vat_rate"), 0.22)
    smap = expense_settings_map(settings)
    # first pass normalize and preserve custom rows
    norm = []
    for i, r in enumerate(rows or [], start=1):
        article = str(r.get("article", r.get("Статья расхода", ""))).strip()
        if not article:
            continue
        s = smap.get(article)
        is_custom = bool(r.get("is_custom", False)) or s is None
        calc_type = (s or {}).get("calc_type", r.get("calc_type", "direct"))
        qty_manager = bool((s or {}).get("qty_manager", True))
        price_manager = bool((s or {}).get("price_manager", True))
        qty = to_float(r.get("qty", r.get("Кол-во")), (s or {}).get("qty_default", 0))
        unit = str(r.get("unit", r.get("Ед.изм.", (s or {}).get("unit", ""))))
        price_net = to_float(r.get("price_net", r.get("Цена, руб. без НДС")), (s or {}).get("price_net_default", 0) or 0)
        price_vat = to_float(r.get("price_vat", r.get("Цена, руб. с НДС")), (s or {}).get("price_vat_default", 0) or 0)
        if s and not qty_manager:
            qty = to_float((s or {}).get("qty_default"), qty)
        if s and not price_manager:
            price_net = to_float((s or {}).get("price_net_default"), price_net)
            price_vat = to_float((s or {}).get("price_vat_default"), price_vat)
        norm.append({"article": article, "qty": qty, "unit": unit, "price_net": price_net, "price_vat": price_vat, "amount_vat": 0, "calc_type": calc_type, "is_custom": is_custom, "comment": str(r.get("comment", r.get("Комментарий", "")) or "")})

    km = next((x["qty"] for x in norm if x["article"] == "Работа водителя"), 0)
    # compute direct rows before payroll tax
    amount_by_article = {}
    for x in norm:
        ct = x["calc_type"]
        if ct == "diesel":
            x["qty"] = km / 100.0 * to_float(settings.get("diesel_l_per_100km"), 12)
            if x["price_vat"] <= 0:
                x["price_vat"] = 78
            x["price_net"] = x["price_vat"] / (1+vat)
            x["amount_vat"] = x["qty"] * x["price_vat"]
        elif ct == "gazelle_amort":
            x["qty"] = km
            if x["price_vat"] <= 0:
                x["price_vat"] = 10
            x["price_net"] = x["price_vat"] / (1+vat)
            x["amount_vat"] = x["qty"] * x["price_vat"]
        elif ct == "payroll_tax":
            x["amount_vat"] = 0
        elif ct == "direct_vat_price":
            if x["price_vat"] <= 0 and x["price_net"] > 0:
                x["price_vat"] = x["price_net"] * (1+vat)
            if x["price_net"] <= 0 and x["price_vat"] > 0:
                x["price_net"] = x["price_vat"] / (1+vat)
            x["amount_vat"] = x["qty"] * x["price_vat"]
        else:
            if x["price_net"] <= 0 and x["price_vat"] > 0:
                x["price_net"] = x["price_vat"] / (1+vat)
            if x["price_vat"] <= 0 and x["price_net"] > 0:
                x["price_vat"] = x["price_net"] * (1+vat)
            x["amount_vat"] = x["qty"] * x["price_vat"]
        amount_by_article[x["article"]] = x["amount_vat"]

    payroll_base_articles = ["Работа водителя", "Работа демонстратора", "Демонстрация криобластера", "Усложненные условия труда", "Ручная работа с кабелем и шланга компрессора", "Использование электрокатушки", "Выгрузка и загрузка компрессора и электрокатушки"]
    payroll_base = sum(amount_by_article.get(a, 0) for a in payroll_base_articles)
    for x in norm:
        if x["calc_type"] == "payroll_tax":
            x["amount_vat"] = payroll_base * to_float(settings.get("payroll_tax_rate"), 0.30)

    # Add company support as a calculation row. It is not editable by manager.
    support = -abs(to_float(settings.get("company_support_vat"), 0))
    norm.append({"article": "Общая фора (помощь от ООО)", "qty": 1, "unit": "усл", "price_net": support/(1+vat), "price_vat": support, "amount_vat": support, "calc_type": "company_support", "is_custom": False, "comment": "Настройка директора"})

    rows_out = []
    for x in norm:
        rows_out.append({
            "Статья расхода": x["article"], "Кол-во": round(x["qty"], 4), "Ед.изм.": x["unit"],
            "Цена, руб. без НДС": round(x["price_net"], 2), "Цена, руб. с НДС": round(x["price_vat"], 2),
            "Сумма затрат, руб. с НДС": round(x["amount_vat"], 2), "Комментарий": x["comment"],
        })
    return pd.DataFrame(rows_out, columns=EXPENSE_COLUMNS)


def expenses_from_df(df, settings):
    df = df_from_any(df, EXPENSE_COLUMNS)
    rows = []
    for i, r in df.iterrows():
        article = str(r.get("Статья расхода", "")).strip()
        if not article or article == "ИТОГО расходы на демонстрацию" or article == "Общая фора (помощь от ООО)":
            continue
        s = expense_settings_map(settings).get(article)
        rows.append({
            "article": article, "qty": to_float(r.get("Кол-во")), "unit": str(r.get("Ед.изм.", "")),
            "price_net": to_float(r.get("Цена, руб. без НДС")), "price_vat": to_float(r.get("Цена, руб. с НДС")),
            "amount_vat": to_float(r.get("Сумма затрат, руб. с НДС")), "calc_type": (s or {}).get("calc_type", "direct"),
            "is_custom": s is None, "comment": str(r.get("Комментарий", "")), "row_order": i+1,
        })
    # reapply formulas and locked settings
    calc_df = calc_expenses_rows(rows, settings)
    out = []
    for i, r in calc_df.iterrows():
        article = str(r.get("Статья расхода", ""))
        if article == "Общая фора (помощь от ООО)":
            continue
        s = expense_settings_map(settings).get(article)
        out.append({
            "article": article, "qty": to_float(r.get("Кол-во")), "unit": str(r.get("Ед.изм.", "")),
            "price_net": to_float(r.get("Цена, руб. без НДС")), "price_vat": to_float(r.get("Цена, руб. с НДС")),
            "amount_vat": to_float(r.get("Сумма затрат, руб. с НДС")), "calc_type": (s or {}).get("calc_type", "direct"),
            "is_custom": s is None, "comment": str(r.get("Комментарий", "")), "row_order": i+1,
        })
    return out


def criterion_label(cr, idx):
    levels = cr.get("levels", [])
    if not levels:
        return ""
    idx = max(0, min(int(idx or 0), len(levels)-1))
    name, score = levels[idx]
    return f"{name}\n[{score} балл.]"


def criteria_choice_labels(cr):
    return [f"{name}\n[{score} балл.]" for name, score in cr.get("levels", [])]


def label_to_level_index(cr, label):
    labels = criteria_choice_labels(cr)
    try:
        return labels.index(label)
    except Exception:
        return 0


def calculate_demo(action, settings):
    vat = to_float(settings.get("vat_rate"), 0.22)
    bonus_rate = to_float(settings.get("bonus_rate"), 0.65)
    expenses_df_full = calc_expenses_rows(action.get("expenses", []), settings)
    support_mask = expenses_df_full["Статья расхода"].astype(str) == COMPANY_SUPPORT_ARTICLE if not expenses_df_full.empty else pd.Series(dtype=bool)
    expenses_df = expenses_df_full.loc[~support_mask].reset_index(drop=True) if not expenses_df_full.empty else pd.DataFrame([], columns=EXPENSE_COLUMNS)
    total_vat = float(expenses_df["Сумма затрат, руб. с НДС"].apply(to_float).sum()) if not expenses_df.empty else 0.0
    support_vat = abs(float(expenses_df_full.loc[support_mask, "Сумма затрат, руб. с НДС"].apply(to_float).sum())) if not expenses_df_full.empty else 0.0
    cost_net = max(0.0, total_vat / (1+vat))
    support_net = max(0.0, support_vat / (1+vat))
    cost_net_after_support = max(0.0, cost_net - support_net)
    criteria = action.get("criteria", {}) or {}
    block_scores = {"P": 0.0, "R": 0.0, "M": 0.0}
    block_max = {"P": 100.0, "R": 100.0, "M": 100.0}
    score_by_code = {}
    for cr in settings.get("criteria", DEFAULT_CRITERIA):
        idx = int(criteria.get(cr["code"], {}).get("level_index", 0))
        idx = max(0, min(idx, len(cr.get("levels", []))-1))
        score = to_float(cr["levels"][idx][1], 0)
        block_scores[cr["block"]] += score
        score_by_code[cr["code"]] = score
    P, R, M = block_scores["P"], block_scores["R"], block_scores["M"]
    QI = to_float(settings.get("p_weight"),0.45)*(P/100) + to_float(settings.get("r_weight"),0.35)*(R/100) + to_float(settings.get("m_weight"),0.20)*(M/100)
    K_raw = 1 - to_float(settings.get("k_reduction_factor"),0.80)*QI
    soft = (score_by_code.get("P2",0) == 0) or (score_by_code.get("P4",0) == 0) or (score_by_code.get("P5",0) == 0)
    hard = (score_by_code.get("P8",0) == 0) or (score_by_code.get("M7",0) == 0)
    if hard:
        K = 1.0
    elif soft:
        K = max(K_raw, to_float(settings.get("min_soft_stop_k"),0.80))
    else:
        K = max(K_raw, to_float(settings.get("min_normal_k"),0.20))
    K = min(1.0, max(0.0, K))
    expense_for_bonus = cost_net_after_support * K
    deduction_net = expense_for_bonus * bonus_rate
    return {
        "expenses_df": expenses_df,
        "total_vat": total_vat,
        "cost_net": cost_net,
        "support_vat": support_vat,
        "support_net": support_net,
        "cost_net_after_support": cost_net_after_support,
        "P": P,
        "R": R,
        "M": M,
        "QI": QI,
        "K_raw": K_raw,
        "K": K,
        "soft_stop": soft,
        "hard_stop": hard,
        "expense_for_bonus": expense_for_bonus,
        "deduction_net": deduction_net,
    }


def last_confirmed_premium_seq(manager_login, state, before_seq=None):
    seqs = []
    for a in state.get("actions", []):
        if a.get("manager_login") == manager_login and a.get("type") == ACTION_PREMIUM and a.get("is_director_confirmed"):
            if before_seq is None or int(a.get("sequence_no",0)) < before_seq:
                seqs.append(int(a.get("sequence_no",0)))
    return max(seqs) if seqs else None


def is_action_locked(action, state):
    m = action.get("manager_login")
    seq = int(action.get("sequence_no", 0))
    for p in state.get("actions", []):
        if p.get("manager_login") == m and p.get("type") == ACTION_PREMIUM and p.get("is_director_confirmed") and int(p.get("sequence_no",0)) >= seq:
            return True
    return False


def period_actions_for_premium(action, state):
    m = action.get("manager_login")
    seq = int(action.get("sequence_no", 0))
    prev = last_confirmed_premium_seq(m, state, before_seq=seq)
    start = prev if prev is not None else -10**9
    return [a for a in state.get("actions", []) if a.get("manager_login") == m and int(a.get("sequence_no",0)) > start and int(a.get("sequence_no",0)) <= seq]


def can_confirm_premium(action, state):
    if action.get("type") != ACTION_PREMIUM:
        return True, ""
    period = period_actions_for_premium(action, state)
    sales = [a for a in period if a.get("type") == ACTION_SALE]
    if not sales:
        return False, "Нельзя подтвердить премию: нет продаж с момента предыдущей подтвержденной премии."
    unconfirmed_demos = [a for a in period if a.get("type") == ACTION_DEMO and not a.get("is_director_confirmed")]
    if unconfirmed_demos:
        return False, "Расчет премии невозможен: в периоде есть демонстрации без подтверждения директора."
    bad_sales = [a for a in sales if not a.get("rows")]
    if bad_sales:
        return False, "Нельзя подтвердить премию: у одной или нескольких продаж нет товаров."
    return True, ""


def calculate_premium(action, state, settings):
    period = period_actions_for_premium(action, state)
    ok, warning = can_confirm_premium(action, state)
    sales = [a for a in period if a.get("type") == ACTION_SALE]
    demos = [a for a in period if a.get("type") == ACTION_DEMO]
    sales_sum = 0.0
    demo_sum = 0.0
    sale_rows = []
    demo_rows = []
    for s in sales:
        calc = calculate_sale(s, state.get("products", []), settings)
        amount = to_float(s.get("confirmed_amount"), calc["bonus_net"])
        sales_sum += amount
        sale_rows.append({"Дата": s.get("date"), "Клиент": s.get("client"), "Премия расчетная": round(calc["bonus_net"],2), "Подтверждено директором": amount})
    for d in demos:
        calc = calculate_demo(d, settings)
        amount = to_float(d.get("confirmed_amount"), calc["deduction_net"] if d.get("is_director_confirmed") else 0)
        demo_sum += amount
        demo_rows.append({"Дата": d.get("date"), "Клиент": d.get("client"), "Вычет расчетный": round(calc["deduction_net"],2), "Подтверждено директором": amount, "Демо подтверждено": bool(d.get("is_director_confirmed"))})
    max_deduction = sales_sum * to_float(settings.get("max_demo_deduction_pct"),1.0)
    actual_demo = min(demo_sum, max_deduction)
    payout = max(0.0, sales_sum - actual_demo)
    return {"ok": ok, "warning": warning, "sales_sum": sales_sum, "demo_sum": demo_sum, "actual_demo": actual_demo, "payout": payout, "sale_rows_df": pd.DataFrame(sale_rows), "demo_rows_df": pd.DataFrame(demo_rows), "period_from_seq": min([int(a.get("sequence_no",0)) for a in period], default=0), "period_to_seq": int(action.get("sequence_no",0))}

# ============================================================
# 6. STATE OPERATIONS
# ============================================================

APP_STATE, INIT_STATUS = load_state_from_db()


def find_action(action_id):
    for a in APP_STATE.get("actions", []):
        if a.get("id") == action_id:
            return a
    return None


def authenticate(login, password):
    login = str(login or "").strip().lower()
    u = USERS.get(login)
    if u and str(password or "") == str(u["password"]):
        return {k:v for k,v in u.items() if k != "password"}
    return None


def visible_actions(user, manager_filter="__all__"):
    if not user:
        return []
    actions = APP_STATE.get("actions", [])
    if is_director(user):
        if manager_filter and manager_filter != "__all__":
            actions = [a for a in actions if a.get("manager_login") == manager_filter]
    else:
        actions = [a for a in actions if a.get("manager_login") == user.get("login")]
    return sorted(actions, key=lambda a: (a.get("manager_login",""), int(a.get("sequence_no",0))))


def action_card_text(a):
    locked = is_action_locked(a, APP_STATE)
    icon = "🔒" if locked else ("✅" if a.get("is_director_confirmed") else "□")
    typ = SHORT_TYPE.get(a.get("type"), a.get("type"))
    try:
        if a.get("type") == ACTION_DEMO:
            calc = calculate_demo(a, APP_STATE["settings"])
            amt = to_float(a.get("confirmed_amount"), calc["deduction_net"])
        elif a.get("type") == ACTION_SALE:
            calc = calculate_sale(a, APP_STATE["products"], APP_STATE["settings"])
            amt = to_float(a.get("confirmed_amount"), calc["bonus_net"])
        else:
            calc = calculate_premium(a, APP_STATE, APP_STATE["settings"])
            amt = to_float(a.get("confirmed_amount"), calc["payout"])
    except Exception:
        amt = 0
    return f"{icon} {int(a.get('sequence_no',0)):03d} · {typ} · {a.get('date','')} · {user_name(a.get('manager_login'))}\n{a.get('client','')} · {money0(amt)} · ID:{a.get('id')}"


def action_choices(user, manager_filter="__all__"):
    return [action_card_text(a) for a in visible_actions(user, manager_filter)]


def action_id_from_choice(choice):
    text = str(choice or "")
    return text.split("ID:")[-1].strip() if "ID:" in text else ""


def next_sequence(manager_login):
    seqs = [int(a.get("sequence_no",0)) for a in APP_STATE.get("actions", []) if a.get("manager_login") == manager_login]
    return (max(seqs) if seqs else 0) + 10


def add_action(action_type, user, manager_login=None):
    if not user:
        return None, "Сначала выполните вход."
    manager_login = manager_login if is_director(user) else user.get("login")
    if manager_login not in MANAGER_LOGINS:
        return None, "Менеджер не выбран."
    if action_type == ACTION_PREMIUM:
        last_seq = last_confirmed_premium_seq(manager_login, APP_STATE) or -10**9
        sales = [a for a in APP_STATE.get("actions", []) if a.get("manager_login") == manager_login and a.get("type") == ACTION_SALE and int(a.get("sequence_no",0)) > last_seq]
        if not sales:
            return None, "Нельзя создать выплату премии: нет продаж с момента предыдущей подтвержденной премии."
    a = {"id": new_id("ACT"), "type": action_type, "manager_login": manager_login, "sequence_no": next_sequence(manager_login), "date": today_str(), "client": "Новый клиент", "city": "", "model": "", "task_description": "", "comment": "", "is_director_confirmed": False, "confirmed_amount": None, "director_comment": ""}
    if action_type == ACTION_DEMO:
        a["expenses"] = default_expense_rows(APP_STATE["settings"])
        a["criteria"] = {cr["code"]: {"level_index": 0, "manager_comment": ""} for cr in APP_STATE["settings"].get("criteria", DEFAULT_CRITERIA)}
    elif action_type == ACTION_SALE:
        a["rows"] = []
    APP_STATE["actions"].append(a)
    msg = persist_state_to_db(APP_STATE)
    return a, f"Добавлено действие. {msg}"


def delete_action(action_id, user):
    a = find_action(action_id)
    if not a:
        return "Действие не найдено."
    if not is_director(user):
        return "Удалять действия может только директор."
    if is_action_locked(a, APP_STATE):
        return "Действие заблокировано подтвержденной премией. Сначала снимите подтверждение закрывающей премии."
    APP_STATE["actions"] = [x for x in APP_STATE["actions"] if x.get("id") != action_id]
    return persist_state_to_db(APP_STATE)


def move_action(action_id, user, direction):
    a = find_action(action_id)
    if not a:
        return "Действие не найдено."
    if not (is_director(user) or a.get("manager_login") == user.get("login")):
        return "Нет прав на перемещение."
    if is_action_locked(a, APP_STATE):
        return "Заблокированное действие нельзя перемещать."
    m = a.get("manager_login")
    open_actions = [x for x in APP_STATE.get("actions", []) if x.get("manager_login") == m and not is_action_locked(x, APP_STATE)]
    open_actions = sorted(open_actions, key=lambda x: int(x.get("sequence_no",0)))
    ids = [x["id"] for x in open_actions]
    if action_id not in ids:
        return "Действие не входит в открытый период."
    i = ids.index(action_id)
    j = i-1 if direction == "up" else i+1
    if j < 0 or j >= len(open_actions):
        return "Дальше переместить нельзя."
    a["sequence_no"], open_actions[j]["sequence_no"] = open_actions[j]["sequence_no"], a["sequence_no"]
    return persist_state_to_db(APP_STATE)

# ============================================================
# 7. UI DATA CONVERSION
# ============================================================


def expense_settings_to_df(settings):
    rows = []
    for s in settings.get("expense_settings", DEFAULT_EXPENSE_SETTINGS):
        rows.append({
            "Статья расхода": s.get("article"), "Ед.изм.": s.get("unit"), "Кол-во по умолчанию": s.get("qty_default"),
            "Цена без НДС по умолчанию": s.get("price_net_default"), "Цена с НДС по умолчанию": s.get("price_vat_default"),
            "Кол-во редактирует менеджер": bool(s.get("qty_manager")), "Цену редактирует менеджер": bool(s.get("price_manager")),
            "Тип расчета": s.get("calc_type"), "Комментарий": s.get("comment", ""),
        })
    return pd.DataFrame(rows, columns=EXPENSE_SETTINGS_COLUMNS)


def expense_settings_from_df(df):
    df = df_from_any(df, EXPENSE_SETTINGS_COLUMNS)
    out = []
    for _, r in df.iterrows():
        article = str(r.get("Статья расхода", "")).strip()
        if not article:
            continue
        out.append({
            "article": article, "unit": str(r.get("Ед.изм.", "")), "qty_default": to_float(r.get("Кол-во по умолчанию"),0),
            "price_net_default": to_float(r.get("Цена без НДС по умолчанию"),0), "price_vat_default": to_float(r.get("Цена с НДС по умолчанию"),0),
            "qty_manager": bool(r.get("Кол-во редактирует менеджер")), "price_manager": bool(r.get("Цену редактирует менеджер")),
            "calc_type": str(r.get("Тип расчета", "direct")), "comment": str(r.get("Комментарий", "")),
        })
    return out or DEFAULT_EXPENSE_SETTINGS


def criteria_to_df(settings):
    rows = []
    for cr in settings.get("criteria", DEFAULT_CRITERIA):
        rows.append({"Блок": cr["block"], "Код": cr["code"], "Критерий": cr["title"], "Описание": cr["desc"], "Уровни JSON": json.dumps(cr["levels"], ensure_ascii=False)})
    return pd.DataFrame(rows, columns=CRITERIA_SETTINGS_COLUMNS)


def criteria_from_df(df):
    df = df_from_any(df, CRITERIA_SETTINGS_COLUMNS)
    out = []
    for _, r in df.iterrows():
        try:
            levels = json.loads(str(r.get("Уровни JSON", "[]")))
        except Exception:
            levels = []
        if str(r.get("Код", "")).strip() and levels:
            out.append({"block": str(r.get("Блок", "")), "code": str(r.get("Код", "")), "title": str(r.get("Критерий", "")), "desc": str(r.get("Описание", "")), "levels": levels})
    return out or DEFAULT_CRITERIA


def ui_settings_to_df(settings):
    ui = settings.get("ui", {})
    rows = [
        ["action_list_width_pct", ui.get("action_list_width_pct",30), "Ширина левой зоны списка действий, %"],
        ["font_base_px", ui.get("font_base_px",13), "Базовый размер шрифта"],
        ["font_title_px", ui.get("font_title_px",18), "Размер заголовков"],
        ["card_padding_px", ui.get("card_padding_px",10), "Внутренние отступы карточек"],
        ["field_gap_px", ui.get("field_gap_px",8), "Расстояние между полями"],
        ["table_row_height_px", ui.get("table_row_height_px",30), "Высота строк таблиц"],
        ["criteria_name_width_pct", ui.get("criteria_name_width_pct",20), "Доля колонки критерия и описания, условные части"],
        ["criteria_levels_width_pct", ui.get("criteria_levels_width_pct",60), "Доля колонки уровней критерия, условные части"],
        ["criteria_comment_width_pct", ui.get("criteria_comment_width_pct",20), "Доля колонки комментария, условные части"],
    ]
    return pd.DataFrame(rows, columns=UI_SETTINGS_COLUMNS)


def ui_settings_from_df(df):
    df = df_from_any(df, UI_SETTINGS_COLUMNS)
    ui = {}
    for _, r in df.iterrows():
        k = str(r.get("Параметр", "")).strip()
        if k:
            ui[k] = to_float(r.get("Значение"), 0)
    return ui


def kpi_html(title, rows, warning=""):
    items = "".join([f"<div class='kpi-item'><span>{a}</span><b>{b}</b></div>" for a,b in rows])
    warn = f"<div class='warning-red'>{warning}</div>" if warning else ""
    return f"<div class='calc-card'><div class='calc-section-title'>{title}</div><div class='kpi-grid'>{items}</div>{warn}</div>"


def demo_kpi(action):
    c = calculate_demo(action, APP_STATE["settings"])
    warn = ""
    if c["hard_stop"]:
        warn = "Жесткий стоп-фактор: коэффициент влияния равен 100%."
    elif c["soft_stop"]:
        warn = "Есть стоп-фактор: коэффициент не может быть ниже 80%."
    return kpi_html("Расчет демонстрации", [
        ("Итого расходы сметы с НДС", money(c["total_vat"])),
        ("Итого расходы сметы без НДС", money(c["cost_net"])),
        ("Общая фора / помощь ООО с НДС", money(c["support_vat"])),
        ("COST без НДС после форы", money(c["cost_net_after_support"])),
        ("P / R / M", f"{c['P']:.0f} / {c['R']:.0f} / {c['M']:.0f}"),
        ("QI", f"{c['QI']:.3f}"),
        ("K", pct(c["K"])),
        ("Расход для премии", money(c["expense_for_bonus"])),
        ("Вычет NET", money(c["deduction_net"])),
    ], warn)


def sale_kpi(action):
    c = calculate_sale(action, APP_STATE["products"], APP_STATE["settings"])
    return kpi_html("Расчет продажи", [("Премия NET расчетная", money(c["bonus_net"])), ("Сумма продажи с НДС", money(c["total_vat"]))])


def premium_kpi(action):
    c = calculate_premium(action, APP_STATE, APP_STATE["settings"])
    return kpi_html("Расчет премии", [
        ("Продажи, подтверждено", money(c["sales_sum"])),
        ("Демо-вычет, подтверждено", money(c["demo_sum"])),
        ("Фактический демо-вычет", money(c["actual_demo"])),
        ("Премия к выплате", money(c["payout"])),
    ], c["warning"])

# ============================================================
# 8. UI CALLBACKS
# ============================================================


def blank_df(columns):
    return pd.DataFrame([], columns=columns)


def expense_rows_to_df(rows):
    out = []
    for row in rows or []:
        article = str(row.get("article", row.get("Статья расхода", ""))).strip()
        if not article or article == "ИТОГО расходы на демонстрацию" or article == COMPANY_SUPPORT_ARTICLE:
            continue
        out.append({
            "Статья расхода": article,
            "Кол-во": to_float(row.get("qty", row.get("Кол-во"))),
            "Ед.изм.": str(row.get("unit", row.get("Ед.изм.", ""))),
            "Цена, руб. без НДС": to_float(row.get("price_net", row.get("Цена, руб. без НДС"))),
            "Цена, руб. с НДС": to_float(row.get("price_vat", row.get("Цена, руб. с НДС"))),
            "Сумма затрат, руб. с НДС": to_float(row.get("amount_vat", row.get("Сумма затрат, руб. с НДС"))),
            "Комментарий": str(row.get("comment", row.get("Комментарий", "")) or ""),
        })
    return pd.DataFrame(out, columns=EXPENSE_COLUMNS)


def parse_demo_calc_state(calc_state_json):
    if isinstance(calc_state_json, dict):
        return calc_state_json
    try:
        raw = json.loads(str(calc_state_json or "{}"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def custom_expenses_from_df(df):
    df = df_from_any(df, EXPENSE_COLUMNS)
    rows = []
    for i, r in df.iterrows():
        article = str(r.get("Статья расхода", "")).strip()
        if not article or article == "ИТОГО расходы на демонстрацию" or article == COMPANY_SUPPORT_ARTICLE or article in FIXED_ARTICLES:
            continue
        rows.append({
            "article": article,
            "qty": to_float(r.get("Кол-во")),
            "unit": str(r.get("Ед.изм.", "")),
            "price_net": to_float(r.get("Цена, руб. без НДС")),
            "price_vat": to_float(r.get("Цена, руб. с НДС")),
            "amount_vat": to_float(r.get("Сумма затрат, руб. с НДС")),
            "calc_type": "direct",
            "is_custom": True,
            "comment": str(r.get("Комментарий", "")),
            "row_order": len(FIXED_ARTICLES) + i + 1,
        })
    return rows


def build_demo_ui_payload(action, settings):
    calc_state, custom_rows = split_calc_state(action or {}, settings)
    return (
        build_demo_calc_html(calc_state, settings),
        json.dumps(calc_state, ensure_ascii=False),
        expense_rows_to_df(custom_rows),
    )


def demo_expenses_from_inputs(calc_state_json, extra_expenses_df, settings):
    fixed_rows = fixed_rows_from_state(parse_demo_calc_state(calc_state_json), settings)
    custom_rows = custom_expenses_from_df(extra_expenses_df)
    return expenses_from_df(expense_rows_to_df(fixed_rows + custom_rows), settings)


def normalize_demo_ui(calc_state_json, extra_expenses_df, settings):
    expenses = demo_expenses_from_inputs(calc_state_json, extra_expenses_df, settings)
    demo_html, demo_state_json, extra_df = build_demo_ui_payload({"expenses": expenses}, settings)
    return expenses, demo_html, demo_state_json, extra_df


def on_login(login, password):
    user = authenticate(login, password)
    if not user:
        return None, gr.update(visible=True), gr.update(visible=False), "<div class='warning-red'>Неверный логин или пароль.</div>", "", gr.update(choices=[], value=None), gr.update(visible=False), gr.update(visible=False)
    director = is_director(user)
    choices = action_choices(user, "__all__" if director else user["login"])
    selected = choices[0] if choices else None
    badge = f"<div class='top-badge'><b>{user['name']}</b><br>Роль: {'Директор' if director else 'Менеджер'}</div>"
    return user, gr.update(visible=False), gr.update(visible=True), "", badge, gr.update(choices=choices, value=selected), gr.update(visible=director, interactive=director, value="__all__"), gr.update(visible=director, interactive=director)


def load_action_details(user, choice):
    action = find_action(action_id_from_choice(choice))
    settings = APP_STATE["settings"]
    default_demo_html, default_demo_state_json, default_demo_extra_df = build_demo_ui_payload({}, settings)
    # default criterion outputs
    crit_values = []
    crit_comments = []
    for cr in settings.get("criteria", DEFAULT_CRITERIA):
        crit_values.append(criterion_label(cr, 0))
        crit_comments.append("")
    if not action:
        return ["", gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), False, 0, ""] + ["", today_str(), "", "", "", "", "", default_demo_html, default_demo_state_json, default_demo_extra_df, ""] + crit_values + crit_comments + [today_str(), "", "", "", blank_df(SALE_COLUMNS), "", "", gr.update(choices=[], value=None), today_str(), "", "", blank_df([]), blank_df([]), ""]

    confirmed_amount = action.get("confirmed_amount")
    director_comment = action.get("director_comment", "")
    if action["type"] == ACTION_DEMO:
        calc = calculate_demo(action, settings)
        demo_html, demo_state_json, demo_extra_df = build_demo_ui_payload(action, settings)
        if confirmed_amount is None:
            confirmed_amount = round(calc["deduction_net"], 2)
        crit_values = []
        crit_comments = []
        for cr in settings.get("criteria", DEFAULT_CRITERIA):
            cv = (action.get("criteria") or {}).get(cr["code"], {"level_index":0, "manager_comment":""})
            crit_values.append(criterion_label(cr, cv.get("level_index", 0)))
            crit_comments.append(cv.get("manager_comment", ""))
        return [action["id"], gr.update(visible=True), gr.update(visible=False), gr.update(visible=False), bool(action.get("is_director_confirmed")), confirmed_amount, director_comment, action.get("client",""), action.get("date",today_str()), action.get("manager_login",""), action.get("city",""), action.get("model",""), action.get("task_description",""), action.get("comment",""), demo_html, demo_state_json, demo_extra_df, demo_kpi(action)] + crit_values + crit_comments + [today_str(), "", "", "", blank_df(SALE_COLUMNS), "", "", gr.update(choices=[], value=None), today_str(), "", "", blank_df([]), blank_df([]), ""]

    if action["type"] == ACTION_SALE:
        calc = calculate_sale(action, APP_STATE["products"], settings)
        if confirmed_amount is None:
            confirmed_amount = round(calc["bonus_net"],2)
        return [action["id"], gr.update(visible=False), gr.update(visible=True), gr.update(visible=False), bool(action.get("is_director_confirmed")), confirmed_amount, director_comment] + ["", today_str(), "", "", "", "", "", default_demo_html, default_demo_state_json, default_demo_extra_df, ""] + crit_values + crit_comments + [action.get("date",today_str()), action.get("manager_login",""), action.get("client",""), action.get("comment",""), calc["rows_df"], sale_kpi(action), "", gr.update(choices=[], value=None), today_str(), "", "", blank_df([]), blank_df([]), ""]

    calc = calculate_premium(action, APP_STATE, settings)
    if confirmed_amount is None:
        confirmed_amount = round(calc["payout"],2)
    sale_df = calc["sale_rows_df"] if not calc["sale_rows_df"].empty else blank_df(["Дата", "Клиент", "Премия расчетная", "Подтверждено директором"])
    demo_df = calc["demo_rows_df"] if not calc["demo_rows_df"].empty else blank_df(["Дата", "Клиент", "Вычет расчетный", "Подтверждено директором", "Демо подтверждено"])
    return [action["id"], gr.update(visible=False), gr.update(visible=False), gr.update(visible=True), bool(action.get("is_director_confirmed")), confirmed_amount, director_comment] + ["", today_str(), "", "", "", "", "", default_demo_html, default_demo_state_json, default_demo_extra_df, ""] + crit_values + crit_comments + [today_str(), "", "", "", blank_df(SALE_COLUMNS), "", "", gr.update(choices=[], value=None), action.get("date",today_str()), action.get("manager_login",""), action.get("comment",""), sale_df, demo_df, premium_kpi(action)]


def refresh_actions(user, manager_filter):
    choices = action_choices(user, manager_filter if is_director(user) else (user or {}).get("login"))
    return gr.update(choices=choices, value=choices[0] if choices else None)


def add_action_ui(user, manager_to_add, manager_filter, tp):
    a, msg = add_action(tp, user, manager_to_add)
    choices = action_choices(user, manager_filter if is_director(user) else (user or {}).get("login"))
    selected = action_card_text(a) if a else (choices[0] if choices else None)
    return [gr.update(choices=choices, value=selected), msg] + load_action_details(user, selected)


def delete_action_ui(user, choice, manager_filter):
    msg = delete_action(action_id_from_choice(choice), user)
    choices = action_choices(user, manager_filter if is_director(user) else (user or {}).get("login"))
    selected = choices[0] if choices else None
    return [gr.update(choices=choices, value=selected), msg] + load_action_details(user, selected)


def move_action_ui(user, choice, manager_filter, direction):
    msg = move_action(action_id_from_choice(choice), user, direction)
    choices = action_choices(user, manager_filter if is_director(user) else (user or {}).get("login"))
    selected_id = action_id_from_choice(choice)
    selected = next((c for c in choices if selected_id in c), choices[0] if choices else None)
    return [gr.update(choices=choices, value=selected), msg] + load_action_details(user, selected)


def save_common_director_fields(user, action, confirmed, confirmed_amount, director_comment):
    if is_director(user):
        if confirmed and action.get("type") == ACTION_PREMIUM:
            ok, warn = can_confirm_premium(action, APP_STATE)
            if not ok:
                return warn
        action["is_director_confirmed"] = bool(confirmed)
        action["confirmed_amount"] = to_float(confirmed_amount, 0)
        action["director_comment"] = str(director_comment or "")
    return ""


def save_demo_ui(user, current_id, confirmed, confirmed_amount, director_comment, client, dt, manager, city, model, task, comment, calc_state_json, extra_expenses_df, *criteria_args):
    a = find_action(current_id)
    if not a or a.get("type") != ACTION_DEMO:
        return "Демонстрация не выбрана.", gr.update(), ""
    if is_action_locked(a, APP_STATE) and not is_director(user):
        return "Действие заблокировано подтвержденной премией.", gr.update(), demo_kpi(a)
    if not (is_director(user) or a.get("manager_login") == user.get("login")):
        return "Нет прав на редактирование.", gr.update(), demo_kpi(a)
    ncrit = len(APP_STATE["settings"].get("criteria", DEFAULT_CRITERIA))
    crit_labels = criteria_args[:ncrit]
    crit_comments = criteria_args[ncrit:]
    if is_director(user):
        a["manager_login"] = manager if manager in MANAGER_LOGINS else a["manager_login"]
    a["client"] = str(client or "")
    a["date"] = safe_date(dt)
    a["city"] = str(city or "")
    a["model"] = str(model or "")
    a["task_description"] = str(task or "")
    a["comment"] = str(comment or "")
    a["expenses"] = demo_expenses_from_inputs(calc_state_json, extra_expenses_df, APP_STATE["settings"])
    crit = {}
    for cr, label, comm in zip(APP_STATE["settings"].get("criteria", DEFAULT_CRITERIA), crit_labels, crit_comments):
        crit[cr["code"]] = {"level_index": label_to_level_index(cr, label), "manager_comment": str(comm or "")}
    a["criteria"] = crit
    calc = calculate_demo(a, APP_STATE["settings"])
    if a.get("confirmed_amount") is None:
        a["confirmed_amount"] = round(calc["deduction_net"],2)
    warn = save_common_director_fields(user, a, confirmed, confirmed_amount, director_comment)
    if warn:
        return warn, gr.update(), demo_kpi(a)
    msg = persist_state_to_db(APP_STATE)
    choices = action_choices(user, "__all__" if is_director(user) else user.get("login"))
    return "Демонстрация сохранена. " + msg, gr.update(choices=choices, value=action_card_text(a)), demo_kpi(a)


def recalc_demo_ui(calc_state_json, extra_expenses_df, *criteria_args):
    ncrit = len(APP_STATE["settings"].get("criteria", DEFAULT_CRITERIA))
    crit_labels = criteria_args[:ncrit]
    crit_comments = criteria_args[ncrit:]
    expenses, demo_html, demo_state_json, demo_extra_df = normalize_demo_ui(calc_state_json, extra_expenses_df, APP_STATE["settings"])
    temp = {"expenses": expenses, "criteria": {}}
    for cr, label, comm in zip(APP_STATE["settings"].get("criteria", DEFAULT_CRITERIA), crit_labels, crit_comments):
        temp["criteria"][cr["code"]] = {"level_index": label_to_level_index(cr, label), "manager_comment": str(comm or "")}
    return demo_html, demo_state_json, demo_extra_df, demo_kpi(temp)


def search_products_ui(query):
    choices = search_products(query, APP_STATE.get("products", []))
    return gr.update(choices=choices, value=choices[0] if choices else None)


def add_selected_product_to_sale(choice, sale_df):
    pid = product_id_from_choice(choice)
    prod = next((normalize_product(p, APP_STATE["settings"]) for p in APP_STATE.get("products", []) if str(p.get("product_id")) == pid), None)
    if not prod:
        return sale_df, "Товар не найден в справочнике. Добавление запрещено.", ""
    rows = sale_rows_from_df(sale_df, APP_STATE["products"], APP_STATE["settings"])
    rows.append(create_sale_row_from_product(prod, 1, APP_STATE["settings"]))
    df = sale_rows_to_df(rows, APP_STATE["products"], APP_STATE["settings"])
    return df, "Товар добавлен из справочника.", sale_kpi({"rows": rows})


def recalc_sale_ui(sale_df):
    rows = sale_rows_from_df(sale_df, APP_STATE["products"], APP_STATE["settings"])
    df = sale_rows_to_df(rows, APP_STATE["products"], APP_STATE["settings"])
    return df, sale_kpi({"rows": rows})


def save_sale_ui(user, current_id, confirmed, confirmed_amount, director_comment, dt, manager, client, comment, sale_df):
    a = find_action(current_id)
    if not a or a.get("type") != ACTION_SALE:
        return "Продажа не выбрана.", gr.update(), ""
    if is_action_locked(a, APP_STATE) and not is_director(user):
        return "Действие заблокировано подтвержденной премией.", gr.update(), sale_kpi(a)
    if not (is_director(user) or a.get("manager_login") == user.get("login")):
        return "Нет прав на редактирование.", gr.update(), sale_kpi(a)
    if is_director(user):
        a["manager_login"] = manager if manager in MANAGER_LOGINS else a["manager_login"]
    a["date"] = safe_date(dt)
    a["client"] = str(client or "")
    a["comment"] = str(comment or "")
    a["rows"] = sale_rows_from_df(sale_df, APP_STATE["products"], APP_STATE["settings"])
    calc = calculate_sale(a, APP_STATE["products"], APP_STATE["settings"])
    if a.get("confirmed_amount") is None:
        a["confirmed_amount"] = round(calc["bonus_net"],2)
    warn = save_common_director_fields(user, a, confirmed, confirmed_amount, director_comment)
    if warn:
        return warn, gr.update(), sale_kpi(a)
    msg = persist_state_to_db(APP_STATE)
    choices = action_choices(user, "__all__" if is_director(user) else user.get("login"))
    return "Продажа сохранена. " + msg, gr.update(choices=choices, value=action_card_text(a)), sale_kpi(a)


def save_premium_ui(user, current_id, confirmed, confirmed_amount, director_comment, dt, manager, comment):
    a = find_action(current_id)
    if not a or a.get("type") != ACTION_PREMIUM:
        return "Премия не выбрана.", gr.update(), "", blank_df([]), blank_df([])
    if not is_director(user) and a.get("manager_login") != user.get("login"):
        return "Нет прав.", gr.update(), premium_kpi(a), blank_df([]), blank_df([])
    if is_director(user):
        a["manager_login"] = manager if manager in MANAGER_LOGINS else a["manager_login"]
    a["date"] = safe_date(dt)
    a["client"] = user_name(a["manager_login"])
    a["comment"] = str(comment or "")
    calc = calculate_premium(a, APP_STATE, APP_STATE["settings"])
    if a.get("confirmed_amount") is None:
        a["confirmed_amount"] = round(calc["payout"],2)
    warn = save_common_director_fields(user, a, confirmed, confirmed_amount, director_comment)
    if warn:
        return warn, gr.update(), premium_kpi(a), calc["sale_rows_df"], calc["demo_rows_df"]
    msg = persist_state_to_db(APP_STATE)
    choices = action_choices(user, "__all__" if is_director(user) else user.get("login"))
    calc = calculate_premium(a, APP_STATE, APP_STATE["settings"])
    return "Премия сохранена. " + msg, gr.update(choices=choices, value=action_card_text(a)), premium_kpi(a), calc["sale_rows_df"], calc["demo_rows_df"]


def save_products_ui(user, products_df):
    if not is_director(user):
        return "Товары может редактировать только директор.", products_to_df(APP_STATE["products"], APP_STATE["settings"])
    APP_STATE["products"] = products_from_df(products_df, APP_STATE["settings"])
    msg = persist_state_to_db(APP_STATE)
    return "Товары сохранены. " + msg, products_to_df(APP_STATE["products"], APP_STATE["settings"])


def create_product_template():
    df = pd.DataFrame([{c:"" for c in PRODUCT_COLUMNS}])
    df.loc[0, "ID товара"] = "NEW-SKU-001"
    df.loc[0, "Артикул"] = "NEW-SKU-001"
    df.loc[0, "Наименование ТМЦ"] = "Новый товар"
    df.loc[0, "Цена руб. без НДС (A)"] = 100000
    df.loc[0, "Цена руб. с НДС"] = 122000
    df.loc[0, "Минимальная цена продажи без НДС (B)"] = 80000
    df.loc[0, "% от маржи (D)"] = 0.65
    with pd.ExcelWriter(PRODUCT_TEMPLATE_PATH, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Товары")
        ws = writer.sheets["Товары"]
        ws.set_column(0, len(PRODUCT_COLUMNS)-1, 24)
    return PRODUCT_TEMPLATE_PATH


def upload_products_from_file(user, file):
    if not is_director(user):
        return "Загружать товары может только директор.", products_to_df(APP_STATE["products"], APP_STATE["settings"])
    if not file:
        return "Файл не выбран.", products_to_df(APP_STATE["products"], APP_STATE["settings"])
    try:
        path = file.name if hasattr(file, "name") else str(file)
        df = pd.read_excel(path)
        for c in PRODUCT_COLUMNS:
            if c not in df.columns:
                df[c] = ""
        APP_STATE["products"] = products_from_df(df[PRODUCT_COLUMNS], APP_STATE["settings"])
        msg = persist_state_to_db(APP_STATE)
        return "Товары загружены из файла. " + msg, products_to_df(APP_STATE["products"], APP_STATE["settings"])
    except Exception as e:
        return f"Ошибка загрузки товаров: {e}", products_to_df(APP_STATE["products"], APP_STATE["settings"])


def save_settings_ui(user, vat_pct, bonus_pct, max_ded_pct, support_vat, payroll_pct, diesel_l, font_family, criteria_df, expense_settings_df, ui_df):
    if not is_director(user):
        return "Настройки может менять только директор."
    s = APP_STATE["settings"]
    s["vat_rate"] = pct_to_decimal(vat_pct,0.22)
    s["bonus_rate"] = pct_to_decimal(bonus_pct,0.65)
    s["max_demo_deduction_pct"] = pct_to_decimal(max_ded_pct,1.0)
    s["company_support_vat"] = to_float(support_vat,30000)
    s["payroll_tax_rate"] = pct_to_decimal(payroll_pct,0.30)
    s["diesel_l_per_100km"] = to_float(diesel_l,12)
    s["font_family"] = "Arial"
    s["criteria"] = criteria_from_df(criteria_df)
    s["expense_settings"] = expense_settings_from_df(expense_settings_df)
    s["ui"] = ui_settings_from_df(ui_df)
    APP_STATE["settings"] = merge_settings(s)
    msg = persist_state_to_db(APP_STATE)
    return "Настройки сохранены. " + msg


def export_json_ui():
    Path(JSON_BACKUP_PATH).write_text(json.dumps(clean_json(APP_STATE), ensure_ascii=False, indent=2), encoding="utf-8")
    return JSON_BACKUP_PATH


def import_json_ui(user, file):
    global APP_STATE
    if not is_director(user):
        return "Импорт JSON доступен только директору."
    if not file:
        return "Файл не выбран."
    try:
        p = file.name if hasattr(file, "name") else str(file)
        state = json.loads(Path(p).read_text(encoding="utf-8"))
        if not isinstance(state, dict) or "settings" not in state or "actions" not in state:
            return "Файл JSON не похож на структуру программы."
        APP_STATE = state
        return "JSON импортирован. " + persist_state_to_db(APP_STATE)
    except Exception as e:
        return f"Ошибка импорта JSON: {e}"


def export_excel_ui():
    with pd.ExcelWriter(EXPORT_XLSX_PATH, engine="xlsxwriter") as writer:
        products_to_df(APP_STATE["products"], APP_STATE["settings"]).to_excel(writer, index=False, sheet_name="Товары")
        pd.DataFrame(APP_STATE["actions"]).drop(columns=["expenses","criteria","rows"], errors="ignore").to_excel(writer, index=False, sheet_name="Действия")
        rows = []
        for a in APP_STATE["actions"]:
            if a["type"] == ACTION_DEMO:
                calc = calculate_demo(a, APP_STATE["settings"])
                rows.append({"ID": a["id"], "Менеджер": user_name(a["manager_login"]), "Клиент": a["client"], "COST": calc["cost_net_after_support"], "K": calc["K"], "Вычет": calc["deduction_net"], "Подтверждено": a.get("confirmed_amount")})
        pd.DataFrame(rows).to_excel(writer, index=False, sheet_name="Демо")
        for ws in writer.sheets.values():
            ws.set_column(0, 30, 22)
    return EXPORT_XLSX_PATH

# ============================================================
# 9. СТИЛЬ
# ============================================================


def build_css(settings=None):
    settings = settings or default_settings()
    ui = settings.get("ui", {})
    # v6.2: единый шрифт во всем UI и таблицах — Arial.
    font = "Arial"
    return f"""
    :root {{
      --font-base: {ui.get('font_base_px',13)}px;
      --font-title: {ui.get('font_title_px',18)}px;
      --card-pad: {ui.get('card_padding_px',10)}px;
      --criteria-row-gap: {ui.get('field_gap_px',8)}px;
      --table-row-height: {ui.get('table_row_height_px',30)}px;
    }}
    .gradio-container,
    .gradio-container *,
    .gradio-container table,
    .gradio-container th,
    .gradio-container td,
    .gradio-container input,
    .gradio-container textarea,
    .gradio-container button,
    .gradio-container select,
    .gradio-container label {{
      font-family:{font}, sans-serif !important;
      color:#111111;
    }}
    .gradio-container {{ background:#f4f7fb !important; font-size:var(--font-base); }}
    .calc-header {{ background:linear-gradient(135deg,#0b2f4d 0%,#13527c 62%,#0f8a5f 100%); color:white; border-radius:20px; padding:16px 20px; box-shadow:0 12px 28px rgba(15,23,42,.14); margin-bottom:12px; }}
    .calc-header h1 {{ margin:0; font-size:24px; color:white !important; }} .calc-header p {{ margin:6px 0 0; opacity:.86; color:white !important; }}
    .calc-card,.top-badge {{ background:white; border:1px solid #d7e0ec; border-radius:16px; padding:var(--card-pad); box-shadow:0 10px 22px rgba(15,23,42,.06); margin-bottom:10px; }}
    .calc-section-title {{ font-size:var(--font-title); font-weight:800; color:#123b63 !important; margin-bottom:8px; }}
    .kpi-grid {{ display:grid; grid-template-columns:repeat(3,minmax(160px,1fr)); gap:8px; }}
    .kpi-item {{ background:#f8fbff; border:1px solid #d7e0ec; border-radius:12px; padding:8px 10px; }}
    .kpi-item span {{ display:block; color:#5b6b83 !important; font-size:12px; }} .kpi-item b {{ display:block; color:#0f172a !important; font-size:15px; margin-top:2px; }}
    .warning-red {{ margin-top:8px; background:rgba(220,38,38,.10); border:1px solid rgba(220,38,38,.35); color:#991b1b !important; padding:10px 12px; border-radius:12px; font-weight:800; }}
    .action-list textarea, .action-list label {{ font-size:12px !important; }}
    .gradio-container table th, .gradio-container table td {{ font-family:Arial, sans-serif !important; color:#111111 !important; line-height:1.22 !important; }}
    .gradio-container [data-testid="dataframe"] textarea,
    .gradio-container [data-testid="dataframe"] input {{ font-family:Arial, sans-serif !important; color:#111111 !important; min-height:var(--table-row-height) !important; }}

    /* Компактная строка критерия: строгое соотношение в информационном блоке
       20% — название и описание; 60% — прямоугольники уровней; 20% — комментарий. */
    .criteria-block-compact {{ margin-top:6px; }}
    .criteria-grid-row {{
      display:grid !important;
      grid-template-columns:
        minmax(0, {ui.get('criteria_name_width_pct',20)}fr)
        minmax(0, {ui.get('criteria_levels_width_pct',60)}fr)
        minmax(0, {ui.get('criteria_comment_width_pct',20)}fr) !important;
      gap:var(--criteria-row-gap) !important;
      align-items:stretch !important;
      border:1px solid #d7e0ec !important;
      border-radius:12px !important;
      background:#ffffff !important;
      padding:8px !important;
      margin-bottom:8px !important;
      width:100% !important;
      box-sizing:border-box !important;
    }}
    .criteria-name-cell {{
      min-width:0 !important;
      background:#f8fbff !important;
      border:1px solid #e2e8f0 !important;
      border-radius:10px !important;
      padding:8px 10px !important;
      min-height:56px !important;
    }}
    .criteria-name-cell, .criteria-name-cell * {{ color:#111111 !important; }}
    .criteria-name-cell p {{ margin:0 !important; line-height:1.2 !important; font-size:12px !important; }}
    .criteria-name-cell strong {{ display:block !important; margin-bottom:3px !important; font-size:13px !important; color:#111111 !important; }}
    .criteria-name-cell, .criteria-levels-cell, .criteria-comment-cell {{ min-width:0 !important; box-sizing:border-box !important; }}
    .criteria-levels-cell {{ padding:0 !important; min-width:0 !important; width:100% !important; }}
    .criteria-comment-cell {{ min-width:0 !important; width:100% !important; }}
    .criteria-comment-cell textarea {{ min-height:56px !important; font-size:12px !important; color:#111111 !important; width:100% !important; }}
    .criteria-radio {{ margin:0 !important; }}
    .criteria-radio fieldset,
    .criteria-radio div[role="radiogroup"] {{
      display:flex !important;
      flex-direction:row !important;
      flex-wrap:nowrap !important;
      gap:6px !important;
      align-items:stretch !important;
      width:100% !important;
    }}
    .criteria-radio label {{
      flex:1 1 0 !important;
      border:1px solid #94a3b8 !important;
      border-radius:10px !important;
      padding:7px 8px !important;
      margin:0 !important;
      background:#f8fafc !important;
      min-height:56px !important;
      display:flex !important;
      align-items:center !important;
      justify-content:center !important;
      text-align:center !important;
      white-space:pre-line !important;
      color:#111111 !important;
      font-size:11.5px !important;
      line-height:1.14 !important;
      cursor:pointer !important;
    }}
    .criteria-radio label input {{ display:none !important; }}
    .criteria-radio label:has(input:checked) {{ border:3px solid #111111 !important; background:#e0f2fe !important; font-weight:800 !important; }}
    .criteria-radio label span {{ color:#111111 !important; }}
    .criteria-accordion, .criteria-accordion * {{ color:#111111 !important; }}
    button {{ border-radius:12px !important; font-weight:700 !important; }}
    """

# ============================================================
# 10. GRADIO APP
# ============================================================

settings0 = APP_STATE["settings"]
criteria_defs = settings0.get("criteria", DEFAULT_CRITERIA)
initial_demo_html, initial_demo_state_json, initial_demo_extra_df = build_demo_ui_payload({}, settings0)


def gradio_has_kwarg(obj, arg_name: str) -> bool:
    """Проверяет поддержку параметра в текущей версии Gradio.
    Нужно для совместимости Colab: в одних версиях css/theme передаются в Blocks(),
    в других — в launch(), а в некоторых launch(css=...) вызывает TypeError.
    """
    try:
        return arg_name in inspect.signature(obj).parameters
    except Exception:
        return False


APP_CSS = build_css(APP_STATE.get("settings", default_settings()))
BLOCKS_KWARGS = {"title": "ИРБИСТЕХ — демонстрации, продажи и премии"}
LAUNCH_KWARGS = {
    "share": env_bool("GRADIO_SHARE", False),
    "debug": env_bool("GRADIO_DEBUG", False),
    "server_name": os.getenv("GRADIO_SERVER_NAME", "127.0.0.1"),
    "server_port": env_int("GRADIO_SERVER_PORT", 7860),
}

for path_str in [JSON_BACKUP_PATH, EXPORT_XLSX_PATH, PRODUCT_TEMPLATE_PATH]:
    try:
        Path(path_str).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

if gradio_has_kwarg(gr.Blocks, "fill_width"):
    BLOCKS_KWARGS["fill_width"] = True

if gradio_has_kwarg(gr.Blocks.launch, "allowed_paths"):
    LAUNCH_KWARGS["allowed_paths"] = [str(DATA_DIR), str(EXPORT_DIR)]

# В этой версии Gradio в Colab app.launch(css=...) не поддерживается,
# а gr.Blocks(css=...) дает предупреждения совместимости. Поэтому CSS
# вставляется обычным <style> внутри приложения. Так код не зависит от
# того, где конкретная версия Gradio ожидает css/theme.
with gr.Blocks(**BLOCKS_KWARGS) as app:
    gr.HTML(f"<style>{APP_CSS}</style>")
    current_user = gr.State(None)
    current_action_id = gr.State("")
    gr.HTML("""
    <div class="calc-header">
      <h1>ИРБИСТЕХ — демонстрации, продажи и премии</h1>
      <p>Учет действий менеджеров, сметы демонстраций, продаж и выплат премий. Данные хранятся в PostgreSQL.</p>
    </div>
    """)

    with gr.Group(visible=True) as login_group:
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML(f"<div class='calc-card'><div class='calc-section-title'>Вход</div>{INIT_STATUS}</div>")
                login_input = gr.Textbox(label="Логин", value="")
                password_input = gr.Textbox(label="Пароль", type="password", value="")
                login_btn = gr.Button("Войти", variant="primary")
                login_error = gr.HTML("")
            with gr.Column(scale=1):
                gr.HTML("<div class='calc-card'><b>Доступы:</b><br>artur / 123<br>ruslan / 111<br>timur / 222<br>maria / 333<br>ildar / 444</div>")

    with gr.Group(visible=False) as app_group:
        user_badge = gr.HTML("")
        with gr.Tabs():
            with gr.Tab("ДЕМОНСТРАЦИИ И ПРОДАЖИ"):
                with gr.Row():
                    with gr.Column(scale=3):
                        gr.HTML("<div class='calc-card'><div class='calc-section-title'>Список действий</div>Карточка умещается в две строки. Серые действия считаются закрытыми подтвержденной премией.</div>")
                        manager_filter = gr.Dropdown(label="Фильтр по менеджеру", choices=MANAGER_FILTER_CHOICES, value="__all__", visible=False)
                        manager_to_add = gr.Dropdown(label="Добавить менеджеру", choices=MANAGER_CHOICES, value=MANAGER_LOGINS[0], visible=False)
                        action_list = gr.Radio(label="Действия", choices=[], elem_classes=["action-list"])
                        with gr.Row():
                            add_demo_btn = gr.Button("+ Демо")
                            add_sale_btn = gr.Button("+ Продажа")
                            add_premium_btn = gr.Button("+ Премия")
                        with gr.Row():
                            move_up_btn = gr.Button("↑ Выше")
                            move_down_btn = gr.Button("↓ Ниже")
                            delete_btn = gr.Button("Удалить")
                        action_status = gr.Textbox(label="Статус", interactive=False)
                    with gr.Column(scale=7):
                        gr.HTML("<div class='calc-card'><div class='calc-section-title'>Подтверждение директора</div>После подтверждения директором менеджер не может менять это действие. Поле суммы можно скорректировать вручную.</div>")
                        with gr.Row():
                            director_confirmed = gr.Checkbox(label="Подтверждено директором", interactive=False)
                            confirmed_amount = gr.Number(label="Сумма, подтвержденная директором", value=0, interactive=False)
                            director_comment = gr.Textbox(label="Комментарий директора", interactive=False)

                        with gr.Group(visible=False) as demo_group:
                            gr.HTML("<div class='calc-card'><div class='calc-section-title'>Демонстрация</div>Основные статьи сметы считаются через встроенный калькулятор. Нестандартные строки можно добавлять отдельно внизу.</div>")
                            with gr.Row():
                                demo_client = gr.Textbox(label="Клиент")
                                demo_date = gr.Textbox(label="Дата")
                                demo_manager = gr.Dropdown(label="Менеджер", choices=MANAGER_CHOICES)
                            with gr.Row():
                                demo_city = gr.Textbox(label="Город")
                                demo_model = gr.Textbox(label="Модель")
                            demo_task = gr.Textbox(label="Задача очистки", lines=2)
                            demo_comment = gr.Textbox(label="Комментарий", lines=2)
                            demo_calc_html = gr.HTML(initial_demo_html)
                            demo_calc_state_json = gr.Textbox(value=initial_demo_state_json, visible=False, show_label=False, elem_id="demo-calc-state-json")
                            demo_extra_expenses_df = dataframe_compat(headers=EXPENSE_COLUMNS, value=initial_demo_extra_df, row_count=(2,"dynamic"), col_count=(7,"fixed"), interactive=True, label="Дополнительные строки сметы")
                            demo_kpi_html = gr.HTML("")

                            gr.HTML("<div class='calc-card'><div class='calc-section-title'>Критерии снижения вычета</div>Каждый критерий занимает одну компактную строку: критерий и описание, уровни с баллами, комментарий менеджера.</div>")
                            criterion_radios = []
                            criterion_comments = []
                            block_titles = {
                                "P": "Блок 1. Подготовка к демонстрации",
                                "R": "Блок 2. Оценка результатов демонстрации",
                                "M": "Блок 3. Управленческий фактор",
                            }
                            block_notes = {
                                "P": "Оценивает качество подготовки до выезда.",
                                "R": "Оценивает фактический и коммерческий результат после показа.",
                                "M": "Учитывает стратегические, логистические и управленческие обстоятельства.",
                            }
                            for block_code in ["P", "R", "M"]:
                                block_open = block_code == "P"
                                with gr.Accordion(block_titles[block_code], open=block_open, elem_classes=["criteria-accordion", "criteria-block-compact"]):
                                    gr.Markdown(f"**{block_titles[block_code]}** — {block_notes[block_code]}")
                                    for cr in [x for x in criteria_defs if x.get("block") == block_code]:
                                        with gr.Row(elem_classes=["criteria-grid-row"]):
                                            gr.Markdown(f"**{cr['code']}. {cr['title']}**\n{cr['desc']}", elem_classes=["criteria-name-cell"])
                                            radio = gr.Radio(
                                                label="",
                                                choices=criteria_choice_labels(cr),
                                                value=criterion_label(cr, 0),
                                                elem_classes=["criteria-radio", "criteria-levels-cell"],
                                                show_label=False,
                                            )
                                            comment = gr.Textbox(
                                                label="Комментарий",
                                                lines=2,
                                                placeholder="Подтверждение выбранного уровня",
                                                elem_classes=["criteria-comment-cell"],
                                            )
                                        criterion_radios.append(radio)
                                        criterion_comments.append(comment)
                            gr.HTML('''
                            <script>
                            (function(){
                              function bindIrbisCriteriaAccordions(){
                                const roots = Array.from(document.querySelectorAll('.criteria-accordion'));
                                roots.forEach(function(root){
                                  const details = root.querySelector('details') || (root.tagName && root.tagName.toLowerCase() === 'details' ? root : null);
                                  if(!details || details.dataset.irbisAccordionBound === '1') return;
                                  details.dataset.irbisAccordionBound = '1';
                                  details.addEventListener('toggle', function(){
                                    if(details.open){
                                      roots.forEach(function(otherRoot){
                                        if(otherRoot === root) return;
                                        const other = otherRoot.querySelector('details') || (otherRoot.tagName && otherRoot.tagName.toLowerCase() === 'details' ? otherRoot : null);
                                        if(other) other.open = false;
                                      });
                                    }
                                  });
                                });
                              }
                              setTimeout(bindIrbisCriteriaAccordions, 300);
                              setTimeout(bindIrbisCriteriaAccordions, 1000);
                              setTimeout(bindIrbisCriteriaAccordions, 2500);
                              try {
                                const observer = new MutationObserver(bindIrbisCriteriaAccordions);
                                observer.observe(document.body, {childList:true, subtree:true});
                              } catch(e) {}
                            })();
                            </script>
                            ''')
                            with gr.Row():
                                demo_recalc_btn = gr.Button("Пересчитать")
                                demo_save_btn = gr.Button("Сохранить демонстрацию", variant="primary")
                            demo_status = gr.Textbox(label="Статус", interactive=False)

                        with gr.Group(visible=False) as sale_group:
                            gr.HTML("<div class='calc-card'><div class='calc-section-title'>Продажа</div>Товар можно добавить только из справочника. Начните вводить минимум 3 символа.</div>")
                            with gr.Row():
                                sale_date = gr.Textbox(label="Дата")
                                sale_manager = gr.Dropdown(label="Менеджер", choices=MANAGER_CHOICES)
                                sale_client = gr.Textbox(label="Клиент")
                            sale_comment = gr.Textbox(label="Комментарий", lines=2)
                            with gr.Row():
                                sale_product_search = gr.Textbox(label="Поиск товара")
                                sale_product_select = gr.Dropdown(label="Подходящие товары", choices=[])
                            sale_rows_df = dataframe_compat(headers=SALE_COLUMNS, value=blank_df(SALE_COLUMNS), row_count=(1,"dynamic"), col_count=(13,"fixed"), interactive=True, label="Товары продажи")
                            sale_kpi_html = gr.HTML("")
                            with gr.Row():
                                sale_recalc_btn = gr.Button("Пересчитать")
                                sale_save_btn = gr.Button("Сохранить продажу", variant="primary")
                            sale_status = gr.Textbox(label="Статус", interactive=False)

                        with gr.Group(visible=False) as premium_group:
                            gr.HTML("<div class='calc-card'><div class='calc-section-title'>Выплата премии</div>Премия считается по подтвержденным директором суммам продаж и демонстраций.</div>")
                            with gr.Row():
                                premium_date = gr.Textbox(label="Дата")
                                premium_manager = gr.Dropdown(label="Менеджер", choices=MANAGER_CHOICES)
                            premium_comment = gr.Textbox(label="Комментарий", lines=2)
                            premium_sales_df = dataframe_compat(label="Продажи периода", value=blank_df([]), interactive=False)
                            premium_demos_df = dataframe_compat(label="Демонстрации периода", value=blank_df([]), interactive=False)
                            premium_kpi_html = gr.HTML("")
                            premium_save_btn = gr.Button("Сохранить премию", variant="primary")
                            premium_status = gr.Textbox(label="Статус", interactive=False)

            with gr.Tab("ТОВАРЫ"):
                gr.HTML("<div class='calc-card'><div class='calc-section-title'>Товары и премии</div>Директор добавляет товары вручную или через Excel-шаблон. Менеджеры видят справочник без редактирования.</div>")
                with gr.Row():
                    product_template_btn = gr.Button("Скачать шаблон товаров")
                    product_template_file = gr.File(label="Шаблон")
                    product_upload = gr.File(label="Загрузить заполненный шаблон", file_types=[".xlsx"])
                    product_upload_btn = gr.Button("Загрузить товары", visible=False)
                    product_save_btn = gr.Button("Сохранить товары", variant="primary", visible=False)
                products_df = dataframe_compat(headers=PRODUCT_COLUMNS, value=products_to_df(APP_STATE["products"], APP_STATE["settings"]), row_count=(5,"dynamic"), col_count=(10,"fixed"), interactive=False, label="Справочник товаров")
                products_status = gr.Textbox(label="Статус", interactive=False)

            with gr.Tab("НАСТРОЙКИ"):
                gr.HTML("<div class='calc-card'><div class='calc-section-title'>Настройки</div>Здесь находятся коэффициенты, баллы, смета, параметры интерфейса, резервные копии JSON и экспорт.</div>")
                with gr.Row():
                    vat_pct = gr.Number(label="НДС, %", value=decimal_to_pct(settings0.get("vat_rate",0.22)), interactive=False)
                    bonus_pct = gr.Number(label="Ставка премии, %", value=decimal_to_pct(settings0.get("bonus_rate",0.65)), interactive=False)
                    max_ded_pct = gr.Number(label="Максимальный вычет из премии, %", value=decimal_to_pct(settings0.get("max_demo_deduction_pct",1)), interactive=False)
                with gr.Row():
                    company_support_vat = gr.Number(label="Общая фора / помощь ООО, руб. с НДС", value=settings0.get("company_support_vat",30000), interactive=False)
                    payroll_pct = gr.Number(label="Налоги на ФОТ, %", value=decimal_to_pct(settings0.get("payroll_tax_rate",0.30)), interactive=False)
                    diesel_l = gr.Number(label="Расход дизеля, л / 100 км", value=settings0.get("diesel_l_per_100km",12), interactive=False)
                    font_family = gr.Dropdown(label="Шрифт интерфейса", choices=FONT_CHOICES, value="Arial", interactive=False)
                criteria_settings_df = dataframe_compat(headers=CRITERIA_SETTINGS_COLUMNS, value=criteria_to_df(settings0), row_count=(22,"dynamic"), col_count=(5,"fixed"), interactive=False, label="Баллы уровней критериев")
                expense_settings_df = dataframe_compat(headers=EXPENSE_SETTINGS_COLUMNS, value=expense_settings_to_df(settings0), row_count=(17,"dynamic"), col_count=(9,"fixed"), interactive=False, label="Настройки сметы демонстрации")
                ui_settings_df = dataframe_compat(headers=UI_SETTINGS_COLUMNS, value=ui_settings_to_df(settings0), row_count=(6,"fixed"), col_count=(3,"fixed"), interactive=False, label="Настройки интерфейса")
                settings_save_btn = gr.Button("Сохранить настройки", variant="primary", visible=False)
                settings_status = gr.Textbox(label="Статус", interactive=False)
                gr.HTML("<div class='calc-card'><div class='calc-section-title'>Резервные копии и экспорт</div></div>")
                with gr.Row():
                    export_json_btn = gr.Button("Скачать JSON")
                    export_json_file = gr.File(label="JSON")
                    import_json_file = gr.File(label="Загрузить JSON", file_types=[".json"])
                    import_json_btn = gr.Button("Импорт JSON")
                    export_xlsx_btn = gr.Button("Экспорт в Excel")
                    export_xlsx_file = gr.File(label="Excel")
                json_status = gr.Textbox(label="Статус JSON/Excel", interactive=False)

    detail_outputs = [current_action_id, demo_group, sale_group, premium_group, director_confirmed, confirmed_amount, director_comment, demo_client, demo_date, demo_manager, demo_city, demo_model, demo_task, demo_comment, demo_calc_html, demo_calc_state_json, demo_extra_expenses_df, demo_kpi_html] + criterion_radios + criterion_comments + [sale_date, sale_manager, sale_client, sale_comment, sale_rows_df, sale_kpi_html, sale_product_search, sale_product_select, premium_date, premium_manager, premium_comment, premium_sales_df, premium_demos_df, premium_kpi_html]

    login_btn.click(on_login, inputs=[login_input, password_input], outputs=[current_user, login_group, app_group, login_error, user_badge, action_list, manager_filter, manager_to_add]).then(load_action_details, inputs=[current_user, action_list], outputs=detail_outputs)
    manager_filter.change(refresh_actions, inputs=[current_user, manager_filter], outputs=[action_list]).then(load_action_details, inputs=[current_user, action_list], outputs=detail_outputs)
    action_list.change(load_action_details, inputs=[current_user, action_list], outputs=detail_outputs)

    add_demo_btn.click(lambda u,m,f: add_action_ui(u,m,f,ACTION_DEMO), inputs=[current_user, manager_to_add, manager_filter], outputs=[action_list, action_status] + detail_outputs)
    add_sale_btn.click(lambda u,m,f: add_action_ui(u,m,f,ACTION_SALE), inputs=[current_user, manager_to_add, manager_filter], outputs=[action_list, action_status] + detail_outputs)
    add_premium_btn.click(lambda u,m,f: add_action_ui(u,m,f,ACTION_PREMIUM), inputs=[current_user, manager_to_add, manager_filter], outputs=[action_list, action_status] + detail_outputs)
    delete_btn.click(delete_action_ui, inputs=[current_user, action_list, manager_filter], outputs=[action_list, action_status] + detail_outputs)
    move_up_btn.click(lambda u,c,f: move_action_ui(u,c,f,"up"), inputs=[current_user, action_list, manager_filter], outputs=[action_list, action_status] + detail_outputs)
    move_down_btn.click(lambda u,c,f: move_action_ui(u,c,f,"down"), inputs=[current_user, action_list, manager_filter], outputs=[action_list, action_status] + detail_outputs)

    crit_inputs = criterion_radios + criterion_comments
    demo_recalc_btn.click(recalc_demo_ui, inputs=[demo_calc_state_json, demo_extra_expenses_df] + crit_inputs, outputs=[demo_calc_html, demo_calc_state_json, demo_extra_expenses_df, demo_kpi_html])
    demo_save_btn.click(save_demo_ui, inputs=[current_user, current_action_id, director_confirmed, confirmed_amount, director_comment, demo_client, demo_date, demo_manager, demo_city, demo_model, demo_task, demo_comment, demo_calc_state_json, demo_extra_expenses_df] + crit_inputs, outputs=[demo_status, action_list, demo_kpi_html])

    sale_product_search.change(search_products_ui, inputs=[sale_product_search], outputs=[sale_product_select])
    sale_product_select.change(add_selected_product_to_sale, inputs=[sale_product_select, sale_rows_df], outputs=[sale_rows_df, sale_status, sale_kpi_html])
    sale_recalc_btn.click(recalc_sale_ui, inputs=[sale_rows_df], outputs=[sale_rows_df, sale_kpi_html])
    sale_save_btn.click(save_sale_ui, inputs=[current_user, current_action_id, director_confirmed, confirmed_amount, director_comment, sale_date, sale_manager, sale_client, sale_comment, sale_rows_df], outputs=[sale_status, action_list, sale_kpi_html])

    premium_save_btn.click(save_premium_ui, inputs=[current_user, current_action_id, director_confirmed, confirmed_amount, director_comment, premium_date, premium_manager, premium_comment], outputs=[premium_status, action_list, premium_kpi_html, premium_sales_df, premium_demos_df])

    product_template_btn.click(create_product_template, outputs=[product_template_file])
    product_upload_btn.click(upload_products_from_file, inputs=[current_user, product_upload], outputs=[products_status, products_df])
    product_save_btn.click(save_products_ui, inputs=[current_user, products_df], outputs=[products_status, products_df])

    settings_save_btn.click(save_settings_ui, inputs=[current_user, vat_pct, bonus_pct, max_ded_pct, company_support_vat, payroll_pct, diesel_l, font_family, criteria_settings_df, expense_settings_df, ui_settings_df], outputs=[settings_status])
    export_json_btn.click(export_json_ui, outputs=[export_json_file])
    import_json_btn.click(import_json_ui, inputs=[current_user, import_json_file], outputs=[json_status])
    export_xlsx_btn.click(export_excel_ui, outputs=[export_xlsx_file])

    def update_permissions(user):
        director = is_director(user)
        # 13 components become editable for director, 1 settings button becomes visible, products grid becomes editable, product upload/save buttons become visible.
        return ([gr.update(interactive=director)] * 13
                + [gr.update(visible=director)]
                + [gr.update(interactive=director)]
                + [gr.update(visible=director), gr.update(visible=director)])

    permission_outputs = [
        director_confirmed, confirmed_amount, director_comment,
        vat_pct, bonus_pct, max_ded_pct, company_support_vat, payroll_pct, diesel_l, font_family,
        criteria_settings_df, expense_settings_df, ui_settings_df,
        settings_save_btn,
        products_df, product_upload_btn, product_save_btn,
    ]
    current_user.change(update_permissions, inputs=[current_user], outputs=permission_outputs)


if __name__ == "__main__":
    app.launch(**LAUNCH_KWARGS)
