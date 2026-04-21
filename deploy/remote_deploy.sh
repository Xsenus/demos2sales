#!/usr/bin/env bash
set -Eeuo pipefail

umask 027

RELEASE_ARCHIVE="${1:?Usage: remote_deploy.sh <release-archive> <release-id>}"
RELEASE_ID="${2:-manual-$(date -u +%Y%m%d%H%M%S)}"

APP_NAME="${APP_NAME:-demos2sales}"
APP_BASE_DIR="${APP_BASE_DIR:-/opt/${APP_NAME}}"
APP_USER="${APP_USER:-www-data}"
APP_GROUP="${APP_GROUP:-${APP_USER}}"
SERVICE_NAME="${SERVICE_NAME:-demos2sales.service}"
RELEASES_TO_KEEP="${RELEASES_TO_KEEP:-5}"

RELEASES_DIR="${APP_BASE_DIR}/releases"
RELEASE_DIR="${RELEASES_DIR}/${RELEASE_ID}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "This deploy script must run as root." >&2
  exit 1
fi

if [[ ! -f "${RELEASE_ARCHIVE}" ]]; then
  echo "Release archive not found: ${RELEASE_ARCHIVE}" >&2
  exit 1
fi

mkdir -p "${RELEASES_DIR}"
rm -rf "${RELEASE_DIR}"
mkdir -p "${RELEASE_DIR}"
tar -xzf "${RELEASE_ARCHIVE}" -C "${RELEASE_DIR}"

if [[ ! -x "${RELEASE_DIR}/deploy/deploy_from_checkout.sh" ]]; then
  chmod +x "${RELEASE_DIR}/deploy/deploy_from_checkout.sh"
fi

APP_NAME="${APP_NAME}" \
APP_BASE_DIR="${APP_BASE_DIR}" \
APP_USER="${APP_USER}" \
APP_GROUP="${APP_GROUP}" \
SERVICE_NAME="${SERVICE_NAME}" \
RELEASES_TO_KEEP="${RELEASES_TO_KEEP}" \
RELEASE_DIR="${RELEASE_DIR}" \
bash "${RELEASE_DIR}/deploy/deploy_from_checkout.sh"

rm -f "${RELEASE_ARCHIVE}" /tmp/remote_deploy.sh
