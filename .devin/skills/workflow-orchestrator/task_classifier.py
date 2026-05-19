#!/usr/bin/env python3
"""
Automatischer Task-Klassifikator Service

Dieser Service überwacht Aufgaben aus verschiedenen Quellen und klassifiziert sie automatisch
für die Weiterleitung an das passende System (WUPHF oder Open Design).
"""

import json
import time
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskSource(Enum):
    WUPHF = "wuphf"
    OPEN_DESIGN = "open_design"
    MANUAL = "manual"
    WEBHOOK = "webhook"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class ClassifiedTask:
    id: str
    description: str
    task_type: str
    confidence: float
    source: TaskSource
    priority: TaskPriority
    metadata: Dict
    created_at: str

class AdvancedTaskClassifier:
    def __init__(self):
        # Erweiterte Keyword-Sets für bessere Klassifikation
        self.design_patterns = {
            "ui_ux": ["ui", "ux", "interface", "user experience", "benutzeroberfläche", "nutzeroberfläche"],
            "visual": ["grafik", "bild", "visual", "illustration", "icon", "logo", "branding"],
            "layout": ["layout", "gestaltung", "aufbau", "struktur", "composition"],
            "presentation": ["präsentation", "slide", "pitch", "deck", "folien"],
            "web_design": ["website", "landing page", "webdesign", "responsive", "mobile-first"],
            "print": ["poster", "flyer", "broschüre", "print", "drucksache"],
            "motion": ["animation", "video", "motion", "kinetic", "transition"],
            "color": ["farbe", "color", "palette", "farbschema", "color scheme"],
            "typography": ["typografie", "schrift", "font", "typography", "lettering"]
        }
        
        self.dev_patterns = {
            "backend": ["api", "backend", "server", "database", "sql", "endpoint"],
            "frontend": ["frontend", "react", "javascript", "typescript", "css", "html"],
            "devops": ["deployment", "ci/cd", "docker", "kubernetes", "infrastructure"],
            "debugging": ["debug", "fix", "error", "bug", "issue", "problem"],
            "architecture": ["architektur", "design pattern", "system design", "struktur"],
            "testing": ["test", "unit test", "integration test", "e2e", "testing"],
            "security": ["security", "auth", "authentication", "authorization", "security"],
            "performance": ["performance", "optimierung", "optimization", "speed"],
            "data": ["data", "migration", "import", "export", "etl", "pipeline"]
        }
        
        # Hybrid-Patterne (Kombination aus Design und Dev)
        self.hybrid_patterns = [
            "component library", "design system", "ui kit", "style guide",
            "web app", "dashboard", "admin panel", "user interface implementation",
            "responsive website", "interactive prototype"
        ]
    
    def classify(self, description: str, source: TaskSource = TaskSource.MANUAL) -> ClassifiedTask:
        """Klassifiziert eine Aufgabe mit erweiterten Pattern-Matching"""
        desc_lower = description.lower()
        
        # Score-Berechnung
        design_score = 0
        dev_score = 0
        
        # Design-Pattern matching
        for category, keywords in self.design_patterns.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    design_score += 1
        
        # Dev-Pattern matching
        for category, keywords in self.dev_patterns.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    dev_score += 1
        
        # Hybrid-Pattern matching
        hybrid_matches = sum(1 for pattern in self.hybrid_patterns if pattern in desc_lower)
        
        # Entscheidung basierend auf Scores
        confidence = 0.0
        task_type = "unknown"
        
        if hybrid_matches > 0:
            task_type = "hybrid"
            confidence = min(0.9, 0.5 + (hybrid_matches * 0.1))
        elif design_score > dev_score:
            task_type = "design"
            confidence = min(0.95, 0.5 + (design_score * 0.05))
        elif dev_score > design_score:
            task_type = "development"
            confidence = min(0.95, 0.5 + (dev_score * 0.05))
        elif design_score == 0 and dev_score == 0:
            task_type = "unknown"
            confidence = 0.0
        else:
            # Gleichstand → basierend auf Kontext entscheiden
            task_type = "hybrid"
            confidence = 0.5
        
        # Priority detection
        priority = self._detect_priority(description)
        
        # Metadata extrahieren
        metadata = self._extract_metadata(description, task_type)
        
        return ClassifiedTask(
            id=self._generate_id(),
            description=description,
            task_type=task_type,
            confidence=confidence,
            source=source,
            priority=priority,
            metadata=metadata,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _detect_priority(self, description: str) -> TaskPriority:
        """Erkennt die Priorität einer Aufgabe"""
        desc_lower = description.lower()
        
        urgent_keywords = ["urgent", "asap", "sofort", "emergency", "kritisch", "critical"]
        high_keywords = ["important", "wichtig", "priority", "hoch", "high"]
        low_keywords = ["wann möglich", "when possible", "nice to have", "optional"]
        
        if any(kw in desc_lower for kw in urgent_keywords):
            return TaskPriority.URGENT
        elif any(kw in desc_lower for kw in high_keywords):
            return TaskPriority.HIGH
        elif any(kw in desc_lower for kw in low_keywords):
            return TaskPriority.LOW
        else:
            return TaskPriority.MEDIUM
    
    def _extract_metadata(self, description: str, task_type: str) -> Dict:
        """Extrahiert relevante Metadaten aus der Beschreibung"""
        metadata = {
            "length": len(description),
            "word_count": len(description.split()),
            "has_numbers": bool(re.search(r'\d', description)),
            "has_urls": bool(re.search(r'http[s]?://', description))
        }
        
        # Task-spezifische Metadaten
        if task_type == "design":
            metadata["detected_design_categories"] = []
            for category, keywords in self.design_patterns.items():
                if any(kw in description.lower() for kw in keywords):
                    metadata["detected_design_categories"].append(category)
        
        elif task_type == "development":
            metadata["detected_dev_categories"] = []
            for category, keywords in self.dev_patterns.items():
                if any(kw in description.lower() for kw in keywords):
                    metadata["detected_dev_categories"].append(category)
        
        return metadata
    
    def _generate_id(self) -> str:
        """Generiert eine eindeutige Task-ID"""
        import uuid
        return f"task_{uuid.uuid4().hex[:8]}"
    
    def batch_classify(self, tasks: List[str], source: TaskSource = TaskSource.MANUAL) -> List[ClassifiedTask]:
        """Klassifiziert mehrere Aufgaben auf einmal"""
        return [self.classify(task, source) for task in tasks]

class TaskWatcher:
    """Überwacht verschiedene Quellen auf neue Aufgaben"""
    
    def __init__(self):
        self.classifier = AdvancedTaskClassifier()
        self.watch_files = [
            Path("/tmp/wuphf_tasks.json"),
            Path("/tmp/open_design_tasks.json"),
            Path("/tmp/manual_tasks.json")
        ]
    
    def watch_and_classify(self) -> List[ClassifiedTask]:
        """Überwacht Dateien und klassifiziert neue Aufgaben"""
        classified_tasks = []
        
        for watch_file in self.watch_files:
            if watch_file.exists():
                try:
                    with open(watch_file, 'r') as f:
                        data = json.load(f)
                    
                    if isinstance(data, list):
                        tasks = data
                    elif isinstance(data, dict) and 'tasks' in data:
                        tasks = data['tasks']
                    else:
                        tasks = [data]
                    
                    for task in tasks:
                        if isinstance(task, str):
                            description = task
                            source = self._detect_source_from_file(watch_file)
                        elif isinstance(task, dict) and 'description' in task:
                            description = task['description']
                            source = TaskSource(task.get('source', 'manual'))
                        else:
                            continue
                        
                        classified = self.classifier.classify(description, source)
                        classified_tasks.append(classified)
                        
                except Exception as e:
                    logger.error(f"Error processing {watch_file}: {e}")
        
        return classified_tasks
    
    def _detect_source_from_file(self, file_path: Path) -> TaskSource:
        """Erkennt die Quelle basierend auf dem Dateinamen"""
        filename = file_path.name.lower()
        
        if "wuphf" in filename:
            return TaskSource.WUPHF
        elif "open_design" in filename or "opendesign" in filename:
            return TaskSource.OPEN_DESIGN
        elif "manual" in filename:
            return TaskSource.MANUAL
        else:
            return TaskSource.MANUAL

def main():
    """Main entry point für den Klassifikator-Service"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Task Classification Service")
    parser.add_argument("--watch", action="store_true", help="Watch mode für kontinuierliche Überwachung")
    parser.add_argument("--task", type=str, help="Einzelne Aufgabe klassifizieren")
    parser.add_argument("--file", type=str, help="Aufgaben aus Datei lesen")
    
    args = parser.parse_args()
    
    classifier = AdvancedTaskClassifier()
    
    if args.watch:
        watcher = TaskWatcher()
        logger.info("Starting watch mode...")
        
        try:
            while True:
                tasks = watcher.watch_and_classify()
                if tasks:
                    logger.info(f"Classified {len(tasks)} tasks")
                    for task in tasks:
                        logger.info(f"  {task.id}: {task.task_type} ({task.confidence:.2f}) - {task.description[:50]}...")
                
                time.sleep(30)  # Alle 30 Sekunden prüfen
                
        except KeyboardInterrupt:
            logger.info("Watch mode stopped")
    
    elif args.task:
        task = classifier.classify(args.task)
        print(json.dumps({
            "id": task.id,
            "task_type": task.task_type,
            "confidence": task.confidence,
            "priority": task.priority.value,
            "metadata": task.metadata
        }, indent=2))
    
    elif args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            tasks = [classifier.classify(t) for t in data]
        else:
            tasks = [classifier.classify(data)]
        
        print(json.dumps([
            {
                "id": t.id,
                "task_type": t.task_type,
                "confidence": t.confidence,
                "priority": t.priority.value,
                "metadata": t.metadata
            } for t in tasks
        ], indent=2))
    
    else:
        print("Usage: python task_classifier.py [--watch] [--task <description>] [--file <path>]")

if __name__ == "__main__":
    main()