
-- 01b_create_empty_schema_demo_calc_v6.2.sql
-- Выполнять после подключения к базе demo_calc.

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
    action_type TEXT NOT NULL CHECK (action_type IN ('Проведенная демонстрация','Проданное оборудование','Выплата премии')),
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
