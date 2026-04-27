import copy
import html
import json


COMPANY_SUPPORT_ARTICLE = "Общая фора (помощь от ООО)"

FIXED_ROW_SPECS = [
    {"id": "driver", "article": "Работа водителя", "qty_field": "driver_km", "qty_mode": "blue", "price_field": "driver_rate_net", "price_mode": "red_net"},
    {"id": "demonstrator", "article": "Работа демонстратора", "qty_field": "demonstrator_hours", "qty_mode": "blue", "price_field": "demonstrator_rate_net", "price_mode": "red_net"},
    {"id": "cryoblaster_demo", "article": "Демонстрация криобластера", "qty_field": "cryoblaster_demo_qty", "qty_mode": "blue", "price_field": "cryoblaster_demo_rate_net", "price_mode": "red_net"},
    {"id": "hard_conditions", "article": "Усложненные условия труда", "qty_field": "hard_conditions_qty", "qty_mode": "blue", "price_field": "hard_conditions_rate_net", "price_mode": "red_net"},
    {"id": "cable_work", "article": "Ручная работа с кабелем и шланга компрессора", "qty_field": "cable_work_qty", "qty_mode": "blue", "price_field": "cable_work_rate_net", "price_mode": "red_net"},
    {"id": "electro_reel", "article": "Использование электрокатушки", "qty_field": "electro_reel_qty", "qty_mode": "blue", "price_field": "electro_reel_rate_net", "price_mode": "blue_net"},
    {"id": "unload", "article": "Выгрузка и загрузка компрессора и электрокатушки", "qty_field": "unload_qty", "qty_mode": "blue", "price_field": "unload_rate_net", "price_mode": "blue_net"},
    {"id": "payroll_tax", "article": "Налоги на ФОТ", "qty_field": None, "qty_mode": "formula", "price_field": None, "price_mode": "formula"},
    {"id": "hotel_manager", "article": "Расходы на отель Менеджера", "qty_field": "hotel_manager_qty", "qty_mode": "blue", "price_field": "hotel_manager_rate_net", "price_mode": "blue_net"},
    {"id": "hotel_driver", "article": "Расходы на отель Водителя", "qty_field": "hotel_driver_qty", "qty_mode": "blue", "price_field": "hotel_driver_rate_net", "price_mode": "blue_net"},
    {"id": "transfer", "article": "Расходы на переезд менеджера", "qty_field": "transfer_qty", "qty_mode": "blue", "price_field": "transfer_rate_net", "price_mode": "blue_net"},
    {"id": "toll", "article": "Расходы на платную дорогу", "qty_field": "toll_qty", "qty_mode": "blue", "price_field": "toll_rate_net", "price_mode": "blue_net"},
    {"id": "daily_allowance", "article": "Суточные для командировки", "qty_field": "daily_allowance_qty", "qty_mode": "red", "price_field": "daily_allowance_rate_net", "price_mode": "red_net"},
    {"id": "diesel", "article": "Расходы на дизель (12 л/100км), л", "qty_field": None, "qty_mode": "formula", "price_field": "diesel_price_vat", "price_mode": "red_vat"},
    {"id": "gazelle_amort", "article": "Амортизация Газели", "qty_field": None, "qty_mode": "formula", "price_field": "gazelle_amort_price_vat", "price_mode": "red_vat"},
    {"id": "ice_purchase", "article": "Расходы на закупку сухого льда", "qty_field": "ice_qty", "qty_mode": "blue", "price_field": "ice_price_vat", "price_mode": "blue_vat"},
    {"id": "ice_delivery", "article": "Расходы на доставку сухого льда в цех", "qty_field": "ice_delivery_qty", "qty_mode": "blue", "price_field": "ice_delivery_rate_net", "price_mode": "red_net"},
]

FIXED_ARTICLES = {item["article"] for item in FIXED_ROW_SPECS}
FIXED_ARTICLE_TO_SPEC = {item["article"]: item for item in FIXED_ROW_SPECS}


def _to_float(value, default=0.0):
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("\xa0", " ").replace(" ", "").replace(",", ".")
    if not text:
        return default
    try:
        return float(text)
    except Exception:
        return default


def _expense_settings_map(settings):
    return {item["article"]: item for item in settings.get("expense_settings", [])}


def _default_row(article, settings):
    expense_settings = _expense_settings_map(settings)
    setting = expense_settings.get(article, {})
    return {
        "article": article,
        "qty": _to_float(setting.get("qty_default"), 0),
        "unit": str(setting.get("unit", "")),
        "price_net": _to_float(setting.get("price_net_default"), 0),
        "price_vat": _to_float(setting.get("price_vat_default"), 0),
        "comment": str(setting.get("comment", "")),
    }


def _rows_by_article(action):
    rows = {}
    for row in action.get("expenses", []) or []:
        article = str(row.get("article", "")).strip()
        if article:
            rows[article] = row
    return rows


def default_calc_state(settings):
    expense_settings = _expense_settings_map(settings)
    red = {
        "vat_pct": round(_to_float(settings.get("vat_rate"), 0.22) * 100, 4),
        "payroll_pct": round(_to_float(settings.get("payroll_tax_rate"), 0.30) * 100, 4),
        "diesel_l_per_100km": _to_float(settings.get("diesel_l_per_100km"), 12),
        "company_support_vat": _to_float(settings.get("company_support_vat"), 30000),
    }
    blue = {}
    comments = {}
    for spec in FIXED_ROW_SPECS:
        row = _default_row(spec["article"], settings)
        comments[spec["article"]] = row.get("comment", "")
        if spec["qty_mode"] == "red":
            red[spec["qty_field"]] = _to_float(row.get("qty"), 0)
        elif spec["qty_mode"] == "blue":
            blue[spec["qty_field"]] = _to_float(row.get("qty"), 0)
        if spec["price_mode"] == "red_net":
            red[spec["price_field"]] = _to_float(row.get("price_net"), 0)
        elif spec["price_mode"] == "red_vat":
            red[spec["price_field"]] = _to_float(row.get("price_vat"), 0)
        elif spec["price_mode"] == "blue_net":
            blue[spec["price_field"]] = _to_float(row.get("price_net"), 0)
        elif spec["price_mode"] == "blue_vat":
            blue[spec["price_field"]] = _to_float(row.get("price_vat"), 0)
    return {"red": red, "blue": blue, "comments": comments}


def split_calc_state(action, settings):
    state = default_calc_state(settings)
    rows = _rows_by_article(action)
    custom_rows = []
    for article, row in rows.items():
        if article == COMPANY_SUPPORT_ARTICLE:
            continue
        if article in FIXED_ARTICLES:
            spec = FIXED_ARTICLE_TO_SPEC[article]
            state["comments"][article] = str(row.get("comment", state["comments"].get(article, "")) or "")
            if spec["qty_mode"] == "blue" and spec["qty_field"]:
                state["blue"][spec["qty_field"]] = _to_float(row.get("qty"), state["blue"].get(spec["qty_field"], 0))
            if spec["price_mode"] == "blue_net" and spec["price_field"]:
                state["blue"][spec["price_field"]] = _to_float(row.get("price_net"), state["blue"].get(spec["price_field"], 0))
            if spec["price_mode"] == "blue_vat" and spec["price_field"]:
                state["blue"][spec["price_field"]] = _to_float(row.get("price_vat"), state["blue"].get(spec["price_field"], 0))
        else:
            custom_rows.append(copy.deepcopy(row))
    return state, custom_rows


def merge_calc_state(raw_state, settings):
    state = default_calc_state(settings)
    if not isinstance(raw_state, dict):
        return state
    if isinstance(raw_state.get("comments"), dict):
        for article, value in raw_state["comments"].items():
            if article in state["comments"]:
                state["comments"][article] = str(value or "")
    if isinstance(raw_state.get("blue"), dict):
        for key, value in raw_state["blue"].items():
            if key in state["blue"]:
                state["blue"][key] = _to_float(value, state["blue"][key])
    return state


def fixed_rows_from_state(raw_state, settings):
    state = merge_calc_state(raw_state, settings)
    expense_settings = _expense_settings_map(settings)
    rows = []
    for index, spec in enumerate(FIXED_ROW_SPECS, start=1):
        setting = expense_settings.get(spec["article"], {})
        row = {
            "article": spec["article"],
            "qty": 0,
            "unit": str(setting.get("unit", "")),
            "price_net": 0,
            "price_vat": 0,
            "amount_vat": 0,
            "calc_type": str(setting.get("calc_type", "direct")),
            "is_custom": False,
            "comment": state["comments"].get(spec["article"], str(setting.get("comment", ""))),
            "row_order": index,
        }
        if spec["qty_mode"] == "blue" and spec["qty_field"]:
            row["qty"] = _to_float(state["blue"].get(spec["qty_field"]), 0)
        elif spec["qty_mode"] == "red" and spec["qty_field"]:
            row["qty"] = _to_float(state["red"].get(spec["qty_field"]), _to_float(setting.get("qty_default"), 0))
        if spec["price_mode"] == "blue_net" and spec["price_field"]:
            row["price_net"] = _to_float(state["blue"].get(spec["price_field"]), 0)
        elif spec["price_mode"] == "blue_vat" and spec["price_field"]:
            row["price_vat"] = _to_float(state["blue"].get(spec["price_field"]), 0)
        elif spec["price_mode"] == "red_net" and spec["price_field"]:
            row["price_net"] = _to_float(state["red"].get(spec["price_field"]), _to_float(setting.get("price_net_default"), 0))
        elif spec["price_mode"] == "red_vat" and spec["price_field"]:
            row["price_vat"] = _to_float(state["red"].get(spec["price_field"]), _to_float(setting.get("price_vat_default"), 0))
        rows.append(row)
    return rows


def build_demo_calc_html(raw_state, settings):
    state = merge_calc_state(raw_state, settings)
    state_json = json.dumps(state, ensure_ascii=False)
    root_id = "irbis-demo-calc-widget"
    rows_html = f"""
      <tr data-row="driver" class="row-input-red-price">
        <td class="col-article">Работа водителя</td>
        <td class="editable blue-cell" contenteditable="true" data-key="driver_km">{html.escape(_fmt_qty(state['blue']['driver_km']))}</td>
        <td class="unit-cell">км</td>
        <td class="red-cell money-cell" data-out="driver.price_net"></td>
        <td class="formula-cell money-cell" data-out="driver.price_vat"></td>
        <td class="money-cell total-cell" data-out="driver.amount"></td>
      </tr>
      <tr data-row="demonstrator" class="row-input-red-price">
        <td class="col-article">Работа демонстратора</td>
        <td class="editable blue-cell" contenteditable="true" data-key="demonstrator_hours">{html.escape(_fmt_qty(state['blue']['demonstrator_hours']))}</td>
        <td class="unit-cell">часы</td>
        <td class="red-cell money-cell" data-out="demonstrator.price_net"></td>
        <td class="formula-cell money-cell" data-out="demonstrator.price_vat"></td>
        <td class="money-cell total-cell" data-out="demonstrator.amount"></td>
      </tr>
      <tr data-row="cryoblaster_demo" class="row-input-red-price">
        <td class="col-article">Демонстрация криобластера</td>
        <td class="editable blue-cell" contenteditable="true" data-key="cryoblaster_demo_qty">{html.escape(_fmt_qty(state['blue']['cryoblaster_demo_qty']))}</td>
        <td class="unit-cell">усл</td>
        <td class="red-cell money-cell" data-out="cryoblaster_demo.price_net"></td>
        <td class="formula-cell money-cell" data-out="cryoblaster_demo.price_vat"></td>
        <td class="money-cell total-cell" data-out="cryoblaster_demo.amount"></td>
      </tr>
      <tr data-row="hard_conditions" class="row-input-red-price">
        <td class="col-article">Усложненные условия труда</td>
        <td class="editable blue-cell" contenteditable="true" data-key="hard_conditions_qty">{html.escape(_fmt_qty(state['blue']['hard_conditions_qty']))}</td>
        <td class="unit-cell">усл</td>
        <td class="red-cell money-cell" data-out="hard_conditions.price_net"></td>
        <td class="formula-cell money-cell" data-out="hard_conditions.price_vat"></td>
        <td class="money-cell total-cell" data-out="hard_conditions.amount"></td>
      </tr>
      <tr data-row="cable_work" class="row-input-red-price">
        <td class="col-article">Ручная работа с кабелем и шланга компрессора</td>
        <td class="editable blue-cell" contenteditable="true" data-key="cable_work_qty">{html.escape(_fmt_qty(state['blue']['cable_work_qty']))}</td>
        <td class="unit-cell">усл</td>
        <td class="red-cell money-cell" data-out="cable_work.price_net"></td>
        <td class="formula-cell money-cell" data-out="cable_work.price_vat"></td>
        <td class="money-cell total-cell" data-out="cable_work.amount"></td>
      </tr>
      <tr data-row="electro_reel" class="row-input-blue">
        <td class="col-article">Использование электрокатушки</td>
        <td class="editable blue-cell" contenteditable="true" data-key="electro_reel_qty">{html.escape(_fmt_qty(state['blue']['electro_reel_qty']))}</td>
        <td class="unit-cell">усл</td>
        <td class="editable blue-cell money-edit" contenteditable="true" data-key="electro_reel_rate_net">{html.escape(_fmt_qty(state['blue']['electro_reel_rate_net']))}</td>
        <td class="formula-cell money-cell" data-out="electro_reel.price_vat"></td>
        <td class="money-cell total-cell" data-out="electro_reel.amount"></td>
      </tr>
      <tr data-row="unload" class="row-input-blue">
        <td class="col-article">Выгрузка и загрузка компрессора и электрокатушки</td>
        <td class="editable blue-cell" contenteditable="true" data-key="unload_qty">{html.escape(_fmt_qty(state['blue']['unload_qty']))}</td>
        <td class="unit-cell">усл</td>
        <td class="editable blue-cell money-edit" contenteditable="true" data-key="unload_rate_net">{html.escape(_fmt_qty(state['blue']['unload_rate_net']))}</td>
        <td class="formula-cell money-cell" data-out="unload.price_vat"></td>
        <td class="money-cell total-cell" data-out="unload.amount"></td>
      </tr>
      <tr data-row="payroll_tax" class="row-auto">
        <td class="col-article">Налоги на ФОТ</td>
        <td class="formula-cell qty-cell" data-out="payroll_tax.qty"></td>
        <td class="unit-cell">усл</td>
        <td class="formula-cell money-cell" data-out="payroll_tax.price_net"></td>
        <td class="formula-cell money-cell" data-out="payroll_tax.price_vat"></td>
        <td class="money-cell total-cell" data-out="payroll_tax.amount"></td>
      </tr>
      <tr data-row="hotel_manager" class="row-input-blue">
        <td class="col-article">Расходы на отель Менеджера</td>
        <td class="editable blue-cell" contenteditable="true" data-key="hotel_manager_qty">{html.escape(_fmt_qty(state['blue']['hotel_manager_qty']))}</td>
        <td class="unit-cell">день x чел</td>
        <td class="editable blue-cell money-edit" contenteditable="true" data-key="hotel_manager_rate_net">{html.escape(_fmt_qty(state['blue']['hotel_manager_rate_net']))}</td>
        <td class="formula-cell money-cell" data-out="hotel_manager.price_vat"></td>
        <td class="money-cell total-cell" data-out="hotel_manager.amount"></td>
      </tr>
      <tr data-row="hotel_driver" class="row-input-blue">
        <td class="col-article">Расходы на отель Водителя</td>
        <td class="editable blue-cell" contenteditable="true" data-key="hotel_driver_qty">{html.escape(_fmt_qty(state['blue']['hotel_driver_qty']))}</td>
        <td class="unit-cell">день x чел</td>
        <td class="editable blue-cell money-edit" contenteditable="true" data-key="hotel_driver_rate_net">{html.escape(_fmt_qty(state['blue']['hotel_driver_rate_net']))}</td>
        <td class="formula-cell money-cell" data-out="hotel_driver.price_vat"></td>
        <td class="money-cell total-cell" data-out="hotel_driver.amount"></td>
      </tr>
      <tr data-row="transfer" class="row-input-blue">
        <td class="col-article">Расходы на переезд менеджера</td>
        <td class="editable blue-cell" contenteditable="true" data-key="transfer_qty">{html.escape(_fmt_qty(state['blue']['transfer_qty']))}</td>
        <td class="unit-cell">усл</td>
        <td class="editable blue-cell money-edit" contenteditable="true" data-key="transfer_rate_net">{html.escape(_fmt_qty(state['blue']['transfer_rate_net']))}</td>
        <td class="formula-cell money-cell" data-out="transfer.price_vat"></td>
        <td class="money-cell total-cell" data-out="transfer.amount"></td>
      </tr>
      <tr data-row="toll" class="row-input-blue">
        <td class="col-article">Расходы на платную дорогу</td>
        <td class="editable blue-cell" contenteditable="true" data-key="toll_qty">{html.escape(_fmt_qty(state['blue']['toll_qty']))}</td>
        <td class="unit-cell">усл</td>
        <td class="editable blue-cell money-edit" contenteditable="true" data-key="toll_rate_net">{html.escape(_fmt_qty(state['blue']['toll_rate_net']))}</td>
        <td class="formula-cell money-cell" data-out="toll.price_vat"></td>
        <td class="money-cell total-cell" data-out="toll.amount"></td>
      </tr>
      <tr data-row="daily_allowance" class="row-fixed-red-price">
        <td class="col-article">Суточные для командировки</td>
        <td class="red-cell qty-cell" data-out="daily_allowance.qty"></td>
        <td class="unit-cell">день x чел</td>
        <td class="red-cell money-cell" data-out="daily_allowance.price_net"></td>
        <td class="formula-cell money-cell" data-out="daily_allowance.price_vat"></td>
        <td class="money-cell total-cell" data-out="daily_allowance.amount"></td>
      </tr>
      <tr data-row="diesel" class="row-auto">
        <td class="col-article">Расходы на дизель (<span data-label="diesel_l_per_100km">12</span> л/100км), л</td>
        <td class="formula-cell qty-cell" data-out="diesel.qty"></td>
        <td class="unit-cell">литры</td>
        <td class="formula-cell money-cell" data-out="diesel.price_net"></td>
        <td class="red-cell money-cell" data-out="diesel.price_vat"></td>
        <td class="money-cell total-cell" data-out="diesel.amount"></td>
      </tr>
      <tr data-row="gazelle_amort" class="row-auto">
        <td class="col-article">Амортизация Газели</td>
        <td class="formula-cell qty-cell" data-out="gazelle_amort.qty"></td>
        <td class="unit-cell">км</td>
        <td class="formula-cell money-cell" data-out="gazelle_amort.price_net"></td>
        <td class="red-cell money-cell" data-out="gazelle_amort.price_vat"></td>
        <td class="money-cell total-cell" data-out="gazelle_amort.amount"></td>
      </tr>
      <tr data-row="ice_purchase" class="row-input-blue-vat-price">
        <td class="col-article">Расходы на закупку сухого льда</td>
        <td class="editable blue-cell" contenteditable="true" data-key="ice_qty">{html.escape(_fmt_qty(state['blue']['ice_qty']))}</td>
        <td class="unit-cell">кг</td>
        <td class="formula-cell money-cell" data-out="ice_purchase.price_net"></td>
        <td class="editable blue-cell money-edit" contenteditable="true" data-key="ice_price_vat">{html.escape(_fmt_qty(state['blue']['ice_price_vat']))}</td>
        <td class="money-cell total-cell" data-out="ice_purchase.amount"></td>
      </tr>
      <tr data-row="ice_delivery" class="row-input-red-price">
        <td class="col-article">Расходы на доставку сухого льда в цех</td>
        <td class="editable blue-cell" contenteditable="true" data-key="ice_delivery_qty">{html.escape(_fmt_qty(state['blue']['ice_delivery_qty']))}</td>
        <td class="unit-cell">усл</td>
        <td class="red-cell money-cell" data-out="ice_delivery.price_net"></td>
        <td class="formula-cell money-cell" data-out="ice_delivery.price_vat"></td>
        <td class="money-cell total-cell" data-out="ice_delivery.amount"></td>
      </tr>
      <tr class="row-total">
        <td class="col-article">ИТОГО расходы на демонстрацию</td>
        <td></td><td></td><td></td><td></td>
        <td class="money-cell grand-total" data-total="total_table">0,00</td>
      </tr>
    """
    return f"""
<div id="{root_id}" class="irbis-demo-calc-widget">
  <div class="calc-header">
    <div>
      <div class="brand-line">Смета демонстрации</div>
      <h2>Калькулятор расходов</h2>
      <p>Заполните вводные менеджера, проверьте системные ставки и итоговую сумму расходов.</p>
    </div>
    <button class="reset-btn" type="button" data-action="reset">Сбросить</button>
  </div>

  <div class="legend-row">
    <div class="legend-item blue-dot">Ввод менеджера</div>
    <div class="legend-item red-dot">Настройки системы</div>
    <div class="legend-item gray-dot">Расчетные значения</div>
  </div>

  <section class="calc-card table-card">
    <div class="section-title">Расходы по статьям</div>
    <div class="hint">Редактируемые ячейки выглядят как поля ввода. Формулы и системные ставки пересчитываются автоматически.</div>
    <div class="table-wrap">
      <table class="calc-table" aria-label="Калькулятор расходов на демонстрацию">
        <thead>
          <tr>
            <th>Статья расхода</th>
            <th>Кол-во</th>
            <th>Ед. изм.</th>
            <th>Цена, руб. без НДС</th>
            <th>Цена, руб. с НДС</th>
            <th>Сумма затрат, руб. с НДС</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
    </div>
    <div class="support-line">
      <span>Общая фора / помощь ООО</span>
      <b data-out="support.value"></b>
    </div>
  </section>
</div>

<style>
#{root_id} {{
  --calc-bg: #f8fafc;
  --calc-card: #ffffff;
  --calc-line: #e2e8f0;
  --calc-line-strong: #cbd5e1;
  --calc-text: #0f172a;
  --calc-muted: #64748b;
  --calc-primary: #2563eb;
  --calc-primary-dark: #1d4ed8;
  --calc-primary-soft: #eff6ff;
  --calc-green: #10b981;
  --calc-green-soft: #ecfdf5;
  --calc-red: #ef4444;
  --calc-red-soft: #fef2f2;
  --calc-gray: #f1f5f9;
  --calc-gray-soft: #f8fafc;
  --calc-blue-cell: #e0f2fe;
  --calc-blue-border: #7dd3fc;
  --calc-red-cell: #fee2e2;
  --calc-red-border: #fecaca;
  --calc-radius-sm: 10px;
  --calc-radius-md: 14px;
  --calc-radius-lg: 18px;
  --calc-shadow-sm: 0 1px 2px rgba(15,23,42,.06), 0 1px 3px rgba(15,23,42,.08);
  --calc-shadow-focus: 0 0 0 4px rgba(37,99,235,.14);
}}
#{root_id} {{
  color: var(--calc-text);
  font-family: Arial, sans-serif;
}}
#{root_id} * {{ box-sizing: border-box; }}
#{root_id} .calc-header {{
  display:flex;
  justify-content:space-between;
  gap:14px;
  align-items:center;
  padding:14px 16px;
  border:1px solid rgba(37,99,235,.18);
  border-radius:var(--calc-radius-lg);
  background:
    radial-gradient(circle at 92% 8%, rgba(16,185,129,.16), transparent 14rem),
    linear-gradient(135deg,#ffffff 0%,#eff6ff 100%);
  color:var(--calc-text);
  box-shadow:var(--calc-shadow-sm);
  margin-bottom:12px;
}}
#{root_id} .calc-header::after {{
  content:none !important;
  display:none !important;
}}
#{root_id} .brand-line {{
  display:inline-flex;
  align-items:center;
  width:fit-content;
  border:1px solid rgba(37,99,235,.18);
  border-radius:999px;
  background:rgba(37,99,235,.08);
  color:var(--calc-primary-dark);
  font-size:11px;
  font-weight:900;
  letter-spacing:.06em;
  line-height:1;
  padding:6px 9px;
  text-transform:uppercase;
  margin-bottom:8px;
}}
#{root_id} h2 {{
  margin:0;
  font-size:20px;
  line-height:1.15;
  letter-spacing:-.03em;
  color:var(--calc-text);
  font-weight:900;
}}
#{root_id} .calc-header p {{
  margin:5px 0 0;
  color:var(--calc-muted);
  font-size:13px;
  line-height:1.45;
  max-width:720px;
}}
#{root_id} .reset-btn {{
  border:1px solid var(--calc-line);
  background:#fff;
  color:var(--calc-text);
  border-radius:var(--calc-radius-md);
  box-shadow:var(--calc-shadow-sm);
  padding:9px 14px;
  min-height:38px;
  font-size:13px;
  font-weight:800;
  cursor:pointer;
  transition:background .16s ease, border-color .16s ease, color .16s ease, box-shadow .16s ease, transform .16s ease;
}}
#{root_id} .reset-btn:hover {{
  background:var(--calc-primary-soft);
  border-color:rgba(37,99,235,.34);
  color:var(--calc-primary-dark);
  transform:translateY(-1px);
}}
#{root_id} .reset-btn:focus-visible {{
  outline:none;
  box-shadow:var(--calc-shadow-focus);
}}
#{root_id} .legend-row {{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-bottom:12px;
}}
#{root_id} .legend-item {{
  display:flex;
  align-items:center;
  gap:7px;
  background:#fff;
  border:1px solid var(--calc-line);
  border-radius:999px;
  box-shadow:0 1px 2px rgba(15,23,42,.04);
  padding:6px 10px;
  color:var(--calc-muted);
  font-size:12px;
  font-weight:700;
  line-height:1.2;
}}
#{root_id} .legend-item::before {{
  content:"";
  width:9px;
  height:9px;
  border-radius:999px;
  flex:0 0 auto;
}}
#{root_id} .blue-dot::before {{ background:#0284c7; }}
#{root_id} .red-dot::before {{ background:var(--calc-red); }}
#{root_id} .gray-dot::before {{ background:#94a3b8; }}
#{root_id} .calc-card {{
  background:var(--calc-card);
  border:1px solid var(--calc-line);
  border-radius:var(--calc-radius-lg);
  padding:16px;
  box-shadow:var(--calc-shadow-sm);
}}
#{root_id} .section-title {{
  color:var(--calc-text);
  font-size:18px;
  font-weight:900;
  letter-spacing:-.03em;
  line-height:1.2;
  margin-bottom:6px;
}}
#{root_id} .hint {{
  color:var(--calc-muted);
  font-size:12px;
  line-height:1.45;
  margin-bottom:12px;
}}
#{root_id} .table-wrap {{
  overflow:auto;
  border:1px solid var(--calc-line);
  border-radius:var(--calc-radius-md);
  background:#fff;
  max-width:100%;
  -webkit-overflow-scrolling:touch;
}}
#{root_id} .calc-table {{
  width:100%;
  border-collapse:separate;
  border-spacing:0;
  background:#fff;
  min-width:1040px;
  font-size:13px;
}}
#{root_id} .calc-table th {{
  position:sticky;
  top:0;
  z-index:2;
  background:var(--calc-gray-soft);
  color:var(--calc-muted);
  padding:11px 12px;
  font-size:11px;
  font-weight:900;
  text-transform:uppercase;
  letter-spacing:.04em;
  border-bottom:1px solid var(--calc-line);
  white-space:nowrap;
}}
#{root_id} .calc-table th:first-child {{
  text-align:left;
  left:0;
  z-index:3;
}}
#{root_id} .calc-table th:not(:first-child) {{
  text-align:right;
}}
#{root_id} .calc-table td {{
  padding:9px 12px;
  border-bottom:1px solid #eef2f7;
  color:var(--calc-text);
  height:44px;
  vertical-align:middle;
}}
#{root_id} .calc-table td:first-child {{
  background:#fff;
  left:0;
  position:sticky;
  z-index:1;
}}
#{root_id} .calc-table tbody tr:nth-child(even) td {{
  background:#fcfdff;
}}
#{root_id} .calc-table tbody tr:nth-child(even) td:first-child {{
  background:#fcfdff;
}}
#{root_id} .calc-table tbody tr:hover td {{
  background:var(--calc-primary-soft);
}}
#{root_id} .calc-table tbody tr:hover td:first-child {{
  background:var(--calc-primary-soft);
}}
#{root_id} .calc-table tbody tr:hover .blue-cell {{
  background:#dbeafe;
}}
#{root_id} .calc-table tbody tr:hover .red-cell {{
  background:var(--calc-red-cell);
}}
#{root_id} .col-article {{
  min-width:330px;
  max-width:420px;
  font-weight:800;
  line-height:1.3;
  text-align:left;
  white-space:normal;
  box-shadow:1px 0 0 #eef2f7;
}}
#{root_id} .money-cell,
#{root_id} .qty-cell,
#{root_id} .unit-cell,
#{root_id} .editable {{ text-align:right; white-space:nowrap; }}
#{root_id} .unit-cell {{ color:var(--calc-muted); font-weight:700; }}
#{root_id} .blue-cell {{
  background:var(--calc-blue-cell);
  border:1px solid var(--calc-blue-border);
  border-radius:var(--calc-radius-sm);
  outline:none;
  color:#0c4a6e;
  font-weight:850;
  min-width:78px;
  min-height:32px;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.62);
  cursor:text;
  transition:background .16s ease, border-color .16s ease, box-shadow .16s ease;
}}
#{root_id} .money-edit {{
  min-width:104px;
}}
#{root_id} .blue-cell:hover {{
  background:#bae6fd;
  border-color:#38bdf8;
}}
#{root_id} .blue-cell:focus {{
  background:#fff;
  border-color:var(--calc-primary);
  box-shadow:var(--calc-shadow-focus);
}}
#{root_id} .editable:focus-visible,
#{root_id} .reset-btn:focus-visible {{
  outline:none;
  box-shadow:var(--calc-shadow-focus);
}}
#{root_id} .red-cell {{
  background:var(--calc-red-cell);
  border:1px solid var(--calc-red-border);
  border-radius:var(--calc-radius-sm);
  color:#991b1b;
  font-weight:850;
  min-width:92px;
  min-height:32px;
}}
#{root_id} .formula-cell {{
  background:var(--calc-gray-soft);
  border-radius:var(--calc-radius-sm);
  color:#475569;
  font-weight:750;
  min-width:92px;
  min-height:32px;
}}
#{root_id} .row-auto td {{ background:var(--calc-gray-soft); }}
#{root_id} .row-auto .formula-cell {{ background:var(--calc-gray); }}
#{root_id} .row-auto .red-cell {{ background:var(--calc-red-cell); }}
#{root_id} .total-cell {{ font-weight:900; color:var(--calc-text); }}
#{root_id} .row-total td {{
  border-top:2px solid var(--calc-primary);
  border-bottom:0;
  background:linear-gradient(180deg,#eff6ff 0%,#dbeafe 100%) !important;
  font-weight:900;
  font-size:14px;
  height:52px;
}}
#{root_id} .row-total td:first-child {{
  background:linear-gradient(180deg,#eff6ff 0%,#dbeafe 100%) !important;
}}
#{root_id} .row-total .col-article {{
  color:var(--calc-primary-dark);
  text-transform:uppercase;
  letter-spacing:.02em;
}}
#{root_id} .grand-total {{
  color:var(--calc-primary-dark);
  font-size:16px;
}}
#{root_id} .support-line {{
  align-items:center;
  display:flex;
  justify-content:space-between;
  gap:12px;
  margin-top:12px;
  background:var(--calc-green-soft);
  border:1px solid rgba(16,185,129,.24);
  border-radius:var(--calc-radius-md);
  color:#047857;
  font-size:13px;
  font-weight:800;
  padding:12px 14px;
}}
#{root_id} .support-line b {{
  color:#065f46;
  font-size:15px;
  font-weight:900;
  white-space:nowrap;
}}
@media (max-width: 980px) {{
  #{root_id} .calc-header {{
    align-items:flex-start;
    flex-direction:column;
  }}
  #{root_id} .reset-btn {{
    width:100%;
  }}
  #{root_id} .calc-card {{
    padding:12px;
  }}
  #{root_id} .table-wrap {{
    overflow-x:auto;
    -webkit-overflow-scrolling:touch;
  }}
  #{root_id} .support-line {{
    align-items:flex-start;
    flex-direction:column;
  }}
}}
@media (max-width: 768px) {{
  #{root_id} .calc-header {{
    padding:12px;
  }}
  #{root_id} h2 {{
    font-size:18px;
  }}
  #{root_id} .legend-row {{
    gap:6px;
  }}
  #{root_id} .legend-item {{
    font-size:11px;
    padding:6px 8px;
  }}
  #{root_id} .calc-table {{
    min-width:960px;
    font-size:12px;
  }}
  #{root_id} .calc-table th,
  #{root_id} .calc-table td {{
    padding:8px 10px;
  }}
  #{root_id} .col-article {{
    min-width:280px;
  }}
}}
</style>

<script>
(function() {{
  const root = document.getElementById('{root_id}');
  if (!root) return;
  const initialState = {state_json};
  const defaults = JSON.parse(JSON.stringify(initialState));
  const red = Object.assign({{}}, initialState.red || {{}});
  const blue = Object.assign({{}}, initialState.blue || {{}});
  const comments = Object.assign({{}}, initialState.comments || {{}});

  function hiddenField() {{
    return document.querySelector('#demo-calc-state-json textarea, #demo-calc-state-json input');
  }}

  function syncHidden() {{
    const hidden = hiddenField();
    if (!hidden) return;
    const payload = JSON.stringify({{ blue, comments }});
    if (hidden.value !== payload) {{
      hidden.value = payload;
      hidden.dispatchEvent(new Event('input', {{ bubbles: true }}));
      hidden.dispatchEvent(new Event('change', {{ bubbles: true }}));
    }}
  }}

  function parseNumber(value, fallback = 0) {{
    if (value === undefined || value === null) return fallback;
    const s = String(value).replace(/\\u00a0/g, ' ').replace(/\\s+/g, '').replace(',', '.').replace(/[^0-9.+\\-]/g, '');
    if (!s || s === '-' || s === '+') return fallback;
    const n = Number(s);
    return Number.isFinite(n) ? n : fallback;
  }}

  function money(value) {{
    const n = Number.isFinite(Number(value)) ? Number(value) : 0;
    return n.toLocaleString('ru-RU', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});
  }}

  function qty(value) {{
    const n = Number.isFinite(Number(value)) ? Number(value) : 0;
    if (Math.abs(n - Math.round(n)) < 1e-9) {{
      return Math.round(n).toLocaleString('ru-RU', {{ maximumFractionDigits: 0 }});
    }}
    return n.toLocaleString('ru-RU', {{ minimumFractionDigits: 0, maximumFractionDigits: 4 }});
  }}

  function netToVat(net, vat) {{ return Number(net || 0) * (1 + vat); }}
  function vatToNet(vatValue, vat) {{ return (1 + vat) ? Number(vatValue || 0) / (1 + vat) : 0; }}

  function setOut(path, value, formatter) {{
    const el = root.querySelector('[data-out=\"' + path + '\"]');
    if (el) el.textContent = formatter(value);
  }}

  function setTotalTable(value) {{
    root.querySelectorAll('[data-total=\"total_table\"]').forEach(el => {{
      el.textContent = money(value) + ' ₽';
    }});
  }}

  function setLabel(key, value) {{
    root.querySelectorAll('[data-label=\"' + key + '\"]').forEach(el => {{
      el.textContent = qty(value);
    }});
  }}

  function row(priceNet, priceVat, amount, rowName, quantity) {{
    setOut(rowName + '.qty', quantity || 0, qty);
    setOut(rowName + '.price_net', priceNet, money);
    setOut(rowName + '.price_vat', priceVat, money);
    setOut(rowName + '.amount', amount, money);
    return {{ priceNet, priceVat, amount, quantity: quantity || 0 }};
  }}

  function calculate() {{
    const vat = parseNumber(red.vat_pct, 22) / 100;
    const payrollRate = parseNumber(red.payroll_pct, 30) / 100;
    setLabel('diesel_l_per_100km', red.diesel_l_per_100km);
    const rows = {{}};

    rows.driver = row(red.driver_rate_net, netToVat(red.driver_rate_net, vat), blue.driver_km * netToVat(red.driver_rate_net, vat), 'driver', blue.driver_km);
    rows.demonstrator = row(red.demonstrator_rate_net, netToVat(red.demonstrator_rate_net, vat), blue.demonstrator_hours * netToVat(red.demonstrator_rate_net, vat), 'demonstrator', blue.demonstrator_hours);
    rows.cryoblaster_demo = row(red.cryoblaster_demo_rate_net, netToVat(red.cryoblaster_demo_rate_net, vat), blue.cryoblaster_demo_qty * netToVat(red.cryoblaster_demo_rate_net, vat), 'cryoblaster_demo', blue.cryoblaster_demo_qty);
    rows.hard_conditions = row(red.hard_conditions_rate_net, netToVat(red.hard_conditions_rate_net, vat), blue.hard_conditions_qty * netToVat(red.hard_conditions_rate_net, vat), 'hard_conditions', blue.hard_conditions_qty);
    rows.cable_work = row(red.cable_work_rate_net, netToVat(red.cable_work_rate_net, vat), blue.cable_work_qty * netToVat(red.cable_work_rate_net, vat), 'cable_work', blue.cable_work_qty);
    rows.electro_reel = row(red.electro_reel_rate_net, netToVat(red.electro_reel_rate_net, vat), blue.electro_reel_qty * netToVat(red.electro_reel_rate_net, vat), 'electro_reel', blue.electro_reel_qty);
    rows.unload = row(red.unload_rate_net, netToVat(red.unload_rate_net, vat), blue.unload_qty * netToVat(red.unload_rate_net, vat), 'unload', blue.unload_qty);

    const payrollBase = rows.driver.amount + rows.demonstrator.amount + rows.cryoblaster_demo.amount + rows.hard_conditions.amount + rows.cable_work.amount + rows.electro_reel.amount + rows.unload.amount;
    rows.payroll_tax = row(0, 0, payrollBase * payrollRate, 'payroll_tax', 0);

    rows.hotel_manager = row(blue.hotel_manager_rate_net, netToVat(blue.hotel_manager_rate_net, vat), blue.hotel_manager_qty * netToVat(blue.hotel_manager_rate_net, vat), 'hotel_manager', blue.hotel_manager_qty);
    rows.hotel_driver = row(blue.hotel_driver_rate_net, netToVat(blue.hotel_driver_rate_net, vat), blue.hotel_driver_qty * netToVat(blue.hotel_driver_rate_net, vat), 'hotel_driver', blue.hotel_driver_qty);
    rows.transfer = row(blue.transfer_rate_net, netToVat(blue.transfer_rate_net, vat), blue.transfer_qty * netToVat(blue.transfer_rate_net, vat), 'transfer', blue.transfer_qty);
    rows.toll = row(blue.toll_rate_net, netToVat(blue.toll_rate_net, vat), blue.toll_qty * netToVat(blue.toll_rate_net, vat), 'toll', blue.toll_qty);
    rows.daily_allowance = row(red.daily_allowance_rate_net, netToVat(red.daily_allowance_rate_net, vat), red.daily_allowance_qty * netToVat(red.daily_allowance_rate_net, vat), 'daily_allowance', red.daily_allowance_qty);

    const dieselQty = blue.driver_km / 100 * red.diesel_l_per_100km;
    rows.diesel = row(vatToNet(red.diesel_price_vat, vat), red.diesel_price_vat, dieselQty * red.diesel_price_vat, 'diesel', dieselQty);
    rows.gazelle_amort = row(vatToNet(red.gazelle_amort_price_vat, vat), red.gazelle_amort_price_vat, blue.driver_km * red.gazelle_amort_price_vat, 'gazelle_amort', blue.driver_km);
    rows.ice_purchase = row(vatToNet(blue.ice_price_vat, vat), blue.ice_price_vat, blue.ice_qty * blue.ice_price_vat, 'ice_purchase', blue.ice_qty);
    rows.ice_delivery = row(red.ice_delivery_rate_net, netToVat(red.ice_delivery_rate_net, vat), blue.ice_delivery_qty * netToVat(red.ice_delivery_rate_net, vat), 'ice_delivery', blue.ice_delivery_qty);

    const total = Object.values(rows).reduce((sum, item) => sum + item.amount, 0);
    setTotalTable(total);
    setOut('support.value', red.company_support_vat, money);
    syncHidden();
  }}

  function reset() {{
    Object.keys(defaults.blue || {{}}).forEach((key) => {{
      blue[key] = defaults.blue[key];
      const cell = root.querySelector('[data-key=\"' + key + '\"]');
      if (cell) cell.textContent = qty(defaults.blue[key]);
    }});
    calculate();
  }}

  root.querySelectorAll('[data-key]').forEach((cell) => {{
    cell.addEventListener('input', function() {{
      const key = cell.getAttribute('data-key');
      blue[key] = parseNumber(cell.textContent, blue[key] || 0);
      calculate();
    }});
    cell.addEventListener('blur', function() {{
      const key = cell.getAttribute('data-key');
      blue[key] = parseNumber(cell.textContent, blue[key] || 0);
      cell.textContent = qty(blue[key]);
      calculate();
    }});
    cell.addEventListener('keydown', function(event) {{
      if (event.key === 'Enter') {{
        event.preventDefault();
        cell.blur();
      }}
    }});
  }});

  const resetBtn = root.querySelector('[data-action=\"reset\"]');
  if (resetBtn) resetBtn.addEventListener('click', reset);

  syncHidden();
  calculate();
}})();
</script>
"""


def _fmt_qty(value):
    number = _to_float(value, 0)
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    text = f"{number:.4f}".rstrip("0").rstrip(".")
    return text or "0"
