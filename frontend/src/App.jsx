import React, { useEffect, useMemo, useState } from "react";
import { api } from "./api";

const ACTION_DEMO = "Проведенная демонстрация";
const ACTION_SALE = "Проданное оборудование";
const ACTION_PREMIUM = "Выплата премии";

const clone = (v) => JSON.parse(JSON.stringify(v));
const money = (v) => `${Number(v || 0).toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽`;
const money0 = (v) => `${Number(v || 0).toLocaleString("ru-RU", { maximumFractionDigits: 0 })} ₽`;
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

function useNotice() {
  const [notice, setNotice] = useState({ type: "", text: "" });
  const show = (text, type = "info") => setNotice({ text, type });
  return { notice, show, clear: () => setNotice({ type: "", text: "" }) };
}

function App() {
  const [user, setUser] = useState(null);
  const [managerChoices, setManagerChoices] = useState([]);
  const [managerFilter, setManagerFilter] = useState("__all__");
  const [mainTab, setMainTab] = useState("actions");
  const [actions, setActions] = useState([]);
  const [selectedActionId, setSelectedActionId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [editor, setEditor] = useState(null);
  const [settings, setSettings] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [productSearch, setProductSearch] = useState("");
  const [productSuggestions, setProductSuggestions] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState("");
  const [demoTab, setDemoTab] = useState("calc");
  const [loginForm, setLoginForm] = useState({ login: "artur", password: "123" });
  const { notice, show, clear } = useNotice();

  const ui = settings?.ui || {};
  const appFont = settings?.font_family || "Arial";
  const detailKind = detail?.kind;

  const pageStyle = useMemo(() => ({
    fontFamily: appFont,
    "--action-list-width": `${ui.action_list_width_pct || 28}%`,
    "--criteria-name-width": `${ui.criteria_name_width_pct || 20}fr`,
    "--criteria-level-width": `${ui.criteria_levels_width_pct || 60}fr`,
    "--criteria-comment-width": `${ui.criteria_comment_width_pct || 20}fr`,
    "--font-base": `${ui.font_base_px || 13}px`,
    "--font-title": `${ui.font_title_px || 18}px`,
    "--card-padding": `${ui.card_padding_px || 10}px`,
    "--field-gap": `${ui.field_gap_px || 8}px`,
  }), [appFont, ui]);

  const loadBootstrap = async (u = user, filter = managerFilter) => {
    if (!u) return;
    setLoading(true);
    try {
      const data = await api.bootstrap(u.login, filter);
      setManagerChoices(data.manager_choices || []);
      setSettings(data.settings);
      setActions(data.actions || []);
      if (!selectedActionId && data.actions?.length) {
        setSelectedActionId(data.actions[0].id);
      } else if (selectedActionId && !data.actions.find((a) => a.id === selectedActionId)) {
        setSelectedActionId(data.actions?.[0]?.id || null);
      }
      const p = await api.products(u.login);
      setProducts(p.items || []);
      clear();
    } catch (e) {
      show(e.message, "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      loadBootstrap(user, managerFilter);
    }
  }, [user, managerFilter]);

  useEffect(() => {
    if (user && selectedActionId) {
      api.actionDetail(user.login, selectedActionId)
        .then((res) => {
          setDetail(res);
          setEditor(clone(res.action));
          if (res.kind !== "demo") setDemoTab("calc");
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
      return;
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
    if (!payload) return undefined;

    let cancelled = false;
    const h = setTimeout(() => {
      api.previewAction(user.login, editor.id, payload)
        .then((res) => {
          if (!cancelled) setDetail(res);
        })
        .catch(() => {});
    }, 250);

    return () => {
      cancelled = true;
      clearTimeout(h);
    };
  }, [editor, user, detailKind]);

  const onLogin = async (e) => {
    e.preventDefault();
    try {
      const data = await api.login(loginForm.login, loginForm.password);
      setUser(data.user);
      setManagerFilter(data.user.role === "director" ? "__all__" : data.user.login);
      show(`Вход выполнен: ${data.user.name}`, "success");
    } catch (e2) {
      show(e2.message, "error");
    }
  };

  const refreshActionsOnly = async (keepId = selectedActionId) => {
    if (!user) return;
    const res = await api.actions(user.login, managerFilter);
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

  const moveCurrentAction = async (direction) => {
    if (!user || !editor?.id) return;
    try {
      await api.moveAction(user.login, editor.id, direction);
      await refreshActionsOnly(editor.id);
      show("Порядок действий обновлен", "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const deleteCurrentAction = async () => {
    if (!user || !editor?.id) return;
    if (!window.confirm("Удалить действие?")) return;
    try {
      await api.deleteAction(user.login, editor.id);
      await refreshActionsOnly(null);
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

  const demoExpenseCommand = async (command, index = 0) => {
    if (!editor?.id || !user) return;
    try {
      const res = command === "add"
        ? await api.addDemoExpenseRow(user.login, editor.id)
        : await api.demoExpenseCommand(user.login, editor.id, command, index);
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
    } catch (e) {
      show(e.message, "error");
    }
  };

  const importProducts = async (file) => {
    if (!user || !file) return;
    try {
      const res = await api.importProducts(user.login, file);
      setProducts(res.items || []);
      show(`Импортировано товаров: ${res.count}`, "success");
    } catch (e) {
      show(e.message, "error");
    }
  };

  const updateEditorField = (field, value) => {
    setEditor((prev) => ({ ...prev, [field]: value }));
  };

  const updateDirectorFields = (field, value) => {
    setEditor((prev) => ({ ...prev, [field]: value }));
  };

  const updateSaleRow = (index, field, value) => {
    setEditor((prev) => {
      const rows = clone(prev.rows || []);
      rows[index] = { ...rows[index], [field]: value };
      return { ...prev, rows };
    });
  };

  const updateExpenseRow = (index, field, value) => {
    setEditor((prev) => {
      const rows = clone(prev.expenses || []);
      rows[index] = { ...rows[index], [field]: value };
      return { ...prev, expenses: rows };
    });
  };

  const updateCriterion = (code, patch) => {
    setEditor((prev) => ({
      ...prev,
      criteria: {
        ...(prev.criteria || {}),
        [code]: { ...(prev.criteria?.[code] || {}), ...patch },
      },
    }));
  };

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
          <div className="login-hint">
            <div><b>Директор:</b> artur / 123</div>
            <div><b>Менеджеры:</b> ruslan / 111, timur / 222, maria / 333, ildar / 444</div>
          </div>
          {notice.text ? <Notice notice={notice} /> : null}
        </div>
      </div>
    );
  }

  return (
    <div className="app" style={pageStyle}>
      <header className="header-bar">
        <div>
          <div className="brand-title">ИРБИСТЕХ — демонстрации, продажи и премии</div>
          <div className="muted compact">Компактный интерфейс на React + FastAPI</div>
        </div>
        <div className="header-user">
          <div>{user.name}</div>
          <div className="muted compact">{user.role === "director" ? "Директор" : "Менеджер"}</div>
        </div>
      </header>

      <div className="top-tabs">
        <TabButton active={mainTab === "actions"} onClick={() => setMainTab("actions")}>Действия</TabButton>
        <TabButton active={mainTab === "settings"} onClick={() => setMainTab("settings")}>Настройки</TabButton>
        <TabButton active={mainTab === "products"} onClick={() => setMainTab("products")}>Товары</TabButton>
        <button className="ghost" onClick={() => loadBootstrap()}>Обновить из БД</button>
      </div>

      {notice.text ? <Notice notice={notice} /> : null}
      {loading ? <div className="loading-strip">Загрузка...</div> : null}

      {mainTab === "actions" && (
        <div className="actions-layout">
          <aside className="action-list-panel">
            <div className="section-head compact-row">
              {user.role === "director" ? (
                <select value={managerFilter} onChange={(e) => setManagerFilter(e.target.value)}>
                  {managerChoices.map((m) => <option key={m.value} value={m.value}>{m.label}</option>)}
                </select>
              ) : (
                <div className="muted compact">{user.name}</div>
              )}
            </div>
            <div className="toolbar-grid">
              <button className="ghost" onClick={() => createAction(ACTION_DEMO)}>+ Демо</button>
              <button className="ghost" onClick={() => createAction(ACTION_SALE)}>+ Продажа</button>
              <button className="ghost" onClick={() => createAction(ACTION_PREMIUM)}>+ Премия</button>
            </div>
            <div className="action-list">
              {actions.map((item) => (
                <button key={item.id} className={`action-card ${selectedActionId === item.id ? "selected" : ""} ${cardClass(item)}`} onClick={() => setSelectedActionId(item.id)}>
                  <div className="line1">{item.line1}</div>
                  <div className="line2">{item.line2}</div>
                </button>
              ))}
            </div>
          </aside>

          <main className="detail-panel">
            {!editor || !detail ? (
              <div className="empty-card">Выберите действие слева.</div>
            ) : (
              <>
                <div className="detail-toolbar">
                  <div className="toolbar-group">
                    <button className="ghost" onClick={() => moveCurrentAction("up")}>↑ Выше</button>
                    <button className="ghost" onClick={() => moveCurrentAction("down")}>↓ Ниже</button>
                    {user.role === "director" && <button className="danger" onClick={deleteCurrentAction}>Удалить</button>}
                  </div>
                  <button className="primary" onClick={saveCurrentAction}>Сохранить</button>
                </div>

                <div className="card confirm-row">
                  <label className="checkbox-row">
                    <input type="checkbox" checked={!!editor.is_director_confirmed} disabled={user.role !== "director"} onChange={(e) => updateDirectorFields("is_director_confirmed", e.target.checked)} />
                    <span>Подтверждено директором</span>
                  </label>
                  <div className="confirm-grid">
                    <input type="number" value={editor.confirmed_amount ?? ""} onChange={(e) => updateDirectorFields("confirmed_amount", e.target.value)} placeholder="Сумма, подтвержденная директором" disabled={user.role !== "director"} />
                    <input value={editor.director_comment || ""} onChange={(e) => updateDirectorFields("director_comment", e.target.value)} placeholder="Комментарий директора" disabled={user.role !== "director"} />
                  </div>
                </div>

                {detailKind === "demo" && (
                  <DemoView
                    detail={detail}
                    editor={editor}
                    demoTab={demoTab}
                    setDemoTab={setDemoTab}
                    setEditor={setEditor}
                    updateEditorField={updateEditorField}
                    updateExpenseRow={updateExpenseRow}
                    updateCriterion={updateCriterion}
                    demoExpenseCommand={demoExpenseCommand}
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
                  />
                )}
                {detailKind === "premium" && (
                  <PremiumView detail={detail} editor={editor} updateEditorField={updateEditorField} />
                )}
              </>
            )}
          </main>
        </div>
      )}

      {mainTab === "settings" && settings && (
        <SettingsView user={user} settings={settings} setSettings={setSettings} saveSettings={saveSettings} />
      )}

      {mainTab === "products" && (
        <ProductsView user={user} products={products} setProducts={setProducts} saveProducts={saveProducts} importProducts={importProducts} />
      )}
    </div>
  );
}

function DemoView({ detail, editor, demoTab, setDemoTab, updateEditorField, updateExpenseRow, updateCriterion, demoExpenseCommand, settings, user }) {
  const calc = detail.calc || {};
  const expenseMap = useMemo(() => Object.fromEntries((settings?.expense_settings || []).map((row) => [row.article, row])), [settings]);
  const criteriaBlocks = detail.criteria_blocks || { P: [], R: [], M: [] };

  return (
    <div className="stack-gap">
      <div className="card fields-grid four">
        <input value={editor.date || ""} onChange={(e) => updateEditorField("date", e.target.value)} placeholder="Дата" />
        <input value={editor.client || ""} onChange={(e) => updateEditorField("client", e.target.value)} placeholder="Клиент" />
        <input value={editor.city || ""} onChange={(e) => updateEditorField("city", e.target.value)} placeholder="Город" />
        <input value={editor.model || ""} onChange={(e) => updateEditorField("model", e.target.value)} placeholder="Модель" />
        <textarea className="span-4" value={editor.task_description || ""} onChange={(e) => updateEditorField("task_description", e.target.value)} placeholder="Задача очистки" />
        <textarea className="span-4" value={editor.comment || ""} onChange={(e) => updateEditorField("comment", e.target.value)} placeholder="Комментарий менеджера" />
      </div>

      <div className="sub-tabs">
        <TabButton active={demoTab === "calc"} onClick={() => setDemoTab("calc")}>Калькулятор</TabButton>
        <TabButton active={demoTab === "P"} onClick={() => setDemoTab("P")}>P — Подготовка</TabButton>
        <TabButton active={demoTab === "R"} onClick={() => setDemoTab("R")}>R — Результат</TabButton>
        <TabButton active={demoTab === "M"} onClick={() => setDemoTab("M")}>M — Управленческий фактор</TabButton>
      </div>

      {demoTab === "calc" && (
        <div className="stack-gap">
          <div className="kpi-grid compact-kpi">
            <Kpi title="Итого с НДС" value={money(calc.total_vat)} />
            <Kpi title="Помощь ООО" value={money(calc.support_vat)} />
            <Kpi title="COST" value={money(calc.cost_net)} />
            <Kpi title="QI" value={Number(calc.QI || 0).toFixed(3)} />
            <Kpi title="K" value={percent(calc.K)} />
            <Kpi title="Вычет NET" value={money(calc.deduction_net)} />
          </div>
          <div className="card">
            <div className="card-head compact-row">
              <h3>Смета демонстрации</h3>
              <button className="ghost" onClick={() => demoExpenseCommand("add")}>+ Пользовательская строка</button>
            </div>
            <div className="table-shell">
              <table className="dense-table">
                <thead>
                  <tr>
                    <th>Статья</th>
                    <th>Кол-во</th>
                    <th>Ед.</th>
                    <th>Цена без НДС</th>
                    <th>Цена с НДС</th>
                    <th>Сумма с НДС</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {(editor.expenses || []).map((row, index) => {
                    const conf = expenseMap[row.article] || {};
                    const canQty = row.is_custom || conf.qty_manager;
                    const canPrice = row.is_custom || conf.price_manager;
                    return (
                      <tr key={`${row.article}-${index}`}>
                        <td>
                          <div className="row-title">{row.article}</div>
                          <div className="muted tiny">{row.comment}</div>
                        </td>
                        <td><input type="number" value={row.qty ?? 0} disabled={!canQty} onChange={(e) => updateExpenseRow(index, "qty", e.target.value)} /></td>
                        <td><input value={row.unit || ""} disabled={!row.is_custom} onChange={(e) => updateExpenseRow(index, "unit", e.target.value)} /></td>
                        <td><input type="number" value={row.price_net ?? 0} disabled={!canPrice} onChange={(e) => updateExpenseRow(index, "price_net", e.target.value)} /></td>
                        <td><input type="number" value={row.price_vat ?? 0} disabled={!canPrice} onChange={(e) => updateExpenseRow(index, "price_vat", e.target.value)} /></td>
                        <td className="align-right strong">{money(row.amount_vat)}</td>
                        <td>
                          <div className="mini-actions">
                            <button className="ghost xs" onClick={() => demoExpenseCommand("up", index)}>↑</button>
                            <button className="ghost xs" onClick={() => demoExpenseCommand("down", index)}>↓</button>
                            <button className="danger xs" onClick={() => demoExpenseCommand("delete", index)}>✕</button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {["P", "R", "M"].includes(demoTab) && (
        <div className="card">
          <div className="criteria-grid-head">
            <div>Критерий</div>
            <div>Уровни</div>
            <div>Комментарий</div>
          </div>
          {(criteriaBlocks[demoTab] || []).map((criterion) => (
            <CriterionRow
              key={criterion.code}
              criterion={criterion}
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

function CriterionRow({ criterion, editorValue, onLevel, onComment }) {
  return (
    <div className="criterion-row">
      <div className="criterion-about">
        <div className="criterion-code">{criterion.code}</div>
        <div className="criterion-title">{criterion.title}</div>
        <div className="criterion-desc">{criterion.desc}</div>
      </div>
      <div className="criterion-levels">
        {criterion.levels.map((level, idx) => (
          <button key={`${criterion.code}-${idx}`} className={`level-box ${editorValue.level_index === idx ? "active" : ""}`} onClick={() => onLevel(idx)}>
            <span>{level[0]}</span>
            <b>[{level[1]}]</b>
          </button>
        ))}
      </div>
      <div className="criterion-comment"><textarea value={editorValue.manager_comment || ""} onChange={(e) => onComment(e.target.value)} placeholder="Подтверждение уровня" /></div>
    </div>
  );
}

function SaleView({ detail, editor, updateEditorField, updateSaleRow, productSearch, setProductSearch, productSuggestions, selectedProductId, setSelectedProductId, addProductToSale, saleRowCommand }) {
  const calc = detail.calc || {};
  return (
    <div className="stack-gap">
      <div className="card fields-grid three">
        <input value={editor.date || ""} onChange={(e) => updateEditorField("date", e.target.value)} placeholder="Дата продажи" />
        <input value={editor.client || ""} onChange={(e) => updateEditorField("client", e.target.value)} placeholder="Клиент" />
        <textarea className="span-3" value={editor.comment || ""} onChange={(e) => updateEditorField("comment", e.target.value)} placeholder="Комментарий" />
      </div>
      <div className="kpi-grid compact-kpi">
        <Kpi title="Итого с НДС" value={money(calc.total_vat)} />
        <Kpi title="Премия NET" value={money(calc.bonus_net)} />
      </div>
      <div className="card">
        <div className="card-head compact-row"><h3>Товары продажи</h3></div>
        <div className="sale-search-row">
          <input value={productSearch} onChange={(e) => setProductSearch(e.target.value)} placeholder="Начните вводить товар (от 3 символов)" />
          <select value={selectedProductId} onChange={(e) => setSelectedProductId(e.target.value)}>
            <option value="">Выберите товар</option>
            {productSuggestions.map((item) => (
              <option key={item.product_id} value={item.product_id}>{item.sku} — {item.name}</option>
            ))}
          </select>
          <button className="primary" onClick={addProductToSale}>Добавить товар</button>
        </div>
        <div className="table-shell">
          <table className="dense-table">
            <thead>
              <tr>
                <th>Артикул</th>
                <th>Наименование</th>
                <th>Цена с НДС</th>
                <th>Цена без НДС</th>
                <th>Кол-во</th>
                <th>Мин. цена</th>
                <th>% премии</th>
                <th>Премия NET</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {(editor.rows || []).map((row, index) => (
                <tr key={`${row.product_id}-${index}`}>
                  <td>{row.sku}</td>
                  <td>{row.name}</td>
                  <td><input type="number" value={row.price_vat ?? 0} onChange={(e) => updateSaleRow(index, "price_vat", e.target.value)} /></td>
                  <td><input type="number" value={row.price_net ?? 0} onChange={(e) => updateSaleRow(index, "price_net", e.target.value)} /></td>
                  <td><input type="number" value={row.qty ?? 1} onChange={(e) => updateSaleRow(index, "qty", e.target.value)} /></td>
                  <td className="readonly-cell">{money(row.min_price_net)}</td>
                  <td className="readonly-cell">{percent(row.margin_pct)}</td>
                  <td className="readonly-cell strong">{money(row.bonus_net)}</td>
                  <td>
                    <div className="mini-actions">
                      <button className="ghost xs" onClick={() => saleRowCommand("up", index)}>↑</button>
                      <button className="ghost xs" onClick={() => saleRowCommand("down", index)}>↓</button>
                      <button className="danger xs" onClick={() => saleRowCommand("delete", index)}>✕</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function PremiumView({ detail, editor, updateEditorField }) {
  const calc = detail.calc || {};
  return (
    <div className="stack-gap">
      <div className="card fields-grid three">
        <input value={editor.date || ""} onChange={(e) => updateEditorField("date", e.target.value)} placeholder="Дата премии" />
        <input value={`${calc.period_from_seq || 0} → ${calc.period_to_seq || 0}`} readOnly />
        <textarea className="span-3" value={editor.comment || ""} onChange={(e) => updateEditorField("comment", e.target.value)} placeholder="Комментарий" />
      </div>
      <div className="kpi-grid compact-kpi">
        <Kpi title="Премия от продаж" value={money(calc.sales_sum)} />
        <Kpi title="Демо-вычет" value={money(calc.actual_demo)} />
        <Kpi title="К выплате" value={money(calc.payout)} />
      </div>
      {calc.warning ? <div className="warning-box">{calc.warning}</div> : null}
      <div className="card">
        <h3>Продажи периода</h3>
        <SimpleTable rows={calc.sale_rows || []} />
      </div>
      <div className="card">
        <h3>Демонстрации периода</h3>
        <SimpleTable rows={calc.demo_rows || []} />
      </div>
    </div>
  );
}

function SettingsView({ user, settings, setSettings, saveSettings }) {
  const isDirector = user.role === "director";
  const setField = (path, value) => {
    setSettings((prev) => {
      const next = clone(prev);
      const parts = path.split(".");
      let cursor = next;
      for (let i = 0; i < parts.length - 1; i += 1) cursor = cursor[parts[i]];
      cursor[parts.at(-1)] = value;
      return next;
    });
  };
  const updateExpense = (index, field, value) => {
    setSettings((prev) => {
      const next = clone(prev);
      next.expense_settings[index][field] = value;
      return next;
    });
  };
  const updateCriterionScore = (cIndex, lIndex, score) => {
    setSettings((prev) => {
      const next = clone(prev);
      next.criteria[cIndex].levels[lIndex][1] = score;
      return next;
    });
  };

  return (
    <div className="stack-gap">
      <div className="card">
        <div className="card-head compact-row">
          <h3>Бизнес-настройки</h3>
          {isDirector && <button className="primary" onClick={saveSettings}>Сохранить</button>}
        </div>
        <div className="fields-grid two">
          <label className="field-stack">
            <span>НДС, %</span>
            <input type="number" value={pctUi(settings.vat_rate)} disabled={!isDirector} onChange={(e) => setField("vat_rate", fromPctUi(e.target.value))} />
          </label>
          <label className="field-stack">
            <span>Ставка премии, %</span>
            <input type="number" value={pctUi(settings.bonus_rate)} disabled={!isDirector} onChange={(e) => setField("bonus_rate", fromPctUi(e.target.value))} />
          </label>
          <label className="field-stack">
            <span>Максимальный вычет из премии, %</span>
            <input type="number" value={pctUi(settings.max_demo_deduction_pct)} disabled={!isDirector} onChange={(e) => setField("max_demo_deduction_pct", fromPctUi(e.target.value))} />
          </label>
          <label className="field-stack">
            <span>Фора / помощь ООО, руб. с НДС</span>
            <input type="number" value={settings.company_support_vat} disabled={!isDirector} onChange={(e) => setField("company_support_vat", plainNum(e.target.value))} />
          </label>
        </div>
      </div>

      <div className="card">
        <div className="card-head compact-row">
          <h3>Настройки интерфейса</h3>
          {isDirector && <button className="primary" onClick={saveSettings}>Сохранить</button>}
        </div>
        <div className="fields-grid two">
          <label className="field-stack">
            <span>Ширина списка действий, %</span>
            <input type="number" value={settings.ui.action_list_width_pct} disabled={!isDirector} onChange={(e) => setField("ui.action_list_width_pct", plainNum(e.target.value))} />
          </label>
          <label className="field-stack">
            <span>Ширина колонки "Критерий", %</span>
            <input type="number" value={settings.ui.criteria_name_width_pct} disabled={!isDirector} onChange={(e) => setField("ui.criteria_name_width_pct", plainNum(e.target.value))} />
          </label>
          <label className="field-stack">
            <span>Ширина колонки "Уровни", %</span>
            <input type="number" value={settings.ui.criteria_levels_width_pct} disabled={!isDirector} onChange={(e) => setField("ui.criteria_levels_width_pct", plainNum(e.target.value))} />
          </label>
          <label className="field-stack">
            <span>Ширина колонки "Комментарий", %</span>
            <input type="number" value={settings.ui.criteria_comment_width_pct} disabled={!isDirector} onChange={(e) => setField("ui.criteria_comment_width_pct", plainNum(e.target.value))} />
          </label>
        </div>
      </div>
      <div className="card">
        <div className="card-head compact-row"><h3>Критерии и баллы</h3>{isDirector && <button className="primary" onClick={saveSettings}>Сохранить</button>}</div>
        <div className="table-shell">
          <table className="dense-table">
            <thead><tr><th>Код</th><th>Блок</th><th>Критерий</th><th>Уровни и баллы</th></tr></thead>
            <tbody>
              {settings.criteria.map((criterion, cIndex) => (
                <tr key={criterion.code}>
                  <td>{criterion.code}</td>
                  <td>{criterion.block}</td>
                  <td><div className="row-title">{criterion.title}</div><div className="muted tiny">{criterion.desc}</div></td>
                  <td>
                    <div className="levels-editor">
                      {criterion.levels.map((level, lIndex) => (
                        <div key={`${criterion.code}-${lIndex}`} className="level-edit-box">
                          <div className="muted tiny">{level[0]}</div>
                          <input type="number" disabled={!isDirector} value={level[1]} onChange={(e) => updateCriterionScore(cIndex, lIndex, Number(e.target.value || 0))} />
                        </div>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <div className="card">
        <div className="card-head compact-row"><h3>Настройки сметы демонстрации</h3>{isDirector && <button className="primary" onClick={saveSettings}>Сохранить</button>}</div>
        <div className="table-shell">
          <table className="dense-table">
            <thead><tr><th>Статья</th><th>Ед.</th><th>Кол-во</th><th>Цена без НДС</th><th>Цена с НДС</th><th>Кол-во ред.</th><th>Цена ред.</th><th>Тип</th></tr></thead>
            <tbody>
              {settings.expense_settings.map((row, index) => (
                <tr key={row.article}>
                  <td>{row.article}</td>
                  <td><input value={row.unit || ""} disabled={!isDirector} onChange={(e) => updateExpense(index, "unit", e.target.value)} /></td>
                  <td><input type="number" value={row.qty_default ?? 0} disabled={!isDirector} onChange={(e) => updateExpense(index, "qty_default", Number(e.target.value || 0))} /></td>
                  <td><input type="number" value={row.price_net_default ?? 0} disabled={!isDirector} onChange={(e) => updateExpense(index, "price_net_default", Number(e.target.value || 0))} /></td>
                  <td><input type="number" value={row.price_vat_default ?? 0} disabled={!isDirector} onChange={(e) => updateExpense(index, "price_vat_default", Number(e.target.value || 0))} /></td>
                  <td><input type="checkbox" checked={!!row.qty_manager} disabled={!isDirector} onChange={(e) => updateExpense(index, "qty_manager", e.target.checked)} /></td>
                  <td><input type="checkbox" checked={!!row.price_manager} disabled={!isDirector} onChange={(e) => updateExpense(index, "price_manager", e.target.checked)} /></td>
                  <td>{row.calc_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ProductsView({ user, products, setProducts, saveProducts, importProducts }) {
  const isDirector = user.role === "director";
  const update = (index, field, value) => setProducts((prev) => {
    const next = clone(prev);
    next[index][field] = value;
    return next;
  });
  const addRow = () => setProducts((prev) => ([...prev, { product_id: `PRD-${Date.now()}`, sku: "", name: "", price_vat: 0, price_net: 0, min_price_net: 0, margin_pct: 0.65, comment: "" }]));
  const removeRow = (index) => setProducts((prev) => prev.filter((_, i) => i !== index));

  return (
    <div className="stack-gap">
      <div className="card">
        <div className="card-head compact-row">
          <h3>Справочник товаров</h3>
          <div className="mini-actions">
            <a className="ghost button-link" href={`${api.baseUrl}/api/products/template`} target="_blank" rel="noreferrer">Скачать шаблон</a>
            {isDirector && <label className="ghost file-btn">Импорт <input type="file" accept=".xlsx,.csv" hidden onChange={(e) => importProducts(e.target.files?.[0])} /></label>}
            {isDirector && <button className="ghost" onClick={addRow}>+ Товар</button>}
            {isDirector && <button className="primary" onClick={saveProducts}>Сохранить</button>}
          </div>
        </div>
        <div className="table-shell">
          <table className="dense-table">
            <thead>
              <tr>
                <th>ID</th><th>Артикул</th><th>Наименование</th><th>Цена с НДС</th><th>Цена без НДС</th><th>Мин. цена</th><th>% премии</th><th>Комментарий</th><th></th>
              </tr>
            </thead>
            <tbody>
              {products.map((row, index) => (
                <tr key={`${row.product_id}-${index}`}>
                  <td><input value={row.product_id || ""} disabled={!isDirector} onChange={(e) => update(index, "product_id", e.target.value)} /></td>
                  <td><input value={row.sku || ""} disabled={!isDirector} onChange={(e) => update(index, "sku", e.target.value)} /></td>
                  <td><input value={row.name || ""} disabled={!isDirector} onChange={(e) => update(index, "name", e.target.value)} /></td>
                  <td><input type="number" value={row.price_vat ?? 0} disabled={!isDirector} onChange={(e) => update(index, "price_vat", e.target.value)} /></td>
                  <td><input type="number" value={row.price_net ?? 0} disabled={!isDirector} onChange={(e) => update(index, "price_net", e.target.value)} /></td>
                  <td><input type="number" value={row.min_price_net ?? 0} disabled={!isDirector} onChange={(e) => update(index, "min_price_net", e.target.value)} /></td>
                  <td><input type="number" step="0.01" value={row.margin_pct ?? 0.65} disabled={!isDirector} onChange={(e) => update(index, "margin_pct", e.target.value)} /></td>
                  <td><input value={row.comment || ""} disabled={!isDirector} onChange={(e) => update(index, "comment", e.target.value)} /></td>
                  <td>{isDirector && <button className="danger xs" onClick={() => removeRow(index)}>✕</button>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function TabButton({ active, children, ...props }) {
  return <button className={`tab-btn ${active ? "active" : ""}`} {...props}>{children}</button>;
}

function Notice({ notice }) {
  return <div className={`notice ${notice.type || "info"}`}>{notice.text}</div>;
}

function Kpi({ title, value }) {
  return <div className="kpi-box"><span>{title}</span><b>{value}</b></div>;
}

function SimpleTable({ rows }) {
  if (!rows?.length) return <div className="muted compact">Нет данных.</div>;
  const headers = Object.keys(rows[0]);
  return (
    <div className="table-shell">
      <table className="dense-table">
        <thead><tr>{headers.map((h) => <th key={h}>{h}</th>)}</tr></thead>
        <tbody>
          {rows.map((row, idx) => <tr key={idx}>{headers.map((h) => <td key={h}>{String(row[h] ?? "")}</td>)}</tr>)}
        </tbody>
      </table>
    </div>
  );
}

function cardClass(item) {
  if (item.is_locked) return "locked";
  if (item.type === ACTION_DEMO) return item.is_director_confirmed ? "demo-confirmed" : "demo-open";
  if (item.type === ACTION_SALE) return item.is_director_confirmed ? "sale-confirmed" : "sale-open";
  return item.is_director_confirmed ? "premium-confirmed" : "premium-open";
}

export default App;
