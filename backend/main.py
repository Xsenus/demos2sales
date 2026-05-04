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
from typing import Any, Dict, List, Optional

import pandas as pd
import psycopg2
from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
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
SHORT_TYPE = {ACTION_DEMO: "Демо", ACTION_SALE: "Продажа", ACTION_PREMIUM: "Премия"}
MANAGER_LOGINS = ["ruslan", "timur", "maria", "ildar"]

USERS = {
    "artur": {"login": "artur", "password": "123", "role": "director", "name": "Артур Гимадеев"},
    "ruslan": {"login": "ruslan", "password": "111", "role": "manager", "name": "Руслан Абдулин"},
    "timur": {"login": "timur", "password": "222", "role": "manager", "name": "Тимур Сафин"},
    "maria": {"login": "maria", "password": "333", "role": "manager", "name": "Мария Иванова"},
    "ildar": {"login": "ildar", "password": "444", "role": "manager", "name": "Ильдар Хасанов"},
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
    if not DB_PASSWORD:
        raise RuntimeError("Переменная DEMO_CALC_DB_PASSWORD не задана.")
    return psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)


def ensure_schema():
    if not USE_POSTGRES:
        return False, "PostgreSQL отключен."
    try:
        conn = db_connect()
        conn.autocommit = True
        with conn.cursor() as cur:
            for stmt in [s.strip() for s in SCHEMA_SQL.split(';') if s.strip()]:
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
        text = str(value).replace("\xa0", " ").replace("руб.", "").replace("%", "").strip()
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


def money0(value: Any) -> str:
    return f"{to_float(value):,.0f} руб.".replace(",", " ")


def clean_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): clean_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
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


def default_settings() -> Dict[str, Any]:
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
            "action_list_width_pct": 28,
            "font_base_px": 13,
            "font_title_px": 18,
            "card_padding_px": 10,
            "field_gap_px": 8,
            "table_row_height_px": 34,
            "criteria_name_width_pct": 20,
            "criteria_levels_width_pct": 60,
            "criteria_comment_width_pct": 20,
        },
        "criteria": deepcopy(DEFAULT_CRITERIA),
        "expense_settings": deepcopy(DEFAULT_EXPENSE_SETTINGS),
    }


def merge_settings(settings: Any) -> Dict[str, Any]:
    base = default_settings()
    if not isinstance(settings, dict):
        return base
    for k, v in settings.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k].update(v)
        else:
            base[k] = v
    if not base.get("criteria"):
        base["criteria"] = deepcopy(DEFAULT_CRITERIA)
    if not base.get("expense_settings"):
        base["expense_settings"] = deepcopy(DEFAULT_EXPENSE_SETTINGS)
    base["font_family"] = "Arial"
    return base


def default_products() -> List[Dict[str, Any]]:
    return deepcopy(DEFAULT_PRODUCTS)


def normalize_product(product: Dict[str, Any], settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    settings = settings or default_settings()
    vat = to_float(settings.get("vat_rate"), 0.22)
    product_id = str(product.get("product_id") or product.get("ID товара") or product.get("sku") or product.get("Артикул") or new_id("PRD"))
    sku = str(product.get("sku") or product.get("Артикул") or product_id)
    name = str(product.get("name") or product.get("Наименование ТМЦ") or product.get("Наименование оборудования") or "")
    price_vat = to_float(product.get("price_vat", product.get("Цена руб. с НДС")), 0)
    price_net = to_float(product.get("price_net", product.get("Цена руб. без НДС (A)", product.get("Цена руб. без НДС"))), 0)
    if price_net <= 0 and price_vat > 0:
        price_net = price_vat / (1 + vat)
    if price_vat <= 0 and price_net > 0:
        price_vat = price_net * (1 + vat)
    min_price_net = to_float(product.get("min_price_net", product.get("Минимальная цена продажи без НДС (B)", product.get("Минимальная цена продажи без НДС"))), 0)
    margin_pct = pct_to_decimal(product.get("margin_pct", product.get("% от маржи (D)", product.get("% от маржи факт"))), 0.65)
    margin = price_net - min_price_net
    bonus = margin * margin_pct
    return {
        "product_id": product_id,
        "sku": sku,
        "name": name,
        "price_vat": round(price_vat, 2),
        "price_net": round(price_net, 2),
        "min_price_net": round(min_price_net, 2),
        "margin_pct": round(margin_pct, 6),
        "margin": round(margin, 2),
        "bonus_net": round(bonus, 2),
        "comment": str(product.get("comment", product.get("Комментарий", ""))),
    }


def product_lookup(products: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    lookup = {}
    for p in products or []:
        n = normalize_product(p)
        for key in [n["product_id"], n["sku"], n["name"]]:
            if key:
                lookup[str(key).strip().lower()] = n
    return lookup


def search_products(query: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    q = str(query or "").strip().lower()
    if len(q) < 3:
        return []
    out = []
    for p in products or []:
        n = normalize_product(p)
        hay = f"{n['product_id']} {n['sku']} {n['name']}".lower()
        if q in hay:
            out.append({"product_id": n["product_id"], "sku": n["sku"], "name": n["name"]})
    return out[:20]


def create_sale_row_from_product(product: Dict[str, Any], qty: float = 1.0, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    p = normalize_product(product, settings)
    qty = max(0.0, to_float(qty, 1.0))
    total_vat = p["price_vat"] * qty
    total_net = p["price_net"] * qty
    margin_unit = p["price_net"] - p["min_price_net"]
    return {
        "product_id": p["product_id"],
        "sku": p["sku"],
        "name": p["name"],
        "price_vat": p["price_vat"],
        "price_net": p["price_net"],
        "qty": qty,
        "total_vat": round(total_vat, 2),
        "total_net": round(total_net, 2),
        "vat_sum": round(total_vat - total_net, 2),
        "min_price_net": p["min_price_net"],
        "margin_unit": round(margin_unit, 2),
        "margin_pct": p["margin_pct"],
        "bonus_net": round(margin_unit * p["margin_pct"] * qty, 2),
    }


def sale_rows_to_records(rows: List[Dict[str, Any]], products: List[Dict[str, Any]], settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    lookup = product_lookup(products)
    out = []
    for r in rows or []:
        rid = str(r.get("product_id", "")).strip()
        sku = str(r.get("sku", "")).strip()
        found = None
        for key in [rid, sku]:
            if key and key.lower() in lookup:
                found = lookup[key.lower()]
                break
        if not found:
            continue
        qty = to_float(r.get("qty"), 1)
        price_vat = to_float(r.get("price_vat"), found["price_vat"])
        price_net = to_float(r.get("price_net"), found["price_net"])
        row = create_sale_row_from_product({**found, "price_vat": price_vat, "price_net": price_net}, qty, settings)
        out.append(row)
    return out


def calculate_sale(action: Dict[str, Any], products: List[Dict[str, Any]], settings: Dict[str, Any]) -> Dict[str, Any]:
    rows = sale_rows_to_records(action.get("rows", []), products, settings)
    bonus = sum(to_float(r.get("bonus_net")) for r in rows)
    total_vat = sum(to_float(r.get("total_vat")) for r in rows)
    return {"rows": rows, "bonus_net": round(float(bonus), 2), "total_vat": round(float(total_vat), 2)}


def expense_settings_map(settings: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {s["article"]: s for s in settings.get("expense_settings", DEFAULT_EXPENSE_SETTINGS)}


def calc_expenses_rows(rows: List[Dict[str, Any]], settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    vat = to_float(settings.get("vat_rate"), 0.22)
    smap = expense_settings_map(settings)
    norm: List[Dict[str, Any]] = []
    for i, r in enumerate(rows or [], start=1):
        article = str(r.get("article", "")).strip()
        if not article:
            continue
        s = smap.get(article)
        is_custom = bool(r.get("is_custom", False)) or s is None
        calc_type = (s or {}).get("calc_type", r.get("calc_type", "direct"))
        qty_manager = bool((s or {}).get("qty_manager", True))
        price_manager = bool((s or {}).get("price_manager", True))
        qty = to_float(r.get("qty"), (s or {}).get("qty_default", 0))
        unit = str(r.get("unit", (s or {}).get("unit", "")))
        price_net = to_float(r.get("price_net"), (s or {}).get("price_net_default", 0) or 0)
        price_vat = to_float(r.get("price_vat"), (s or {}).get("price_vat_default", 0) or 0)
        if s and not qty_manager:
            qty = to_float((s or {}).get("qty_default"), qty)
        if s and not price_manager:
            price_net = to_float((s or {}).get("price_net_default"), price_net)
            price_vat = to_float((s or {}).get("price_vat_default"), price_vat)
        norm.append({
            "row_order": i,
            "article": article,
            "qty": qty,
            "unit": unit,
            "price_net": price_net,
            "price_vat": price_vat,
            "amount_vat": 0,
            "calc_type": calc_type,
            "is_custom": is_custom,
            "comment": str(r.get("comment", "") or ""),
        })

    km = next((x["qty"] for x in norm if x["article"] == "Работа водителя"), 0)
    amount_by_article = {}
    for x in norm:
        ct = x["calc_type"]
        if ct == "diesel":
            x["qty"] = km / 100.0 * to_float(settings.get("diesel_l_per_100km"), 12)
            if x["price_vat"] <= 0:
                x["price_vat"] = 78
            x["price_net"] = x["price_vat"] / (1 + vat)
            x["amount_vat"] = x["qty"] * x["price_vat"]
        elif ct == "gazelle_amort":
            x["qty"] = km
            if x["price_vat"] <= 0:
                x["price_vat"] = 10
            x["price_net"] = x["price_vat"] / (1 + vat)
            x["amount_vat"] = x["qty"] * x["price_vat"]
        elif ct == "payroll_tax":
            x["amount_vat"] = 0
        elif ct == "direct_vat_price":
            if x["price_vat"] <= 0 and x["price_net"] > 0:
                x["price_vat"] = x["price_net"] * (1 + vat)
            if x["price_net"] <= 0 and x["price_vat"] > 0:
                x["price_net"] = x["price_vat"] / (1 + vat)
            x["amount_vat"] = x["qty"] * x["price_vat"]
        else:
            if x["price_net"] <= 0 and x["price_vat"] > 0:
                x["price_net"] = x["price_vat"] / (1 + vat)
            if x["price_vat"] <= 0 and x["price_net"] > 0:
                x["price_vat"] = x["price_net"] * (1 + vat)
            x["amount_vat"] = x["qty"] * x["price_vat"]
        amount_by_article[x["article"]] = x["amount_vat"]

    for x in norm:
        if x["calc_type"] == "payroll_tax":
            base_articles = ["Работа водителя", "Работа демонстратора", "Демонстрация криобластера", "Усложненные условия труда", "Ручная работа с кабелем и шланга компрессора"]
            base_amount_net = 0.0
            for article in base_articles:
                base_amount_net += to_float(amount_by_article.get(article)) / (1 + vat)
            tax_net = base_amount_net * to_float(settings.get("payroll_tax_rate"), 0.30)
            x["price_net"] = tax_net
            x["price_vat"] = tax_net * (1 + vat)
            x["qty"] = 1
            x["amount_vat"] = x["price_vat"]
        x["price_net"] = round(to_float(x["price_net"]), 2)
        x["price_vat"] = round(to_float(x["price_vat"]), 2)
        x["amount_vat"] = round(to_float(x["amount_vat"]), 2)
    return norm


def default_expense_rows(settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for i, s in enumerate(settings.get("expense_settings", DEFAULT_EXPENSE_SETTINGS), start=1):
        rows.append({
            "row_order": i,
            "article": s["article"],
            "qty": s.get("qty_default") or 0,
            "unit": s.get("unit", ""),
            "price_net": s.get("price_net_default") or 0,
            "price_vat": s.get("price_vat_default") or 0,
            "amount_vat": 0,
            "calc_type": s.get("calc_type", "direct"),
            "is_custom": False,
            "comment": s.get("comment", ""),
        })
    return calc_expenses_rows(rows, settings)


def calculate_demo(action: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
    vat = to_float(settings.get("vat_rate"), 0.22)
    bonus_rate = to_float(settings.get("bonus_rate"), 0.65)
    total_vat = 0.0
    expenses = calc_expenses_rows(action.get("expenses", []), settings)
    total_vat = sum(to_float(r.get("amount_vat")) for r in expenses)
    support_vat = to_float(settings.get("company_support_vat"), 0)
    cost_net = max(0.0, total_vat / (1 + vat) - support_vat / (1 + vat))

    criteria_state = action.get("criteria", {}) or {}
    score_by_code: Dict[str, float] = {}
    block_scores = {"P": 0.0, "R": 0.0, "M": 0.0}
    for cr in settings.get("criteria", DEFAULT_CRITERIA):
        item = criteria_state.get(cr["code"], {})
        idx = int(item.get("level_index", 0))
        idx = max(0, min(idx, len(cr.get("levels", [])) - 1))
        score = to_float(cr["levels"][idx][1], 0)
        score_by_code[cr["code"]] = score
        block_scores[cr["block"]] += score
    P = block_scores["P"]
    R = block_scores["R"]
    M = block_scores["M"]
    QI = (
        to_float(settings.get("p_weight"), 0.45) * (P / 100)
        + to_float(settings.get("r_weight"), 0.35) * (R / 100)
        + to_float(settings.get("m_weight"), 0.20) * (M / 100)
    )
    K_raw = 1 - to_float(settings.get("k_reduction_factor"), 0.80) * QI
    soft = score_by_code.get("P2", 0) == 0 or score_by_code.get("P4", 0) == 0 or score_by_code.get("P5", 0) == 0
    hard = score_by_code.get("P8", 0) == 0 or score_by_code.get("M7", 0) == 0
    if hard:
        K = 1.0
    elif soft:
        K = max(K_raw, to_float(settings.get("min_soft_stop_k"), 0.80))
    else:
        K = max(K_raw, to_float(settings.get("min_normal_k"), 0.20))
    K = min(1.0, max(0.0, K))
    expense_for_bonus = cost_net * K
    deduction_net = expense_for_bonus * bonus_rate
    return {
        "expenses": expenses,
        "total_vat": round(total_vat, 2),
        "support_vat": round(support_vat, 2),
        "cost_net": round(cost_net, 2),
        "P": round(P, 2),
        "R": round(R, 2),
        "M": round(M, 2),
        "QI": round(QI, 6),
        "K_raw": round(K_raw, 6),
        "K": round(K, 6),
        "soft_stop": soft,
        "hard_stop": hard,
        "expense_for_bonus": round(expense_for_bonus, 2),
        "deduction_net": round(deduction_net, 2),
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
    for a in state.get("actions", []):
        if a.get("manager_login") == manager and a.get("type") == ACTION_PREMIUM and a.get("is_director_confirmed") and int(a.get("sequence_no", 0)) >= seq:
            return True
    return False


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


def calculate_premium(action: Dict[str, Any], state: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
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
        sale_rows.append({
            "action_id": s["id"],
            "date": s.get("date"),
            "client": s.get("client"),
            "bonus_calc": round(calc["bonus_net"], 2),
            "director_amount": round(amount, 2),
        })
    for d in demos:
        calc = calculate_demo(d, settings)
        amount = to_float(d.get("confirmed_amount"), calc["deduction_net"] if d.get("is_director_confirmed") else 0)
        demo_sum += amount
        demo_rows.append({
            "action_id": d["id"],
            "date": d.get("date"),
            "client": d.get("client"),
            "deduction_calc": round(calc["deduction_net"], 2),
            "director_amount": round(amount, 2),
            "is_director_confirmed": bool(d.get("is_director_confirmed")),
        })
    max_deduction = sales_sum * to_float(settings.get("max_demo_deduction_pct"), 1.0)
    actual_demo = min(demo_sum, max_deduction)
    payout = max(0.0, sales_sum - actual_demo)
    return {
        "ok": ok,
        "warning": warning,
        "sales_sum": round(sales_sum, 2),
        "demo_sum": round(demo_sum, 2),
        "actual_demo": round(actual_demo, 2),
        "payout": round(payout, 2),
        "sale_rows": sale_rows,
        "demo_rows": demo_rows,
        "period_from_seq": min([int(a.get("sequence_no", 0)) for a in period], default=0),
        "period_to_seq": int(action.get("sequence_no", 0)),
    }


def action_display_amount(action: Dict[str, Any], state: Dict[str, Any]) -> float:
    settings = state["settings"]
    if action.get("type") == ACTION_DEMO:
        calc = calculate_demo(action, settings)
        return to_float(action.get("confirmed_amount"), calc["deduction_net"])
    if action.get("type") == ACTION_SALE:
        calc = calculate_sale(action, state["products"], settings)
        return to_float(action.get("confirmed_amount"), calc["bonus_net"])
    calc = calculate_premium(action, state, settings)
    return to_float(action.get("confirmed_amount"), calc["payout"])


def build_action_summary(action: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    amount = action_display_amount(action, state)
    locked = is_action_locked(action, state)
    line1 = f"{int(action.get('sequence_no', 0)):03d} · {SHORT_TYPE.get(action['type'], action['type'])} · {safe_date(action.get('date'))}"
    line2 = f"{action.get('client', '')} · {money0(amount)}"
    return {
        "id": action["id"],
        "type": action["type"],
        "sequence_no": int(action.get("sequence_no", 0)),
        "date": safe_date(action.get("date")),
        "client": action.get("client", ""),
        "manager_login": action.get("manager_login"),
        "manager_name": USERS.get(action.get("manager_login"), {}).get("name", action.get("manager_login")),
        "is_director_confirmed": bool(action.get("is_director_confirmed")),
        "is_locked": locked,
        "display_amount": round(amount, 2),
        "line1": line1,
        "line2": line2,
    }


def visible_actions(user: Dict[str, Any], state: Dict[str, Any], manager_filter: str = "__all__") -> List[Dict[str, Any]]:
    actions = state.get("actions", [])
    if user["role"] == "director":
        if manager_filter and manager_filter != "__all__":
            actions = [a for a in actions if a.get("manager_login") == manager_filter]
    else:
        actions = [a for a in actions if a.get("manager_login") == user["login"]]
    actions = sorted(actions, key=lambda a: (a.get("manager_login", ""), int(a.get("sequence_no", 0))))
    return [build_action_summary(a, state) for a in actions]


def next_sequence_no(manager_login: str, state: Dict[str, Any]) -> int:
    seqs = [int(a.get("sequence_no", 0)) for a in state.get("actions", []) if a.get("manager_login") == manager_login]
    return (max(seqs) if seqs else 0) + 10


def create_demo_state() -> Dict[str, Any]:
    settings = default_settings()
    products = [normalize_product(p, settings) for p in default_products()]

    def mk_criteria(default_idx: int = 1):
        return {cr["code"]: {"level_index": min(default_idx, len(cr["levels"]) - 1), "manager_comment": ""} for cr in settings["criteria"]}

    actions: List[Dict[str, Any]] = []
    seq = 10
    for manager, client, city, model in [
        ("ruslan", "Центр Транс Техмаш", "Рязань", "TRANSFORMER 2.0 MAX"),
        ("timur", "Полипластик", "Москва", "ONE 2.0"),
        ("maria", "Кондитерская фабрика", "Казань", "MINI 3.0"),
    ]:
        actions.append({
            "id": new_id("DEMO"), "type": ACTION_DEMO, "manager_login": manager, "sequence_no": seq,
            "date": today_str(), "client": client, "city": city, "model": model,
            "task_description": "Демо-задача", "comment": "", "is_director_confirmed": False,
            "confirmed_amount": None, "director_comment": "", "expenses": default_expense_rows(settings), "criteria": mk_criteria(1),
        })
        seq += 10
        actions.append({
            "id": new_id("SALE"), "type": ACTION_SALE, "manager_login": manager, "sequence_no": seq,
            "date": today_str(), "client": client, "comment": "", "is_director_confirmed": False,
            "confirmed_amount": None, "director_comment": "", "rows": [create_sale_row_from_product(products[0], 1, settings)],
        })
        seq += 10
    return {"settings": settings, "products": products, "actions": actions}


# ==============================
# Persistence
# ==============================

def load_state_from_db():
    ok, msg = ensure_schema()
    if not ok:
        if Path(JSON_BACKUP_PATH).exists():
            return json.loads(Path(JSON_BACKUP_PATH).read_text(encoding="utf-8")), msg
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
            settings = merge_settings(row["settings"] if row else default_settings())

            cur.execute("SELECT * FROM products ORDER BY sku")
            products = [normalize_product(dict(r), settings) for r in cur.fetchall()]

            cur.execute("SELECT * FROM actions ORDER BY manager_login, sequence_no")
            action_rows = [dict(r) for r in cur.fetchall()]
            actions: List[Dict[str, Any]] = []
            for a in action_rows:
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
                actions.append(action)
        conn.close()
        return {"settings": settings, "products": products, "actions": actions}, "OK"
    except Exception as e:
        if Path(JSON_BACKUP_PATH).exists():
            return json.loads(Path(JSON_BACKUP_PATH).read_text(encoding="utf-8")), f"Ошибка БД, загружен JSON backup: {e}"
        return create_demo_state(), f"Ошибка БД: {e}"


def persist_state_to_db(state: Dict[str, Any]) -> str:
    Path(JSON_BACKUP_PATH).write_text(json.dumps(clean_json(state), ensure_ascii=False, indent=2), encoding="utf-8")
    ok, msg = ensure_schema()
    if not ok:
        return f"База недоступна, сохранен JSON backup: {msg}"
    conn = db_connect()
    try:
        conn.autocommit = False
        with conn.cursor() as cur:
            cur.execute("TRUNCATE demo_criterion_values, demo_expenses, sale_rows, actions, products, app_settings, app_users RESTART IDENTITY CASCADE")
            execute_values(cur, "INSERT INTO app_users(login,password,role,name,is_active) VALUES %s", [
                (u["login"], u["password"], u["role"], u["name"], True) for u in USERS.values()
            ])
            cur.execute("INSERT INTO app_settings(id, settings) VALUES (1, %s)", (Json(clean_json(state.get("settings", default_settings()))),))
            products = [normalize_product(p, state.get("settings", default_settings())) for p in state.get("products", [])]
            execute_values(cur, "INSERT INTO products(product_id, sku, name, price_vat, price_net, min_price_net, margin_pct, comment) VALUES %s", [
                (p["product_id"], p["sku"], p["name"], p["price_vat"], p["price_net"], p["min_price_net"], p["margin_pct"], p.get("comment", "")) for p in products
            ])
            for a in state.get("actions", []):
                cur.execute(
                    """INSERT INTO actions(action_id, action_type, manager_login, sequence_no, action_date, client, city, model, task_description, comment, is_director_confirmed, confirmed_amount, director_comment)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        a["id"], a["type"], a["manager_login"], int(a.get("sequence_no", 0)), safe_date(a.get("date")), a.get("client", ""),
                        a.get("city", ""), a.get("model", ""), a.get("task_description", ""), a.get("comment", ""),
                        bool(a.get("is_director_confirmed")), a.get("confirmed_amount"), a.get("director_comment", ""),
                    ),
                )
                if a["type"] == ACTION_DEMO:
                    expense_rows = []
                    for i, r in enumerate(calc_expenses_rows(a.get("expenses", []), state.get("settings", default_settings())), start=1):
                        expense_rows.append((a["id"], i, r.get("article", ""), to_float(r.get("qty")), r.get("unit", ""), to_float(r.get("price_net")), to_float(r.get("price_vat")), to_float(r.get("amount_vat")), r.get("calc_type", "direct"), bool(r.get("is_custom", False)), r.get("comment", "")))
                    if expense_rows:
                        execute_values(cur, "INSERT INTO demo_expenses(action_id,row_order,article,qty,unit,price_net,price_vat,amount_vat,calc_type,is_custom,comment) VALUES %s", expense_rows)
                    criteria_rows = []
                    for code, value in (a.get("criteria", {}) or {}).items():
                        criteria_rows.append((a["id"], code, int(value.get("level_index", 0)), value.get("manager_comment", "")))
                    if criteria_rows:
                        execute_values(cur, "INSERT INTO demo_criterion_values(action_id,criterion_code,level_index,manager_comment) VALUES %s", criteria_rows)
                elif a["type"] == ACTION_SALE:
                    rows = []
                    for i, r in enumerate(sale_rows_to_records(a.get("rows", []), state.get("products", []), state.get("settings", default_settings())), start=1):
                        rows.append((a["id"], i, r["product_id"], r["sku"], r["name"], r["price_vat"], r["price_net"], r["qty"], r["total_vat"], r["total_net"], r["vat_sum"], r["min_price_net"], r["margin_unit"], r["margin_pct"], r["bonus_net"]))
                    if rows:
                        execute_values(cur, "INSERT INTO sale_rows(action_id,row_order,product_id,sku,name,price_vat,price_net,qty,total_vat,total_net,vat_sum,min_price_net,margin_unit,margin_pct,bonus_net) VALUES %s", rows)
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
    login = str(login or "").strip().lower()
    user = USERS.get(login)
    if user and str(password or "") == str(user["password"]):
        return {k: v for k, v in user.items() if k != "password"}
    return None


def get_user_from_header(x_user_login: str = Header(..., alias="X-User-Login")) -> Dict[str, Any]:
    login = str(x_user_login or "").strip().lower()
    user = USERS.get(login)
    if not user:
        raise HTTPException(status_code=401, detail="Неизвестный пользователь")
    return {k: v for k, v in user.items() if k != "password"}


def assert_director(user: Dict[str, Any]):
    if user["role"] != "director":
        raise HTTPException(status_code=403, detail="Доступно только директору")


# ==============================
# Action ops
# ==============================

def find_action(state: Dict[str, Any], action_id: str) -> Optional[Dict[str, Any]]:
    for a in state.get("actions", []):
        if a.get("id") == action_id:
            return a
    return None


def add_action(state: Dict[str, Any], user: Dict[str, Any], action_type: str, manager_login: Optional[str] = None) -> Dict[str, Any]:
    if user["role"] == "director":
        manager_login = manager_login if manager_login in MANAGER_LOGINS else MANAGER_LOGINS[0]
    else:
        manager_login = user["login"]
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
        "city": "",
        "model": "",
        "task_description": "",
        "comment": "",
        "is_director_confirmed": False,
        "confirmed_amount": None,
        "director_comment": "",
    }
    if action_type == ACTION_DEMO:
        action["expenses"] = default_expense_rows(state["settings"])
        action["criteria"] = {cr["code"]: {"level_index": 0, "manager_comment": ""} for cr in state["settings"]["criteria"]}
    elif action_type == ACTION_SALE:
        action["rows"] = []
    state["actions"].append(action)
    return action


def move_action(state: Dict[str, Any], user: Dict[str, Any], action_id: str, direction: str) -> str:
    a = find_action(state, action_id)
    if not a:
        raise HTTPException(status_code=404, detail="Действие не найдено")
    if user["role"] != "director" and a.get("manager_login") != user["login"]:
        raise HTTPException(status_code=403, detail="Нет прав на перемещение")
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
    settings = state["settings"]
    auto_update_confirmed = not bool(action.get("is_director_confirmed")) or action.get("confirmed_amount") is None
    if action["type"] == ACTION_DEMO:
        action["expenses"] = calc_expenses_rows(action.get("expenses", []), settings)
        calc = calculate_demo(action, settings)
        if auto_update_confirmed:
            action["confirmed_amount"] = calc["deduction_net"]
    elif action["type"] == ACTION_SALE:
        action["rows"] = sale_rows_to_records(action.get("rows", []), state["products"], settings)
        calc = calculate_sale(action, state["products"], settings)
        if auto_update_confirmed:
            action["confirmed_amount"] = calc["bonus_net"]
    elif action["type"] == ACTION_PREMIUM:
        calc = calculate_premium(action, state, settings)
        if auto_update_confirmed:
            action["confirmed_amount"] = calc["payout"]


def update_action(state: Dict[str, Any], user: Dict[str, Any], action_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    a = find_action(state, action_id)
    if not a:
        raise HTTPException(status_code=404, detail="Действие не найдено")
    if is_action_locked(a, state) and user["role"] != "director":
        raise HTTPException(status_code=400, detail="Действие заблокировано подтвержденной премией")
    if user["role"] != "director" and a.get("manager_login") != user["login"]:
        raise HTTPException(status_code=403, detail="Нет прав на редактирование")

    if user["role"] == "director":
        manager_login = payload.get("manager_login")
        if manager_login in MANAGER_LOGINS:
            a["manager_login"] = manager_login

    for field in ["date", "client", "city", "model", "task_description", "comment"]:
        if field in payload:
            if field == "date":
                a["date"] = safe_date(payload.get("date"))
            else:
                a[field] = str(payload.get(field) or "")

    if a["type"] == ACTION_DEMO:
        if "expenses" in payload and isinstance(payload["expenses"], list):
            a["expenses"] = payload["expenses"]
        if "criteria" in payload and isinstance(payload["criteria"], dict):
            a["criteria"] = payload["criteria"]
    elif a["type"] == ACTION_SALE:
        if "rows" in payload and isinstance(payload["rows"], list):
            a["rows"] = payload["rows"]
    elif a["type"] == ACTION_PREMIUM:
        pass

    if user["role"] == "director":
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
        item["current_level_index"] = int(current.get("level_index", 0))
        item["manager_comment"] = current.get("manager_comment", "")
        blocks[cr["block"]].append(item)
    return blocks


def serialize_action_detail(action: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    base = deepcopy(action)
    settings = state["settings"]
    base["is_locked"] = is_action_locked(action, state)
    if action["type"] == ACTION_DEMO:
        calc = calculate_demo(action, settings)
        return clean_json({"action": base, "kind": "demo", "calc": calc, "criteria_blocks": serialize_criteria_blocks(action, settings)})
    if action["type"] == ACTION_SALE:
        calc = calculate_sale(action, state["products"], settings)
        return clean_json({"action": base, "kind": "sale", "calc": calc})
    calc = calculate_premium(action, state, settings)
    return clean_json({"action": base, "kind": "premium", "calc": calc})


# ==============================
# API
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


app = FastAPI(title="ИРБИСТЕХ API", version="1.0.0")
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
    return clean_json({"ok": True, "db_message": msg, "actions": len(state.get("actions", []))})


@app.post("/api/auth/login")
def api_login(payload: LoginIn):
    user = authenticate(payload.login, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    return clean_json({"user": user})


@app.get("/api/bootstrap")
def api_bootstrap(user: Dict[str, Any] = Depends(get_user_from_header), manager_filter: str = Query("__all__")):
    state, msg = load_state_from_db()
    return clean_json({
        "user": user,
        "db_message": msg,
        "settings": state["settings"],
        "manager_choices": [{"value": "__all__", "label": "Все менеджеры"}] + [{"value": m, "label": USERS[m]["name"]} for m in MANAGER_LOGINS],
        "actions": visible_actions(user, state, manager_filter),
        "products_count": len(state.get("products", [])),
    })


@app.get("/api/actions")
def api_actions(user: Dict[str, Any] = Depends(get_user_from_header), manager_filter: str = Query("__all__")):
    state, _ = load_state_from_db()
    return clean_json({"items": visible_actions(user, state, manager_filter)})


@app.get("/api/actions/{action_id}")
def api_action_detail(action_id: str, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    action = find_action(state, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Действие не найдено")
    if user["role"] != "director" and action.get("manager_login") != user["login"]:
        raise HTTPException(status_code=403, detail="Нет доступа к действию")
    return serialize_action_detail(action, state)


@app.post("/api/actions/{action_id}/preview")
def api_action_preview(action_id: str, body: ActionPatchIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    preview_state = deepcopy(state)
    action = update_action(preview_state, user, action_id, body.payload)
    return serialize_action_detail(action, preview_state)


@app.post("/api/actions")
def api_create_action(body: CreateActionIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    action = add_action(state, user, body.action_type, body.manager_login)
    sync_action_after_edit(action, state)
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
    if user["role"] != "director" and action.get("manager_login") != user["login"]:
        raise HTTPException(status_code=403, detail="Нет прав")
    if is_action_locked(action, state):
        raise HTTPException(status_code=400, detail="Действие заблокировано")
    product = next((normalize_product(p, state["settings"]) for p in state.get("products", []) if str(p.get("product_id")) == body.product_id), None)
    if not product:
        raise HTTPException(status_code=400, detail="Товар не найден в справочнике")
    rows = sale_rows_to_records(action.get("rows", []), state["products"], state["settings"])
    rows.append(create_sale_row_from_product(product, 1, state["settings"]))
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
    rows = sale_rows_to_records(action.get("rows", []), state["products"], state["settings"])
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
    state, _ = load_state_from_db()
    action = find_action(state, action_id)
    if not action or action.get("type") != ACTION_DEMO:
        raise HTTPException(status_code=404, detail="Демонстрация не найдена")
    rows = calc_expenses_rows(action.get("expenses", []), state["settings"])
    rows.append({
        "row_order": len(rows) + 1,
        "article": f"Пользовательская строка {len(rows) + 1}",
        "qty": 0,
        "unit": "усл",
        "price_net": 0,
        "price_vat": 0,
        "amount_vat": 0,
        "calc_type": "direct",
        "is_custom": True,
        "comment": "",
    })
    action["expenses"] = rows
    sync_action_after_edit(action, state)
    persist_state_to_db(state)
    return serialize_action_detail(action, state)


@app.post("/api/actions/{action_id}/demo-expenses/command")
def api_demo_expense_command(action_id: str, body: DemoExpenseCommandIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    action = find_action(state, action_id)
    if not action or action.get("type") != ACTION_DEMO:
        raise HTTPException(status_code=404, detail="Демонстрация не найдена")
    rows = calc_expenses_rows(action.get("expenses", []), state["settings"])
    idx = body.index
    if idx < 0 or idx >= len(rows):
        raise HTTPException(status_code=400, detail="Неверный индекс строки")
    if body.command == "delete":
        rows.pop(idx)
    elif body.command == "up" and idx > 0:
        rows[idx - 1], rows[idx] = rows[idx], rows[idx - 1]
    elif body.command == "down" and idx < len(rows) - 1:
        rows[idx + 1], rows[idx] = rows[idx], rows[idx + 1]
    for i, row in enumerate(rows, start=1):
        row["row_order"] = i
    action["expenses"] = rows
    sync_action_after_edit(action, state)
    persist_state_to_db(state)
    return serialize_action_detail(action, state)


@app.get("/api/products")
def api_products(user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    return clean_json({"items": [normalize_product(p, state["settings"]) for p in state.get("products", [])]})


@app.get("/api/products/search")
def api_products_search(q: str = Query(""), user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    return clean_json({"items": search_products(q, state.get("products", []))})


@app.put("/api/products")
def api_products_save(body: ProductsBulkIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    assert_director(user)
    state, _ = load_state_from_db()
    state["products"] = [normalize_product(p, state["settings"]) for p in body.products]
    persist_state_to_db(state)
    return clean_json({"items": state["products"]})


@app.get("/api/products/template")
def api_products_template():
    cols = [
        "product_id", "sku", "name", "price_vat", "price_net", "min_price_net", "margin_pct", "comment"
    ]
    df = pd.DataFrame([{c: "" for c in cols}])
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="products")
    bio.seek(0)
    headers = {"Content-Disposition": 'attachment; filename="products_template.xlsx"'}
    return StreamingResponse(bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)


@app.post("/api/products/import")
def api_products_import(file: UploadFile = File(...), user: Dict[str, Any] = Depends(get_user_from_header)):
    assert_director(user)
    raw = file.file.read()
    if file.filename.lower().endswith(".csv"):
        df = pd.read_csv(io.BytesIO(raw))
    else:
        df = pd.read_excel(io.BytesIO(raw))
    products = [normalize_product(r, default_settings()) for r in df.to_dict("records") if str(r.get("name") or r.get("Наименование ТМЦ") or "").strip()]
    state, _ = load_state_from_db()
    state["products"] = products
    persist_state_to_db(state)
    return clean_json({"items": products, "count": len(products)})


@app.get("/api/settings")
def api_settings(user: Dict[str, Any] = Depends(get_user_from_header)):
    state, _ = load_state_from_db()
    return clean_json({"settings": state["settings"]})


@app.put("/api/settings")
def api_settings_save(body: SettingsIn, user: Dict[str, Any] = Depends(get_user_from_header)):
    assert_director(user)
    state, _ = load_state_from_db()
    state["settings"] = merge_settings(body.settings)
    persist_state_to_db(state)
    return clean_json({"settings": state["settings"]})


@app.exception_handler(Exception)
def all_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc), "trace": traceback.format_exc(limit=4)})
