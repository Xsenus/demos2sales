
-- 03_clear_demo_calc_data_v6.2.sql
-- Очищает все данные, но сохраняет структуру таблиц.

TRUNCATE TABLE
    demo_criterion_values,
    demo_expenses,
    sale_rows,
    actions,
    products,
    app_settings,
    app_users
RESTART IDENTITY CASCADE;
