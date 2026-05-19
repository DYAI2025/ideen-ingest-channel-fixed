#!/usr/bin/env python3
"""
Workflow Orchestrator - Automatische Weiterleitung zwischen WUPHF und Open Design

Dieser Orchestrator analysiert Aufgaben und leitet sie an das optimale System weiter:
- Design-Tasks → Open Design
- Development-Tasks → WUPHF  
- Hybrid-Tasks → Kombinierter Workflow
"""

import json
import re
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import requests
import os

class TaskType(Enum):
    DESIGN = "design"
    DEVELOPMENT = "development"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"

@dataclass
class Task:
    description: str
    priority: str = "medium"
    context: Dict = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

class WorkflowOrchestrator:
    def __init__(self):
        # Konfiguration
        self.wuphf_url = os.getenv("WUPHF_URL", "http://localhost:30000")
        self.open_design_url = os.getenv("OPEN_DESIGN_URL", "http://localhost:3000")
        
        # Keywords für Klassifikation
        self.design_keywords = [
            "design", "ui", "ux", "interface", "layout", "grafik", "bild",
            "präsentation", "slide", "poster", "farbe", "typografie", "logo",
            "branding", "visual", "wireframe", "mockup", "prototype", "css",
            "styling", "theme", "icon", "illustration", "animation", "video"
        ]
        
        self.dev_keywords = [
            "code", "programmieren", "entwicklung", "api", "backend", "frontend",
            "database", "sql", "algorithmus", "debug", "fix", "refactor",
            "architektur", "server", "deployment", "test", "git", "commit",
            "function", "class", "variable", "script", "integration", "library"
        ]
        
        # Status tracking
        self.active_tasks: Dict[str, Dict] = {}
    
    def classify_task(self, task: Task) -> TaskType:
        """Klassifiziert eine Aufgabe basierend auf Keywords"""
        desc_lower = task.description.lower()
        
        design_score = sum(1 for kw in self.design_keywords if kw in desc_lower)
        dev_score = sum(1 for kw in self.dev_keywords if kw in desc_lower)
        
        if design_score > 0 and dev_score > 0:
            return TaskType.HYBRID
        elif design_score > 0:
            return TaskType.DESIGN
        elif dev_score > 0:
            return TaskType.DEVELOPMENT
        else:
            return TaskType.UNKNOWN
    
    def route_task(self, task: Task) -> Dict:
        """Leitet eine Aufgabe an das passende System weiter"""
        task_type = self.classify_task(task)
        task_id = self._generate_task_id()
        
        result = {
            "task_id": task_id,
            "task_type": task_type.value,
            "description": task.description,
            "status": "processing",
            "result": None
        }
        
        try:
            if task_type == TaskType.DESIGN:
                result["result"] = self._route_to_open_design(task)
            elif task_type == TaskType.DEVELOPMENT:
                result["result"] = self._route_to_wuphf(task)
            elif task_type == TaskType.HYBRID:
                result["result"] = self._route_hybrid(task)
            else:
                result["status"] = "unknown_task_type"
                result["result"] = "Could not classify task - please provide more context"
        except Exception as e:
            result["status"] = "error"
            result["result"] = f"Error processing task: {str(e)}"
        
        self.active_tasks[task_id] = result
        return result
    
    def _route_to_open_design(self, task: Task) -> Dict:
        """Leitet Design-Aufgaben an Open Design weiter"""
        try:
            # Open Design Client verwenden
            from open_design_client import create_design_task_auto
            
            result = create_design_task_auto(
                description=task.description,
                open_design_url=self.open_design_url
            )
            
            return {
                "system": "open_design",
                "status": result.get("status", "unknown"),
                "data": result.get("data", {}),
                "message": result.get("message", "Task routed to Open Design"),
                "task_id": result.get("task_id")
            }
        except ImportError:
            # Fallback zu direct API call
            return self._fallback_direct_api(task)
        except Exception as e:
            return {
                "system": "open_design",
                "status": "error",
                "error": str(e),
                "message": f"Error routing to Open Design: {str(e)}"
            }
    
    def _fallback_direct_api(self, task: Task) -> Dict:
        """Fallback: Direkter API Call"""
        try:
            response = requests.post(
                f"{self.open_design_url}/api/runs",
                json={
                    "skill": self._detect_design_skill(task.description),
                    "brief": task.description,
                    "designSystem": "default"
                },
                timeout=30
            )
            response.raise_for_status()
            
            return {
                "system": "open_design",
                "status": "success",
                "data": response.json(),
                "message": "Task routed to Open Design for design execution (fallback mode)"
            }
        except requests.exceptions.RequestException as e:
            return self._fallback_open_design_cli(task)
    
    def _route_to_wuphf(self, task: Task) -> Dict:
        """Leitet Development-Aufgaben an WUPHF weiter"""
        try:
            # WUPHF API call über office-members
            response = requests.post(
                f"{self.wuphf_url}/office-members",
                json={
                    "action": "create",
                    "slug": "orchestrator-task",
                    "name": "Workflow Task",
                    "role": "developer",
                    "expertise": ["development", "integration"],
                    "personality": "Technical coordinator who handles development tasks",
                    "permission_mode": "auto"
                },
                timeout=30
            )
            
            # Task an den passenden Agent senden
            return {
                "system": "wuphf",
                "status": "success",
                "data": response.json() if response.status_code == 200 else {"error": response.text},
                "message": "Task routed to WUPHF for development execution"
            }
        except requests.exceptions.RequestException as e:
            return {
                "system": "wuphf",
                "status": "error",
                "error": str(e),
                "message": "Could not reach WUPHF API"
            }
    
    def _route_hybrid(self, task: Task) -> Dict:
        """Koordiniert hybride Aufgaben zwischen beiden Systemen"""
        # Aufteilung in Design und Development Teilaufgaben
        design_part = self._extract_design_part(task.description)
        dev_part = self._extract_dev_part(task.description)
        
        results = []
        
        if design_part:
            design_task = Task(description=design_part, context=task.context)
            design_result = self._route_to_open_design(design_task)
            results.append(design_result)
        
        if dev_part:
            dev_task = Task(description=dev_part, context=task.context)
            dev_result = self._route_to_wuphf(dev_task)
            results.append(dev_result)
        
        return {
            "system": "hybrid",
            "status": "success",
            "results": results,
            "message": f"Hybrid task split: {len(results)} sub-tasks processed"
        }
    
    def _fallback_open_design_cli(self, task: Task) -> Dict:
        """Fallback: Open Design CLI direkt aufrufen"""
        try:
            # Prüfen ob Open Design installiert ist
            result = subprocess.run(
                ["pnpm", "tools-dev", "status"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd="/tmp/open-design"
            )
            
            if result.returncode == 0:
                return {
                    "system": "open_design_cli",
                    "status": "success",
                    "message": "Open Design CLI available - would route task here",
                    "note": "Implement CLI integration for full automation"
                }
            else:
                return {
                    "system": "open_design_cli",
                    "status": "unavailable",
                    "message": "Open Design CLI not available - please install Open Design"
                }
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {
                "system": "open_design_cli",
                "status": "error",
                "error": str(e),
                "message": "Open Design CLI not found or not responsive"
            }
    
    def _detect_design_skill(self, description: str) -> str:
        """Erkennt die passende Design-Skill basierend auf der Beschreibung"""
        desc_lower = description.lower()
        
        if "website" in desc_lower or "landing" in desc_lower or "web" in desc_lower:
            return "web-prototype"
        elif "app" in desc_lower or "mobile" in desc_lower:
            return "mobile-app"
        elif "dashboard" in desc_lower or "admin" in desc_lower:
            return "dashboard"
        elif "präsentation" in desc_lower or "slide" in desc_lower or "pitch" in desc_lower:
            return "guizang-ppt"
        elif "poster" in desc_lower or "grafik" in desc_lower:
            return "magazine-poster"
        else:
            return "web-prototype"  # Default
    
    def _extract_design_part(self, description: str) -> Optional[str]:
        """Extrahiert den Design-relevanten Teil einer hybriden Aufgabe"""
        desc_lower = description.lower()
        
        # Einfache Heuristik: Sätze mit Design-Keywords
        sentences = re.split(r'[.!?]', description)
        design_sentences = [
            s.strip() for s in sentences 
            if any(kw in s.lower() for kw in self.design_keywords)
        ]
        
        return ". ".join(design_sentences) if design_sentences else None
    
    def _extract_dev_part(self, description: str) -> Optional[str]:
        """Extrahiert den Development-relevanten Teil einer hybriden Aufgabe"""
        desc_lower = description.lower()
        
        sentences = re.split(r'[.!?]', description)
        dev_sentences = [
            s.strip() for s in sentences 
            if any(kw in s.lower() for kw in self.dev_keywords)
        ]
        
        return ". ".join(dev_sentences) if dev_sentences else None
    
    def _generate_task_id(self) -> str:
        """Generiert eine eindeutige Task-ID"""
        import time
        return f"task_{int(time.time() * 1000)}"
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Gibt den Status einer Aufgabe zurück"""
        return self.active_tasks.get(task_id)

# HTTP API Server für den Orchestrator
from flask import Flask, request, jsonify

app = Flask(__name__)
orchestrator = WorkflowOrchestrator()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "workflow-orchestrator"})

@app.route('/route', methods=['POST'])
def route_task():
    """API-Endpoint für Task-Routing"""
    data = request.json
    task = Task(
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        context=data.get('context', {})
    )
    
    result = orchestrator.route_task(task)
    return jsonify(result)

@app.route('/task/<task_id>', methods=['GET'])
def get_task(task_id: str):
    """API-Endpoint für Task-Status"""
    result = orchestrator.get_task_status(task_id)
    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Task not found"}), 404

if __name__ == '__main__':
    port = int(os.getenv('ORCHESTRATOR_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)