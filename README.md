# demos2sales

React + FastAPI система учета демонстраций, продаж и премий ИРБИСТЕХ.

Текущая бизнес-версия перенесена из архива `irbistech_react_fastapi_v1_fixed_v2.zip`, при этом сохранена production-инфраструктура текущего репозитория: GitHub Actions, nginx/systemd, same-origin `/api`, lockfile frontend и VPS env-настройки.

## Структура

- `backend/` — FastAPI API, бизнес-логика расчетов, импорт/экспорт Excel по товарам и работа с PostgreSQL.
- `frontend/` — React UI на Vite.
- `db/` — SQL-скрипты для базы `demo_calc`.
- `deploy/` — systemd, nginx и скрипты публикации на VPS.

## Бизнес-логика v3 / Доработка 3

- В демонстрации есть вкладки `Расчеты с водителем`, `Смета демонстрации`, `Расчет вычета`, `P`, `R`, `M`.
- Смета демонстрации фиксирована для всех демонстраций, приведена к Excel-диапазону `0_Расходы на демо!B1:G24` и разбита на водительскую часть и прочие расходы ООО ИРБИСТЕХ.
- Поле `Время работы демонстратором` влияет на расчеты с водителем и строку `Работа демонстратора*`; НПД считается через коэффициент `0.94`.
- Вычет демо считается по формуле `[VIC] = [K2] × [K1] × [DEMO_COST]`, где `[K2] = [xP] × [xR] × [xM]`; критерии P/R/M перенесены из Excel-листов `1_Подготовка`, `2_Результат`, `3_Управленческий`.
- Менеджеры привязаны к офисам Казань/Москва; офисные ставки влияют на смету и продажи.
- Продажи считаются через `[CASH] / [CASH_ALL]` с учетом `PR0`, фактической цены продажи, `MR` и `ST`.
- В премии выводятся `[CASH_ALL_CONFIRM]`, `[VIC_CONFIRM]` и итог `[PROFIT]`.
- В списке действий есть скрытие старых действий, итоговые суммы, перемещение и удаление.
- Справочник товаров поддерживает Excel-экспорт/импорт, сохранение порядка, стрелки перемещения и офисные параметры `MR/PR/ST`.
- `public.sql` в корне архива содержит актуальную схему и демо-данные для быстрой сверки/загрузки.

## Локальный запуск

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DEMO_CALC_DB_PASSWORD=ВАШ_ПАРОЛЬ
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

В dev-режиме Vite проксирует `/api` на `http://127.0.0.1:8000`. В production frontend работает с same-origin `/api` через nginx.

## Переменные окружения

Основной пример находится в `.env.example` и `backend/.env.example`.

В production на VPS файл должен лежать здесь:

```bash
/opt/demos2sales/shared/.env
```

Минимально нужны:

```bash
DEMO_CALC_DB_HOST=127.0.0.1
DEMO_CALC_DB_PORT=5464
DEMO_CALC_DB_NAME=demo_calc
DEMO_CALC_DB_USER=admin
DEMO_CALC_DB_PASSWORD=...
DEMO_CALC_AUTO_SEED_EMPTY_DB=0
DEMO_CALC_JSON_BACKUP_PATH=/opt/demos2sales/shared/data/state_backup.json
```

## Проверки

```bash
python -m py_compile backend/main.py
cd frontend
npm ci
npm run build
```

## Деплой

GitHub Actions workflow `.github/workflows/deploy.yml` собирает frontend, проверяет backend, отправляет архив на VPS и запускает `deploy/remote_deploy.sh`.

Скрипт `deploy/deploy_from_checkout.sh` на сервере:

- создает backend venv;
- устанавливает Python-зависимости;
- выполняет `npm ci` и `npm run build`;
- ставит `demos2sales.service`;
- обновляет nginx config `demos2sales.irbistech.com`;
- перезапускает только `demos2sales.service`;
- проверяет `/api/health`;
- делает pre-deploy backup в `/opt/demos2sales/backups`.

Текущая production-схема:

- React static: `/opt/demos2sales/current/frontend/dist`;
- FastAPI: `127.0.0.1:7861`;
- public domain: `https://demos2sales.irbistech.com`;
- API route: `https://demos2sales.irbistech.com/api/...`.
