#!/usr/bin/env python3
"""
Open Design API Client

Vereinfacht die Kommunikation mit der Open Design API für die Integration in WUPHF.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class OpenDesignClient:
    """Client für die Open Design API"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """Prüft ob Open Design verfügbar ist"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Open Design nicht verfügbar: {str(e)}",
                "available": False
            }
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """Listet verfügbare Design-Skills auf"""
        try:
            response = self.session.get(f"{self.base_url}/api/skills", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Abrufen der Skills: {e}")
            return []
    
    def list_design_systems(self) -> List[Dict[str, Any]]:
        """Listet verfügbare Design-Systeme auf"""
        try:
            response = self.session.get(f"{self.base_url}/api/design-systems", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Abrufen der Design-Systeme: {e}")
            return []
    
    def create_design_task(self, 
                          brief: str,
                          skill: str = "web-prototype",
                          design_system: str = "default",
                          scenario: str = "design") -> Dict[str, Any]:
        """
        Erstellt eine neue Design-Aufgabe in Open Design
        
        Args:
            brief: Beschreibung der Design-Aufgabe
            skill: Zu verwendender Design-Skill
            design_system: Zu verwendendes Design-System
            scenario: Szenario (design, marketing, etc.)
        """
        try:
            payload = {
                "skill": skill,
                "brief": brief,
                "designSystem": design_system,
                "scenario": scenario
            }
            
            response = self.session.post(
                f"{self.base_url}/api/runs",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Design-Aufgabe erstellt: {result.get('id', 'unknown')}")
            
            return {
                "status": "success",
                "task_id": result.get('id'),
                "message": "Design-Aufgabe erfolgreich an Open Design übergeben",
                "data": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Erstellen der Design-Aufgabe: {e}")
            return {
                "status": "error",
                "message": f"Fehler bei Open Design API: {str(e)}",
                "fallback": self._suggest_manual_workflow(brief, skill)
            }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Ruft den Status einer Design-Aufgabe ab"""
        try:
            response = self.session.get(f"{self.base_url}/api/runs/{task_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Abrufen des Task-Status: {e}")
            return {
                "status": "error",
                "message": f"Konnte Status nicht abrufen: {str(e)}"
            }
    
    def get_task_artifacts(self, task_id: str) -> List[Dict[str, Any]]:
        """Ruft die generierten Artefakte einer Aufgabe ab"""
        try:
            response = self.session.get(f"{self.base_url}/api/runs/{task_id}/artifacts", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fehler beim Abrufen der Artefakte: {e}")
            return []
    
    def suggest_skill(self, description: str) -> str:
        """Schlägt den passenden Skill basierend auf der Beschreibung vor"""
        desc_lower = description.lower()
        
        skill_mapping = {
            "web-prototype": ["website", "landing", "web", "internet", "online"],
            "mobile-app": ["app", "mobile", "android", "ios", "smartphone"],
            "dashboard": ["dashboard", "admin", "analytics", "charts", "daten"],
            "guizang-ppt": ["präsentation", "slide", "pitch", "folien", "deck"],
            "magazine-poster": ["poster", "grafik", "magazin", "print", "flyer"],
            "saas-landing": ["saas", "software", "landing page", "pricing"],
            "wireframe-sketch": ["wireframe", "sketch", "konzept", "entwurf"]
        }
        
        best_skill = "web-prototype"  # Default
        best_match_count = 0
        
        for skill, keywords in skill_mapping.items():
            match_count = sum(1 for kw in keywords if kw in desc_lower)
            if match_count > best_match_count:
                best_match_count = match_count
                best_skill = skill
        
        return best_skill
    
    def _suggest_manual_workflow(self, brief: str, skill: str) -> str:
        """Gibt eine Anleitung für manuelle Nutzung als Fallback"""
        return (
            f"Open Design API nicht verfügbar. Manuelle Alternative:\n"
            f"1. CD nach /tmp/open-design\n"
            f"2. Starte Open Design: pnpm tools-dev start\n"
            f"3. Öffne http://localhost:3000 im Browser\n"
            f"4. Wähle Skill: {skill}\n"
            f"5. Gib ein: {brief}\n"
        )
    
    def import_claude_design_export(self, zip_path: str) -> Dict[str, Any]:
        """Importiert ein Claude Design Export in Open Design"""
        try:
            with open(zip_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(
                    f"{self.base_url}/api/import/claude-design",
                    files=files,
                    timeout=60
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Fehler beim Import: {e}")
            return {
                "status": "error",
                "message": f"Import fehlgeschlagen: {str(e)}"
            }

# Convenience Funktionen für einfache Nutzung
def create_design_task_auto(description: str, open_design_url: str = "http://localhost:3000") -> Dict[str, Any]:
    """
    Automatische Erstellung einer Design-Aufgabe mit Skill-Detection
    
    Args:
        description: Beschreibung der Design-Aufgabe
        open_design_url: URL der Open Design API
    """
    client = OpenDesignClient(open_design_url)
    
    # Prüfen ob Open Design verfügbar ist
    health = client.health_check()
    if not health.get("available", False):
        return {
            "status": "error",
            "message": "Open Design nicht verfügbar",
            "health_check": health
        }
    
    # Skill automatisch erkennen
    skill = client.suggest_skill(description)
    
    # Aufgabe erstellen
    return client.create_design_task(
        brief=description,
        skill=skill
    )

if __name__ == "__main__":
    # Test usage
    import sys
    
    if len(sys.argv) > 1:
        description = " ".join(sys.argv[1:])
        result = create_design_task_auto(description)
        print(json.dumps(result, indent=2))
    else:
        # Health check
        client = OpenDesignClient()
        health = client.health_check()
        print(json.dumps(health, indent=2))