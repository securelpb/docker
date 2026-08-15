#!/bin/bash

# Define paths and router IP
ROUTER_IP="router.lan"
CERT_DIR="/home/alex/src/docker/OpenClaw/nginx/certs"
DOMAIN="securesmith.net"
PASSWORD="my-temporary-password"

echo "[*] Pulling certificates from RouterOS..."
scp $ROUTER_IP:cert_export_$DOMAIN.crt $CERT_DIR/$DOMAIN.crt
scp $ROUTER_IP:cert_export_$DOMAIN.key $CERT_DIR/$DOMAIN.enc.key

echo "[*] Decrypting the private key for Nginx..."
openssl rsa -in $CERT_DIR/$DOMAIN.enc.key -out $CERT_DIR/$DOMAIN.key -passin pass:$PASSWORD
chmod 600 $CERT_DIR/$DOMAIN.key
rm $CERT_DIR/$DOMAIN.enc.key

echo "[*] Building the Full Certificate Chain..."
ISSUER_URL=$(openssl x509 -in $CERT_DIR/$DOMAIN.crt -noout -text | grep "CA Issuers" | awk -F 'URI:' '{print $2}' | tr -d ' ')

if [ -n "$ISSUER_URL" ]; then
    echo "[*] Downloading Intermediate CA from: $ISSUER_URL"
    curl -s $ISSUER_URL -o $CERT_DIR/intermediate.der
    openssl x509 -inform der -in $CERT_DIR/intermediate.der -out $CERT_DIR/intermediate.pem
    cat $CERT_DIR/intermediate.pem >> $CERT_DIR/$DOMAIN.crt
    rm $CERT_DIR/intermediate.der $CERT_DIR/intermediate.pem
else
    echo "[!] Could not extract Issuer URL. Proceeding with leaf cert only."
fi

echo "[*] Reloading Nginx to apply the new certificates..."
docker compose -f /home/alex/src/docker/OpenClaw/docker-compose.yml restart nginx

echo "[*] Certificate sync complete!"