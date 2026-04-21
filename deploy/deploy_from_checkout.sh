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
SERVICE_SOURCE="${RELEASE_DIR}/deploy/demos2sales.service"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "This deploy script must run as root." >&2
  exit 1
fi

if [[ ! -d "${RELEASE_DIR}" ]]; then
  echo "Release directory not found: ${RELEASE_DIR}" >&2
  exit 1
fi

if [[ ! -f "${RELEASE_DIR}/requirements.txt" ]]; then
  echo "requirements.txt not found in ${RELEASE_DIR}" >&2
  exit 1
fi

if [[ ! "${RELEASES_TO_KEEP}" =~ ^[0-9]+$ ]] || [[ "${RELEASES_TO_KEEP}" -lt 1 ]]; then
  echo "RELEASES_TO_KEEP must be a positive integer, got: ${RELEASES_TO_KEEP}" >&2
  exit 1
fi

command -v python3 >/dev/null 2>&1 || { echo "python3 is required"; exit 1; }
command -v systemctl >/dev/null 2>&1 || { echo "systemctl is required"; exit 1; }

mkdir -p "${RELEASES_DIR}" "${SHARED_DIR}/data" "${SHARED_DIR}/exports"

if [[ ! -f "${SHARED_DIR}/.env" ]]; then
  echo "Missing ${SHARED_DIR}/.env. Create it from .env.example before deploy." >&2
  exit 1
fi

python3 -m venv "${RELEASE_DIR}/.venv"
"${RELEASE_DIR}/.venv/bin/pip" install --upgrade pip
"${RELEASE_DIR}/.venv/bin/pip" install -r "${RELEASE_DIR}/requirements.txt"

if [[ -f "${SERVICE_SOURCE}" ]]; then
  install -m 644 "${SERVICE_SOURCE}" "/etc/systemd/system/${SERVICE_NAME}"
fi

ln -sfn "${RELEASE_DIR}" "${CURRENT_LINK}"
chown -h "${APP_USER}:${APP_GROUP}" "${CURRENT_LINK}"
chown -R "${APP_USER}:${APP_GROUP}" "${APP_BASE_DIR}"

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}" >/dev/null 2>&1 || true
systemctl restart "${SERVICE_NAME}"

find "${RELEASES_DIR}" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' \
  | sort -nr \
  | awk -v keep="${RELEASES_TO_KEEP}" 'NR > keep {print $2}' \
  | xargs -r rm -rf

echo "Deployment finished."
echo "Current release: ${RELEASE_DIR}"
systemctl --no-pager --full status "${SERVICE_NAME}" || true
