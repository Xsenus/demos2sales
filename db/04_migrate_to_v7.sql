-- 04_migrate_to_v7.sql
-- Безопасная миграция текущей базы под v7.
-- Файлы отчетов по демонстрациям сохраняются на VPS, а метаданные хранятся в actions.payload.demo_report.

ALTER TABLE actions ADD COLUMN IF NOT EXISTS payload JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE app_users ADD COLUMN IF NOT EXISTS office_city TEXT NOT NULL DEFAULT 'Казань';
ALTER TABLE products ADD COLUMN IF NOT EXISTS row_order INTEGER NOT NULL DEFAULT 0;
ALTER TABLE products ADD COLUMN IF NOT EXISTS city_params JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE demo_expenses ADD COLUMN IF NOT EXISTS row_code TEXT NOT NULL DEFAULT '';

-- Добавить офисную ставку «Работа демонстратора*» для филиалов, если ее еще нет в JSON-настройках.
UPDATE app_settings
SET settings = jsonb_set(
    jsonb_set(
      settings,
      '{office_rates,Казань,demo_work_rate}',
      to_jsonb(COALESCE(NULLIF(settings #>> '{office_rates,Казань,demo_work_rate}', '')::numeric, 1350.0::numeric)),
      true
    ),
    '{office_rates,Москва,demo_work_rate}',
    to_jsonb(COALESCE(NULLIF(settings #>> '{office_rates,Москва,demo_work_rate}', '')::numeric, 1350.0::numeric)),
    true
)
WHERE id = 1;

-- Разрешить менеджеру корректировать количество по строке «Амортизация Газели и ТО».
UPDATE app_settings
SET settings = jsonb_set(settings, '{expense_settings}', updated.rows, true)
FROM (
  SELECT id,
         jsonb_agg(
           CASE
             WHEN elem ->> 'code' = 'o_gazelle_amort' THEN
               elem || jsonb_build_object(
                 'qty_manager', true,
                 'comment', 'Количество корректирует менеджер; административная ставка подставляется по офису менеджера'
               )
             ELSE elem
           END
           ORDER BY ord
         ) AS rows
  FROM app_settings,
       jsonb_array_elements(settings -> 'expense_settings') WITH ORDINALITY AS t(elem, ord)
  WHERE jsonb_typeof(settings -> 'expense_settings') = 'array'
  GROUP BY id
) AS updated
WHERE app_settings.id = updated.id;
