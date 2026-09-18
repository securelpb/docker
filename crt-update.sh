#!/bin/bash
set -e

# Define paths and router IP
ROUTER_IP="router.lan"
ROUTER_EXPORT_DIR="usb1/nginx/certs"
CERT_DIR="/var/local/nginx/certs"
DOMAIN="securesmith.net"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create a temporary directory for downloading and processing
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

echo "[*] Pulling certificates from RouterOS to temporary directory..."
scp "$ROUTER_IP:$ROUTER_EXPORT_DIR/$DOMAIN.crt" "$TMP_DIR/$DOMAIN.crt"
scp "$ROUTER_IP:$ROUTER_EXPORT_DIR/$DOMAIN.key" "$TMP_DIR/$DOMAIN.key"

echo "[*] Building the Full Certificate Chain in temporary directory..."
ISSUER_URL=$(openssl x509 -in "$TMP_DIR/$DOMAIN.crt" -noout -text 2>/dev/null | grep "CA Issuers" | awk -F 'URI:' '{print $2}' | tr -d ' ')

if [ -n "$ISSUER_URL" ]; then
    echo "[*] Downloading Intermediate CA from: $ISSUER_URL"
    if curl -s "$ISSUER_URL" -o "$TMP_DIR/intermediate.der"; then
        openssl x509 -inform der -in "$TMP_DIR/intermediate.der" -out "$TMP_DIR/intermediate.pem" 2>/dev/null
        if [ -s "$TMP_DIR/intermediate.pem" ]; then
            cat "$TMP_DIR/intermediate.pem" >> "$TMP_DIR/$DOMAIN.crt"
        fi
    fi
else
    echo "[!] Could not extract Issuer URL. Proceeding with leaf cert only."
fi

# Compare the new certificate and key with the existing files
if [ -f "$CERT_DIR/$DOMAIN.crt" ] && cmp -s "$TMP_DIR/$DOMAIN.crt" "$CERT_DIR/$DOMAIN.crt" && [ -f "$CERT_DIR/$DOMAIN.key" ] && cmp -s "$TMP_DIR/$DOMAIN.key" "$CERT_DIR/$DOMAIN.key"; then
    echo "[*] Certificate has not changed. No update or restart needed."
    exit 0
fi

echo "[*] Certificate change detected. Updating certificates in $CERT_DIR..."
mkdir -p "$CERT_DIR"
cp "$TMP_DIR/$DOMAIN.crt" "$CERT_DIR/$DOMAIN.crt"
cp "$TMP_DIR/$DOMAIN.key" "$CERT_DIR/$DOMAIN.key"
chmod 600 "$CERT_DIR/$DOMAIN.key"

CURRENT_HOST="$(hostname -s 2>/dev/null || hostname)"

echo "[*] Reloading Nginx services..."
if [ "$CURRENT_HOST" = "hal" ]; then
    echo "[*] Host is 'hal': Restarting OpenClaw Nginx..."
    docker compose -f "$SCRIPT_DIR/OpenClaw/docker-compose.yml" restart nginx
elif [ "$CURRENT_HOST" = "art" ]; then
    echo "[*] Host is 'art': Restarting ThingsBoard Nginx..."
    docker compose -f "$SCRIPT_DIR/thingsboard/docker-compose.yml" restart nginx
else
    echo "[*] Host '$CURRENT_HOST' does not match 'hal' or 'art'. Skipping Nginx restart."
fi

echo "[*] Certificate sync complete!"
