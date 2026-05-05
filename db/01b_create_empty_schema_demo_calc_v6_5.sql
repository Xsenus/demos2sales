-- 01b_create_empty_schema_demo_calc_v6_5.sql
-- Выполнять после подключения к базе demo_calc.

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

ALTER TABLE app_users ADD COLUMN IF NOT EXISTS office_city TEXT NOT NULL DEFAULT 'Казань';
ALTER TABLE products ADD COLUMN IF NOT EXISTS row_order INTEGER NOT NULL DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS city_params JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE actions ADD COLUMN IF NOT EXISTS payload JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS pr0_vat NUMERIC(14,2) NOT NULL DEFAULT 0;
ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS mr_unit NUMERIC(14,2) NOT NULL DEFAULT 0;
ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS pr_unit NUMERIC(14,2) NOT NULL DEFAULT 0;
ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS st_pct NUMERIC(8,6) NOT NULL DEFAULT 0;
ALTER TABLE sale_rows ADD COLUMN IF NOT EXISTS cash_net NUMERIC(14,2) NOT NULL DEFAULT 0;

DROP VIEW IF EXISTS v_actions_with_lock;
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
