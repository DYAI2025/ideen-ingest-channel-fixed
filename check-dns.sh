#!/bin/bash

# DNS Check Script für vision.dyai.cloud

DOMAIN="vision.dyai.cloud"
EXPECTED_IP="93.128.152.173"

echo "🔍 Prüfe DNS für $DOMAIN"
echo "================================"

# Prüfe ob Domain auf die richtige IP zeigt
CURRENT_IP=$(dig +short $DOMAIN @8.8.8.8)

if [ -z "$CURRENT_IP" ]; then
    echo "❌ Domain ist noch nicht im DNS"
    echo "   Bitte folgenden DNS Record erstellen:"
    echo "   Typ: A"
    echo "   Name: vision.dyai.cloud"
    echo "   Wert: $EXPECTED_IP"
    echo "   TTL: 300 (5 Minuten)"
    exit 1
fi

if [ "$CURRENT_IP" = "$EXPECTED_IP" ]; then
    echo "✅ DNS korrekt: $DOMAIN → $CURRENT_IP"
else
    echo "⚠️  DNS zeigt auf falsche IP:"
    echo "   Erwartet: $EXPECTED_IP"
    echo "   Aktuell:  $CURRENT_IP"
    echo "   Bitte DNS Record aktualisieren"
    exit 1
fi

# Prüfe verschiedene DNS Server
echo ""
echo "📡 DNS Propagation Check:"
for server in "8.8.8.8" "1.1.1.1" "ns1.dyai.cloud"; do
    IP=$(dig +short $DOMAIN @$server 2>/dev/null || echo "N/A")
    echo "   $server: $IP"
done

echo ""
echo "✅ DNS ist bereit für SSL-Zertifikate!"