-- 05_migrate_to_v9_preserve.sql
-- Неразрушающий патч v9 для действующей БД demo_calc.
-- Скрипт НЕ удаляет таблицы, НЕ очищает действия и сохраняет текущих пользователей, действия,
-- демонстрации, продажи, премии, файлы отчетов и свойства действий.

BEGIN;

-- 1. Актуализация структуры без удаления данных.
ALTER TABLE IF EXISTS public.app_users
    ADD COLUMN IF NOT EXISTS office_city TEXT NOT NULL DEFAULT 'Казань';

ALTER TABLE IF EXISTS public.products
    ADD COLUMN IF NOT EXISTS row_order INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS city_params JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE IF EXISTS public.actions
    ADD COLUMN IF NOT EXISTS payload JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE IF EXISTS public.demo_expenses
    ADD COLUMN IF NOT EXISTS row_code TEXT NOT NULL DEFAULT '';

ALTER TABLE IF EXISTS public.sale_rows
    ADD COLUMN IF NOT EXISTS pr0_vat NUMERIC(14,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS mr_unit NUMERIC(14,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS pr_unit NUMERIC(14,2) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS st_pct NUMERIC(8,6) NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS cash_net NUMERIC(14,2) NOT NULL DEFAULT 0;

-- 2. Новое название строки сметы.
UPDATE public.demo_expenses
SET article = 'Ручное перетаскивание кабеля и РВД катушки'
WHERE row_code = 'd_electro_reel'
   OR article = 'Использование электрокатушки';

-- 3. В товарах v9 используется prem_max по каждому городу.
-- Старые ключи pr/mr/st сохраняются для обратной совместимости, но расчет продажи берет prem_max.
UPDATE public.products p
SET city_params = COALESCE((
    SELECT jsonb_object_agg(city_key, city_value || jsonb_build_object(
        'prem_max', to_jsonb(
            COALESCE(
                NULLIF(city_value ->> 'prem_max', '')::numeric,
                NULLIF(city_value ->> 'pr', '')::numeric,
                ROUND(COALESCE(p.price_net, 0) * 0.10, 2)
            )
        ),
        'pr', to_jsonb(
            COALESCE(
                NULLIF(city_value ->> 'prem_max', '')::numeric,
                NULLIF(city_value ->> 'pr', '')::numeric,
                ROUND(COALESCE(p.price_net, 0) * 0.10, 2)
            )
        )
    ))
    FROM jsonb_each(COALESCE(p.city_params, '{}'::jsonb)) AS e(city_key, city_value)
), '{}'::jsonb);

-- Если у товара city_params был пустым, добавляем Казань/Москва по умолчанию.
UPDATE public.products p
SET city_params = jsonb_build_object(
    'Казань', jsonb_build_object('prem_max', ROUND(COALESCE(p.price_net, 0) * 0.10, 2), 'pr', ROUND(COALESCE(p.price_net, 0) * 0.10, 2), 'mr', ROUND(COALESCE(p.price_net, 0) * 0.20, 2), 'st', 0.565),
    'Москва', jsonb_build_object('prem_max', ROUND(COALESCE(p.price_net, 0) * 0.10, 2), 'pr', ROUND(COALESCE(p.price_net, 0) * 0.10, 2), 'mr', ROUND(COALESCE(p.price_net, 0) * 0.20, 2), 'st', 0.465)
)
WHERE COALESCE(p.city_params, '{}'::jsonb) = '{}'::jsonb;

-- 4. Обновляем настройки без сброса всей БД.
UPDATE public.app_settings
SET settings = jsonb_set(COALESCE(settings, '{}'::jsonb), '{ui,geo_api_key}', to_jsonb(COALESCE(settings #>> '{ui,geo_api_key}', '')), true)
WHERE id = 1;

UPDATE public.app_settings
SET settings = jsonb_set(settings, '{office_rates,Казань,demo_work_rate}', to_jsonb(COALESCE(NULLIF(settings #>> '{office_rates,Казань,demo_work_rate}', '')::numeric, 1350)), true)
WHERE id = 1;

UPDATE public.app_settings
SET settings = jsonb_set(settings, '{office_rates,Москва,demo_work_rate}', to_jsonb(COALESCE(NULLIF(settings #>> '{office_rates,Москва,demo_work_rate}', '')::numeric, 1350)), true)
WHERE id = 1;

-- Настройки сметы: переименование электрокатушки и разрешение корректировать количество амортизации Газели.
UPDATE public.app_settings s
SET settings = jsonb_set(
    s.settings,
    '{expense_settings}',
    COALESCE((
        SELECT jsonb_agg(
            CASE
                WHEN item ->> 'code' = 'd_electro_reel'
                    THEN item || jsonb_build_object('article', 'Ручное перетаскивание кабеля и РВД катушки')
                WHEN item ->> 'code' = 'o_gazelle_amort'
                    THEN item || jsonb_build_object('qty_manager', true, 'comment', 'Количество корректирует менеджер; административная ставка подставляется по офису менеджера')
                WHEN item ->> 'code' = 'd_demo_work'
                    THEN item || jsonb_build_object('comment', 'Количество = время на административные процедуры + время работы на демонстрации; ставка NET на руки подставляется по офису менеджера; НПД считается через 0.94')
                ELSE item
            END
        )
        FROM jsonb_array_elements(COALESCE(s.settings -> 'expense_settings', '[]'::jsonb)) AS item
    ), '[]'::jsonb),
    true
)
WHERE s.id = 1;

-- 5. Продажи v9: премия строки = prem_max × количество.
-- Действия и строки продаж сохраняются, меняются только расчетные производные поля.
WITH sale_calc AS (
    SELECT
        sr.id,
        p.name AS product_name,
        p.price_vat AS product_price_vat,
        p.price_net AS product_price_net,
        COALESCE(
            NULLIF(p.city_params -> COALESCE(u.office_city, 'Казань') ->> 'prem_max', '')::numeric,
            NULLIF(p.city_params -> COALESCE(u.office_city, 'Казань') ->> 'pr', '')::numeric,
            ROUND(COALESCE(p.price_net, 0) * 0.10, 2)
        ) AS prem_max,
        COALESCE(
            NULLIF(p.city_params -> COALESCE(u.office_city, 'Казань') ->> 'mr', '')::numeric,
            ROUND(COALESCE(p.price_net, 0) * 0.20, 2)
        ) AS mr_unit,
        COALESCE(
            NULLIF(p.city_params -> COALESCE(u.office_city, 'Казань') ->> 'st', '')::numeric,
            CASE WHEN COALESCE(u.office_city, 'Казань') = 'Москва' THEN 0.465 ELSE 0.565 END
        ) AS st_pct,
        COALESCE(sr.qty, 1) AS qty
    FROM public.sale_rows sr
    JOIN public.actions a ON a.action_id = sr.action_id
    JOIN public.app_users u ON u.login = a.manager_login
    JOIN public.products p ON p.product_id = sr.product_id
)
UPDATE public.sale_rows sr
SET
    name = sale_calc.product_name,
    pr0_vat = sale_calc.product_price_vat,
    price_vat = sale_calc.product_price_vat,
    price_net = sale_calc.product_price_net,
    total_vat = sale_calc.product_price_vat * sale_calc.qty,
    total_net = sale_calc.product_price_net * sale_calc.qty,
    vat_sum = (sale_calc.product_price_vat - sale_calc.product_price_net) * sale_calc.qty,
    mr_unit = sale_calc.mr_unit,
    pr_unit = sale_calc.prem_max,
    st_pct = sale_calc.st_pct,
    cash_net = sale_calc.prem_max * sale_calc.qty
FROM sale_calc
WHERE sr.id = sale_calc.id;

COMMIT;

-- Контроль: данные не удалены.
SELECT 'users' AS entity, COUNT(*) AS rows_count FROM public.app_users
UNION ALL
SELECT 'actions', COUNT(*) FROM public.actions
UNION ALL
SELECT 'products', COUNT(*) FROM public.products
UNION ALL
SELECT 'sale_rows', COUNT(*) FROM public.sale_rows
UNION ALL
SELECT 'demo_expenses', COUNT(*) FROM public.demo_expenses;
