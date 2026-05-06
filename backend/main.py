import io
import json
import math
import os
import traceback
import uuid
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import psycopg2
from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from psycopg2.extras import Json, RealDictCursor, execute_values

BASE_DIR = Path(__file__).resolve().parent
JSON_BACKUP_PATH = os.getenv("DEMO_CALC_JSON_BACKUP_PATH", str(BASE_DIR / "state_backup.json"))

DB_HOST = os.getenv("DEMO_CALC_DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DEMO_CALC_DB_PORT", "5464"))
DB_NAME = os.getenv("DEMO_CALC_DB_NAME", "demo_calc")
DB_USER = os.getenv("DEMO_CALC_DB_USER", "admin")
DB_PASSWORD = os.getenv("DEMO_CALC_DB_PASSWORD", "")
AUTO_SEED_EMPTY_DATABASE = os.getenv(
    "DEMO_CALC_AUTO_SEED_EMPTY_DB",
    os.getenv("DEMO_CALC_AUTO_SEED_EMPTY_DATABASE", "0"),
) == "1"
USE_POSTGRES = True

ACTION_DEMO = "Проведенная демонстрация"
ACTION_SALE = "Проданное оборудование"
ACTION_PREMIUM = "Выплата премии"
SHORT_TYPE = {ACTION_DEMO: "Демонстрация", ACTION_SALE: "Продажа", ACTION_PREMIUM: "Премия"}
DEFAULT_OFFICE_CITIES = ["Казань", "Москва"]

DEFAULT_USERS = {
    "artur": {"login": "artur", "password": "123", "role": "director", "name": "Артур Гимадеев", "office_city": "Казань"},
    "ruslan": {"login": "ruslan", "password": "111", "role": "manager", "name": "Абдулин Руслан", "office_city": "Казань"},
    "natalia": {"login": "natalia", "password": "222", "role": "manager", "name": "Денисова Наталья", "office_city": "Казань"},
}

MONTHS_RU = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
    7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря",
}

with open(BASE_DIR / "default_criteria.json", "r", encoding="utf-8") as f:
    DEFAULT_CRITERIA = json.load(f)
with open(BASE_DIR / "default_expense_settings.json", "r", encoding="utf-8") as f:
    DEFAULT_EXPENSE_SETTINGS = json.load(f)
with open(BASE_DIR / "default_products.json", "r", encoding="utf-8") as f:
    DEFAULT_PRODUCTS = json.load(f)

SCHEMA_SQL = r"""
CREATE TABLE IF NOT EXISTS app_users (
    login TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('director','manager')),
    name TEXT NOT NULL,
    office_city TEXT NOT NULL DEFAULT 'Казань',
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
    row_order INTEGER NOT NULL DEFAULT 0,
    sku TEXT NOT NULL,
    name TEXT NOT NULL,
    price_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    price_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    city_params JSONB NOT NULL DEFAULT '{}'::jsonb,
    comment TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS actions (
    action_id TEXT PRIMARY KEY,
    action_type TEXT NOT NULL CHECK (action_type IN ('Проведенная демонстрация','Проданное оборудование','Выплата премии')),
    manager_login TEXT NOT NULL REFERENCES app_users(login),
    sequence_no INTEGER NOT NULL,
    action_date DATE NOT NULL,
    client TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    model TEXT NOT NULL DEFAULT '',
    task_description TEXT NOT NULL DEFAULT '',
    comment TEXT NOT NULL DEFAULT '',
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
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
    row_code TEXT NOT NULL DEFAULT '',
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
    pr0_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    price_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    price_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    qty NUMERIC(14,4) NOT NULL DEFAULT 1,
    total_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    total_net NUMERIC(14,2) NOT NULL DEFAULT 0,
    vat_sum NUMERIC(14,2) NOT NULL DEFAULT 0,
    mr_unit NUMERIC(14,2) NOT NULL DEFAULT 0,
    pr_unit NUMERIC(14,2) NOT NULL DEFAULT 0,
    st_pct NUMERIC(8,6) NOT NULL DEFAULT 0,
    cash_net NUMERIC(14,2) NOT NULL DEFAULT 0
);
CREATE OR REPLACE VIEW v_actions_with_lock AS
SELECT
    a.*,
    EXISTS (
        SELECT 1
        FROM actions p
        WHERE p.manager_login = a.manager_login
          AND p.action_type = 'Выплата премии'
          AND p.is_director_confirmed = TRUE
          AND p.sequence_no >= a.sequence_no
    ) AS is_locked
FROM actions a;
"""

MIGRATION_SQL = [
    "ALTER TABLE app_users ADD COLUMN IF NOT EXISTS office_city TEXT NOT NULL DEFAULT 'Казань'",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS row_order INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS city_params JSONB NOT NULL DEFAULT '{}'::jsonb",
    "ALTER TABLE actions ADD COLUMN IF NOT EXISTS payload JSONB NOT NULL DEFAULT '{}'::jsonb",
    "ALTER TABLE demo_expenses ADD COLUMN IF NOT EXISTS row_code TEXT NOT NULL DEFAULT ''",
    "ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS pr0_vat NUMERIC(14,2) NOT NULL DEFAULT 0",
    "ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS mr_unit NUMERIC(14,2) NOT NULL DEFAULT 0",
    "ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS pr_unit NUMERIC(14,2) NOT NULL DEFAULT 0",
    "ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS st_pct NUMERIC(8,6) NOT NULL DEFAULT 0",
    "ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS cash_net NUMERIC(14,2) NOT NULL DEFAULT 0",
]


def db_connect():
    if not DB_PASSWORD:
        raise RuntimeError("Переменная DEMO_CALC_DB_PASSWORD не задана.")
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)


def ensure_schema() -> Tuple[bool, str]:
    if not USE_POSTGRES:
        return False, "PostgreSQL отключен."
    try:
        conn = db_connect()
        conn.autocommit = True
        with conn.cursor() as cur:
            schema_statements = [s.strip() for s in SCHEMA_SQL.split(";") if s.strip()]
            view_statements = [s for s in schema_statements if s.upper().startswith("CREATE OR REPLACE VIEW V_ACTIONS_WITH_LOCK")]
            table_statements = [s for s in schema_statements if s not in view_statements]
            cur.execute("DROP VIEW IF EXISTS v_actions_with_lock")
            for stmt in table_statements:
                cur.execute(stmt)
            for stmt in MIGRATION_SQL:
                cur.execute(stmt)
            for stmt in view_statements:
                cur.execute(stmt)
        conn.close()
        return True, "OK"
    except Exception as e:
        return False, str(e)


# ==============================
# Helpers
# ==============================

def today_str() -> str:
    return date.today().isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        if isinstance(value, float) and math.isnan(value):
            return default
        text = str(value).replace("\xa0", " ").replace("руб.", "").replace("₽", "").replace("%", "").strip()
        text = text.replace(" ", "").replace(",", ".")
        if text == "":
            return default
        return float(text)
    except Exception:
        return default


def pct_to_decimal(value: Any, default: float = 0.0) -> float:
    v = to_float(value, default)
    return v / 100.0 if v > 1.0 else v


def decimal_to_pct(value: Any) -> float:
    return round(to_float(value, 0.0) * 100, 4)


def safe_date(text: Any, default: Optional[str] = None) -> str:
    default = default or today_str()
    try:
        return datetime.fromisoformat(str(text)[:10]).date().isoformat()
    except Exception:
        return default


def date_obj(text: Any):
    try:
        return datetime.fromisoformat(str(text)[:10]).date()
    except Exception:
        return date.min


def ru_date(text: Any) -> str:
    d = date_obj(text)
    if d == date.min:
        d = date.today()
    return f"{d.day:02d} {MONTHS_RU.get(d.month, '')} {d.year} г."


def money0(value: Any) -> str:
    return f"{to_float(value):,.0f} руб.".replace(",", " ")


def clean_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): clean_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_json(v) for v in obj]
    if isinstance(obj, tuple):
        return [clean_json(v) for v in obj]
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    try:
        if pd.isna(obj):
            return None
    except Exception:
        pass
    return obj


def office_names(settings: Dict[str, Any]) -> List[str]:
    raw = settings.get("office_cities") or DEFAULT_OFFICE_CITIES
    names = []
    for item in raw:
        name = str(item.get("name") if isinstance(item, dict) else item).strip()
        if name and name not in names:
            names.append(name)
    return names or DEFAULT_OFFICE_CITIES[:]


def default_office_rates() -> Dict[str, Dict[str, float]]:
    # Три административные ставки из Excel-калькулятора зависят от офиса менеджера.
    # Для Москвы значения взяты из примера «Москва 300 км»: 20 / 6000 / 22000.
    return {
        "Казань": {"driver_km_rate": 15.0, "cryoblaster_rate": 4000.0, "gazelle_rate": 18000.0, "sale_st": 0.565, "latitude": 55.796127, "longitude": 49.106414},
        "Москва": {"driver_km_rate": 20.0, "cryoblaster_rate": 6000.0, "gazelle_rate": 22000.0, "sale_st": 0.465, "latitude": 55.7987966, "longitude": 37.965255},
    }


def default_settings() -> Dict[str, Any]:
    return {
        "vat_rate": 0.22,
        "k1": 0.65,
        "payroll_tax_rate": 0.30,
        "npd_factor": 0.94,
        "driver_avg_speed_kmh": 75.0,
        "diesel_l_per_100km": 15.0,
        "office_cities": deepcopy(DEFAULT_OFFICE_CITIES),
        "office_rates": default_office_rates(),
        "font_family": "Arial",
        "ui": {
            "action_list_width_pct": 31,
            "font_base_px": 13,
            "font_title_px": 18,
            "card_padding_px": 10,
            "field_gap_px": 8,
            "table_row_height_px": 30,
            "criteria_name_width_pct": 20,
            "criteria_levels_width_pct": 60,
            "criteria_comment_width_pct": 20,
            "geo_api_key": "",
        },
        "criteria": deepcopy(DEFAULT_CRITERIA),
        "expense_settings": deepcopy(DEFAULT_EXPENSE_SETTINGS),
    }


def merge_settings(settings: Any) -> Dict[str, Any]:
    base = default_settings()
    legacy_upgrade = False
    if not isinstance(settings, dict):
        return base
    deprecated_keys = {"company" + "_support_vat", "bonus" + "_rate", "max_demo" + "_deduction_pct", "driver_prep_hours"}
    for k, v in settings.items():
        if k in deprecated_keys:
            legacy_upgrade = True
            continue
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k].update(clean_json(v))
        else:
            base[k] = clean_json(v)

    default_criterion_codes = {c["code"] for c in DEFAULT_CRITERIA}
    current_criterion_codes = {str(c.get("code")) for c in base.get("criteria", []) if isinstance(c, dict)}
    if not base.get("criteria") or current_criterion_codes != default_criterion_codes:
        base["criteria"] = deepcopy(DEFAULT_CRITERIA)
        legacy_upgrade = True

    default_expense_codes = {e["code"] for e in DEFAULT_EXPENSE_SETTINGS}
    current_expense_codes = {str(e.get("code")) for e in base.get("expense_settings", []) if isinstance(e, dict) and e.get("code")}
    if not base.get("expense_settings") or current_expense_codes != default_expense_codes:
        base["expense_settings"] = deepcopy(DEFAULT_EXPENSE_SETTINGS)
        legacy_upgrade = True

    for row in base.get("expense_settings", []):
        row.setdefault("code", str(row.get("article", "")))
        row.setdefault("section", "other")
        row.setdefault("qty_manager", True)
        row.setdefault("price_manager", True)

    names = office_names(base)
    default_rates = default_office_rates()
    if legacy_upgrade:
        # Старые выгрузки хранили не те значения для Excel-ставок и Газель как ставку за км.
        base["office_rates"] = deepcopy(default_rates)
        base["diesel_l_per_100km"] = 15.0
    rates = base.setdefault("office_rates", {})
    for name in names:
        rates.setdefault(name, deepcopy(default_rates.get(name, {"driver_km_rate": 15, "cryoblaster_rate": 4000, "gazelle_rate": 18000, "sale_st": 0.50, "latitude": 0.0, "longitude": 0.0})))
        rates[name].setdefault("driver_km_rate", default_rates.get(name, {}).get("driver_km_rate", 15.0))
        rates[name].setdefault("cryoblaster_rate", default_rates.get(name, {}).get("cryoblaster_rate", 4000.0))
        rates[name].setdefault("gazelle_rate", default_rates.get(name, {}).get("gazelle_rate", 18000.0))
        rates[name].setdefault("sale_st", default_rates.get(name, {}).get("sale_st", 0.50))
        rates[name].setdefault("latitude", default_rates.get(name, {}).get("latitude", 0.0))
        rates[name].setdefault("longitude", default_rates.get(name, {}).get("longitude", 0.0))
        if to_float(rates[name].get("gazelle_rate"), 0) < 1000:
            rates[name]["gazelle_rate"] = default_rates.get(name, {}).get("gazelle_rate", 18000.0)
    base.setdefault("npd_factor", 0.94)
    base.setdefault("driver_avg_speed_kmh", 75.0)
    base.setdefault("diesel_l_per_100km", 15.0)
    base.setdefault("ui", {}).setdefault("geo_api_key", "")
    base["font_family"] = "Arial"
    return base


def default_products() -> List[Dict[str, Any]]:
    return deepcopy(DEFAULT_PRODUCTS)


def normalize_users(users: Any) -> List[Dict[str, Any]]:
    if isinstance(users, dict):
        iterable = users.values()
    elif isinstance(users, list):
        iterable = users
    else:
        iterable = DEFAULT_USERS.values()
    out = []
    seen = set()
    for u in iterable:
        login = str(u.get("login") or "").strip().lower()
        if not login or login in seen:
            continue
        role = str(u.get("role") or "manager")
        if role not in {"director", "manager"}:
            role = "manager"
        out.append({
            "login": login,
            "password": str(u.get("password") or ""),
            "role": role,
            "name": str(u.get("name") or login),
            "office_city": str(u.get("office_city") or "Казань"),
            "is_active": bool(u.get("is_active", True)),
        })
        seen.add(login)
    return out or normalize_users(DEFAULT_USERS)


def users_map(state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {u["login"]: u for u in normalize_users(state.get("users"))}


def user_public(u: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in u.items() if k != "password"}


def manager_logins(state: Dict[str, Any]) -> List[str]:
    return [u["login"] for u in normalize_users(state.get("users")) if u.get("role") == "manager" and u.get("is_active", True)]


def manager_office_city(state: Dict[str, Any], login: str) -> str:
    u = users_map(state).get(str(login or "").lower())
    city = (u or {}).get("office_city") or "Казань"
    names = office_names(state.get("settings", default_settings()))
    return city if city in names else names[0]


def office_rate(settings: Dict[str, Any], city: str, key: str, default: float = 0.0) -> float:
    rates = settings.get("office_rates") or {}
    city_rates = rates.get(city) or rates.get(office_names(settings)[0]) or {}
    return to_float(city_rates.get(key), default)


def default_office_params(price_net: float, settings: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    params = {}
    for city in office_names(settings):
        params[city] = {
            "mr": round(price_net * 0.20, 2),
            "pr": round(price_net * 0.10, 2),
            "st": round(office_rate(settings, city, "sale_st", 0.50), 6),
        }
    return params


def normalize_product(product: Dict[str, Any], settings: Optional[Dict[str, Any]] = None, row_order: Optional[int] = None) -> Dict[str, Any]:
    settings = settings or default_settings()
    vat = to_float(settings.get("vat_rate"), 0.22)
    product_id = str(product.get("product_id") or product.get("ID товара") or product.get("sku") or product.get("Артикул") or new_id("PRD"))
    sku = str(product.get("sku") or product.get("Артикул") or product_id)
    name = str(product.get("name") or product.get("Наименование") or product.get("Наименование ТМЦ") or product.get("Наименование оборудования") or "")
    price_vat = to_float(product.get("price_vat", product.get("Цена с НДС (прайс) [PR0]", product.get("Цена руб. с НДС"))), 0)
    price_net = to_float(product.get("price_net", product.get("Цена без НДС (прайс)", product.get("Цена руб. без НДС"))), 0)
    if price_net <= 0 and price_vat > 0:
        price_net = price_vat / (1 + vat)
    if price_vat <= 0 and price_net > 0:
        price_vat = price_net * (1 + vat)
    city_params = product.get("office_params") or product.get("city_params") or {}
    if isinstance(city_params, str):
        try:
            city_params = json.loads(city_params)
        except Exception:
            city_params = {}
    defaults = default_office_params(price_net, settings)
    norm_params: Dict[str, Dict[str, float]] = {}
    for city in office_names(settings):
        raw = city_params.get(city, {}) if isinstance(city_params, dict) else {}
        # Excel import supports both «Казань_MR» and exact Russian names.
        mr = to_float(raw.get("mr", product.get(f"{city}_MR", product.get(f"{city} MR"))), defaults[city]["mr"])
        pr = to_float(raw.get("pr", product.get(f"{city}_PR", product.get(f"{city} PR"))), defaults[city]["pr"])
        st = pct_to_decimal(raw.get("st", product.get(f"{city}_ST", product.get(f"{city} ST"))), defaults[city]["st"])
        norm_params[city] = {"mr": round(mr, 2), "pr": round(pr, 2), "st": round(st, 6)}
    return {
        "product_id": product_id,
        "sku": sku,
        "name": name,
        "price_vat": round(price_vat, 2),
        "price_net": round(price_net, 2),
        "row_order": int(to_float(product.get("row_order"), row_order or 0)),
        "office_params": norm_params,
        "city_params": norm_params,
        "comment": str(product.get("comment", product.get("Комментарий", ""))),
    }


def product_lookup(products: List[Dict[str, Any]], settings: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    lookup = {}
    for i, p in enumerate(products or [], start=1):
        n = normalize_product(p, settings, i)
        for key in [n["product_id"], n["sku"], n["name"]]:
            if key:
                lookup[str(key).strip().lower()] = n
    return lookup


def sorted_products(products: List[Dict[str, Any]], settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    normalized = [normalize_product(p, settings, i) for i, p in enumerate(products or [], start=1)]
    for i, p in enumerate(normalized, start=1):
        if not p.get("row_order"):
            p["row_order"] = i
    return sorted(normalized, key=lambda p: (int(p.get("row_order") or 0), p.get("sku", "")))


def search_products(query: str, products: List[Dict[str, Any]], settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    q = str(query or "").strip().lower()
    if len(q) < 3:
        return []
    out = []
    for p in sorted_products(products, settings):
        hay = f"{p['product_id']} {p['sku']} {p['name']}".lower()
        if q in hay:
            out.append({"product_id": p["product_id"], "sku": p["sku"], "name": p["name"]})
    return out[:20]


def product_params_for_city(product: Dict[str, Any], city: str, settings: Dict[str, Any]) -> Dict[str, float]:
    p = normalize_product(product, settings)
    params = p.get("office_params") or {}
    if city not in params:
        city = office_names(settings)[0]
    raw = params.get(city, {})
    return {
        "mr": to_float(raw.get("mr"), p["price_net"] * 0.20),
        "pr": to_float(raw.get("pr"), p["price_net"] * 0.10),
        "st": pct_to_decimal(raw.get("st"), office_rate(settings, city, "sale_st", 0.50)),
    }


def create_sale_row_from_product(product: Dict[str, Any], qty: float, settings: Dict[str, Any], office_city: str, sale_price_vat: Optional[float] = None) -> Dict[str, Any]:
    p = normalize_product(product, settings)
    params = product_params_for_city(p, office_city, settings)
    qty = max(0.0, to_float(qty, 1.0))
    pr0 = to_float(p.get("price_vat"), 0)
    sale_price_vat = to_float(sale_price_vat, pr0)
    mr = max(0.0, to_float(params.get("mr"), 0))
    st = pct_to_decimal(params.get("st"), 0)
    pr_limit = to_float(params.get("pr"), 0)
    price_net = sale_price_vat / (1 + to_float(settings.get("vat_rate"), 0.22)) if sale_price_vat else 0
    discount = max(0.0, pr0 - sale_price_vat)
    # По формуле из задания: CASH = (1 - ([PR0]-[PR])/[MR]) × [ST] × [MR].
    # Здесь [PR] в строке продажи трактуется как фактическая цена продажи с НДС.
    if mr > 0:
        cash_unit = (1 - discount / mr) * st * mr
    else:
        cash_unit = 0
    cash_unit = max(0.0, cash_unit)
    total_vat = sale_price_vat * qty
    total_net = price_net * qty
    cash_net = cash_unit * qty
    return {
        "product_id": p["product_id"],
        "sku": p["sku"],
        "name": p["name"],
        "pr0_vat": round(pr0, 2),
        "price_vat": round(sale_price_vat, 2),
        "price_net": round(price_net, 2),
        "qty": qty,
        "total_vat": round(total_vat, 2),
        "total_net": round(total_net, 2),
        "vat_sum": round(total_vat - total_net, 2),
        "mr_unit": round(mr, 2),
        "pr_unit": round(pr_limit, 2),
        "st_pct": round(st, 6),
        "cash_net": round(cash_net, 2),
    }


def sale_rows_to_records(action: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    settings = state["settings"]
    lookup = product_lookup(state.get("products", []), settings)
    office_city = manager_office_city(state, action.get("manager_login"))
    out = []
    for r in action.get("rows", []) or []:
        keys = [str(r.get("product_id", "")).strip().lower(), str(r.get("sku", "")).strip().lower()]
        found = next((lookup[k] for k in keys if k and k in lookup), None)
        if not found:
            continue
        qty = to_float(r.get("qty"), 1)
        sale_price_vat = to_float(r.get("price_vat"), found["price_vat"])
        out.append(create_sale_row_from_product(found, qty, settings, office_city, sale_price_vat))
    return out


def calculate_sale(action: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    rows = sale_rows_to_records(action, state)
    cash_all = sum(to_float(r.get("cash_net")) for r in rows)
    total_vat = sum(to_float(r.get("total_vat")) for r in rows)
    return {"rows": rows, "cash_all": round(cash_all, 2), "total_vat": round(total_vat, 2)}


def expense_settings_map(settings: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {str(s.get("code") or s.get("article")): s for s in settings.get("expense_settings", DEFAULT_EXPENSE_SETTINGS)}


def expense_key(row: Dict[str, Any], fallback_order: int = 0) -> str:
    return str(row.get("code") or row.get("row_code") or f"{row.get('article', '')}::{row.get('unit', '')}::{fallback_order}")


def get_demo_meta(action: Dict[str, Any]) -> Dict[str, Any]:
    meta = deepcopy(action.get("demo_meta") or {})
    payload = action.get("payload") or {}
    if isinstance(payload, dict):
        meta.update(payload.get("demo_meta") or {})
    meta.setdefault("demo_hours", 2.0)
    meta.setdefault("driver_prep_hours", 2.0)
    return meta


def base_amount_net_for_row(qty: float, price_net: float, price_vat: float, vat: float, calc_type: str, settings: Optional[Dict[str, Any]] = None) -> Tuple[float, float, float, float]:
    settings = settings or default_settings()
    npd = max(0.01, to_float(settings.get("npd_factor"), 0.94))
    amount_net = 0.0
    amount_vat = 0.0

    if calc_type in {"npd_direct", "office_driver_km", "demo_work_total", "office_cryoblaster"}:
        price_vat = 0
        amount_net = qty * price_net / npd
        amount_vat = amount_net * (1 + vat)
    elif calc_type == "npd_cash_input":
        price_net = qty
        price_vat = 0
        amount_net = price_net / npd
        amount_vat = amount_net * (1 + vat)
    elif calc_type == "cash_amount_vat":
        price_vat = qty
        price_net = price_vat / (1 + vat) if price_vat else 0
        amount_net = price_net
        amount_vat = price_vat
    elif calc_type in {"direct_vat_price", "diesel"}:
        if price_vat <= 0 and price_net > 0:
            price_vat = price_net * (1 + vat)
        if price_net <= 0 and price_vat > 0:
            price_net = price_vat / (1 + vat)
        amount_net = qty * price_net
        amount_vat = qty * price_vat
    else:
        if price_net <= 0 and price_vat > 0:
            price_net = price_vat / (1 + vat)
        if price_vat <= 0 and price_net > 0:
            price_vat = price_net * (1 + vat)
        amount_net = qty * price_net
        amount_vat = qty * price_vat
    return price_net, price_vat, amount_net, amount_vat


def normalize_demo_rows(action: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    settings = state["settings"]
    vat = to_float(settings.get("vat_rate"), 0.22)
    office_city = manager_office_city(state, action.get("manager_login"))
    existing = action.get("expenses", []) or []
    existing_by_code = {expense_key(r, i): r for i, r in enumerate(existing, start=1)}
    existing_by_article_unit = {(str(r.get("article", "")), str(r.get("unit", ""))): r for r in existing}
    rows: List[Dict[str, Any]] = []
    meta = get_demo_meta(action)
    demo_hours = to_float(meta.get("demo_hours"), 2.0)
    if demo_hours <= 0:
        demo_hours = 2.0
    prep_hours = to_float(meta.get("driver_prep_hours"), 2.0)
    if prep_hours < 0:
        prep_hours = 0.0

    # Kilometers are needed by several Excel formulas.
    default_km = 300.0
    for r in existing:
        if str(r.get("calc_type")) == "office_driver_km" or str(r.get("article")) == "Работа водителя за километраж по маячку А5/А6":
            default_km = to_float(r.get("qty"), default_km)
            break

    for i, s in enumerate(settings.get("expense_settings", DEFAULT_EXPENSE_SETTINGS), start=1):
        code = str(s.get("code") or f"expense_{i}")
        article = s.get("article", "")
        unit = str(s.get("unit", ""))
        old = existing_by_code.get(code) or existing_by_article_unit.get((str(article), unit), {})
        calc_type = s.get("calc_type", "direct")
        qty = to_float(old.get("qty"), s.get("qty_default", 0))
        price_net = to_float(old.get("price_net"), s.get("price_net_default", 0) or 0)
        price_vat = to_float(old.get("price_vat"), s.get("price_vat_default", 0) or 0)
        if not bool(s.get("qty_manager", True)):
            qty = to_float(s.get("qty_default"), qty)
        if not bool(s.get("price_manager", True)):
            price_net = to_float(s.get("price_net_default"), price_net)
            price_vat = to_float(s.get("price_vat_default"), price_vat)

        if calc_type == "office_driver_km":
            price_net = office_rate(settings, office_city, "driver_km_rate", price_net or 15)
            price_vat = 0
            default_km = qty
        elif calc_type == "demo_work_total":
            qty = prep_hours + demo_hours
            if price_net <= 0:
                price_net = 1350
            price_vat = 0
        elif calc_type == "npd_cash_input":
            price_net = qty
            price_vat = 0
        elif calc_type == "office_cryoblaster":
            price_net = office_rate(settings, office_city, "cryoblaster_rate", price_net or 4000)
            price_vat = 0
        elif calc_type == "diesel":
            qty = default_km / 100.0 * to_float(settings.get("diesel_l_per_100km"), 15.0)
            if price_vat <= 0:
                price_vat = to_float(s.get("price_vat_default"), 72)
            price_net = price_vat / (1 + vat) if price_vat else 0
        elif calc_type == "office_gazelle_amort_total":
            qty = to_float(s.get("qty_default"), 1) or 1
            price_net = office_rate(settings, office_city, "gazelle_rate", price_net or 18000)
            price_vat = price_net * (1 + vat)

        price_net, price_vat, amount_net, amount_vat = base_amount_net_for_row(qty, price_net, price_vat, vat, calc_type, settings)
        rows.append({
            "row_order": i,
            "code": code,
            "row_code": code,
            "article": article,
            "section": s.get("section", "other"),
            "qty": round(to_float(qty), 4),
            "unit": unit,
            "price_net": round(price_net, 2),
            "price_vat": round(price_vat, 2),
            "amount_net": round(amount_net, 2),
            "amount_vat": round(amount_vat, 2),
            "calc_type": calc_type,
            "is_custom": False,
            "comment": s.get("comment", ""),
            "qty_manager": bool(s.get("qty_manager", True)),
            "price_manager": bool(s.get("price_manager", True)),
        })
    return rows


def default_expense_rows(state: Dict[str, Any], manager_login: Optional[str] = None) -> List[Dict[str, Any]]:
    action = {"manager_login": manager_login or manager_logins(state)[0] if manager_logins(state) else "ruslan", "expenses": [], "demo_meta": {"demo_hours": 2, "driver_prep_hours": 2}}
    return normalize_demo_rows(action, state)


def calculate_criteria_coeffs(action: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
    criteria_state = action.get("criteria", {}) or {}
    block_data = {"P": {"score": 0.0, "max": 0.0}, "R": {"score": 0.0, "max": 0.0}, "M": {"score": 0.0, "max": 0.0}}
    for cr in settings.get("criteria", DEFAULT_CRITERIA):
        block = cr.get("block") or "P"
        levels = cr.get("levels", []) or []
        if block not in block_data or not levels:
            continue
        item = criteria_state.get(cr["code"], {})
        idx = int(to_float(item.get("level_index"), 0))
        idx = max(0, min(idx, len(levels) - 1))
        scores = [to_float(l[1], 0) for l in levels]
        block_data[block]["score"] += scores[idx]
        block_data[block]["max"] += max(scores) if scores else 0
    result: Dict[str, Any] = {}
    for block in ["P", "R", "M"]:
        score = block_data[block]["score"]
        max_score = block_data[block]["max"] or 1
        # xP/xR/xM are block efficiency coefficients from the Excel sheets: score / max score.
        efficiency = min(1.0, max(0.0, score / max_score))
        result[block] = round(score, 2)
        result[f"{block}_max"] = round(max_score, 2)
        result[f"x{block}"] = round(efficiency, 6)
    result["K2"] = round(result["xP"] * result["xR"] * result["xM"], 6)
    return result


def calculate_demo(action: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    settings = state["settings"]
    vat = to_float(settings.get("vat_rate"), 0.22)
    expenses = normalize_demo_rows(action, state)
    total_vat = sum(to_float(r.get("amount_vat")) for r in expenses)
    demo_cost = total_vat / (1 + vat)
    coeffs = calculate_criteria_coeffs(action, settings)
    k1 = to_float(settings.get("k1"), 0.65)
    vic = demo_cost * coeffs["K2"] * k1
    by_section = {
        "driver": sum(to_float(r.get("amount_vat")) for r in expenses if r.get("section") == "driver"),
        "other": sum(to_float(r.get("amount_vat")) for r in expenses if r.get("section") != "driver"),
    }
    by_code = {expense_key(r, i): r for i, r in enumerate(expenses, start=1)}
    km = to_float(by_code.get("d_driver_km", {}).get("qty"), 0)
    meta = get_demo_meta(action)
    demo_hours = to_float(meta.get("demo_hours"), 2)
    prep_hours = to_float(meta.get("driver_prep_hours"), 2)
    avg_speed = max(1.0, to_float(settings.get("driver_avg_speed_kmh"), 75))
    road_hours = km / avg_speed
    shift_hours = road_hours + prep_hours + demo_hours
    npd_invoice = sum(to_float(r.get("amount_net")) for r in expenses if r.get("section") == "driver")
    reward_net = npd_invoice * max(0.01, to_float(settings.get("npd_factor"), 0.94))
    driver_rate = reward_net / shift_hours if shift_hours else 0
    demo_count = to_float(by_code.get("d_cryoblaster", {}).get("qty"), 0)
    settlement = [
        {"name": "Время в дороге при средней скорости 75 км/ч (туда-обратно)", "value": round(road_hours, 2), "unit": "ч", "formula": "Кругорейс / 75"},
        {"name": "Время на мед. и тех. осмотр, подписание актов, забор льда", "value": round(prep_hours, 2), "unit": "ч", "formula": "Поле над вкладками"},
        {"name": "Время работы демонстратором", "value": round(demo_hours, 2), "unit": "ч", "formula": "Поле над вкладками"},
        {"name": "Общее время трудовой смены", "value": round(shift_hours, 2), "unit": "ч", "formula": "Сумма трех строк выше"},
        {"name": "Расчетная ставка для водителя-демонстратора", "value": round(driver_rate, 2), "unit": "руб./ч", "formula": "Вознаграждение NET / смена"},
        {"name": "Вознаграждение водителя NET за смену, руб.", "value": round(reward_net, 2), "unit": "руб.", "formula": "Сумма НПД × 0.94"},
        {"name": "Сумма для счета НПД за смену", "value": round(npd_invoice, 2), "unit": "руб.", "formula": "Сумма затрат Части 1 без НДС"},
        {"name": "Эквивалент зарплаты в месяц (21 смена) NET, руб.", "value": round(reward_net * 21, 2), "unit": "руб.", "formula": "Вознаграждение × 21"},
        {"name": "Эквивалент зарплаты в месяц (30 смен) NET, руб.", "value": round(reward_net * 30, 2), "unit": "руб.", "formula": "Вознаграждение × 30"},
    ]
    settlement_summary = [
        {"name": "Кругорейс, км", "value": round(km, 2), "unit": "км"},
        {"name": "Кол-во демо по 3 часа на месте", "value": round(demo_count, 2), "unit": "усл"},
        {"name": "Длительность смены водителя, часы", "value": round(shift_hours, 2), "unit": "ч"},
        {"name": "Вознаграждение водителя NET за смену, руб.", "value": round(reward_net, 2), "unit": "руб."},
    ]
    return {
        "expenses": expenses,
        "driver_settlement": settlement,
        "driver_settlement_summary": settlement_summary,
        "total_vat": round(total_vat, 2),
        "demo_cost_net": round(demo_cost, 2),
        "cost_net": round(demo_cost, 2),
        "section_driver_vat": round(by_section["driver"], 2),
        "section_other_vat": round(by_section["other"], 2),
        "K1": round(k1, 6),
        "K2": coeffs["K2"],
        "xP": coeffs["xP"],
        "xR": coeffs["xR"],
        "xM": coeffs["xM"],
        "P": coeffs["P"],
        "R": coeffs["R"],
        "M": coeffs["M"],
        "P_max": coeffs["P_max"],
        "R_max": coeffs["R_max"],
        "M_max": coeffs["M_max"],
        "VIC": round(vic, 2),
        "deduction_net": round(vic, 2),
    }


def last_confirmed_premium_seq(manager_login: str, state: Dict[str, Any], before_seq: Optional[int] = None) -> Optional[int]:
    seqs = []
    for a in state.get("actions", []):
        if a.get("manager_login") == manager_login and a.get("type") == ACTION_PREMIUM and a.get("is_director_confirmed"):
            s = int(a.get("sequence_no", 0))
            if before_seq is None or s < before_seq:
                seqs.append(s)
    return max(seqs) if seqs else None


def is_action_locked(action: Dict[str, Any], state: Dict[str, Any]) -> bool:
    seq = int(action.get("sequence_no", 0))
    manager = action.get("manager_login")
    return any(
        a.get("manager_login") == manager and a.get("type") == ACTION_PREMIUM and a.get("is_director_confirmed") and int(a.get("sequence_no", 0)) >= seq
        for a in state.get("actions", [])
    )


def period_actions_for_premium(action: Dict[str, Any], state: Dict[str, Any]) -> List[Dict[str, Any]]:
    manager = action.get("manager_login")
    seq = int(action.get("sequence_no", 0))
    prev = last_confirmed_premium_seq(manager, state, before_seq=seq)
    start = prev if prev is not None else -10**9
    return [a for a in state.get("actions", []) if a.get("manager_login") == manager and int(a.get("sequence_no", 0)) > start and int(a.get("sequence_no", 0)) <= seq]


def can_confirm_premium(action: Dict[str, Any], state: Dict[str, Any]):
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


def calculate_premium(action: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    period = period_actions_for_premium(action, state)
    ok, warning = can_confirm_premium(action, state)
    sales = [a for a in period if a.get("type") == ACTION_SALE]
    demos = [a for a in period if a.get("type") == ACTION_DEMO]
    sales_sum = 0.0
    demo_sum = 0.0
    sale_rows = []
    demo_rows = []
    for s in sales:
        calc = calculate_sale(s, state)
        amount = to_float(s.get("confirmed_amount"), calc["cash_all"]) if s.get("is_director_confirmed") else 0.0
        sales_sum += amount
        sale_rows.append({
            "action_id": s["id"],
            "Дата": s.get("date"),
            "Клиент": s.get("client"),
            "Премия расчетная [CASH_ALL], руб.": round(calc["cash_all"], 2),
            "Подтвержденная премия от продаж [CASH_ALL_CONFIRM], руб.": round(amount, 2),
        })
    for d in demos:
        calc = calculate_demo(d, state)
        amount = to_float(d.get("confirmed_amount"), calc["VIC"]) if d.get("is_director_confirmed") else 0.0
        demo_sum += amount
        demo_rows.append({
            "action_id": d["id"],
            "Дата": d.get("date"),
            "Клиент": d.get("client"),
            "Вычет расчетный [VIC], руб.": round(calc["VIC"], 2),
            "Подтвержденное уменьшение премии [VIC_CONFIRM], руб.": round(amount, 2),
            "is_director_confirmed": bool(d.get("is_director_confirmed")),
        })
    profit = sales_sum - demo_sum
    return {
        "ok": ok,
        "warning": warning,
        "sales_sum": round(sales_sum, 2),
        "cash_all_confirm": round(sales_sum, 2),
        "demo_sum": round(demo_sum, 2),
        "vic_confirm": round(demo_sum, 2),
        "payout": round(profit, 2),
        "profit": round(profit, 2),
        "sale_rows": sale_rows,
        "demo_rows": demo_rows,
        "period_from_seq": min([int(a.get("sequence_no", 0)) for a in period], default=0),
        "period_to_seq": int(action.get("sequence_no", 0)),
    }


def action_display_amount(action: Dict[str, Any], state: Dict[str, Any]) -> float:
    if action.get("type") == ACTION_DEMO:
        calc = calculate_demo(action, state)
        return to_float(action.get("confirmed_amount"), calc["VIC"])
    if action.get("type") == ACTION_SALE:
        calc = calculate_sale(action, state)
        return to_float(action.get("confirmed_amount"), calc["cash_all"])
    calc = calculate_premium(action, state)
    return to_float(action.get("confirmed_amount"), calc["profit"])


def action_total_vat(action: Dict[str, Any], state: Dict[str, Any]) -> float:
    if action.get("type") == ACTION_DEMO:
        return to_float(calculate_demo(action, state).get("total_vat"))
    if action.get("type") == ACTION_SALE:
        return to_float(calculate_sale(action, state).get("total_vat"))
    return action_display_amount(action, state)


def build_action_summary(action: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    amount = action_display_amount(action, state)
    locked = is_action_locked(action, state)
    display_for_title = action_total_vat(action, state) if action.get("type") in {ACTION_DEMO, ACTION_SALE} else amount
    line = f"{ru_date(action.get('date'))} | {SHORT_TYPE.get(action['type'], action['type'])} | {action.get('client', '')} | {money0(display_for_title)}"
    return {
        "id": action["id"],
        "type": action["type"],
        "sequence_no": int(action.get("sequence_no", 0)),
        "date": safe_date(action.get("date")),
        "client": action.get("client", ""),
        "manager_login": action.get("manager_login"),
        "manager_name": users_map(state).get(action.get("manager_login"), {}).get("name", action.get("manager_login")),
        "office_city": manager_office_city(state, action.get("manager_login")),
        "is_director_confirmed": bool(action.get("is_director_confirmed")),
        "is_locked": locked,
        "display_amount": round(amount, 2),
        "confirmed_amount": round(to_float(action.get("confirmed_amount"), 0), 2) if action.get("confirmed_amount") is not None else None,
        "title_amount": round(display_for_title, 2),
        "line1": line,
        "line2": "",
    }


def visible_actions(user: Dict[str, Any], state: Dict[str, Any], manager_filter: str = "__all__", hide_old: bool = False) -> List[Dict[str, Any]]:
    actions = state.get("actions", [])
    if user["role"] == "director":
        if manager_filter and manager_filter != "__all__":
            actions = [a for a in actions if a.get("manager_login") == manager_filter]
    else:
        actions = [a for a in actions if a.get("manager_login") == user["login"]]
    if hide_old:
        actions = [a for a in actions if not is_action_locked(a, state)]
    actions = sorted(actions, key=lambda a: (a.get("manager_login", ""), int(a.get("sequence_no", 0))))
    return [build_action_summary(a, state) for a in actions]


def next_sequence_no(manager_login: str, state: Dict[str, Any]) -> int:
    seqs = [int(a.get("sequence_no", 0)) for a in state.get("actions", []) if a.get("manager_login") == manager_login]
    return (max(seqs) if seqs else 0) + 10


def mk_criteria(settings: Dict[str, Any], default_idx: int = 1):
    return {cr["code"]: {"level_index": min(default_idx, len(cr.get("levels", [])) - 1), "manager_comment": ""} for cr in settings.get("criteria", [])}


def create_demo_state() -> Dict[str, Any]:
    """Пустое рабочее состояние: директор, два менеджера из Казани, товары и настройки, без действий."""
    settings = default_settings()
    users = normalize_users(DEFAULT_USERS)
    products = [normalize_product(p, settings, i) for i, p in enumerate(default_products(), start=1)]
    return {"settings": settings, "users": users, "products": products, "actions": []}


# ==============================
# Persistence
# ==============================

def load_state_from_db():
    ok, msg = ensure_schema()
    if not ok:
        if Path(JSON_BACKUP_PATH).exists():
            state = json.loads(Path(JSON_BACKUP_PATH).read_text(encoding="utf-8"))
            state["settings"] = merge_settings(state.get("settings"))
            state["users"] = normalize_users(state.get("users", DEFAULT_USERS))
            return state, msg
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

            cur.execute("SELECT login,password,role,name,office_city,is_active FROM app_users ORDER BY role, name")
            users = normalize_users([dict(r) for r in cur.fetchall()])

            cur.execute("SELECT settings FROM app_settings WHERE id=1")
            row = cur.fetchone()
            settings = merge_settings(row["settings"] if row else default_settings())

            cur.execute("SELECT * FROM products ORDER BY row_order, sku")
            products = [normalize_product(dict(r), settings, i) for i, r in enumerate(cur.fetchall(), start=1)]

            cur.execute("SELECT * FROM actions ORDER BY manager_login, sequence_no")
            action_rows = [dict(r) for r in cur.fetchall()]
            state = {"settings": settings, "users": users, "products": products, "actions": []}
            for a in action_rows:
                payload = a.get("payload") or {}
                action = {
                    "id": a["action_id"],
                    "type": a["action_type"],
                    "manager_login": a["manager_login"],
                    "sequence_no": int(a["sequence_no"]),
                    "date": str(a["action_date"]),
                    "client": a.get("client") or "",
                    "city": a.get("city") or "",
                    "model": a.get("model") or "",
                    "task_description": a.get("task_description") or "",
                    "comment": a.get("comment") or "",
                    "payload": payload,
                    "demo_meta": payload.get("demo_meta", {}) if isinstance(payload, dict) else {},
                    "is_director_confirmed": bool(a.get("is_director_confirmed")),
                    "confirmed_amount": float(a["confirmed_amount"]) if a.get("confirmed_amount") is not None else None,
                    "director_comment": a.get("director_comment") or "",
                }
                if action["type"] == ACTION_DEMO:
                    cur.execute("SELECT * FROM demo_expenses WHERE action_id=%s ORDER BY row_order", (action["id"],))
                    action["expenses"] = [clean_json(dict(r)) for r in cur.fetchall()]
                    cur.execute("SELECT * FROM demo_criterion_values WHERE action_id=%s", (action["id"],))
                    criteria = {}
                    for r in cur.fetchall():
                        criteria[r["criterion_code"]] = {"level_index": int(r["level_index"]), "manager_comment": r.get("manager_comment") or ""}
                    action["criteria"] = criteria
                elif action["type"] == ACTION_SALE:
                    cur.execute("SELECT * FROM sale_rows WHERE action_id=%s ORDER BY row_order", (action["id"],))
                    action["rows"] = [clean_json(dict(r)) for r in cur.fetchall()]
                state["actions"].append(action)
        conn.close()
        return state, "OK"
    except Exception as e:
        if Path(JSON_BACKUP_PATH).exists():
            state = json.loads(Path(JSON_BACKUP_PATH).read_text(encoding="utf-8"))
            state["settings"] = merge_settings(state.get("settings"))
            state["users"] = normalize_users(state.get("users", DEFAULT_USERS))
            return state, f"Ошибка БД, загружен JSON backup: {e}"
        return create_demo_state(), f"Ошибка БД: {e}"


def persist_state_to_db(state: Dict[str, Any]) -> str:
    state["settings"] = merge_settings(state.get("settings"))
    state["users"] = normalize_users(state.get("users", DEFAULT_USERS))
    state["products"] = sorted_products(state.get("products", []), state["settings"])
    Path(JSON_BACKUP_PATH).write_text(json.dumps(clean_json(state), ensure_ascii=False, indent=2), encoding="utf-8")
    ok, msg = ensure_schema()
    if not ok:
        return f"База недоступна, сохранен JSON backup: {msg}"
    conn = db_connect()
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("TRUNCATE demo_criterion_values, demo_expenses, sale_rows, actions, products, app_settings, app_users RESTART IDENTITY CASCADE")
            execute_values(cur, "INSERT INTO app_users(login,password,role,name,office_city,is_active) VALUES %s", [
                (u["login"], u["password"], u["role"], u["name"], u.get("office_city", "Казань"), bool(u.get("is_active", True))) for u in state["users"]
            ])
            cur.execute("INSERT INTO app_settings(id, settings) VALUES (1, %s)", (Json(clean_json(state["settings"])),))
            products = [normalize_product(p, state["settings"], i) for i, p in enumerate(state.get("products", []), start=1)]
            execute_values(cur, "INSERT INTO products(product_id,row_order,sku,name,price_vat,price_net,city_params,comment) VALUES %s", [
                (p["product_id"], int(p.get("row_order") or i), p["sku"], p["name"], p["price_vat"], p["price_net"], Json(clean_json(p.get("office_params", {}))), p.get("comment", ""))
                for i, p in enumerate(products, start=1)
            ])
            for a in state.get("actions", []):
                payload = deepcopy(a.get("payload") or {})
                if a.get("type") == ACTION_DEMO:
                    payload["demo_meta"] = get_demo_meta(a)
                cur.execute(
                    """INSERT INTO actions(action_id, action_type, manager_login, sequence_no, action_date, client, city, model, task_description, comment, payload, is_director_confirmed, confirmed_amount, director_comment)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        a["id"], a["type"], a["manager_login"], int(a.get("sequence_no", 0)), safe_date(a.get("date")), a.get("client", ""),
                        a.get("city", ""), a.get("model", ""), a.get("task_description", ""), a.get("comment", ""), Json(clean_json(payload)),
                        bool(a.get("is_director_confirmed")), a.get("confirmed_amount"), a.get("director_comment", ""),
                    ),
                )
                if a["type"] == ACTION_DEMO:
                    expense_rows = []
                    for i, r in enumerate(normalize_demo_rows(a, state), start=1):
                        expense_rows.append((a["id"], i, r.get("code") or r.get("row_code") or f"expense_{i}", r.get("article", ""), to_float(r.get("qty")), r.get("unit", ""), to_float(r.get("price_net")), to_float(r.get("price_vat")), to_float(r.get("amount_vat")), r.get("calc_type", "direct"), False, r.get("comment", "")))
                    if expense_rows:
                        execute_values(cur, "INSERT INTO demo_expenses(action_id,row_order,row_code,article,qty,unit,price_net,price_vat,amount_vat,calc_type,is_custom,comment) VALUES %s", expense_rows)
                    criteria_rows = []
                    for code, value in (a.get("criteria", {}) or {}).items():
                        criteria_rows.append((a["id"], code, int(value.get("level_index", 0)), value.get("manager_comment", "")))
                    if criteria_rows:
                        execute_values(cur, "INSERT INTO demo_criterion_values(action_id,criterion_code,level_index,manager_comment) VALUES %s", criteria_rows)
                elif a["type"] == ACTION_SALE:
                    rows = []
                    for i, r in enumerate(sale_rows_to_records(a, state), start=1):
                        rows.append((a["id"], i, r["product_id"], r["sku"], r["name"], r["pr0_vat"], r["price_vat"], r["price_net"], r["qty"], r["total_vat"], r["total_net"], r["vat_sum"], r["mr_unit"], r["pr_unit"], r["st_pct"], r["cash_net"]))
                    if rows:
                        execute_values(cur, "INSERT INTO sale_rows(action_id,row_order,product_id,sku,name,pr0_vat,price_vat,price_net,qty,total_vat,total_net,vat_sum,mr_unit,pr_unit,st_pct,cash_net) VALUES %s", rows)
        conn.commit()
        conn.close()
        return "OK"
    except Exception:
        conn.rollback()
        conn.close()
        raise


# ==============================
# Auth and permissions
# ==============================

def authenticate(login: str, password: str) -> Optional[Dict[str, Any]]:
    state, _ = load_state_from_db()
    login = str(login or "").strip().lower()
    user = users_map(state).get(login)
    if user and user.get("is_active", True) and str(password or "") == str(user["password"]):
        return user_public(user)
    return None


def get_user_from_header(x_user_login: str = Header(..., alias="X-User-Login")) -> Dict[str, Any]:
    state, _ = load_state_from_db()
    login = str(x_user_login or "").strip().lower()
    user = users_map(state).get(login)
    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Неизвестный пользователь")
    return user_public(user)


def assert_director(user: Dict[str, Any]):
    if user["role"] != "director":
        raise HTTPException(status_code=403, detail="Доступно только директору")


# ==============================
# Action ops
# ==============================

def find_action(state: Dict[str, Any], action_id: str) -> Optional[Dict[str, Any]]:
    return next((a for a in state.get("actions", []) if a.get("id") == action_id), None)


def add_action(state: Dict[str, Any], user: Dict[str, Any], action_type: str, manager_login: Optional[str] = None) -> Dict[str, Any]:
    managers = manager_logins(state)
    if user["role"] == "director":
        manager_login = manager_login if manager_login in managers else (managers[0] if managers else user["login"])
    else:
        manager_login = user["login"]
    if action_type not in {ACTION_DEMO, ACTION_SALE, ACTION_PREMIUM}:
        raise HTTPException(status_code=400, detail="Неверный тип действия")
    if action_type == ACTION_PREMIUM:
        temp_action = {"type": ACTION_PREMIUM, "manager_login": manager_login, "sequence_no": next_sequence_no(manager_login, state)}
        ok, warn = can_confirm_premium(temp_action, state)
        if not ok:
            raise HTTPException(status_code=400, detail=warn)
    action = {
        "id": new_id("ACT"),
        "type": action_type,
        "manager_login": manager_login,
        "sequence_no": next_sequence_no(manager_login, state),
        "date": today_str(),
        "client": "",
        "city": manager_office_city(state, manager_login),
        "model": "",
        "task_description": "",
        "comment": "",
        "payload": {},
        "is_director_confirmed": False,
        "confirmed_amount": None,
        "director_comment": "",
    }
    if action_type == ACTION_DEMO:
        action["demo_meta"] = {"demo_hours": 2, "driver_prep_hours": 2}
        action["expenses"] = default_expense_rows(state, manager_login)
        action["criteria"] = mk_criteria(state["settings"], 0)
    elif action_type == ACTION_SALE:
        action["rows"] = []
    state["actions"].append(action)
    sync_action_after_edit(action, state)
    return action


def move_action(state: Dict[str, Any], user: Dict[str, Any], action_id: str, direction: str) -> str:
    a = find_action(state, action_id)
    if not a:
        raise HTTPException(status_code=404, detail="Действие не найдено")
    if user["role"] != "director" and a.get("manager_login") != user["login"]:
        raise HTTPException(status_code=403, detail="Нет прав на перемещение")
    if user["role"] != "director" and a.get("is_director_confirmed"):
        raise HTTPException(status_code=400, detail="Подтвержденное директором действие нельзя перемещать менеджеру")
    if is_action_locked(a, state):
        raise HTTPException(status_code=400, detail="Заблокированное действие нельзя перемещать")
    manager = a.get("manager_login")
    open_actions = [x for x in state.get("actions", []) if x.get("manager_login") == manager and not is_action_locked(x, state)]
    open_actions = sorted(open_actions, key=lambda x: int(x.get("sequence_no", 0)))
    ids = [x["id"] for x in open_actions]
    if action_id not in ids:
        raise HTTPException(status_code=400, detail="Действие не входит в открытый период")
    i = ids.index(action_id)
    j = i - 1 if direction == "up" else i + 1
    if j < 0 or j >= len(open_actions):
        raise HTTPException(status_code=400, detail="Перемещение невозможно")
    a["sequence_no"], open_actions[j]["sequence_no"] = open_actions[j]["sequence_no"], a["sequence_no"]
    return "OK"


def delete_action(state: Dict[str, Any], user: Dict[str, Any], action_id: str) -> str:
    assert_director(user)
    action = find_action(state, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Действие не найдено")
    if is_action_locked(action, state):
        raise HTTPException(status_code=400, detail="Заблокированное действие нельзя удалить")
    state["actions"] = [a for a in state.get("actions", []) if a.get("id") != action_id]
    return "OK"


def sync_action_after_edit(action: Dict[str, Any], state: Dict[str, Any]):
    auto_update_confirmed = not bool(action.get("is_director_confirmed")) or action.get("confirmed_amount") is None
    if action["type"] == ACTION_DEMO:
        action["expenses"] = normalize_demo_rows(action, state)
        calc = calculate_demo(action, state)
        if auto_update_confirmed:
            action["confirmed_amount"] = calc["VIC"]
    elif action["type"] == ACTION_SALE:
        action["rows"] = sale_rows_to_records(action, state)
        calc = calculate_sale(action, state)
        if auto_update_confirmed:
            action["confirmed_amount"] = calc["cash_all"]
    elif action["type"] == ACTION_PREMIUM:
        calc = calculate_premium(action, state)
        if auto_update_confirmed:
            action["confirmed_amount"] = calc["profit"]


def patch_demo_meta(action: Dict[str, Any], payload: Dict[str, Any]):
    incoming = payload.get("demo_meta")
    if isinstance(incoming, dict):
        meta = get_demo_meta(action)
        meta.update(incoming)
        action["demo_meta"] = meta
        action.setdefault("payload", {})["demo_meta"] = meta


def update_action(state: Dict[str, Any], user: Dict[str, Any], action_id: str, payload: Dict[str, Any], preview: bool = False) -> Dict[str, Any]:
    a = find_action(state, action_id)
    if not a:
        raise HTTPException(status_code=404, detail="Действие не найдено")
    if is_action_locked(a, state) and not preview:
        raise HTTPException(status_code=400, detail="Действие заблокировано подтвержденной премией")
    if user["role"] != "director" and a.get("manager_login") != user["login"]:
        raise HTTPException(status_code=403, detail="Нет прав на редактирование")
    if user["role"] != "director" and a.get("is_director_confirmed") and not preview:
        raise HTTPException(status_code=400, detail="Подтвержденное директором действие нельзя редактировать менеджеру")

    managers = manager_logins(state)
    if user["role"] == "director":
        manager_login = payload.get("manager_login")
        if manager_login in managers and not is_action_locked(a, state):
            a["manager_login"] = manager_login

    for field in ["date", "client", "city", "model", "task_description", "comment"]:
        if field in payload:
            if field == "date":
                a["date"] = safe_date(payload.get("date"))
            else:
                a[field] = str(payload.get(field) or "")

    if a["type"] == ACTION_DEMO:
        patch_demo_meta(a, payload)
        if "expenses" in payload and isinstance(payload["expenses"], list):
            a["expenses"] = payload["expenses"]
        if "criteria" in payload and isinstance(payload["criteria"], dict):
            a["criteria"] = payload["criteria"]
    elif a["type"] == ACTION_SALE:
        if "rows" in payload and isinstance(payload["rows"], list):
            a["rows"] = payload["rows"]

    if user["role"] == "director" and not preview:
        confirm_value = payload.get("is_director_confirmed")
        if confirm_value is not None:
            future = bool(confirm_value)
            if future and a["type"] == ACTION_PREMIUM:
                ok, warn = can_confirm_premium(a, state)
                if not ok:
                    raise HTTPException(status_code=400, detail=warn)
            a["is_director_confirmed"] = future
        if "confirmed_amount" in payload:
            a["confirmed_amount"] = to_float(payload.get("confirmed_amount"), 0)
        if "director_comment" in payload:
            a["director_comment"] = str(payload.get("director_comment") or "")

    sync_action_after_edit(a, state)
    return a


def serialize_criteria_blocks(action: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    state_values = action.get("criteria", {}) or {}
    blocks = {"P": [], "R": [], "M": []}
    for cr in settings.get("criteria", DEFAULT_CRITERIA):
        item = deepcopy(cr)
        current = state_values.get(cr["code"], {"level_index": 0, "manager_comment": ""})
        item["current_level_index"] = int(to_float(current.get("level_index"), 0))
        item["manager_comment"] = current.get("manager_comment", "")
        blocks.setdefault(cr.get("block", "P"), []).append(item)
    return blocks


def serialize_action_detail(action: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    base = deepcopy(action)
    base["is_locked"] = is_action_locked(action, state)
    base["manager_office_city"] = manager_office_city(state, action.get("manager_login"))
    if action["type"] == ACTION_DEMO:
        base["demo_meta"] = get_demo_meta(action)
        calc = calculate_demo(action, state)
        # В карточку отдаем уже нормализованную фиксированную смету из Excel-логики,
        # чтобы старые БД с 3 строками автоматически раскрывались до полной сметы.
        base["expenses"] = calc["expenses"]
        base.setdefault("criteria", {})
        result = {"action": base, "kind": "demo", "calc": calc, "criteria_blocks": serialize_criteria_blocks(action, state["settings"])}
    elif action["type"] == ACTION_SALE:
        calc = calculate_sale(action, state)
        base["rows"] = calc["rows"]
        result = {"action": base, "kind": "sale", "calc": calc}
    else:
        calc = calculate_premium(action, state)
        result = {"action": base, "kind": "premium", "calc": calc}
    return clean_json(result)


# ==============================
# API schemas
# ==============================

class LoginIn(BaseModel):
    login: str
    password: str


class CreateActionIn(BaseModel):
    action_type: str
    manager_login: Optional[str] = None


class MoveIn(BaseModel):
    direction: str


class ActionPatchIn(BaseModel):
    payload: Dict[str, Any]


class AddProductIn(BaseModel):
    product_id: str


class SaleRowCommandIn(BaseModel):
    command: str
    index: int


class DemoExpenseCommandIn(BaseModel):
    command: str
    index: int


class ProductsBulkIn(BaseModel):
    products: List[Dict[str, Any]]


class SettingsIn(BaseModel):
    settings: Dict[str, Any]


app = FastAPI(title="ИРБИСТЕХ API", version="3.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def api_health():
    state, msg = load_state_from_db()
    return clean_json({"ok": True, "db_message": msg, "actions": len(state.get("actions", [])), "version": "v3"})


@app.post("/api/auth/login")
def api_login(payload: LoginIn):
    user = authenticate(payload.login, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return clean_json({"user": user})


@app.get("/api/bootstrap")
def api_bootstrap(user: Dict[str, Any] = Depends(get_user_from_header), manager_filter: str = Query("__all__"), hide_old: bool = Query(False)):
    state, msg = load_state_from_db()
    users = normalize_users(state.get("users"))
    managers = [u for u in users if u.get("role") == "manager" and u.get("is_active", True)]
    return clean_json({
        "user": user,
        "db_message": msg,
        "settings": state["settings"],
        "manager_choices": [{"value": "__all__", "label": "Все менеджеры"}] + [{"value": m["login"], "label": f"{m['name']} · {m.get('office_city', '')}"} for m in managers],
        "actions": visible_actions(user, state, manager_filter, hide_old),
        "products_count": len(state.get("products", [])),
        "office_cities": office_names(state["settings"]),
    })


@app.get("/api/actions")
def api_actions(user: Dict[str, Any] = Depends(get_user_from_header), manager_filter: str = Query("__all__"), hide_old: bool = Query(False)):
    state, _ = load_state_from_db()
    return clean_json({"items": visible_actions(user, state, manager_filter, hide_old)})


@app.get("/api/actions/{action_id}")
def api_action_detail(action_id: str, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    action = find_action(state, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Действие не найдено")
    if user["role"] != "director" and action.get("manager_login") != user["login"]:
        raise HTTPException(status_code=403, detail="Нет доступа к действию")
    return serialize_action_detail(action, state)


@app.post("/api/actions")
def api_create_action(body: CreateActionIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    action = add_action(state, user, body.action_type, body.manager_login)
    persist_state_to_db(state)
    return clean_json({"action": serialize_action_detail(action, state), "actions": visible_actions(user, state, "__all__" if user["role"] == "director" else user["login"])})


@app.patch("/api/actions/{action_id}")
def api_update_action(action_id: str, body: ActionPatchIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    action = update_action(state, user, action_id, body.payload)
    persist_state_to_db(state)
    return clean_json({"action": serialize_action_detail(action, state), "actions": visible_actions(user, state, "__all__" if user["role"] == "director" else user["login"])})


@app.delete("/api/actions/{action_id}")
def api_delete_action(action_id: str, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    delete_action(state, user, action_id)
    persist_state_to_db(state)
    return clean_json({"ok": True, "actions": visible_actions(user, state, "__all__" if user["role"] == "director" else user["login"])})


@app.post("/api/actions/{action_id}/move")
def api_move_action(action_id: str, body: MoveIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    move_action(state, user, action_id, body.direction)
    persist_state_to_db(state)
    return clean_json({"ok": True, "actions": visible_actions(user, state, "__all__" if user["role"] == "director" else user["login"])})


@app.post("/api/actions/{action_id}/sale-rows/add-product")
def api_add_product_to_sale(action_id: str, body: AddProductIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    action = find_action(state, action_id)
    if not action or action.get("type") != ACTION_SALE:
        raise HTTPException(status_code=404, detail="Продажа не найдена")
    if is_action_locked(action, state):
        raise HTTPException(status_code=400, detail="Действие заблокировано")
    if user["role"] != "director" and action.get("manager_login") != user["login"]:
        raise HTTPException(status_code=403, detail="Нет прав")
    if user["role"] != "director" and action.get("is_director_confirmed"):
        raise HTTPException(status_code=400, detail="Подтвержденное директором действие нельзя редактировать менеджеру")
    product = next((normalize_product(p, state["settings"]) for p in state.get("products", []) if str(p.get("product_id")) == body.product_id), None)
    if not product:
        raise HTTPException(status_code=400, detail="Товар не найден в справочнике")
    rows = sale_rows_to_records(action, state)
    rows.append(create_sale_row_from_product(product, 1, state["settings"], manager_office_city(state, action.get("manager_login"))))
    action["rows"] = rows
    sync_action_after_edit(action, state)
    persist_state_to_db(state)
    return serialize_action_detail(action, state)


@app.post("/api/actions/{action_id}/sale-rows/command")
def api_sale_row_command(action_id: str, body: SaleRowCommandIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    action = find_action(state, action_id)
    if not action or action.get("type") != ACTION_SALE:
        raise HTTPException(status_code=404, detail="Продажа не найдена")
    if is_action_locked(action, state):
        raise HTTPException(status_code=400, detail="Действие заблокировано")
    if user["role"] != "director" and action.get("is_director_confirmed"):
        raise HTTPException(status_code=400, detail="Подтвержденное директором действие нельзя редактировать менеджеру")
    rows = sale_rows_to_records(action, state)
    idx = body.index
    if idx < 0 or idx >= len(rows):
        raise HTTPException(status_code=400, detail="Неверный индекс строки")
    if body.command == "delete":
        rows.pop(idx)
    elif body.command == "up" and idx > 0:
        rows[idx - 1], rows[idx] = rows[idx], rows[idx - 1]
    elif body.command == "down" and idx < len(rows) - 1:
        rows[idx + 1], rows[idx] = rows[idx], rows[idx + 1]
    action["rows"] = rows
    sync_action_after_edit(action, state)
    persist_state_to_db(state)
    return serialize_action_detail(action, state)


@app.post("/api/actions/{action_id}/demo-expenses/add-row")
def api_demo_add_row(action_id: str, user: Dict[str, Any] = Depends(get_user_from_header)):
    # Пользовательские строки удалены из UI и логики: смета теперь одинаковая для всех демонстраций.
    state, _ = load_state_from_db()
    action = find_action(state, action_id)
    if not action or action.get("type") != ACTION_DEMO:
        raise HTTPException(status_code=404, detail="Демонстрация не найдена")
    return serialize_action_detail(action, state)


@app.post("/api/actions/{action_id}/demo-expenses/command")
def api_demo_expense_command(action_id: str, body: DemoExpenseCommandIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    # Движение/удаление строк сметы отключено: порядок и состав задаются настройками.
    state, _ = load_state_from_db()
    action = find_action(state, action_id)
    if not action or action.get("type") != ACTION_DEMO:
        raise HTTPException(status_code=404, detail="Демонстрация не найдена")
    return serialize_action_detail(action, state)


@app.post("/api/actions/{action_id}/preview")
def api_action_preview(action_id: str, body: ActionPatchIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    preview_state = deepcopy(state)
    action = update_action(preview_state, user, action_id, body.payload, preview=True)
    return serialize_action_detail(action, preview_state)


@app.get("/api/products")
def api_products(user: Dict[str, Any] = Depends(get_user_from_header)):
    assert_director(user)
    state, _ = load_state_from_db()
    return clean_json({"items": sorted_products(state.get("products", []), state["settings"]), "office_cities": office_names(state["settings"])})


@app.get("/api/products/search")
def api_products_search(q: str = Query(""), user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    return clean_json({"items": search_products(q, state.get("products", []), state["settings"])})


@app.put("/api/products")
def api_products_save(body: ProductsBulkIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    assert_director(user)
    state, _ = load_state_from_db()
    state["products"] = [normalize_product(p, state["settings"], i) for i, p in enumerate(body.products, start=1)]
    for i, p in enumerate(state["products"], start=1):
        p["row_order"] = i
    persist_state_to_db(state)
    return clean_json({"items": state["products"]})


def products_to_excel(products: List[Dict[str, Any]], settings: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for p in sorted_products(products, settings):
        row = {
            "Артикул": p["sku"],
            "Наименование": p["name"],
            "Цена с НДС (прайс) [PR0], руб./шт": p["price_vat"],
            "Цена без НДС (прайс), руб./шт": p["price_net"],
        }
        for city in office_names(settings):
            params = p.get("office_params", {}).get(city, {})
            row[f"{city}_MR"] = to_float(params.get("mr"), p["price_net"] * 0.20)
            row[f"{city}_PR"] = to_float(params.get("pr"), p["price_net"] * 0.10)
            row[f"{city}_ST"] = decimal_to_pct(params.get("st", office_rate(settings, city, "sale_st", 0.5)))
        rows.append(row)
    return pd.DataFrame(rows)


@app.get("/api/products/template")
def api_products_template():
    state, _ = load_state_from_db()
    df = products_to_excel(state.get("products", []), state["settings"])
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="products")
    bio.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="irbistech_products.xlsx"'}
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


def read_products_excel(raw: bytes, filename: str, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    if filename.lower().endswith(".csv"):
        df = pd.read_csv(io.BytesIO(raw))
    else:
        df = pd.read_excel(io.BytesIO(raw), sheet_name=0)
    products = []
    for i, r in enumerate(df.to_dict("records"), start=1):
        sku = str(r.get("Артикул") or r.get("sku") or "").strip()
        name = str(r.get("Наименование") or r.get("name") or "").strip()
        if not sku and not name:
            continue
        item = {
            "product_id": sku or new_id("PRD"),
            "sku": sku or name,
            "name": name,
            "price_vat": r.get("Цена с НДС (прайс) [PR0], руб./шт", r.get("price_vat", 0)),
            "price_net": r.get("Цена без НДС (прайс), руб./шт", r.get("price_net", 0)),
            "row_order": i,
            "office_params": {},
        }
        for city in office_names(settings):
            item["office_params"][city] = {
                "mr": to_float(r.get(f"{city}_MR"), 0),
                "pr": to_float(r.get(f"{city}_PR"), 0),
                "st": pct_to_decimal(r.get(f"{city}_ST"), office_rate(settings, city, "sale_st", 0.5)),
            }
        products.append(normalize_product(item, settings, i))
    return products


@app.post("/api/products/import")
def api_products_import(file: UploadFile = File(...), user: Dict[str, Any] = Depends(get_user_from_header)):
    assert_director(user)
    raw = file.file.read()
    state, _ = load_state_from_db()
    imported = read_products_excel(raw, file.filename, state["settings"])
    imported_skus = {p["sku"] for p in imported}
    used_skus = sorted({row.get("sku") for a in state.get("actions", []) if a.get("type") == ACTION_SALE for row in a.get("rows", []) if row.get("sku")})
    missing = [sku for sku in used_skus if sku not in imported_skus]
    if missing:
        raise HTTPException(status_code=400, detail=f"В импортируемом файле отсутствуют товары с артикулами: {', '.join(missing)}")
    state["products"] = imported
    persist_state_to_db(state)
    return clean_json({"items": imported, "count": len(imported), "message": "Импорт успешно проведен"})


@app.get("/api/settings")
def api_settings(user: Dict[str, Any] = Depends(get_user_from_header)):
    assert_director(user)
    state, _ = load_state_from_db()
    return clean_json({"settings": state["settings"]})


@app.put("/api/settings")
def api_settings_save(body: SettingsIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    assert_director(user)
    state, _ = load_state_from_db()
    state["settings"] = merge_settings(body.settings)
    # Обновляем производные строки/расчеты после изменения норм и ставок.
    for a in state.get("actions", []):
        sync_action_after_edit(a, state)
    persist_state_to_db(state)
    return clean_json({"settings": state["settings"]})


@app.exception_handler(Exception)
def all_exception_handler(request, exc):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(status_code=500, content={"detail": str(exc), "trace": traceback.format_exc(limit=4)})
