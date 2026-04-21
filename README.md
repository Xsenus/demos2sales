# demos2sales

Внутренняя система учета демонстраций, продаж и премий ИРБИСТЕХ.

Приложение работает как Gradio UI поверх PostgreSQL и уже развернуто на:

- production: `https://demos2sales.irbistech.com/`
- server: `79.174.94.14`
- app dir on VPS: `/opt/demos2sales`
- git remote on VPS: `/opt/git/demos2sales.git`
- local `origin`: `demos2sales-vps:/opt/git/demos2sales.git`

## Что делает система

- ведет журнал действий менеджеров: демонстрации, продажи, выплаты премий;
- считает смету демонстрации и вычет из премии;
- считает премию по продаже;
- агрегирует период до выплаты премии;
- хранит данные в PostgreSQL базе `demo_calc`;
- работает за `nginx + systemd`.

## Текущий стек

- Python 3.12+
- Gradio
- pandas
- PostgreSQL
- systemd
- nginx

## Структура проекта

- `serve.py` — точка запуска production-сервиса.
- `irbistech_demo_sales_premiums_colab_v6_5_sql(1).py` — основная бизнес-логика приложения.
- `demo_calculator_widget.py` — встроенный калькулятор сметы демонстрации.
- `requirements.txt` — Python-зависимости.
- `.env.example` — пример production-конфига.
- `deploy/demos2sales.service` — systemd unit.
- `deploy/deploy_from_checkout.sh` — deploy-скрипт для release-based выкладки.
- `deploy/remote_deploy.sh` — удаленный deploy-скрипт для GitHub Actions.
- `deploy/post-receive.example` — пример hook для bare git repo на VPS.
- `deploy/demos2sales.nginx.conf.example` — reference nginx-конфиг.
- `.github/workflows/deploy.yml` — GitHub Actions workflow для production-деплоя.

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python serve.py
```

По умолчанию приложение поднимается на `127.0.0.1:7860`.

## Проверка перед публикацией

```bash
python -m py_compile "irbistech_demo_sales_premiums_colab_v6_5_sql(1).py" demo_calculator_widget.py serve.py
```

## Git и автодеплой

Сейчас поддерживаются две схемы деплоя:

1. `VPS git remote` — уже рабочая резервная схема, где push идет прямо в bare-repo на сервере.
2. `GitHub Actions` — целевая схема, где push идет в GitHub, а GitHub сам выкладывает релиз на VPS.

Для проекта настроена схема:

1. Локальный рабочий каталог `demos2sales` — обычный git-репозиторий.
2. На VPS поднят bare-репозиторий `/opt/git/demos2sales.git`.
3. `git push origin main` отправляет изменения в bare-репозиторий.
4. `post-receive` hook на VPS автоматически:
   - создает новый release в `/opt/demos2sales/releases/<timestamp>-<sha>`;
   - разворачивает код из нового коммита;
   - собирает `.venv` и ставит зависимости;
   - переключает `/opt/demos2sales/current`;
   - перезапускает `demos2sales.service`;
   - чистит старые релизы.

Это значит, что публикация кода и деплой сведены к одному действию:

```bash
git add .
git commit -m "Update demos2sales"
git push origin main
```

SSH alias для этого репозитория хранится в локальном `~/.ssh/config`:

- host: `demos2sales-vps`
- key: `~/.ssh/id_ed25519_demos2sales_vps`

## GitHub Actions схема

Для GitHub-схемы в проект уже добавлен workflow:

- `.github/workflows/deploy.yml`

Он делает следующее:

1. Забирает код из GitHub.
2. Ставит Python и зависимости.
3. Проверяет Python-файлы через `py_compile`.
4. Собирает release archive.
5. Подключается к VPS по SSH.
6. Загружает архив и `deploy/remote_deploy.sh`.
7. Создает новый release в `/opt/demos2sales/releases/...`.
8. Переключает `current` и перезапускает `demos2sales.service`.

### Секреты, которые нужно добавить в GitHub repository secrets

- `VPS_HOST` = `79.174.94.14`
- `VPS_PORT` = `22`
- `VPS_USER` = `root`
- `VPS_SSH_KEY` = приватный ключ GitHub Actions для deploy

### Ключ для GitHub Actions

Под GitHub Actions выделен отдельный deploy-ключ:

- private key: `~/.ssh/id_ed25519_demos2sales_github_actions`
- public key: `~/.ssh/id_ed25519_demos2sales_github_actions.pub`

Публичная часть должна быть добавлена на VPS в `root/.ssh/authorized_keys`, а приватную часть нужно положить в GitHub secret `VPS_SSH_KEY`.

### Когда появится GitHub-репозиторий

После создания пустого репозитория на GitHub рекомендуется:

```bash
git remote rename origin vps
git remote add origin <github-repo-url>
git push -u origin main
```

Тогда:

- `origin` будет GitHub;
- `vps` останется резервным прямым deploy-remote;
- production будет выкатываться через GitHub Actions.

## Production окружение

Основные runtime-пути:

- code: `/opt/demos2sales/current`
- shared env: `/opt/demos2sales/shared/.env`
- shared data: `/opt/demos2sales/shared/data`
- shared exports: `/opt/demos2sales/shared/exports`
- service: `demos2sales.service`

Приложение в production работает от пользователя `www-data`.

## Важные замечания

- `.env` не хранится в git и живет только на сервере.
- runtime-папка `data/` не коммитится.
- база `demo_calc` является общей рабочей базой проекта, ее нельзя пересоздавать seed-скриптами на production.
- исходный main-файл пока оставлен в клиентском имени, чтобы не ломать совместимость с уже развернутым сервисом.
