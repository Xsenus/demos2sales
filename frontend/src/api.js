const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, { method = "GET", headers = {}, body, userLogin, isForm = false } = {}) {
  const finalHeaders = { ...headers };
  if (userLogin) finalHeaders["X-User-Login"] = userLogin;
  if (!isForm) finalHeaders["Content-Type"] = "application/json";
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: finalHeaders,
    body: body ? (isForm ? body : JSON.stringify(body)) : undefined,
  });
  let data = null;
  const text = await response.text();
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { detail: text || `HTTP ${response.status}` };
  }
  if (!response.ok) {
    throw new Error(data?.detail || `HTTP ${response.status}`);
  }
  return data;
}

export const api = {
  baseUrl: API_BASE,
  login: (login, password) => request("/api/auth/login", { method: "POST", body: { login, password } }),
  health: () => request("/api/health"),
  bootstrap: (userLogin, managerFilter = "__all__", hideOld = false) => request(`/api/bootstrap?manager_filter=${encodeURIComponent(managerFilter)}&hide_old=${hideOld ? "true" : "false"}`, { userLogin }),
  actions: (userLogin, managerFilter = "__all__", hideOld = false) => request(`/api/actions?manager_filter=${encodeURIComponent(managerFilter)}&hide_old=${hideOld ? "true" : "false"}`, { userLogin }),
  actionDetail: (userLogin, actionId) => request(`/api/actions/${actionId}`, { userLogin }),
  previewAction: (userLogin, actionId, payload) => request(`/api/actions/${actionId}/preview`, { method: "POST", userLogin, body: { payload } }),
  createAction: (userLogin, actionType, managerLogin) => request("/api/actions", { method: "POST", userLogin, body: { action_type: actionType, manager_login: managerLogin } }),
  updateAction: (userLogin, actionId, payload) => request(`/api/actions/${actionId}`, { method: "PATCH", userLogin, body: { payload } }),
  moveAction: (userLogin, actionId, direction) => request(`/api/actions/${actionId}/move`, { method: "POST", userLogin, body: { direction } }),
  deleteAction: (userLogin, actionId) => request(`/api/actions/${actionId}`, { method: "DELETE", userLogin }),
  searchProducts: (userLogin, q) => request(`/api/products/search?q=${encodeURIComponent(q)}`, { userLogin }),
  addProductToSale: (userLogin, actionId, productId) => request(`/api/actions/${actionId}/sale-rows/add-product`, { method: "POST", userLogin, body: { product_id: productId } }),
  saleRowCommand: (userLogin, actionId, command, index) => request(`/api/actions/${actionId}/sale-rows/command`, { method: "POST", userLogin, body: { command, index } }),
  addDemoExpenseRow: (userLogin, actionId) => request(`/api/actions/${actionId}/demo-expenses/add-row`, { method: "POST", userLogin }),
  demoExpenseCommand: (userLogin, actionId, command, index) => request(`/api/actions/${actionId}/demo-expenses/command`, { method: "POST", userLogin, body: { command, index } }),
  products: (userLogin) => request("/api/products", { userLogin }),
  saveProducts: (userLogin, products) => request("/api/products", { method: "PUT", userLogin, body: { products } }),
  settings: (userLogin) => request("/api/settings", { userLogin }),
  saveSettings: (userLogin, settings) => request("/api/settings", { method: "PUT", userLogin, body: { settings } }),
  importProducts: (userLogin, file) => {
    const fd = new FormData();
    fd.append("file", file);
    return request("/api/products/import", { method: "POST", userLogin, body: fd, isForm: true, headers: {} });
  },
};
