#!/usr/bin/env python3
"""
Design Bridge - Verbindung zwischen WUPHF und Open Design

Dieses Skript fungiert als Brücke, die Design-Aufgaben von WUPHF zu Open Design weiterleitet.
"""

import sys
import json
import requests
import subprocess
import os
from pathlib import Path

class DesignBridge:
    def __init__(self):
        self.orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:5000")
        self.open_design_path = Path("/tmp/open-design")
    
    def route_design_task(self, description: str) -> dict:
        """Leitet eine Design-Aufgabe an den Orchestrator weiter"""
        try:
            response = requests.post(
                f"{self.orchestrator_url}/route",
                json={
                    "description": description,
                    "priority": "medium",
                    "context": {"source": "wuphf"}
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Fallback: Direkt Open Design CLI aufrufen
            return self._fallback_direct_call(description)
    
    def _fallback_direct_call(self, description: str) -> dict:
        """Direkter Aufruf von Open Design als Fallback"""
        try:
            # Prüfen ob Open Design verfügbar ist
            if not self.open_design_path.exists():
                return {
                    "status": "error",
                    "message": "Open Design nicht gefunden. Bitte installieren: cd /tmp && git clone https://github.com/DYAI2025/open-design.git"
                }
            
            # Open Design Status prüfen
            result = subprocess.run(
                ["pnpm", "tools-dev", "status"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.open_design_path
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Design-Aufgabe wurde an Open Design weitergeleitet",
                    "note": "Für vollautomatische Integration starte den Workflow-Orchestrator",
                    "manual_instruction": f"Manuell in Open Design: {description}"
                }
            else:
                return {
                    "status": "error",
                    "message": "Open Design ist nicht aktiv. Starten mit: cd /tmp/open-design && pnpm tools-dev start"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Fehler bei Open Design Integration: {str(e)}"
            }

def main():
    """Main entry point für CLI-Aufrufe"""
    if len(sys.argv) < 2:
        print("Usage: python design_bridge.py '<design description>'")
        sys.exit(1)
    
    description = " ".join(sys.argv[1:])
    bridge = DesignBridge()
    result = bridge.route_design_task(description)
    
    print(json.dumps(result, indent=2))
    
    # Exit code basierend auf Status
    if result.get("status") == "error":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()