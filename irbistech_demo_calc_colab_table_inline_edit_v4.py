# ============================================================
# ИРБИСТЕХ — калькулятор расходов на демонстрацию
# Вариант 1: табличный интерфейс с редактированием голубых ячеек прямо в таблице
# Формат: одна ячейка Google Colab
# Без Gradio-компонентов и без вкладок.
# Версия: без блока KPI, без строки общей форы от ООО; фиксированные параметры перенесены в красные настройки.
# ============================================================

from IPython.display import HTML, display

IRBIS_CALC_HTML = r'''
<div id="irbis-calc-v1-inline-edit" class="irbis-calc-app">
  <div class="calc-header">
    <div>
      <div class="brand-line">ООО «ИРБИСТЕХ»</div>
      <h1>Калькулятор расходов на демонстрацию</h1>
      <p>Голубые ячейки редактируются прямо в таблице. Красные настройки задаются отдельно выше калькулятора. Ед. изм. не редактируются.</p>
    </div>
    <button class="reset-btn" type="button" data-action="reset">Сбросить</button>
  </div>

  <div class="legend-row">
    <div class="legend-item blue-dot">Голубые ячейки — ввод пользователя</div>
    <div class="legend-item red-dot">Красные значения — настройки</div>
    <div class="legend-item gray-dot">Серые значения — формулы</div>
  </div>

  <section class="calc-card">
    <div class="section-title">Красные настройки</div>
    <div class="settings-grid">
      <label class="setting-card red-setting"><span>НДС, %</span><input data-red="vat_pct" value="22"></label>
      <label class="setting-card red-setting"><span>Налоги на ФОТ, %</span><input data-red="payroll_pct" value="30"></label>
      <label class="setting-card red-setting"><span>Работа водителя, руб. без НДС</span><input data-red="driver_rate_net" value="15"></label>
      <label class="setting-card red-setting"><span>Работа демонстратора, руб. без НДС</span><input data-red="demonstrator_rate_net" value="1350"></label>
      <label class="setting-card red-setting"><span>Демонстрация криобластера, руб. без НДС</span><input data-red="cryoblaster_demo_rate_net" value="4000"></label>
      <label class="setting-card red-setting"><span>Усложненные условия труда, руб. без НДС</span><input data-red="hard_conditions_rate_net" value="1700"></label>
      <label class="setting-card red-setting"><span>Ручная работа с кабелем, руб. без НДС</span><input data-red="cable_work_rate_net" value="3500"></label>
      <label class="setting-card red-setting"><span>Использование электрокатушки, руб. без НДС</span><input data-red="electro_reel_rate_net" value="1500"></label>
      <label class="setting-card red-setting"><span>Выгрузка и загрузка компрессора и электрокатушки, руб. без НДС</span><input data-red="unload_rate_net" value="1500"></label>
      <label class="setting-card red-setting"><span>Суточные, кол-во день х чел</span><input data-red="daily_allowance_qty" value="6"></label>
      <label class="setting-card red-setting"><span>Суточные, руб. без НДС</span><input data-red="daily_allowance_rate_net" value="1500"></label>
      <label class="setting-card red-setting"><span>Расход дизеля, л / 100 км</span><input data-red="diesel_l_per_100km" value="12"></label>
      <label class="setting-card red-setting"><span>Цена дизеля, руб. с НДС</span><input data-red="diesel_price_vat" value="78"></label>
      <label class="setting-card red-setting"><span>Амортизация Газели, руб. с НДС / км</span><input data-red="gazelle_amort_price_vat" value="10"></label>
      <label class="setting-card red-setting"><span>Доставка сухого льда в цех, руб. без НДС</span><input data-red="ice_delivery_rate_net" value="1500"></label>
    </div>
  </section>

  <section class="calc-card table-card">
    <div class="section-title">Расчет по строкам</div>
    <div class="hint">Кликните по голубой ячейке и введите число. Можно использовать запятую вместо точки.</div>
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
          <tr data-row="driver" class="row-input-red-price">
            <td class="col-article">Работа водителя</td>
            <td class="editable blue-cell" contenteditable="true" data-key="driver_km">1800</td>
            <td class="unit-cell">км</td>
            <td class="red-cell money-cell" data-out="driver.price_net"></td>
            <td class="formula-cell money-cell" data-out="driver.price_vat"></td>
            <td class="money-cell total-cell" data-out="driver.amount"></td>
          </tr>
          <tr data-row="demonstrator" class="row-input-red-price">
            <td class="col-article">Работа демонстратора</td>
            <td class="editable blue-cell" contenteditable="true" data-key="demonstrator_hours">16</td>
            <td class="unit-cell">часы</td>
            <td class="red-cell money-cell" data-out="demonstrator.price_net"></td>
            <td class="formula-cell money-cell" data-out="demonstrator.price_vat"></td>
            <td class="money-cell total-cell" data-out="demonstrator.amount"></td>
          </tr>
          <tr data-row="cryoblaster_demo" class="row-input-red-price">
            <td class="col-article">Демонстрация криобластера</td>
            <td class="editable blue-cell" contenteditable="true" data-key="cryoblaster_demo_qty">5</td>
            <td class="unit-cell">усл</td>
            <td class="red-cell money-cell" data-out="cryoblaster_demo.price_net"></td>
            <td class="formula-cell money-cell" data-out="cryoblaster_demo.price_vat"></td>
            <td class="money-cell total-cell" data-out="cryoblaster_demo.amount"></td>
          </tr>
          <tr data-row="hard_conditions" class="row-input-red-price">
            <td class="col-article">Усложненные условия труда</td>
            <td class="editable blue-cell" contenteditable="true" data-key="hard_conditions_qty">0</td>
            <td class="unit-cell">усл</td>
            <td class="red-cell money-cell" data-out="hard_conditions.price_net"></td>
            <td class="formula-cell money-cell" data-out="hard_conditions.price_vat"></td>
            <td class="money-cell total-cell" data-out="hard_conditions.amount"></td>
          </tr>
          <tr data-row="cable_work" class="row-input-red-price">
            <td class="col-article">Ручная работа с кабелем и шланга компрессора</td>
            <td class="editable blue-cell" contenteditable="true" data-key="cable_work_qty">0</td>
            <td class="unit-cell">усл</td>
            <td class="red-cell money-cell" data-out="cable_work.price_net"></td>
            <td class="formula-cell money-cell" data-out="cable_work.price_vat"></td>
            <td class="money-cell total-cell" data-out="cable_work.amount"></td>
          </tr>
          <tr data-row="electro_reel" class="row-input-red-price">
            <td class="col-article">Использование электрокатушки</td>
            <td class="editable blue-cell" contenteditable="true" data-key="electro_reel_qty">1</td>
            <td class="unit-cell">усл</td>
            <td class="red-cell money-cell" data-out="electro_reel.price_net"></td>
            <td class="formula-cell money-cell" data-out="electro_reel.price_vat"></td>
            <td class="money-cell total-cell" data-out="electro_reel.amount"></td>
          </tr>
          <tr data-row="unload" class="row-input-red-price">
            <td class="col-article">Выгрузка и загрузка компрессора и электрокатушки</td>
            <td class="editable blue-cell" contenteditable="true" data-key="unload_qty">0</td>
            <td class="unit-cell">усл</td>
            <td class="red-cell money-cell" data-out="unload.price_net"></td>
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
            <td class="editable blue-cell" contenteditable="true" data-key="hotel_manager_qty">3</td>
            <td class="unit-cell">день х чел</td>
            <td class="editable blue-cell money-edit" contenteditable="true" data-key="hotel_manager_rate_net">2800</td>
            <td class="formula-cell money-cell" data-out="hotel_manager.price_vat"></td>
            <td class="money-cell total-cell" data-out="hotel_manager.amount"></td>
          </tr>
          <tr data-row="hotel_driver" class="row-input-blue">
            <td class="col-article">Расходы на отель Водителя</td>
            <td class="editable blue-cell" contenteditable="true" data-key="hotel_driver_qty">3</td>
            <td class="unit-cell">день х чел</td>
            <td class="editable blue-cell money-edit" contenteditable="true" data-key="hotel_driver_rate_net">2800</td>
            <td class="formula-cell money-cell" data-out="hotel_driver.price_vat"></td>
            <td class="money-cell total-cell" data-out="hotel_driver.amount"></td>
          </tr>
          <tr data-row="transfer" class="row-input-blue">
            <td class="col-article">Расходы на переезд менеджера</td>
            <td class="editable blue-cell" contenteditable="true" data-key="transfer_qty">0</td>
            <td class="unit-cell">усл</td>
            <td class="editable blue-cell money-edit" contenteditable="true" data-key="transfer_rate_net">3000</td>
            <td class="formula-cell money-cell" data-out="transfer.price_vat"></td>
            <td class="money-cell total-cell" data-out="transfer.amount"></td>
          </tr>
          <tr data-row="toll" class="row-input-blue">
            <td class="col-article">Расходы на платную дорогу</td>
            <td class="editable blue-cell" contenteditable="true" data-key="toll_qty">0</td>
            <td class="unit-cell">усл</td>
            <td class="editable blue-cell money-edit" contenteditable="true" data-key="toll_rate_net">0</td>
            <td class="formula-cell money-cell" data-out="toll.price_vat"></td>
            <td class="money-cell total-cell" data-out="toll.amount"></td>
          </tr>
          <tr data-row="daily_allowance" class="row-fixed-red-price">
            <td class="col-article">Суточные для командировки</td>
            <td class="red-cell qty-cell" data-out="daily_allowance.qty"></td>
            <td class="unit-cell">день х чел</td>
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
            <td class="editable blue-cell" contenteditable="true" data-key="ice_qty">300</td>
            <td class="unit-cell">кг</td>
            <td class="formula-cell money-cell" data-out="ice_purchase.price_net"></td>
            <td class="editable blue-cell money-edit" contenteditable="true" data-key="ice_price_vat">90</td>
            <td class="money-cell total-cell" data-out="ice_purchase.amount"></td>
          </tr>
          <tr data-row="ice_delivery" class="row-input-red-price">
            <td class="col-article">Расходы на доставку сухого льда в цех</td>
            <td class="editable blue-cell" contenteditable="true" data-key="ice_delivery_qty">0</td>
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
        </tbody>
      </table>
    </div>
  </section>
</div>

<style>
#irbis-calc-v1-inline-edit {
  --bg: #f4f7fb;
  --card: #ffffff;
  --line: #d7e0ec;
  --line-soft: #edf2f7;
  --text: #0f172a;
  --muted: #5b6b83;
  --accent1: #0b2f4d;
  --accent2: #13527c;
  --accent3: #0f8a5f;
  --blue: rgba(0, 176, 240, .16);
  --blue-strong: rgba(0, 176, 240, .42);
  --red: rgba(239, 68, 68, .13);
  --red-strong: rgba(239, 68, 68, .36);
  --gray: rgba(148, 163, 184, .12);
  font-family: Arial, Helvetica, sans-serif;
  background: var(--bg);
  color: var(--text);
  padding: 14px;
  border-radius: 22px;
  box-sizing: border-box;
}
#irbis-calc-v1-inline-edit * { box-sizing: border-box; }
#irbis-calc-v1-inline-edit .calc-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  background: linear-gradient(135deg, var(--accent1) 0%, var(--accent2) 62%, var(--accent3) 100%);
  color: white;
  border-radius: 20px;
  padding: 18px 20px;
  box-shadow: 0 12px 28px rgba(15,23,42,.14);
  margin-bottom: 12px;
}
#irbis-calc-v1-inline-edit .brand-line {
  font-size: 12px;
  letter-spacing: .08em;
  text-transform: uppercase;
  opacity: .82;
  margin-bottom: 4px;
}
#irbis-calc-v1-inline-edit h1 {
  margin: 0;
  font-size: 25px;
  line-height: 1.16;
}
#irbis-calc-v1-inline-edit .calc-header p {
  margin: 7px 0 0;
  max-width: 980px;
  opacity: .9;
  line-height: 1.35;
}
#irbis-calc-v1-inline-edit .reset-btn {
  border: 1px solid rgba(255,255,255,.55);
  background: rgba(255,255,255,.14);
  color: white;
  padding: 10px 14px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}
#irbis-calc-v1-inline-edit .reset-btn:hover { background: rgba(255,255,255,.22); }
#irbis-calc-v1-inline-edit .legend-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 0 0 10px;
}
#irbis-calc-v1-inline-edit .legend-item {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 7px 11px 7px 26px;
  position: relative;
  color: var(--muted);
  font-size: 13px;
}
#irbis-calc-v1-inline-edit .legend-item::before {
  content: "";
  width: 10px;
  height: 10px;
  border-radius: 50%;
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
}
#irbis-calc-v1-inline-edit .blue-dot::before { background: #00b0f0; }
#irbis-calc-v1-inline-edit .red-dot::before { background: #ef4444; }
#irbis-calc-v1-inline-edit .gray-dot::before { background: #94a3b8; }
#irbis-calc-v1-inline-edit .calc-card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 10px 22px rgba(15,23,42,.06);
  margin-bottom: 10px;
}
#irbis-calc-v1-inline-edit .section-title {
  font-size: 18px;
  font-weight: 800;
  color: #123b63;
  margin-bottom: 8px;
}
#irbis-calc-v1-inline-edit .settings-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(150px, 1fr));
  gap: 8px;
}
#irbis-calc-v1-inline-edit .setting-card {
  background: #f8fbff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 9px 10px;
}
#irbis-calc-v1-inline-edit .red-setting { background: var(--red); border-color: var(--red-strong); }
#irbis-calc-v1-inline-edit .setting-card span {
  display: block;
  color: var(--muted);
  font-size: 12px;
  line-height: 1.22;
  margin-bottom: 5px;
}
#irbis-calc-v1-inline-edit .setting-card input {
  width: 100%;
  border: 1px solid rgba(15,23,42,.16);
  border-radius: 9px;
  padding: 7px 8px;
  font: 700 14px/1.2 Arial, sans-serif;
  color: var(--text);
  background: rgba(255,255,255,.76);
  outline: none;
}
#irbis-calc-v1-inline-edit .setting-card input:focus { border-color: #13527c; box-shadow: 0 0 0 3px rgba(19,82,124,.12); }
#irbis-calc-v1-inline-edit .hint {
  color: var(--muted);
  font-size: 13px;
  margin: -3px 0 9px;
}
#irbis-calc-v1-inline-edit .table-wrap {
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: 14px;
}
#irbis-calc-v1-inline-edit .calc-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
  min-width: 980px;
}
#irbis-calc-v1-inline-edit .calc-table th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #eef4fb;
  color: #123b63;
  text-align: left;
  border-bottom: 1px solid var(--line);
  padding: 10px 12px;
  white-space: nowrap;
}
#irbis-calc-v1-inline-edit .calc-table td {
  border-bottom: 1px solid var(--line-soft);
  padding: 9px 12px;
  vertical-align: middle;
}
#irbis-calc-v1-inline-edit .col-article { min-width: 330px; font-weight: 700; }
#irbis-calc-v1-inline-edit .money-cell,
#irbis-calc-v1-inline-edit .qty-cell,
#irbis-calc-v1-inline-edit .unit-cell,
#irbis-calc-v1-inline-edit .editable { text-align: right; white-space: nowrap; }
#irbis-calc-v1-inline-edit .unit-cell { color: #334155; font-weight: 600; }
#irbis-calc-v1-inline-edit .blue-cell {
  background: var(--blue);
  border-left: 1px solid var(--blue-strong);
  border-right: 1px solid var(--blue-strong);
  font-weight: 800;
  cursor: text;
}
#irbis-calc-v1-inline-edit .blue-cell:hover { background: rgba(0,176,240,.24); }
#irbis-calc-v1-inline-edit .blue-cell:focus {
  outline: 2px solid #00a3df;
  outline-offset: -2px;
  background: rgba(0,176,240,.28);
}
#irbis-calc-v1-inline-edit .red-cell { background: var(--red); border-color: var(--red-strong); }
#irbis-calc-v1-inline-edit .formula-cell { background: #fff; }
#irbis-calc-v1-inline-edit .row-auto td { background: var(--gray); }
#irbis-calc-v1-inline-edit .row-auto .formula-cell { background: var(--gray); }
#irbis-calc-v1-inline-edit .row-auto .red-cell { background: var(--red); border-color: var(--red-strong); }
#irbis-calc-v1-inline-edit .total-cell { font-weight: 800; color: #0f172a; }
#irbis-calc-v1-inline-edit .row-total td {
  border-top: 2px solid #123b63;
  background: #f8fbff;
  font-weight: 900;
  font-size: 14px;
}
#irbis-calc-v1-inline-edit .grand-total { color: #0b2f4d; }
@media (max-width: 980px) {
  #irbis-calc-v1-inline-edit .settings-grid { grid-template-columns: repeat(2, minmax(150px, 1fr)); }
  #irbis-calc-v1-inline-edit .calc-header { flex-direction: column; }
}
</style>

<script>
(function () {
  const root = document.getElementById('irbis-calc-v1-inline-edit');
  if (!root) return;

  const defaultsRed = {
    vat_pct: 22,
    payroll_pct: 30,
    driver_rate_net: 15,
    demonstrator_rate_net: 1350,
    cryoblaster_demo_rate_net: 4000,
    hard_conditions_rate_net: 1700,
    cable_work_rate_net: 3500,
    electro_reel_rate_net: 1500,
    unload_rate_net: 1500,
    daily_allowance_qty: 6,
    daily_allowance_rate_net: 1500,
    diesel_l_per_100km: 12,
    diesel_price_vat: 78,
    gazelle_amort_price_vat: 10,
    ice_delivery_rate_net: 1500
  };

  const defaultsBlue = {
    driver_km: 1800,
    demonstrator_hours: 16,
    cryoblaster_demo_qty: 5,
    hard_conditions_qty: 0,
    cable_work_qty: 0,
    electro_reel_qty: 1,
    unload_qty: 0,
    hotel_manager_qty: 3,
    hotel_manager_rate_net: 2800,
    hotel_driver_qty: 3,
    hotel_driver_rate_net: 2800,
    transfer_qty: 0,
    transfer_rate_net: 3000,
    toll_qty: 0,
    toll_rate_net: 0,
    ice_qty: 300,
    ice_price_vat: 90,
    ice_delivery_qty: 0
  };


  const red = Object.assign({}, defaultsRed);
  const blue = Object.assign({}, defaultsBlue);

  function parseNumber(value, fallback = 0) {
    if (value === undefined || value === null) return fallback;
    let s = String(value)
      .replace(/\u00a0/g, ' ')
      .replace(/\s+/g, '')
      .replace(',', '.')
      .replace(/[^0-9.+\-]/g, '');
    if (s === '' || s === '-' || s === '+') return fallback;
    const n = Number(s);
    return Number.isFinite(n) ? n : fallback;
  }

  function money(value) {
    const n = Number.isFinite(Number(value)) ? Number(value) : 0;
    return n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function qty(value) {
    const n = Number.isFinite(Number(value)) ? Number(value) : 0;
    if (Math.abs(n - Math.round(n)) < 1e-9) {
      return Math.round(n).toLocaleString('ru-RU', { maximumFractionDigits: 0 });
    }
    return n.toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 4 });
  }

  function netToVat(net, vat) { return Number(net || 0) * (1 + vat); }
  function vatToNet(vatValue, vat) { return (1 + vat) ? Number(vatValue || 0) / (1 + vat) : 0; }

  function setOut(path, value, formatter) {
    const el = root.querySelector('[data-out="' + path + '"]');
    if (el) el.textContent = formatter(value);
  }

  function setTotalTable(value) {
    root.querySelectorAll('[data-total="total_table"]').forEach(el => {
      el.textContent = money(value) + ' ₽';
    });
  }

  function setLabel(key, value) {
    root.querySelectorAll('[data-label="' + key + '"]').forEach(el => {
      el.textContent = qty(value);
    });
  }

  function row(priceNet, priceVat, amount, rowName, quantity) {
    setOut(rowName + '.qty', quantity || 0, qty);
    setOut(rowName + '.price_net', priceNet, money);
    setOut(rowName + '.price_vat', priceVat, money);
    setOut(rowName + '.amount', amount, money);
    return { priceNet, priceVat, amount, quantity: quantity || 0 };
  }

  function calculate() {
    const vat = red.vat_pct / 100;
    const payrollRate = red.payroll_pct / 100;
    setLabel('diesel_l_per_100km', red.diesel_l_per_100km);
    const rows = {};

    rows.driver = row(red.driver_rate_net, netToVat(red.driver_rate_net, vat), blue.driver_km * netToVat(red.driver_rate_net, vat), 'driver');
    rows.demonstrator = row(red.demonstrator_rate_net, netToVat(red.demonstrator_rate_net, vat), blue.demonstrator_hours * netToVat(red.demonstrator_rate_net, vat), 'demonstrator');
    rows.cryoblaster_demo = row(red.cryoblaster_demo_rate_net, netToVat(red.cryoblaster_demo_rate_net, vat), blue.cryoblaster_demo_qty * netToVat(red.cryoblaster_demo_rate_net, vat), 'cryoblaster_demo');
    rows.hard_conditions = row(red.hard_conditions_rate_net, netToVat(red.hard_conditions_rate_net, vat), blue.hard_conditions_qty * netToVat(red.hard_conditions_rate_net, vat), 'hard_conditions');
    rows.cable_work = row(red.cable_work_rate_net, netToVat(red.cable_work_rate_net, vat), blue.cable_work_qty * netToVat(red.cable_work_rate_net, vat), 'cable_work');
    rows.electro_reel = row(red.electro_reel_rate_net, netToVat(red.electro_reel_rate_net, vat), blue.electro_reel_qty * netToVat(red.electro_reel_rate_net, vat), 'electro_reel');
    rows.unload = row(red.unload_rate_net, netToVat(red.unload_rate_net, vat), blue.unload_qty * netToVat(red.unload_rate_net, vat), 'unload');

    const payrollBase = rows.driver.amount + rows.demonstrator.amount + rows.cryoblaster_demo.amount + rows.hard_conditions.amount + rows.cable_work.amount + rows.electro_reel.amount + rows.unload.amount;
    rows.payroll_tax = row(0, 0, payrollBase * payrollRate, 'payroll_tax', 0);

    rows.hotel_manager = row(blue.hotel_manager_rate_net, netToVat(blue.hotel_manager_rate_net, vat), blue.hotel_manager_qty * netToVat(blue.hotel_manager_rate_net, vat), 'hotel_manager');
    rows.hotel_driver = row(blue.hotel_driver_rate_net, netToVat(blue.hotel_driver_rate_net, vat), blue.hotel_driver_qty * netToVat(blue.hotel_driver_rate_net, vat), 'hotel_driver');
    rows.transfer = row(blue.transfer_rate_net, netToVat(blue.transfer_rate_net, vat), blue.transfer_qty * netToVat(blue.transfer_rate_net, vat), 'transfer');
    rows.toll = row(blue.toll_rate_net, netToVat(blue.toll_rate_net, vat), blue.toll_qty * netToVat(blue.toll_rate_net, vat), 'toll');
    rows.daily_allowance = row(red.daily_allowance_rate_net, netToVat(red.daily_allowance_rate_net, vat), red.daily_allowance_qty * netToVat(red.daily_allowance_rate_net, vat), 'daily_allowance', red.daily_allowance_qty);

    const dieselQty = blue.driver_km / 100 * red.diesel_l_per_100km;
    rows.diesel = row(vatToNet(red.diesel_price_vat, vat), red.diesel_price_vat, dieselQty * red.diesel_price_vat, 'diesel', dieselQty);

    rows.gazelle_amort = row(vatToNet(red.gazelle_amort_price_vat, vat), red.gazelle_amort_price_vat, blue.driver_km * red.gazelle_amort_price_vat, 'gazelle_amort', blue.driver_km);

    rows.ice_purchase = row(vatToNet(blue.ice_price_vat, vat), blue.ice_price_vat, blue.ice_qty * blue.ice_price_vat, 'ice_purchase');
    rows.ice_delivery = row(red.ice_delivery_rate_net, netToVat(red.ice_delivery_rate_net, vat), blue.ice_delivery_qty * netToVat(red.ice_delivery_rate_net, vat), 'ice_delivery');

    const total = Object.values(rows).reduce((s, r) => s + r.amount, 0);
    setTotalTable(total);
  }

  function syncRedFromInputs() {
    root.querySelectorAll('[data-red]').forEach(input => {
      const key = input.getAttribute('data-red');
      red[key] = parseNumber(input.value, defaultsRed[key]);
    });
  }

  function syncBlueFromCells() {
    root.querySelectorAll('[data-key]').forEach(cell => {
      const key = cell.getAttribute('data-key');
      blue[key] = parseNumber(cell.textContent, defaultsBlue[key]);
    });
  }

  function reset() {
    Object.keys(defaultsRed).forEach(key => {
      red[key] = defaultsRed[key];
      const input = root.querySelector('[data-red="' + key + '"]');
      if (input) input.value = String(defaultsRed[key]);
    });
    Object.keys(defaultsBlue).forEach(key => {
      blue[key] = defaultsBlue[key];
      const cell = root.querySelector('[data-key="' + key + '"]');
      if (cell) cell.textContent = qty(defaultsBlue[key]);
    });
    calculate();
  }

  root.querySelectorAll('[data-red]').forEach(input => {
    input.addEventListener('input', function () {
      syncRedFromInputs();
      calculate();
    });
  });

  root.querySelectorAll('[data-key]').forEach(cell => {
    cell.addEventListener('input', function () {
      const key = cell.getAttribute('data-key');
      blue[key] = parseNumber(cell.textContent, defaultsBlue[key]);
      calculate();
    });
    cell.addEventListener('blur', function () {
      const key = cell.getAttribute('data-key');
      blue[key] = parseNumber(cell.textContent, defaultsBlue[key]);
      cell.textContent = qty(blue[key]);
      calculate();
    });
    cell.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') {
        event.preventDefault();
        cell.blur();
      }
    });
  });

  const resetBtn = root.querySelector('[data-action="reset"]');
  if (resetBtn) resetBtn.addEventListener('click', reset);

  syncRedFromInputs();
  syncBlueFromCells();
  calculate();
})();
</script>
'''

display(HTML(IRBIS_CALC_HTML))
