import React, { useEffect, useMemo, useRef, useState } from "react";
import { api } from "./api";

const ACTION_DEMO = "Проведенная демонстрация";
const ACTION_SALE = "Проданное оборудование";
const ACTION_PREMIUM = "Выплата премии";

const clone = (v) => JSON.parse(JSON.stringify(v ?? null));
const money = (v) => `${Number(v || 0).toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽`;
const money0 = (v) => `${Number(v || 0).toLocaleString("ru-RU", { maximumFractionDigits: 0 })} ₽`;
const formatDateRu = (v) => {
  const raw = String(v || "").slice(0, 10);
  const m = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  return m ? `${m[3]}.${m[2]}.${m[1]}` : raw;
};
const dateInputValue = (v) => {
  const raw = String(v || "").slice(0, 10);
  return /^\d{4}-\d{2}-\d{2}$/.test(raw) ? raw : "";
};
const oneDecimalComma = (v, fallback = 0) => {
  const n = plainNum(v);
  const value = Number.isFinite(n) ? n : fallback;
  return value.toLocaleString("ru-RU", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
};
const round2 = (v) => Math.round((Number(v) || 0) * 100) / 100;
const percent = (v) => `${(Number(v || 0) * 100).toFixed(1)}%`;
const pctUi = (v) => {
  const n = Number(v || 0);
  return Number.isFinite(n) ? Number((n * 100).toFixed(2)) : 0;
};
const fromPctUi = (v) => {
  const s = String(v ?? "").replace(",", ".");
  const n = Number(s);
  return Number.isFinite(n) ? n / 100 : 0;
};
const plainNum = (v) => {
  const s = String(v ?? "").replace(",", ".");
  const n = Number(s);
  return Number.isFinite(n) ? n : 0;
};
const officeNames = (settings) => (settings?.office_cities || ["Казань", "Москва"]).map((x) => (typeof x === "string" ? x : x.name)).filter(Boolean);
const expenseKey = (row, fallback = "") => String(row?.code || row?.row_code || `${row?.article || ""}::${row?.unit || ""}::${fallback}`);
const clampActionListWidth = (value) => Math.min(46, Math.max(24, Number(value) || 31));
const savedActionListWidth = () => {
  if (typeof window === "undefined") return null;
  const stored = Number(window.localStorage.getItem("demos2sales.actionListWidthPct"));
  return Number.isFinite(stored) && stored > 0 ? clampActionListWidth(stored) : null;
};

const readSavedUser = () => {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem("demos2sales.currentUser");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
};
const readSavedSidebarCollapsed = () => {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem("demos2sales.sidebarCollapsed") === "1";
};
const productColumnsStorageKey = (login) => `demos2sales.products.columnWidths.${login || "director"}`;
const defaultProductColumnWidths = {
  order: 74,
  sku: 170,
  name: 360,
  price_vat: 160,
  price_net: 160,
  mr: 150,
  pr: 170,
  st: 155,
};
const readProductColumnWidths = (login) => {
  if (typeof window === "undefined") return { ...defaultProductColumnWidths };
  try {
    const raw = window.localStorage.getItem(productColumnsStorageKey(login));
    return { ...defaultProductColumnWidths, ...(raw ? JSON.parse(raw) : {}) };
  } catch {
    return { ...defaultProductColumnWidths };
  }
};
const stopTagForCriterion = (code) => {
  if (["P2", "P4", "P5"].includes(String(code))) return "SOFT_STOP";
  if (String(code) === "P8") return "HARD_STOP";
  return "";
};
const levelStopTag = (code, score) => (Number(score || 0) <= 0 ? stopTagForCriterion(code) : "");
const levelEfficiencyExample = (idx, count, score) => {
  if (Number(score || 0) <= 0) return "Применяется, когда условие не выполнено или не подтверждено.";
  const ratio = count <= 1 ? 1 : idx / Math.max(1, count - 1);
  if (ratio < 0.34) return "Пример: условие выполнено частично, без полного подтверждения.";
  if (ratio < 0.67) return "Пример: условие подтверждено, но есть ограничения.";
  return "Пример: условие подтверждено полностью, эффект высокий.";
};

function useNotice() {
  const [notice, setNotice] = useState({ type: "", text: "" });
  const show = (text, type = "info") => setNotice({ text, type });
  return { notice, show, clear: () => setNotice({ type: "", text: "" }) };
}

function App() {
  const [user, setUser] = useState(() => readSavedUser());
  const [managerChoices, setManagerChoices] = useState([]);
  const [managerFilter, setManagerFilter] = useState(() => {
    const saved = readSavedUser();
    return saved?.role === "manager" ? saved.login : "__all__";
  });
  const [mainTab, setMainTab] = useState("actions");
  const [actions, setActions] = useState([]);
  const [hideOldActions, setHideOldActions] = useState(false);
  const [selectedActionId, setSelectedActionId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [editor, setEditor] = useState(null);
  const [settings, setSettings] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [productSearch, setProductSearch] = useState("");
  const [productSuggestions, setProductSuggestions] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState("");
  const [demoTab, setDemoTab] = useState("estimate");
  const [actionListWidth, setActionListWidth] = useState(savedActionListWidth);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(readSavedSidebarCollapsed);
  const [loginForm, setLoginForm] = useState({ login: "", password: "" });
  const { notice, show, clear } = useNotice();

  const ui = settings?.ui || {};
  const appFont = settings?.font_family && settings.font_family !== "Arial" ? settings.font_family : "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", Arial, sans-serif";
  const detailKind = detail?.kind;
  const actionList = actions || [];
  const resolvedActionListWidth = actionListWidth ?? clampActionListWidth(ui.action_list_width_pct || 31);
  const listTotals = useMemo(() => actionList.reduce((acc, item) => {
    const confirmed = item.is_director_confirmed ? Number(item.confirmed_amount ?? item.display_amount ?? 0) : 0;
    if (item.type === ACTION_SALE) acc.cash += confirmed;
    if (item.type === ACTION_DEMO) acc.vic += confirmed;
    if (item.type === ACTION_PREMIUM) acc.profit += confirmed;
    return acc;
  }, { profit: 0, cash: 0, vic: 0 }), [actionList]);

  const pageStyle = useMemo(() => ({
    fontFamily: appFont,
    "--action-list-width": `${resolvedActionListWidth}%`,
    "--criteria-name-width": `${ui.criteria_name_width_pct || 20}fr`,
    "--criteria-level-width": `${ui.criteria_levels_width_pct || 60}fr`,
    "--criteria-comment-width": `${ui.criteria_comment_width_pct || 20}fr`,
    "--font-base": `${ui.font_base_px || 13}px`,
    "--font-title": `${ui.font_title_px || 18}px`,
    "--card-padding": `${ui.card_padding_px || 10}px`,
    "--field-gap": `${ui.field_gap_px || 8}px`,
  }), [appFont, resolvedActionListWidth, ui]);

  const startPanelResize = (event) => {
    if (event.button !== 0) return;
    const layout = event.currentTarget.parentElement;
    const rect = layout.getBoundingClientRect();
    const onMove = (moveEvent) => {
      const next = clampActionListWidth(((moveEvent.clientX - rect.left) / rect.width) * 100);
      setActionListWidth(next);
      window.localStorage.setItem("demos2sales.actionListWidthPct", String(next));
    };
    const onUp = () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      document.body.classList.remove("is-resizing-panels");
    };
    event.preventDefault();
    document.body.classList.add("is-resizing-panels");
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp, { once: true });
  };

  const loadBootstrap = async (u = user, filter = managerFilter, hideOld = hideOldActions) => {
    if (!u) return;
    setLoading(true);
    try {
      const data = await api.bootstrap(u.login, filter, hideOld);
      setManagerChoices(data.manager_choices || []);
      setSettings(data.settings);
      setActions(data.actions || []);
      if (!selectedActionId && data.actions?.length) {
        setSelectedActionId(data.actions[0].id);
      } else if (selectedActionId && !data.actions.find((a) => a.id === selectedActionId)) {
        setSelectedActionId(data.actions?.[0]?.id || null);
      }
      if (u.role === "director") {
        const p = await api.products(u.login);
        setProducts(p.items || []);
      } else {
        setProducts([]);
      }
      clear();
    } catch (e) {
      show(e.message, "error");
      if (String(e.message || "").includes("Неизвестный пользователь")) {
        window.localStorage.removeItem("demos2sales.currentUser");
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) loadBootstrap(user, managerFilter, hideOldActions);
  }, [user, managerFilter, hideOldActions]);

  useEffect(() => {
    if (user?.role !== "director" && mainTab !== "actions") {
      setMainTab("actions");
    }
  }, [user, mainTab]);

  useEffect(() => {
    if (user && selectedActionId) {
      api.actionDetail(user.login, selectedActionId)
        .then((res) => {
          setDetail(res);
          setEditor(clone(res.action));
          if (res.kind !== "demo") setDemoTab("estimate");
        })
        .catch((e) => show(e.message, "error"));
    } else {
      setDetail(null);
      setEditor(null);
    }
  }, [user, selectedActionId]);

  useEffect(() => {
    if (!user || productSearch.trim().length < 3 || detailKind !== "sale") {
      setProductSuggestions([]);
      return undefined;
    }
    const h = setTimeout(() => {
      api.searchProducts(user.login, productSearch).then((res) => {
        setProductSuggestions(res.items || []);
      }).catch(() => setProductSuggestions([]));
    }, 200);
    return () => clearTimeout(h);
  }, [productSearch, user, detailKind]);

  useEffect(() => {
    if (!user || !editor?.id || !detailKind || !["demo", "sale"].includes(detailKind)) return undefined;
    let payload = null;
    if (detailKind === "demo") {
      payload = {
        date: editor.date,
        client: editor.client,
        city: editor.city,
        model: editor.model,
        task_description: editor.task_description,
        comment: editor.comment,
        demo_meta: editor.demo_meta || {},
        expenses: editor.expenses || [],
        criteria: editor.criteria || {},
      };
    }
    if (detailKind === "sale") {
      payload = {
        date: editor.date,
        client: editor.client,
        comment: editor.comment,
        rows: editor.rows || [],
      };
    }
    let cancelled = false;
    const h = setTimeout(() => {
      api.previewAction(user.login, editor.id, payload)
        .then((res) => { if (!cancelled) setDetail(res); })
        .catch(() => {});
    }, 250);
    return () => { cancelled = true; clearTimeout(h); };
  }, [editor, user, detailKind]);

  const onLogin = async (e) => {
    e.preventDefault();
    try {
      const data = await api.login(loginForm.login, loginForm.password);
      window.localStorage.setItem("demos2sales.currentUser", JSON.stringify(data.user));
      setUser(data.user);
      setManagerFilter(data.user.role === "director" ? "__all__" : data.user.login);
      show(`Вход выполнен: ${data.user.name}`, "success");
    } catch (e2) {
      show(e2.message, "error");
    }
  };

  const refreshActionsOnly = async (keepId = selectedActionId) => {
    if (!user) return;
    const res = await api.actions(user.login, managerFilter, hideOldActions);
    setActions(res.items || []);
    if (keepId && res.items?.find((a) => a.id === keepId)) setSelectedActionId(keepId);
    else setSelectedActionId(res.items?.[0]?.id || null);
  };

  const createAction = async (actionType) => {
    if (!user) return;
    try {
      const res = await api.createAction(user.login, actionType, user.role === "director" && managerFilter !== "__all__" ? managerFilter : undefined);
      setSelectedActionId(res.action.action.id);
      await refreshActionsOnly(res.action.action.id);
      show(`Добавлено действие: ${actionType}`, "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const saveCurrentAction = async () => {
    if (!user || !editor?.id) return;
    try {
      const res = await api.updateAction(user.login, editor.id, editor);
      setDetail(res.action);
      setEditor(clone(res.action.action));
      await refreshActionsOnly(res.action.action.id);
      show("Изменения сохранены", "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const moveActionById = async (actionId, direction) => {
    if (!user || !actionId) return;
    try {
      await api.moveAction(user.login, actionId, direction);
      await refreshActionsOnly(actionId);
      show("Порядок действий обновлен", "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const deleteActionById = async (actionId) => {
    if (!user || !actionId) return;
    if (!window.confirm("Удалить действие?")) return;
    try {
      await api.deleteAction(user.login, actionId);
      await refreshActionsOnly(actionId === selectedActionId ? null : selectedActionId);
      show("Действие удалено", "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const addProductToSale = async () => {
    if (!selectedProductId || !editor?.id || !user) return;
    try {
      const res = await api.addProductToSale(user.login, editor.id, selectedProductId);
      setDetail(res);
      setEditor(clone(res.action));
      setProductSearch("");
      setSelectedProductId("");
      setProductSuggestions([]);
      await refreshActionsOnly(editor.id);
      show("Товар добавлен", "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const saleRowCommand = async (command, index) => {
    if (!editor?.id || !user) return;
    try {
      const res = await api.saleRowCommand(user.login, editor.id, command, index);
      setDetail(res);
      setEditor(clone(res.action));
      await refreshActionsOnly(editor.id);
    } catch (e) {
      show(e.message, "error");
    }
  };

  const saveProducts = async () => {
    if (!user) return;
    try {
      const res = await api.saveProducts(user.login, products);
      setProducts(res.items || []);
      show("Справочник товаров сохранен", "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const saveSettings = async () => {
    if (!user || !settings) return;
    try {
      const res = await api.saveSettings(user.login, settings);
      setSettings(res.settings);
      show("Настройки сохранены", "success");
      await loadBootstrap(user, managerFilter, hideOldActions);
    } catch (e) {
      show(e.message, "error");
    }
  };

  const importProducts = async (file) => {
    if (!user || !file) return;
    try {
      const res = await api.importProducts(user.login, file);
      setProducts(res.items || []);
      show(res.message || `Импортировано товаров: ${res.count}`, "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const uploadDemoReport = async (file) => {
    if (!user || !editor?.id || !file) return;
    try {
      const res = await api.uploadDemoReport(user.login, editor.id, file);
      setDetail(res.action);
      setEditor(clone(res.action.action));
      show("Отчет по демонстрации загружен", "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const deleteDemoReport = async () => {
    if (!user || !editor?.id) return;
    if (!window.confirm("Удалить отчет по демонстрации?")) return;
    try {
      const res = await api.deleteDemoReport(user.login, editor.id);
      setDetail(res.action);
      setEditor(clone(res.action.action));
      show("Отчет удален", "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const downloadDemoReport = async () => {
    if (!user || !editor?.id) return;
    const report = editor.demo_report || editor.payload?.demo_report || {};
    try {
      await api.downloadDemoReport(user.login, editor.id, report.original_name || "demo_report");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const updateEditorField = (field, value) => setEditor((prev) => ({ ...prev, [field]: value }));
  const updateDirectorFields = (field, value) => setEditor((prev) => ({ ...prev, [field]: value }));
  const updateDemoMeta = (field, value) => setEditor((prev) => ({ ...prev, demo_meta: { ...(prev.demo_meta || {}), [field]: value } }));
  const updateSaleRow = (index, field, value) => setEditor((prev) => {
    const rows = clone(prev.rows || []);
    rows[index] = { ...rows[index], [field]: value };
    return { ...prev, rows };
  });
  const patchExpenseRow = (row, field, value) => {
    const current = { ...(row || {}) };
    current[field] = value;

    // В Части 2 сметы менеджер может вводить цену без НДС или с НДС.
    // Второе поле сразу пересчитывается через текущую ставку НДС, чтобы смета не расходилась визуально.
    if (current.section !== "driver" && ["price_net", "price_vat"].includes(field)) {
      const vat = plainNum(settings?.vat_rate ?? 0.22);
      if (field === "price_net") current.price_vat = round2(plainNum(value) * (1 + vat));
      if (field === "price_vat") current.price_net = round2(plainNum(value) / (1 + vat));
    }
    return current;
  };
  const updateExpenseRow = (index, field, value) => {
    if (index < 0) return;
    const sourceRow = editor?.expenses?.[index] || detail?.calc?.expenses?.[index] || {};
    const patched = patchExpenseRow(sourceRow, field, value);
    setEditor((prev) => {
      const rows = clone(prev.expenses || []);
      rows[index] = patched;
      return { ...prev, expenses: rows };
    });
    setDetail((prev) => {
      if (!prev?.calc?.expenses?.length) return prev;
      const rows = clone(prev.calc.expenses || []);
      const targetKey = expenseKey(patched, index);
      const calcIndex = rows.findIndex((row, idx) => expenseKey(row, idx) === targetKey);
      const targetIndex = calcIndex >= 0 ? calcIndex : index;
      rows[targetIndex] = { ...(rows[targetIndex] || {}), ...patched };
      return { ...prev, calc: { ...prev.calc, expenses: rows } };
    });
  };
  const updateCriterion = (code, patch) => setEditor((prev) => ({
    ...prev,
    criteria: { ...(prev.criteria || {}), [code]: { ...(prev.criteria?.[code] || {}), ...patch } },
  }));
  const logout = () => {
    window.localStorage.removeItem("demos2sales.currentUser");
    setUser(null);
    setManagerChoices([]);
    setManagerFilter("__all__");
    setMainTab("actions");
    setActions([]);
    setSelectedActionId(null);
    setDetail(null);
    setEditor(null);
    setSettings(null);
    setProducts([]);
    setProductSearch("");
    setProductSuggestions([]);
    setSelectedProductId("");
    show("Вы вышли из системы", "info");
  };
  const toggleSidebar = () => {
    setSidebarCollapsed((prev) => {
      const next = !prev;
      window.localStorage.setItem("demos2sales.sidebarCollapsed", next ? "1" : "0");
      return next;
    });
  };
  const userRoleLabel = user ? (user.role === "director" ? "Директор" : `Менеджер · ${user.office_city || ""}`) : "";
  const activePageTitle = user ? (mainTab === "settings" ? "Настройки" : mainTab === "products" ? "Товары" : "Действия") : "";
  const activePageSubtitle = user
    ? (mainTab === "settings"
      ? "Бизнес-параметры, интерфейс, критерии и смета демонстрации"
      : mainTab === "products"
        ? "Справочник товаров, офисные параметры и Excel-обмен"
        : "Последовательность демонстраций, продаж и премий по менеджерам")
    : "";

  if (!user) {
    return (
      <div className="app login-shell" style={pageStyle}>
        <div className="login-card">
          <div className="brand-title">ИРБИСТЕХ — демонстрации, продажи и премии</div>
          <p className="muted compact">Вход в систему учета демонстраций, продаж и премий.</p>
          <form onSubmit={onLogin} className="login-form">
            <label>Логин</label>
            <input value={loginForm.login} onChange={(e) => setLoginForm({ ...loginForm, login: e.target.value })} />
            <label>Пароль</label>
            <input type="password" value={loginForm.password} onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })} />
            <button type="submit" className="primary">Войти</button>
          </form>
          {notice.text ? <Notice notice={notice} /> : null}
        </div>
      </div>
    );
  }

  return (
    <div className="app app-shell top-menu-layout" style={pageStyle}>
      <aside className="sidebar">
        <button className="sidebar-toggle" type="button" onClick={toggleSidebar} title={sidebarCollapsed ? "Развернуть меню" : "Свернуть меню"}>{sidebarCollapsed ? "›" : "‹"}</button>
        <div className="brand">
          <div className="logo" aria-hidden="true">И</div>
          <div className="brand-copy">
            <h1>ИРБИСТЕХ</h1>
            <p>Демонстрации · продажи · премии</p>
          </div>
        </div>

        <nav className="nav top-tabs" aria-label="Основные разделы">
          <TabButton active={mainTab === "actions"} onClick={() => setMainTab("actions")}>
            <span className="ico">📋</span><span className="nav-text">Действия</span><span className="count">{actionList.length}</span>
          </TabButton>
          {user.role === "director" && <TabButton active={mainTab === "settings"} onClick={() => setMainTab("settings")}><span className="ico">⚙</span><span className="nav-text">Настройки</span></TabButton>}
          {user.role === "director" && <TabButton active={mainTab === "products"} onClick={() => setMainTab("products")}><span className="ico">▦</span><span className="nav-text">Товары</span><span className="count">{products.length}</span></TabButton>}
        </nav>

        <div className="sidebar-card">
          <div className="sidebar-card-title">Текущий пользователь</div>
          <div className="sidebar-user-name">{user.name}</div>
          <div className="sidebar-user-role">{userRoleLabel}</div>
          <button className="ghost sidebar-logout" onClick={logout}>Выйти</button>
        </div>
      </aside>

      <section className="main">
        <header className="topbar horizontal-topbar">
          <div className="topbar-brand">
            <div className="logo" aria-hidden="true">И</div>
            <div className="brand-copy">
              <h1>ИРБИСТЕХ</h1>
              <p>Демонстрации · продажи · премии</p>
            </div>
          </div>
          <nav className="nav top-tabs horizontal-nav" aria-label="Основные разделы">
            <TabButton active={mainTab === "actions"} onClick={() => setMainTab("actions")}>
              <span className="ico">📋</span><span className="nav-text">Действия</span><span className="count">{actionList.length}</span>
            </TabButton>
            {user.role === "director" && <TabButton active={mainTab === "settings"} onClick={() => setMainTab("settings")}><span className="ico">⚙</span><span className="nav-text">Настройки</span></TabButton>}
            {user.role === "director" && <TabButton active={mainTab === "products"} onClick={() => setMainTab("products")}><span className="ico">▦</span><span className="nav-text">Товары</span><span className="count">{products.length}</span></TabButton>}
          </nav>
          <div className="topbar-title-block">
            <div className="breadcrumb-title">{activePageTitle}</div>
            <div className="breadcrumb-subtitle">{activePageSubtitle}</div>
          </div>
          <div className="topbar-actions">
            <button className="ghost" onClick={() => loadBootstrap()}>Обновить из БД</button>
            <details className="header-profile">
              <summary className="profile-summary">
                <span className="profile-copy">
                  <span className="profile-name">{user.name}</span>
                  <span className="profile-role">{userRoleLabel}</span>
                </span>
                <span className="profile-chevron">⌄</span>
              </summary>
              <div className="profile-menu">
                <div className="profile-menu-info">
                  <div className="profile-menu-name">{user.name}</div>
                  <div className="profile-menu-role">{userRoleLabel}</div>
                </div>
                <button className="ghost profile-logout" onClick={logout}>Выйти</button>
              </div>
            </details>
          </div>
        </header>

        <main className="content">
          {notice.text ? <Notice notice={notice} /> : null}
          {loading ? <div className="loading-strip"><span className="spin" /> Загрузка...</div> : null}

          {mainTab === "actions" && (
            <div className="actions-layout">
              <aside className="action-list-panel panel">
                <div className="section-head compact-row">
                  {user.role === "director" ? (
                    <select value={managerFilter} onChange={(e) => setManagerFilter(e.target.value)}>
                      {managerChoices.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
                    </select>
                  ) : <div className="badge blue">{user.name}</div>}
                </div>
                <div className="toolbar-grid">
                  <button className="ghost" onClick={() => createAction(ACTION_DEMO)}>+ Демо</button>
                  <button className="ghost" onClick={() => createAction(ACTION_SALE)}>+ Продажа</button>
                  <button className="ghost" onClick={() => createAction(ACTION_PREMIUM)}>+ Премия</button>
                </div>
                <label className="checkbox-row small-check">
                  <input type="checkbox" checked={hideOldActions} onChange={(e) => setHideOldActions(e.target.checked)} />
                  <span>Скрыть старые действия</span>
                </label>
                <div className="list-totals grid cards compact-cards">
                  <Kpi title="Премия к выплате [PROFIT]" value={money0(listTotals.profit)} />
                  <Kpi title="Подтвержденная премия от продаж [CASH_ALL_CONFIRM]" value={money0(listTotals.cash)} />
                  <Kpi title="Подтвержденное уменьшение премии [VIC_CONFIRM]" value={money0(listTotals.vic)} />
                </div>
                <div className="action-list">
                  {actionList.map((item) => (
                    <div key={item.id} className={`action-card ${selectedActionId === item.id ? "selected" : ""} ${cardClass(item)}`} onClick={() => setSelectedActionId(item.id)} role="button" tabIndex={0}>
                      <div className="action-title-one-line">{user.role === "director" && item.manager_name ? `${item.line1} | ${item.manager_name}` : item.line1}</div>
                      <div className="action-title-buttons">
                        <button className="ghost icon-btn" title="Выше" onClick={(e) => { e.stopPropagation(); moveActionById(item.id, "up"); }}>↑</button>
                        <button className="ghost icon-btn" title="Ниже" onClick={(e) => { e.stopPropagation(); moveActionById(item.id, "down"); }}>↓</button>
                        {user.role === "director" && <button className="danger icon-btn" title="Удалить" onClick={(e) => { e.stopPropagation(); deleteActionById(item.id); }}>×</button>}
                      </div>
                    </div>
                  ))}
                  {!actionList.length ? <div className="empty">Действий пока нет.</div> : null}
                </div>
              </aside>

              <div className="panel-resizer" role="separator" aria-label="Изменить ширину списка действий" onPointerDown={startPanelResize} />

              <main className="detail-panel panel">
                {!editor || !detail ? <div className="empty-card empty">Выберите действие слева.</div> : (
                  <>
                    <div className="detail-toolbar"><button className="primary" onClick={saveCurrentAction}>Сохранить</button></div>
                    <div className="card confirm-row one-line-confirm">
                      <label className="checkbox-row nowrap">
                        <input type="checkbox" checked={!!editor.is_director_confirmed} disabled={user.role !== "director" || editor.is_locked} onChange={(e) => updateDirectorFields("is_director_confirmed", e.target.checked)} />
                        <span>Подтверждено директором</span>
                      </label>
                      <label className="field-stack compact-field">
                        <span>{detailKind === "demo" ? "Подтвержденное уменьшение премии [VIC_CONFIRM]" : detailKind === "sale" ? "Подтвержденная премия от продаж [CASH_ALL_CONFIRM]" : "Премия к выплате [PROFIT]"}</span>
                        <input type="number" value={editor.confirmed_amount ?? ""} onChange={(e) => updateDirectorFields("confirmed_amount", e.target.value)} placeholder="Сумма" disabled={user.role !== "director" || editor.is_locked} />
                      </label>
                      <label className="field-stack compact-field wide-field">
                        <span>Комментарий директора</span>
                        <input value={editor.director_comment || ""} onChange={(e) => updateDirectorFields("director_comment", e.target.value)} placeholder="Комментарий" disabled={user.role !== "director" || editor.is_locked} />
                      </label>
                    </div>

                    {detailKind === "demo" && (
                      <DemoView
                        detail={detail}
                        editor={editor}
                        demoTab={demoTab}
                        setDemoTab={setDemoTab}
                        updateEditorField={updateEditorField}
                        updateDemoMeta={updateDemoMeta}
                        updateExpenseRow={updateExpenseRow}
                        updateCriterion={updateCriterion}
                        uploadDemoReport={uploadDemoReport}
                        deleteDemoReport={deleteDemoReport}
                        downloadDemoReport={downloadDemoReport}
                        settings={settings}
                        user={user}
                      />
                    )}
                    {detailKind === "sale" && (
                      <SaleView
                        detail={detail}
                        editor={editor}
                        updateEditorField={updateEditorField}
                        updateSaleRow={updateSaleRow}
                        productSearch={productSearch}
                        setProductSearch={setProductSearch}
                        productSuggestions={productSuggestions}
                        selectedProductId={selectedProductId}
                        setSelectedProductId={setSelectedProductId}
                        addProductToSale={addProductToSale}
                        saleRowCommand={saleRowCommand}
                        user={user}
                      />
                    )}
                    {detailKind === "premium" && <PremiumView detail={detail} editor={editor} updateEditorField={updateEditorField} user={user} />}
                  </>
                )}
              </main>
            </div>
          )}

          {user.role === "director" && mainTab === "settings" && settings && <SettingsView user={user} settings={settings} setSettings={setSettings} saveSettings={saveSettings} />}
          {user.role === "director" && mainTab === "products" && <ProductsView user={user} settings={settings} products={products} setProducts={setProducts} saveProducts={saveProducts} importProducts={importProducts} />}
        </main>
      </section>
    </div>
  );
}

function DemoView({ detail, editor, demoTab, setDemoTab, updateEditorField, updateDemoMeta, updateExpenseRow, updateCriterion, uploadDemoReport, deleteDemoReport, downloadDemoReport, settings, user }) {
  const calc = detail.calc || {};
  const expenseMap = useMemo(() => Object.fromEntries((settings?.expense_settings || []).map((row, index) => [expenseKey(row, index), row])), [settings]);
  const criteriaBlocks = detail.criteria_blocks || { P: [], R: [], M: [] };
  const expenseRows = calc.expenses?.length ? calc.expenses : (editor.expenses || []);
  const editorExpenseRows = editor.expenses || [];
  const readonly = !!editor.is_locked || (user.role !== "director" && !!editor.is_director_confirmed);
  const demoHours = editor.demo_meta?.demo_hours ?? 2;
  const driverPrepHours = editor.demo_meta?.driver_prep_hours ?? 2;
  const reportInputRef = useRef(null);
  const demoReport = editor.demo_report || editor.payload?.demo_report || null;
  const canManageReport = !editor.is_director_confirmed && !editor.is_locked && !readonly;
  return (
    <div className="stack-gap">
      <div className="card fields-grid compact-info-grid">
        <Field label="Дата"><DateInput value={editor.date} disabled={readonly} onChange={(value) => updateEditorField("date", value)} /></Field>
        <Field label="Клиент"><input value={editor.client || ""} disabled={readonly} onChange={(e) => updateEditorField("client", e.target.value)} /></Field>
        <Field label="Город/адрес демонстрации" className="span-2">
          <div className="field-with-button">
            <input value={editor.city || ""} disabled={readonly} onChange={(e) => updateEditorField("city", e.target.value)} />
            <button className="ghost route-btn" disabled>Расчет пути</button>
          </div>
        </Field>
        <Field label="Модель"><input value={editor.model || ""} disabled={readonly} onChange={(e) => updateEditorField("model", e.target.value)} /></Field>
        <Field label="Описание задачи" className="span-2"><textarea value={editor.task_description || ""} disabled={readonly} onChange={(e) => updateEditorField("task_description", e.target.value)} /></Field>
        <Field label="Комментарий менеджера" className="span-2"><textarea value={editor.comment || ""} disabled={readonly} onChange={(e) => updateEditorField("comment", e.target.value)} /></Field>
        <Field label="Отчет по демонстрации" className="span-2">
          <div className="demo-report-box">
            {!demoReport ? (
              <>
                <button type="button" className="ghost" disabled={!canManageReport} onClick={() => reportInputRef.current?.click()}>Загрузить один файл отчета по демонстрации</button>
                <input ref={reportInputRef} type="file" hidden onChange={(e) => { const file = e.target.files?.[0]; if (file) uploadDemoReport(file); e.target.value = ""; }} />
              </>
            ) : (
              <>
                <div className="report-file-name" title={demoReport.original_name}>{demoReport.original_name}</div>
                <button type="button" className="danger" disabled={!canManageReport} onClick={deleteDemoReport}>Удалить отчет</button>
                <button type="button" className="ghost" onClick={downloadDemoReport}>Скачать отчет</button>
              </>
            )}
          </div>
        </Field>
      </div>

      <div className="card demo-hours-row">
        <Field label="Время работы на демонстрации, ч">
          <input type="text" inputMode="decimal" value={oneDecimalComma(demoHours)} disabled={readonly} onChange={(e) => updateDemoMeta("demo_hours", e.target.value)} />
          <div className="field-help">
            <b>Включает только:</b> время монтажа, демонстрации и обратной сборки на территории клиента; работа с электрическим компрессором, электрокатушкой и криобластером.
            <br /><b>НЕ включает:</b> любое вождение, так как маяк фиксирует все перемещения автомобиля; остановка для питания во время вождения; остановка для отдыха во время вождения.
          </div>
        </Field>
        <Field label="Время на административные процедуры, ч">
          <input type="text" inputMode="decimal" value={oneDecimalComma(driverPrepHours)} disabled={readonly} onChange={(e) => updateDemoMeta("driver_prep_hours", e.target.value)} />
          <div className="field-help">
            <b>Включает только:</b> подготовительно-заключительное время до выезда и после возвращения; время приемки и сдачи автомобиля, оборудования и документов; время ожидания в местах погрузки, разгрузки, допуска на объект; время оформления документов по выезду и демонстрации; работа на заправке, авторемонте, автомойке; время иных обязательных процедур перед выездом и после рейса.
          </div>
        </Field>
        <div className="muted compact span-2">Оба поля используются в «Расчетах с водителем» и в Части 1 сметы демонстрации.</div>
      </div>

      <div className="sub-tabs">
        <TabButton active={demoTab === "estimate"} onClick={() => setDemoTab("estimate")}>Смета демонстрации</TabButton>
        <TabButton active={demoTab === "P"} onClick={() => setDemoTab("P")}>P — Подготовка</TabButton>
        <TabButton active={demoTab === "R"} onClick={() => setDemoTab("R")}>R — Результат</TabButton>
        <TabButton active={demoTab === "M"} onClick={() => setDemoTab("M")}>M — Управленческий фактор</TabButton>
        <TabButton active={demoTab === "driver"} onClick={() => setDemoTab("driver")}>Расчеты с водителем</TabButton>
        <TabButton active={demoTab === "deduction"} onClick={() => setDemoTab("deduction")}>Расчет вычета</TabButton>
      </div>

      {demoTab === "driver" && <DriverSettlement calc={calc} />}
      {demoTab === "estimate" && (
        <div className="stack-gap">
          <ExpenseSection
            title="Часть 1. Статья расходов по совместителю водителю-демонстратору (ГПХ, ПНД)"
            rows={expenseRows.filter((row) => row.section === "driver")}
            allRows={editorExpenseRows}
            expenseMap={expenseMap}
            updateExpenseRow={updateExpenseRow}
            readonly={readonly}
          />
          <ExpenseSection
            title="Часть 2. Другие статьи расходов ООО ИРБИСТЕХ"
            rows={expenseRows.filter((row) => row.section !== "driver")}
            allRows={editorExpenseRows}
            expenseMap={expenseMap}
            updateExpenseRow={updateExpenseRow}
            readonly={readonly}
          />
          <div className="card totals-card">
            <Kpi title="ИТОГО расходы на демонстрацию, руб. с НДС" value={money(calc.total_vat)} />
            <Kpi title="ИТОГО расходы на демонстрацию [DEMO_COST], руб. без НДС" value={money(calc.demo_cost_net)} />
          </div>
        </div>
      )}
      {demoTab === "deduction" && <DeductionTab calc={calc} confirmed={editor.confirmed_amount} />}
      {["P", "R", "M"].includes(demoTab) && (
        <div className="card">
          <div className="criteria-tab-head">
            <h3>{demoTab === "P" ? "P — Подготовка" : demoTab === "R" ? "R — Результат" : "M — Управленческий фактор"}</h3>
            <Kpi title={`x${demoTab}`} value={Number(calc[`x${demoTab}`] || 0).toFixed(3)} />
          </div>
          <div className="criteria-grid-head"><div>Критерий</div><div>Уровни</div><div>Комментарий менеджера</div></div>
          {(criteriaBlocks[demoTab] || []).map((criterion) => (
            <CriterionRow
              key={criterion.code}
              criterion={criterion}
              readonly={readonly}
              editorValue={editor.criteria?.[criterion.code] || { level_index: 0, manager_comment: "" }}
              onLevel={(levelIndex) => updateCriterion(criterion.code, { level_index: levelIndex })}
              onComment={(value) => updateCriterion(criterion.code, { manager_comment: value })}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function DriverSettlement({ calc }) {
  const settlementValue = (row) => {
    if (typeof row.value !== "number") return row.value;
    const formatted = row.unit === "ч" || row.name?.includes("Время") || row.name?.includes("смены") ? oneDecimalComma(row.value) : row.value.toLocaleString("ru-RU");
    return `${formatted} ${row.unit || ""}`;
  };
  return (
    <div className="stack-gap">
      <div className="kpi-grid driver-summary-grid">
        {(calc.driver_settlement_summary || []).map((row) => (
          <Kpi key={row.name} title={row.name} value={settlementValue(row)} />
        ))}
      </div>
      <div className="card">
        <h3>Расчеты с водителем</h3>
        <table className="dense-table two-col-table driver-settlement-table">
          <thead><tr><th>Параметр</th><th>Значение</th><th>Формула / источник</th></tr></thead>
          <tbody>
            {(calc.driver_settlement || []).map((row) => (
              <tr key={row.name}>
                <td>{row.name}</td>
                <td className="align-right strong">{settlementValue(row)}</td>
                <td className="muted tiny">{row.formula || ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DeductionTab({ calc, confirmed }) {
  const yesNo = (value) => Number(value || 0) ? "Да" : "Нет";
  return (
    <div className="stack-gap">
      <div className="kpi-grid six-kpi">
        <Kpi title="[DEMO_COST] без НДС" value={money(calc.demo_cost_net)} />
        <Kpi title={`[xP] ${Number(calc.P || 0).toFixed(0)} / ${Number(calc.P_max || 0).toFixed(0)}`} value={Number(calc.xP || 0).toFixed(3)} />
        <Kpi title={`[xR] ${Number(calc.R || 0).toFixed(0)} / ${Number(calc.R_max || 0).toFixed(0)}`} value={Number(calc.xR || 0).toFixed(3)} />
        <Kpi title={`[xM] ${Number(calc.M || 0).toFixed(0)} / ${Number(calc.M_max || 0).toFixed(0)}`} value={Number(calc.xM || 0).toFixed(3)} />
        <Kpi title="[K2] взвешенная эффективность" value={Number(calc.K2 || 0).toFixed(3)} />
        <Kpi title="SOFT_STOP — мягкий стоп-фактор" value={yesNo(calc.SOFT_STOP)} />
        <Kpi title="HARD_STOP — жесткий стоп-фактор" value={yesNo(calc.HARD_STOP)} />
        <Kpi title="[K3] коэфф. эффективности с учетом стоп-факторов" value={Number(calc.K3 || 0).toFixed(3)} />
        <Kpi title="Множитель вычета (2 - [K3])" value={Number(calc.vic_multiplier || (2 - Number(calc.K3 || 0))).toFixed(3)} />
        <Kpi title="Ставка премии от маржи [СТМ]" value={`${(Number(calc.sale_st || 0) * 100).toFixed(1)}%`} />
      </div>
      <div className="formula-box">
        [K2] = 0,45 × [xP] + 0,35 × [xR] + 0,20 × [xM] — эффективность без стоп-факторов.<br />
        SOFT_STOP = да, если не выбран объект очистки, не подтверждены воздух/площадка или не согласованы критерии успеха. HARD_STOP = да, если карточка подготовки отсутствует или управленческий блок равен нулю.<br />
        [K3] = 0 при HARD_STOP; min(0,5; [K2]) при SOFT_STOP; [K2] без стоп-факторов.<br />
        Уменьшение премии / Вычет [VIC], NET руб. = [DEMO_COST] × (2 - [K3]) × [СТМ]. Подтвержденная директором сумма хранится как подтвержденное уменьшение премии [VIC_CONFIRM].
      </div>
      <div className="card totals-card">
        <Kpi title="Вычет из маржи демонстрации, руб. без НДС" value={money(calc.deduction_margin_net)} />
        <Kpi title="Уменьшение премии / Вычет [VIC], NET руб." value={money(calc.VIC)} />
        <Kpi title="Подтвержденное уменьшение премии [VIC_CONFIRM]" value={money(confirmed)} />
      </div>
    </div>
  );
}

function ExpenseSection({ title, rows, allRows, expenseMap, updateExpenseRow, readonly }) {
  const rowIndex = (row, mapIndex) => allRows.findIndex((x, idx) => expenseKey(x, idx) === expenseKey(row, mapIndex));
  const isDriverSection = rows.some((row) => row.section === "driver");
  const priceNetTitle = isDriverSection ? "Цена, руб. на руки NET" : "Цена, руб. без НДС";
  const amountNetTitle = isDriverSection ? "Сумма затрат (ПНД), руб. без НДС" : "Сумма без НДС";
  const amountVatTitle = isDriverSection ? "Сумма эквивалент руб. с НДС" : "Сумма затрат, руб. с НДС";
  return (
    <div className="card">
      <div className="card-head compact-row"><h3>{title}</h3></div>
      <div className="table-shell">
        <table className="dense-table expense-table">
          <thead><tr><th>Статья</th><th>Кол-во</th><th>Ед.</th><th>{priceNetTitle}</th>{!isDriverSection && <th>Цена, руб. с НДС</th>}<th>{amountNetTitle}</th><th>{amountVatTitle}</th></tr></thead>
          <tbody>
            {rows.map((row, mapIndex) => {
              const index = rowIndex(row, mapIndex);
              const conf = expenseMap[expenseKey(row, mapIndex)] || row;
              const canQty = !readonly && !!conf.qty_manager;
              const canPrice = !readonly && !!conf.price_manager;
              const priceNetReadOnly = row.calc_type === "cash_amount_vat" || row.calc_type === "npd_cash_input";
              const priceVatReadOnly = ["npd_direct", "office_driver_km", "demo_work_total", "npd_cash_input", "office_cryoblaster"].includes(row.calc_type);
              return (
                <tr key={expenseKey(row, mapIndex)}>
                  <td><div className="row-title expense-title-with-help"><span>{row.article}</span>{expenseKey(row, mapIndex) === "d_hard_conditions" && <span className="conditions-help">См. условия и надбавки<span className="conditions-tooltip">Улица, +10…+20°C, без осадков — 300 руб./ч.
Улица, жара свыше +20°C до +28°C — 500 руб./ч.
Улица, сильная жара свыше +28°C — 800 руб./ч.
Холод от 0°C до +10°C — 500 руб./ч.
Мороз ниже 0°C до −10°C — 800 руб./ч.
Сильный мороз ниже −10°C — 1 200 руб./ч.
Дождь / мокрый снег — 800 руб./ч.
Снегопад / наледь / скользкая площадка — 1 000 руб./ч.
Грязная среда: грязь, масло, сажа, шлам — 700 руб./ч.
Шумная среда свыше 80 дБ — 500 руб./ч.
Очень шумная среда свыше 90 дБ — 800 руб./ч.
Работа в респираторе / защитной маске — 600 руб./ч.
Работа в противогазе — 1 500 руб./ч.</span></span>}</div><div className="muted tiny">{row.comment}</div></td>
                  <td><input className={!canQty ? "locked-input" : "manager-input"} type={row.calc_type === "demo_work_total" ? "text" : "number"} inputMode="decimal" value={row.calc_type === "demo_work_total" ? oneDecimalComma(row.qty) : (row.qty ?? 0)} disabled={!canQty} onChange={(e) => updateExpenseRow(index, "qty", e.target.value)} /></td>
                  <td><input className="locked-input" value={row.unit || ""} disabled /></td>
                  <td><input className={!canPrice || priceNetReadOnly ? "locked-input" : "manager-input"} type="number" value={row.price_net ?? 0} disabled={!canPrice || priceNetReadOnly} onChange={(e) => updateExpenseRow(index, "price_net", e.target.value)} /></td>
                  {!isDriverSection && <td><input className={!canPrice || priceVatReadOnly ? "locked-input" : "manager-input"} type="number" value={row.price_vat ?? 0} disabled={!canPrice || priceVatReadOnly} onChange={(e) => updateExpenseRow(index, "price_vat", e.target.value)} /></td>}
                  <td className="align-right strong readonly-cell">{money(row.amount_net)}</td>
                  <td className="align-right strong readonly-cell">{money(row.amount_vat)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CriterionRow({ criterion, editorValue, onLevel, onComment, readonly }) {
  const levelCount = criterion.levels?.length || 1;
  return (
    <div className="criterion-row">
      <div className="criterion-about"><div className="criterion-code">{criterion.code}</div><div className="criterion-title">{criterion.title}</div><div className="criterion-desc">{criterion.desc}</div></div>
      <div className="criterion-levels">
        {criterion.levels.map((level, idx) => {
          const tag = levelStopTag(criterion.code, level[1]);
          return (
            <button key={`${criterion.code}-${idx}`} disabled={readonly} className={`level-box level-tone-${Math.round((idx / Math.max(1, levelCount - 1)) * 4)} ${Number(editorValue.level_index) === idx ? "active" : ""}`} onClick={() => onLevel(idx)}>
              <span className="level-title-strong">{level[0]}{tag ? <span className={`stop-tag ${tag === "HARD_STOP" ? "hard" : "soft"}`}>[{tag}]</span> : null}</span>
              <em className="level-example-text">{levelEfficiencyExample(idx, levelCount, level[1])}</em>
              <b>[{level[1]}]</b>
            </button>
          );
        })}
      </div>
      <div className="criterion-comment"><textarea disabled={readonly} value={editorValue.manager_comment || ""} onChange={(e) => onComment(e.target.value)} placeholder="Комментарий менеджера" /></div>
    </div>
  );
}

function SaleView({ detail, editor, updateEditorField, updateSaleRow, productSearch, setProductSearch, productSuggestions, selectedProductId, setSelectedProductId, addProductToSale, saleRowCommand, user }) {
  const calc = detail.calc || {};
  const readonly = !!editor.is_locked || (user.role !== "director" && !!editor.is_director_confirmed);
  return (
    <div className="stack-gap">
      <div className="card fields-grid compact-info-grid sale-info-grid">
        <Field label="Дата продажи"><DateInput value={editor.date} disabled={readonly} onChange={(value) => updateEditorField("date", value)} /></Field>
        <Field label="Клиент"><input value={editor.client || ""} disabled={readonly} onChange={(e) => updateEditorField("client", e.target.value)} /></Field>
        <Field label="Комментарий" className="span-2"><textarea value={editor.comment || ""} disabled={readonly} onChange={(e) => updateEditorField("comment", e.target.value)} /></Field>
      </div>
      <div className="kpi-grid sale-kpi">
        <Kpi title="Сумма продажи с НДС" value={money(calc.total_vat)} />
        <Kpi title="Суммарная премия за продажу [CASH_ALL]" value={money(calc.cash_all)} />
        <Kpi title="Подтвержденная премия от продаж [CASH_ALL_CONFIRM]" value={money(editor.confirmed_amount)} />
      </div>
      <div className="card sale-products-card">
        <div className="card-head compact-row"><h3>Товары продажи</h3></div>
        <div className="sale-search-row">
          <input value={productSearch} disabled={readonly} onChange={(e) => { setProductSearch(e.target.value); setSelectedProductId(""); }} placeholder="Начните вводить товар (от 3 символов)" />
          <select className="product-suggestions-select" size={Math.min(6, Math.max(2, productSuggestions.length || 1))} value={selectedProductId} disabled={readonly || productSearch.trim().length < 3} onChange={(e) => setSelectedProductId(e.target.value)}>
            <option value="">{productSearch.trim().length < 3 ? "Введите минимум 3 символа" : "Найденные товары"}</option>
            {productSuggestions.map((item) => <option key={item.product_id} value={item.product_id}>{item.sku} — {item.name}</option>)}
          </select>
          <button className="primary" disabled={readonly || !selectedProductId} onClick={addProductToSale}>Добавить товар</button>
        </div>
        <div className="table-shell">
          <table className="dense-table">
            <thead><tr><th>Артикул</th><th>Наименование</th><th>Цена с НДС (прайс) [PR0]</th><th>Цена продажи [PR]</th><th>Кол-во</th><th>Премия NET за продажу [CASH]</th><th></th></tr></thead>
            <tbody>
              {(editor.rows || []).map((row, index) => (
                <tr key={`${row.product_id}-${index}`}>
                  <td>{row.sku}</td>
                  <td>{row.name}</td>
                  <td className="readonly-cell align-right">{money(row.pr0_vat || row.price_vat)}</td>
                  <td><input type="number" disabled={readonly} value={row.price_vat ?? 0} onChange={(e) => updateSaleRow(index, "price_vat", e.target.value)} /></td>
                  <td><input type="number" disabled={readonly} value={row.qty ?? 1} onChange={(e) => updateSaleRow(index, "qty", e.target.value)} /></td>
                  <td className="readonly-cell strong align-right">{money(row.cash_net)}</td>
                  <td><div className="mini-actions sale-row-actions"><button className="ghost xs" disabled={readonly} onClick={() => saleRowCommand("up", index)}>↑</button><button className="ghost xs" disabled={readonly} onClick={() => saleRowCommand("down", index)}>↓</button><button className="danger xs" disabled={readonly} onClick={() => saleRowCommand("delete", index)}>✕</button></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function PremiumView({ detail, editor, updateEditorField, user }) {
  const calc = detail.calc || {};
  const readonly = !!editor.is_locked || (user.role !== "director" && !!editor.is_director_confirmed);
  return (
    <div className="stack-gap">
      <div className="card fields-grid compact-info-grid sale-info-grid">
        <Field label="Дата премии"><DateInput value={editor.date} disabled={readonly} onChange={(value) => updateEditorField("date", value)} /></Field>
        <Field label="Период"><input value={`${calc.period_from_seq || 0} → ${calc.period_to_seq || 0}`} readOnly /></Field>
        <Field label="Комментарий" className="span-2"><textarea value={editor.comment || ""} disabled={readonly} onChange={(e) => updateEditorField("comment", e.target.value)} /></Field>
      </div>
      <div className="kpi-grid premium-kpi">
        <Kpi title="Подтвержденная премия от продаж [CASH_ALL_CONFIRM], руб." value={money(calc.cash_all_confirm)} />
        <Kpi title="Подтвержденное уменьшение премии [VIC_CONFIRM], руб." value={money(calc.vic_confirm)} />
        <Kpi title="Премия к выплате [PROFIT], руб." value={money(calc.profit)} />
      </div>
      {calc.warning ? <div className="warning-box">{calc.warning}</div> : null}
      <div className="card"><h3>Продажи периода</h3><PremiumSalesTable rows={calc.sale_rows || []} /></div>
      <div className="card"><h3>Демонстрации периода</h3><PremiumDemoTable rows={calc.demo_rows || []} /></div>
    </div>
  );
}

function PremiumSalesTable({ rows }) {
  if (!rows.length) return <div className="muted compact">Нет данных.</div>;
  return (
    <div className="table-shell"><table className="dense-table"><thead><tr><th>Дата</th><th>Клиент</th><th>Премия расчетная [CASH_ALL], руб.</th><th>Подтвержденная премия от продаж [CASH_ALL_CONFIRM], руб.</th></tr></thead><tbody>
      {rows.map((r) => <tr key={r.action_id}><td>{formatDateRu(r["Дата"])}</td><td>{r["Клиент"]}</td><td className="align-right">{money(r["Премия расчетная [CASH_ALL], руб."])}</td><td className="align-right strong">{money(r["Подтвержденная премия от продаж [CASH_ALL_CONFIRM], руб."])}</td></tr>)}
    </tbody></table></div>
  );
}

function PremiumDemoTable({ rows }) {
  if (!rows.length) return <div className="muted compact">Нет данных.</div>;
  return (
    <div className="table-shell"><table className="dense-table"><thead><tr><th>Дата</th><th>Клиент</th><th>Уменьшение премии / Вычет [VIC], NET руб.</th><th>Подтвержденное уменьшение премии [VIC_CONFIRM], руб.</th></tr></thead><tbody>
      {rows.map((r) => <tr key={r.action_id}><td>{formatDateRu(r["Дата"])}</td><td>{r["Клиент"]}</td><td className="align-right">{money(r["Уменьшение премии / Вычет [VIC], NET руб."])}</td><td className="align-right strong">{money(r["Подтвержденное уменьшение премии [VIC_CONFIRM], руб."])}</td></tr>)}
    </tbody></table></div>
  );
}

function SettingsView({ user, settings, setSettings, saveSettings }) {
  const isDirector = user.role === "director";
  const [criteriaTab, setCriteriaTab] = useState("P");
  const [expenseTab, setExpenseTab] = useState("settlement");
  const cities = officeNames(settings);
  const setField = (path, value) => setSettings((prev) => {
    const next = clone(prev);
    const parts = path.split(".");
    let cursor = next;
    for (let i = 0; i < parts.length - 1; i += 1) {
      if (!cursor[parts[i]]) cursor[parts[i]] = {};
      cursor = cursor[parts[i]];
    }
    cursor[parts.at(-1)] = value;
    return next;
  });
  const updateExpense = (code, field, value) => setSettings((prev) => {
    const next = clone(prev);
    const index = next.expense_settings.findIndex((row, rowIndex) => expenseKey(row, rowIndex) === code);
    if (index >= 0) next.expense_settings[index][field] = value;
    return next;
  });
  const updateCriterionScore = (code, lIndex, score) => setSettings((prev) => {
    const next = clone(prev);
    const cIndex = next.criteria.findIndex((c) => c.code === code);
    if (cIndex >= 0) next.criteria[cIndex].levels[lIndex][1] = score;
    return next;
  });
  const updateOfficeRate = (city, key, value) => setSettings((prev) => {
    const next = clone(prev);
    if (!next.office_rates) next.office_rates = {};
    if (!next.office_rates[city]) next.office_rates[city] = {};
    next.office_rates[city][key] = value;
    return next;
  });
  const expenses = settings.expense_settings || [];
  const visibleExpenseRows = expenseTab === "driver" ? expenses.filter((row) => row.section === "driver") : expenseTab === "other" ? expenses.filter((row) => row.section !== "driver") : [];
  return (
    <div className="stack-gap">
      <div className="settings-row">
        <div className="card">
          <div className="card-head compact-row save-left">{isDirector && <button className="primary" onClick={saveSettings}>Сохранить</button>}<h3>Бизнес-настройки</h3></div>
          <div className="fields-grid two">
            <Field label="[K1] — коэффициент ответственности"><input type="number" step="0.01" value={settings.k1 ?? 0.65} disabled={!isDirector} onChange={(e) => setField("k1", plainNum(e.target.value))} /></Field>
            <Field label="НДС, %"><input type="number" value={pctUi(settings.vat_rate)} disabled={!isDirector} onChange={(e) => setField("vat_rate", fromPctUi(e.target.value))} /></Field>
            <Field label="НПД, коэффициент к оплате"><input type="number" step="0.01" value={settings.npd_factor ?? 0.94} disabled={!isDirector} onChange={(e) => setField("npd_factor", plainNum(e.target.value))} /></Field>
            <Field label="Средняя скорость, км/ч"><input type="number" value={settings.driver_avg_speed_kmh ?? 75} disabled={!isDirector} onChange={(e) => setField("driver_avg_speed_kmh", plainNum(e.target.value))} /></Field>
            <Field label="Дизель, л/100 км"><input type="number" value={settings.diesel_l_per_100km ?? 15} disabled={!isDirector} onChange={(e) => setField("diesel_l_per_100km", plainNum(e.target.value))} /></Field>
          </div>
          <OfficeRatesTable cities={cities} settings={settings} isDirector={isDirector} updateOfficeRate={updateOfficeRate} />
        </div>
        <div className="card">
          <div className="card-head compact-row save-left">{isDirector && <button className="primary" onClick={saveSettings}>Сохранить</button>}<h3>Настройки интерфейса</h3></div>
          <div className="fields-grid two">
            <Field label="Ширина списка действий, %"><input type="number" value={settings.ui.action_list_width_pct} disabled={!isDirector} onChange={(e) => setField("ui.action_list_width_pct", plainNum(e.target.value))} /></Field>
            <Field label="Ширина “Критерий”, %"><input type="number" value={settings.ui.criteria_name_width_pct} disabled={!isDirector} onChange={(e) => setField("ui.criteria_name_width_pct", plainNum(e.target.value))} /></Field>
            <Field label="Ширина “Уровни”, %"><input type="number" value={settings.ui.criteria_levels_width_pct} disabled={!isDirector} onChange={(e) => setField("ui.criteria_levels_width_pct", plainNum(e.target.value))} /></Field>
            <Field label="Ширина “Комментарий”, %"><input type="number" value={settings.ui.criteria_comment_width_pct} disabled={!isDirector} onChange={(e) => setField("ui.criteria_comment_width_pct", plainNum(e.target.value))} /></Field>
            <Field label="Гео API-ключ"><input value={settings.ui.geo_api_key || ""} disabled={!isDirector} onChange={(e) => setField("ui.geo_api_key", e.target.value)} /></Field>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-head compact-row save-left">{isDirector && <button className="primary" onClick={saveSettings}>Сохранить</button>}<h3>Критерии и баллы</h3></div>
        <div className="sub-tabs"><TabButton active={criteriaTab === "P"} onClick={() => setCriteriaTab("P")}>P — Подготовка</TabButton><TabButton active={criteriaTab === "R"} onClick={() => setCriteriaTab("R")}>R — Результат</TabButton><TabButton active={criteriaTab === "M"} onClick={() => setCriteriaTab("M")}>M — Управленческий</TabButton></div>
        <div className="table-shell"><table className="dense-table"><thead><tr><th>Код</th><th>Критерий</th><th>Уровни и баллы</th></tr></thead><tbody>
          {settings.criteria.filter((criterion) => criterion.block === criteriaTab).map((criterion) => (
            <tr key={criterion.code}><td>{criterion.code}</td><td><div className="row-title">{criterion.title}</div><div className="muted tiny">{criterion.desc}</div></td><td><div className="levels-editor">
              {criterion.levels.map((level, lIndex) => {
                const tag = levelStopTag(criterion.code, level[1]);
                return <div key={`${criterion.code}-${lIndex}`} className="level-edit-box"><div><div className="level-title-strong">{level[0]}{tag ? <span className={`stop-tag ${tag === "HARD_STOP" ? "hard" : "soft"}`}>[{tag}]</span> : null}</div><div className="level-example-text">{levelEfficiencyExample(lIndex, criterion.levels.length, level[1])}</div></div><input type="number" disabled={!isDirector} value={level[1]} onChange={(e) => updateCriterionScore(criterion.code, lIndex, Number(e.target.value || 0))} /></div>;
              })}
            </div></td></tr>
          ))}
        </tbody></table></div>
      </div>

      <div className="card">
        <div className="card-head compact-row save-left">{isDirector && <button className="primary" onClick={saveSettings}>Сохранить</button>}<h3>Настройки сметы демонстрации</h3></div>
        <OfficeRatesTable cities={cities} settings={settings} isDirector={isDirector} updateOfficeRate={updateOfficeRate} compact />
        <div className="sub-tabs"><TabButton active={expenseTab === "settlement"} onClick={() => setExpenseTab("settlement")}>Расчеты с водителем</TabButton><TabButton active={expenseTab === "driver"} onClick={() => setExpenseTab("driver")}>Часть 1</TabButton><TabButton active={expenseTab === "other"} onClick={() => setExpenseTab("other")}>Часть 2</TabButton></div>
        {expenseTab === "settlement" ? <SettlementSettingsInfo /> : <ExpenseSettingsTable rows={visibleExpenseRows} isDirector={isDirector} updateExpense={updateExpense} />}
      </div>
    </div>
  );
}

function OfficeRatesTable({ cities, settings, isDirector, updateOfficeRate, compact = false }) {
  return (
    <div className={`office-rates ${compact ? "compact-rates" : ""}`}>
      <table className="dense-table">
        <thead><tr><th>Офис продаж</th><th>Работа водителя за километраж</th><th>Работа демонстратора*</th><th>Демонстрация криобластера</th><th>Амортизация Газели и ТО</th><th>ST продажи, %</th><th>Широта</th><th>Долгота</th></tr></thead>
        <tbody>
          {cities.map((city) => {
            const row = settings.office_rates?.[city] || {};
            return <tr key={city}><td className="row-title">{city}</td><td><input type="number" disabled={!isDirector} value={row.driver_km_rate ?? 0} onChange={(e) => updateOfficeRate(city, "driver_km_rate", plainNum(e.target.value))} /></td><td><input type="number" disabled={!isDirector} value={row.demo_work_rate ?? 1350} onChange={(e) => updateOfficeRate(city, "demo_work_rate", plainNum(e.target.value))} /></td><td><input type="number" disabled={!isDirector} value={row.cryoblaster_rate ?? 0} onChange={(e) => updateOfficeRate(city, "cryoblaster_rate", plainNum(e.target.value))} /></td><td><input type="number" disabled={!isDirector} value={row.gazelle_rate ?? 0} onChange={(e) => updateOfficeRate(city, "gazelle_rate", plainNum(e.target.value))} /></td><td><input type="number" disabled={!isDirector} value={pctUi(row.sale_st ?? 0)} onChange={(e) => updateOfficeRate(city, "sale_st", fromPctUi(e.target.value))} /></td><td><input type="number" step="0.000001" disabled={!isDirector} value={row.latitude ?? 0} onChange={(e) => updateOfficeRate(city, "latitude", plainNum(e.target.value))} /></td><td><input type="number" step="0.000001" disabled={!isDirector} value={row.longitude ?? 0} onChange={(e) => updateOfficeRate(city, "longitude", plainNum(e.target.value))} /></td></tr>;
          })}
        </tbody>
      </table>
    </div>
  );
}

function SettlementSettingsInfo() {
  return <div className="formula-box">Расчеты с водителем используют Excel-логику строк 26B:35C: кругорейс / средняя скорость, административное время, время работы на демонстрации, сумма НПД по Части 1 и коэффициент НПД 0.94. Город офиса менеджера фиксируется в БД и подставляет три городские ставки автоматически.</div>;
}

function ExpenseSettingsTable({ rows, isDirector, updateExpense }) {
  return (
    <div className="table-shell"><table className="dense-table"><thead><tr><th>Код</th><th>Статья</th><th>Ед.</th><th>Кол-во</th><th>Цена без НДС / NET</th><th>Цена с НДС</th><th>Кол-во ред.</th><th>Цена ред.</th><th>Тип</th></tr></thead><tbody>
      {rows.map((row, index) => {
        const code = expenseKey(row, index);
        return <tr key={code}><td className="muted tiny">{code}</td><td><div className="row-title">{row.article}</div><div className="muted tiny">{row.comment}</div></td><td><input value={row.unit || ""} disabled={!isDirector} onChange={(e) => updateExpense(code, "unit", e.target.value)} /></td><td><input type="number" value={row.qty_default ?? 0} disabled={!isDirector} onChange={(e) => updateExpense(code, "qty_default", Number(e.target.value || 0))} /></td><td><input type="number" value={row.price_net_default ?? 0} disabled={!isDirector} onChange={(e) => updateExpense(code, "price_net_default", Number(e.target.value || 0))} /></td><td><input type="number" value={row.price_vat_default ?? 0} disabled={!isDirector} onChange={(e) => updateExpense(code, "price_vat_default", Number(e.target.value || 0))} /></td><td><input type="checkbox" checked={!!row.qty_manager} disabled={!isDirector} onChange={(e) => updateExpense(code, "qty_manager", e.target.checked)} /></td><td><input type="checkbox" checked={!!row.price_manager} disabled={!isDirector} onChange={(e) => updateExpense(code, "price_manager", e.target.checked)} /></td><td>{row.calc_type}</td></tr>;
      })}
    </tbody></table></div>
  );
}

function ProductsView({ user, settings, products, setProducts, saveProducts, importProducts }) {
  const isDirector = user.role === "director";
  const cities = officeNames(settings);
  const [selectedCity, setSelectedCity] = useState(cities[0] || "Казань");
  const [columnWidths, setColumnWidths] = useState(() => readProductColumnWidths(user.login));
  const columns = [
    ["order", ""],
    ["sku", "Артикул"],
    ["name", "Наименование"],
    ["price_vat", "Цена с НДС (прайс) [PR0]"],
    ["price_net", "Цена без НДС (прайс)"],
    ["mr", "Маржа без НДС [MR]"],
    ["pr", "Макс. премия NET [PR]"],
    ["st", "Ставка премии от маржи [ST]"],
  ];
  const saveWidths = (next) => {
    setColumnWidths(next);
    window.localStorage.setItem(productColumnsStorageKey(user.login), JSON.stringify(next));
  };
  const startColumnResize = (key, event) => {
    if (!isDirector || event.button !== 0) return;
    event.preventDefault();
    event.stopPropagation();
    const startX = event.clientX;
    const startWidth = Number(columnWidths[key] || defaultProductColumnWidths[key] || 140);
    const onMove = (moveEvent) => {
      const width = Math.max(60, Math.min(720, Math.round(startWidth + moveEvent.clientX - startX)));
      saveWidths({ ...columnWidths, [key]: width });
    };
    const onUp = () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      document.body.classList.remove("is-resizing-products");
    };
    document.body.classList.add("is-resizing-products");
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp, { once: true });
  };
  const colStyle = (key) => ({ width: `${columnWidths[key] || defaultProductColumnWidths[key]}px`, minWidth: `${columnWidths[key] || defaultProductColumnWidths[key]}px` });
  const moveProduct = (index, direction) => setProducts((prev) => {
    const next = clone(prev);
    const target = direction === "up" ? index - 1 : index + 1;
    if (target < 0 || target >= next.length) return prev;
    [next[index], next[target]] = [next[target], next[index]];
    return next.map((row, i) => ({ ...row, row_order: i + 1 }));
  });
  return (
    <div className="stack-gap">
      <div className="card products-card">
        <div className="card-head compact-row products-head">
          <h3>Справочник товаров</h3>
          <div className="mini-actions products-actions"><select className="city-select" value={selectedCity} onChange={(e) => setSelectedCity(e.target.value)}>{cities.map((city) => <option key={city} value={city}>{city}</option>)}</select><a className="ghost button-link" href={`${api.baseUrl}/api/products/template`} target="_blank" rel="noreferrer">Скачать excel</a>{isDirector && <label className="ghost file-btn">Импорт excel<input type="file" accept=".xlsx,.csv" hidden onChange={(e) => importProducts(e.target.files?.[0])} /></label>}{isDirector && <button className="primary" onClick={saveProducts}>Сохранить порядок</button>}</div>
        </div>
        <div className="muted tiny products-resize-hint">Ширину колонок можно менять перетаскиванием правой границы заголовка. Настройка сохраняется для директора в браузере.</div>
        <div className="table-shell products-table-shell"><table className="dense-table products-table"><thead><tr>{columns.map(([key, label]) => <ResizableTh key={key} style={colStyle(key)} onResize={(event) => startColumnResize(key, event)}>{label}</ResizableTh>)}</tr></thead><tbody>
          {products.map((row, index) => {
            const params = row.office_params?.[selectedCity] || row.city_params?.[selectedCity] || {};
            return <tr key={`${row.product_id}-${index}`}><td style={colStyle("order")}><div className="mini-actions product-row-actions"><button className="ghost xs" disabled={!isDirector} onClick={() => moveProduct(index, "up")}>↑</button><button className="ghost xs" disabled={!isDirector} onClick={() => moveProduct(index, "down")}>↓</button></div></td><td style={colStyle("sku")}>{row.sku}</td><td style={colStyle("name")}>{row.name}</td><td style={colStyle("price_vat")} className="align-right">{money(row.price_vat)}</td><td style={colStyle("price_net")} className="align-right">{money(row.price_net)}</td><td style={colStyle("mr")} className="align-right">{money(params.mr)}</td><td style={colStyle("pr")} className="align-right">{money(params.pr)}</td><td style={colStyle("st")} className="align-right">{percent(params.st)}</td></tr>;
          })}
        </tbody></table></div>
      </div>
    </div>
  );
}

function ResizableTh({ children, style, onResize }) {
  return <th className="resizable-th" style={style}><span>{children}</span><i className="col-resize-handle" onPointerDown={onResize} /></th>;
}

function DateInput({ value, disabled, onChange }) {
  return (
    <div className="date-picker-wrap">
      <input className="date-display-input" value={formatDateRu(value)} readOnly disabled={disabled} aria-hidden="true" tabIndex={-1} />
      <input className="date-native-overlay" type="date" value={dateInputValue(value)} disabled={disabled} onChange={(e) => onChange(e.target.value)} aria-label="Дата" />
    </div>
  );
}

function Field({ label, children, className = "" }) {
  return <label className={`field-stack ${className}`}><span>{label}</span>{children}</label>;
}
function TabButton({ active, children, ...props }) { return <button className={`tab-btn ${active ? "active" : ""}`} {...props}>{children}</button>; }
function Notice({ notice }) { return <div className={`notice ${notice.type || "info"}`}>{notice.text}</div>; }
function Kpi({ title, value }) { return <div className="kpi-box"><span>{title}</span><b>{value}</b></div>; }
function cardClass(item) {
  if (item.is_locked) return "locked";
  if (item.type === ACTION_DEMO) return item.is_director_confirmed ? "demo-confirmed" : "demo-open";
  if (item.type === ACTION_SALE) return item.is_director_confirmed ? "sale-confirmed" : "sale-open";
  return item.is_director_confirmed ? "premium-confirmed" : "premium-open";
}

export default App;
