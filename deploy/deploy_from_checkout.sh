#!/usr/bin/env bash
set -Eeuo pipefail

umask 027

APP_NAME="${APP_NAME:-demos2sales}"
APP_BASE_DIR="${APP_BASE_DIR:-/opt/${APP_NAME}}"
APP_USER="${APP_USER:-www-data}"
APP_GROUP="${APP_GROUP:-${APP_USER}}"
SERVICE_NAME="${SERVICE_NAME:-demos2sales.service}"
RELEASES_TO_KEEP="${RELEASES_TO_KEEP:-5}"
RELEASE_DIR="${RELEASE_DIR:-$(pwd)}"
RELEASES_DIR="${APP_BASE_DIR}/releases"
SHARED_DIR="${APP_BASE_DIR}/shared"
CURRENT_LINK="${APP_BASE_DIR}/current"
BACKUPS_DIR="${APP_BASE_DIR}/backups"
SERVICE_SOURCE="${RELEASE_DIR}/deploy/demos2sales.service"
NGINX_SOURCE="${RELEASE_DIR}/deploy/demos2sales.nginx.conf"
NGINX_TARGET="${NGINX_TARGET:-/etc/nginx/sites-available/demos2sales.irbistech.com.conf}"
INSTALL_NGINX_CONFIG="${INSTALL_NGINX_CONFIG:-1}"
CREATE_DEPLOY_BACKUP="${CREATE_DEPLOY_BACKUP:-1}"
BACKEND_PORT="${BACKEND_PORT:-7861}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "This deploy script must run as root." >&2
  exit 1
fi

if [[ ! -d "${RELEASE_DIR}" ]]; then
  echo "Release directory not found: ${RELEASE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${RELEASE_DIR}/backend/requirements.txt" ]]; then
  echo "backend/requirements.txt not found in ${RELEASE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${RELEASE_DIR}/frontend/package.json" ]]; then
  echo "frontend/package.json not found in ${RELEASE_DIR}" >&2
  exit 1
fi

if [[ ! "${RELEASES_TO_KEEP}" =~ ^[0-9]+$ ]] || [[ "${RELEASES_TO_KEEP}" -lt 1 ]]; then
  echo "RELEASES_TO_KEEP must be a positive integer, got: ${RELEASES_TO_KEEP}" >&2
  exit 1
fi

command -v python3 >/dev/null 2>&1 || { echo "python3 is required"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required"; exit 1; }
command -v systemctl >/dev/null 2>&1 || { echo "systemctl is required"; exit 1; }

mkdir -p "${RELEASES_DIR}" "${SHARED_DIR}/data" "${SHARED_DIR}/uploads/demo_reports" "${BACKUPS_DIR}"

if [[ ! -f "${SHARED_DIR}/.env" ]]; then
  echo "Missing ${SHARED_DIR}/.env. Create it from .env.example before deploy." >&2
  exit 1
fi

if [[ "${CREATE_DEPLOY_BACKUP}" == "1" ]]; then
  backup_dir="${BACKUPS_DIR}/pre-deploy-$(date -u +%Y%m%d%H%M%S)"
  mkdir -p "${backup_dir}"
  readlink -f "${CURRENT_LINK}" > "${backup_dir}/current_link.txt" 2>/dev/null || true
  [[ -f "/etc/systemd/system/${SERVICE_NAME}" ]] && cp -a "/etc/systemd/system/${SERVICE_NAME}" "${backup_dir}/${SERVICE_NAME}" || true
  [[ -e "${NGINX_TARGET}" ]] && cp -aL "${NGINX_TARGET}" "${backup_dir}/demos2sales.irbistech.com.conf" || true
  if command -v pg_dump >/dev/null 2>&1 && id postgres >/dev/null 2>&1; then
    runuser -u postgres -- pg_dump -p 5464 -Fc demo_calc > "${backup_dir}/demo_calc.dump" 2>/dev/null || rm -f "${backup_dir}/demo_calc.dump"
  fi
  echo "Backup directory: ${backup_dir}"
fi

python3 -m venv "${RELEASE_DIR}/backend/.venv"
"${RELEASE_DIR}/backend/.venv/bin/pip" install --upgrade pip
"${RELEASE_DIR}/backend/.venv/bin/pip" install -r "${RELEASE_DIR}/backend/requirements.txt"

pushd "${RELEASE_DIR}/frontend" >/dev/null
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
npm run build
rm -rf node_modules
popd >/dev/null

install -m 644 "${SERVICE_SOURCE}" "/etc/systemd/system/${SERVICE_NAME}"

if [[ "${INSTALL_NGINX_CONFIG}" == "1" ]]; then
  install -m 644 "${NGINX_SOURCE}" "${NGINX_TARGET}"
fi

ln -sfn "${RELEASE_DIR}" "${CURRENT_LINK}"
chown -h "${APP_USER}:${APP_GROUP}" "${CURRENT_LINK}"
chown -R "${APP_USER}:${APP_GROUP}" "${APP_BASE_DIR}"
chmod -R u=rwX,g=rX,o=rX "${RELEASE_DIR}"

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}" >/dev/null 2>&1 || true
systemctl restart "${SERVICE_NAME}"

for _ in $(seq 1 30); do
  if curl -fsS --max-time 3 "http://127.0.0.1:${BACKEND_PORT}/api/health" >/dev/null; then
    break
  fi
  sleep 1
done

curl -fsS --max-time 5 "http://127.0.0.1:${BACKEND_PORT}/api/health" >/dev/null

if [[ "${INSTALL_NGINX_CONFIG}" == "1" ]]; then
  nginx -t
  systemctl reload nginx
fi

find "${RELEASES_DIR}" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' \
  | sort -nr \
  | awk -v keep="${RELEASES_TO_KEEP}" 'NR > keep {print $2}' \
  | xargs -r rm -rf

echo "Deployment finished."
echo "Current release: ${RELEASE_DIR}"
systemctl --no-pager --full status "${SERVICE_NAME}" || true
