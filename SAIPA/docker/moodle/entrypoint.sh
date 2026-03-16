#!/bin/bash
set -e

MOODLE_TAG="${MOODLE_TAG:-v4.4.12}"
MOODLE_DIR="/var/www/html"
MOODLE_DATA="/var/www/moodledata"

log() { echo "[SAIPA-MOODLE] $*"; }

# ── 1. Download Moodle if not present ─────────────────────────────────────────
if [ ! -f "$MOODLE_DIR/version.php" ]; then
    log "Downloading Moodle ${MOODLE_TAG} from GitHub..."
    wget -q -L \
        "https://github.com/moodle/moodle/archive/refs/tags/${MOODLE_TAG}.tar.gz" \
        -O /tmp/moodle.tar.gz
    log "Extracting Moodle..."
    tar -xzf /tmp/moodle.tar.gz --strip-components=1 -C "$MOODLE_DIR"
    rm /tmp/moodle.tar.gz
    # Make top-level dirs writable by www-data for runtime cache files.
    # Avoid recursive chown to prevent clobbering bind-mounted plugin dirs.
    chown www-data:www-data "$MOODLE_DIR"
    log "Moodle ${MOODLE_TAG} extracted OK"
fi

# ── 2. Create moodledata directory ─────────────────────────────────────────────
mkdir -p "$MOODLE_DATA"
chown -R www-data:www-data "$MOODLE_DATA"

# ── 3. Wait for PostgreSQL ──────────────────────────────────────────────────────
log "Waiting for PostgreSQL at ${MOODLE_DB_HOST}:${MOODLE_DB_PORT}..."
until pg_isready -h "${MOODLE_DB_HOST}" -p "${MOODLE_DB_PORT}" \
                 -U "${MOODLE_DB_USER}" -d "${MOODLE_DB_NAME}" 2>/dev/null; do
    sleep 2
done
log "PostgreSQL is ready"

# ── 4. Install Moodle (first run only) ─────────────────────────────────────────
if [ ! -f "$MOODLE_DIR/config.php" ]; then
    log "Running Moodle CLI installer (this takes ~2 minutes)..."
    php "$MOODLE_DIR/admin/cli/install.php" \
        --dbtype=pgsql \
        --dbhost="${MOODLE_DB_HOST}" \
        --dbport="${MOODLE_DB_PORT}" \
        --dbname="${MOODLE_DB_NAME}" \
        --dbuser="${MOODLE_DB_USER}" \
        --dbpass="${MOODLE_DB_PASSWORD}" \
        --dataroot="$MOODLE_DATA" \
        --wwwroot="${MOODLE_WWWROOT}" \
        --adminuser="${MOODLE_ADMIN_USER}" \
        --adminpass="${MOODLE_ADMIN_PASSWORD}" \
        --adminemail="${MOODLE_ADMIN_EMAIL}" \
        --fullname="${MOODLE_SITE_NAME}" \
        --shortname="${MOODLE_SITE_SHORTNAME}" \
        --agree-license \
        --non-interactive
    chown www-data:www-data "$MOODLE_DIR/config.php"
    chown -R www-data:www-data "$MOODLE_DATA"
    log "Moodle installation complete"
else
    log "Moodle already installed — skipping install"
fi

# ── 5. Start cron in background ────────────────────────────────────────────────
(while true; do
    su -s /bin/sh www-data -c "php $MOODLE_DIR/admin/cli/cron.php" >> /var/log/moodle-cron.log 2>&1
    sleep 60
done) &

log "Starting Apache..."
exec apache2-foreground
