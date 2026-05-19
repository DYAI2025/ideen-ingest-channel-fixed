#!/bin/bash
# Setup-Skript für die WUPHF + Open Design Integration

set -e

echo "🚀 WUPHF + Open Design Integration Setup"
echo "=========================================="

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Pfad zum Orchestrator
ORCHESTRATOR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WUPHF_ROOT="$(cd "$ORCHESTRATOR_DIR/../../../.." && pwd)"

echo -e "${GREEN}✓${NC} Pfad zum Orchestrator: $ORCHESTRATOR_DIR"
echo -e "${GREEN}✓${NC} WUPHF Root: $WUPHF_ROOT"

# 1. Python Dependencies installieren
echo -e "${YELLOW}→${NC} Installiere Python Dependencies..."
cd "$ORCHESTRATOR_DIR"
pip install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Python Dependencies installiert"
else
    echo -e "${RED}✗${NC} Fehler beim Installieren der Dependencies"
    exit 1
fi

# 2. Open Design prüfen/klonen
echo -e "${YELLOW}→${NC} Prüfe Open Design Installation..."
if [ ! -d "/tmp/open-design" ]; then
    echo -e "${YELLOW}→${NC} Klone Open Design Repository..."
    cd /tmp
    git clone https://github.com/DYAI2025/open-design.git --quiet
    echo -e "${GREEN}✓${NC} Open Design geklont nach /tmp/open-design"
else
    echo -e "${GREEN}✓${NC} Open Design bereits vorhanden"
fi

# 3. Open Design Dependencies installieren
echo -e "${YELLOW}→${NC} Installiere Open Design Dependencies..."
cd /tmp/open-design
if [ ! -d "node_modules" ]; then
    pnpm install --silent
    echo -e "${GREEN}✓${NC} Open Design Dependencies installiert"
else
    echo -e "${GREEN}✓${NC} Open Design Dependencies bereits installiert"
fi

# 4. Skripte ausführbar machen
echo -e "${YELLOW}→${NC} Mache Skripte ausführbar..."
chmod +x "$ORCHESTRATOR_DIR/orchestrator.py"
chmod +x "$ORCHESTRATOR_DIR/task_classifier.py"
chmod +x "$ORCHESTRATOR_DIR/open_design_client.py"
chmod +x "$ORCHESTRATOR_DIR/../design-workflow/design_bridge.py"
echo -e "${GREEN}✓${NC} Skripte ausführbar gemacht"

# 5. Environment Variablen setzen
echo -e "${YELLOW}→${NC} Setze Environment Variablen..."
export WUPHF_URL="${WUPHF_URL:-http://localhost:30000}"
export OPEN_DESIGN_URL="${OPEN_DESIGN_URL:-http://localhost:3000}"
export ORCHESTRATOR_PORT="${ORCHESTRATOR_PORT:-5000}"

echo -e "${GREEN}✓${NC} Environment Variablen:"
echo "  WUPHF_URL=$WUPHF_URL"
echo "  OPEN_DESIGN_URL=$OPEN_DESIGN_URL"
echo "  ORCHESTRATOR_PORT=$ORCHESTRATOR_PORT"

# 6. Konfigurationsdatei erstellen
echo -e "${YELLOW}→${NC} Erstelle Konfigurationsdatei..."
cat > "$ORCHESTRATOR_DIR/config.json" <<EOF
{
  "wuphf_url": "$WUPHF_URL",
  "open_design_url": "$OPEN_DESIGN_URL",
  "orchestrator_port": $ORCHESTRATOR_PORT,
  "auto_classify": true,
  "hybrid_tasks": true,
  "fallback_to_manual": true
}
EOF

echo -e "${GREEN}✓${NC} Konfiguration gespeichert in config.json"

# 7. System Health Check
echo -e "${YELLOW}→${NC} System Health Check..."

# WUPHF prüfen
echo -n "  WUPHF: "
if curl -s "$WUPHF_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Verfügbar"
else
    echo -e "${YELLOW}⚠${NC} Nicht verfügbar (wird gestartet wenn benötigt)"
fi

# Open Design prüfen
echo -n "  Open Design: "
if curl -s "$OPEN_DESIGN_URL/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Verfügbar"
else
    echo -e "${YELLOW}⚠${NC} Nicht verfügbar (wird gestartet wenn benötigt)"
fi

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}✓${NC} Setup abgeschlossen!"
echo ""
echo "Nächste Schritte:"
echo "1. Starte WUPHF: cd $WUPHF_ROOT && ./wuphf --provider ollama"
echo "2. Starte Open Design (optional): cd /tmp/open-design && pnpm tools-dev start"
echo "3. Starte Orchestrator: cd $ORCHESTRATOR_DIR && python orchestrator.py"
echo ""
echo "Oder nutze den automatischen Watch-Mode:"
echo "  python task_classifier.py --watch"
echo ""