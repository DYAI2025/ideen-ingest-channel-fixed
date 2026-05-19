# Agenten Überwachungs-Guide

## 🎯 Die 4 Überwachungs-Methoden:

### 1. Web UI (Beste Echtzeit-Überwachung)
**URL**: http://127.0.0.1:7891

**Was du siehst:**
- Live Chat aller Agenten
- Kanäle (#general, #standup, etc.)
- Agent-Aktivitäten in Echtzeit
- Aufgaben und Delegationen

**Wie nutzt du es:**
1. Öffne http://127.0.0.1:7891 im Browser
2. Beobachte den #general Channel
3. Agenten posten dort ihre Fortschritte
4. Du kannst direkt mit Agenten interagieren

### 2. Wiki-Tasks (Aufgaben-Überwachung)
**Pfad**: `~/.wuphf/wiki/tasks/`

**Was du siehst:**
- Alle delegierten Aufgaben
- Prioritäten und Deadlines
- Agent-Zuweisungen

**Befehle:**
```bash
# Alle Aufgaben auflisten
ls -lh ~/.wuphf/wiki/tasks/

# Spezifische Aufgabe ansehen
cat ~/.wuphf/wiki/tasks/research-task-*.md
```

### 3. Terminal-Logs (System-Überwachung)
**WUPHF Logs:**
```bash
# WUPHF Ausgabe überwachen
# (Im Terminal wo WUPHF läuft)
```

**Orchestrator Logs:**
```bash
# Orchestrator Ausgabe
python3 orchestrator.py launch_campaign
```

### 4. Datei-System (Ergebnis-Überwachung)
**Agenten-Verzeichnisse:**
```bash
# Agenten-Speicherorte
ls -la ~/.wuphf/wiki/agents/
```

**Wiki-Änderungen:**
```bash
# Kürzlich geänderte Dateien
find ~/.wuphf/wiki/ -type f -mtime -1
```

## 🚀 Empfohlener Überwachungs-Workflow:

### Schritt 1: Orchestrator starten
```bash
python3 orchestrator.py launch_campaign
```

### Schritt 2: Web UI öffnen
```
http://127.0.0.1:7891
```

### Schritt 3: #general Channel überwachen
- Agenten posten dort wenn sie Aufgaben aufgreifen
- Siehst Delegationen und Fortschritte
- Du kannst direkt intervenieren falls nötig

### Schritt 4: Wiki-Tasks prüfen
```bash
# Alle Aufgaben auflisten
ls -lh ~/.wuphf/wiki/tasks/

# Details sehen
cat ~/.wuphf/wiki/tasks/research-task-*.md
```

### Schritt 5: Ergebnisse prüfen
```bash
# Kürzliche Agenten-Aktivitäten
find ~/.wuphf/wiki/agents/ -type f -mtime -0.1
```

## 🎛️ Manuelles Eingreifen (falls nötig):

### Aufgabe direkt an Agenten:
```bash
# Im Web UI #general Channel:
@research Erledige die Research-Aufgabe ASAP

# Oder Wiki-Task erstellen:
echo "# Task for research

Priority: high
Deadline: ASAP

## Task
Deine spezifische Aufgabe hier" > ~/.wuphf/wiki/tasks/manual-research.md
```

### Agent-Konfiguration prüfen:
```bash
# Aktuelle Konfiguration
cat ~/.wuphf/config.json

# Welche Agenten sind aktiv?
# (Im Web UI unter "Office Members")
```

## 📈 Performance-Tracking:

### Orchestrator-Performance:
- Confidence Scores (im Orchestrator-Output)
- Modell-Wahl (openrouter/free, deepseek, etc.)
- Erfolgsrate der Delegation

### Agenten-Performance:
- Aufgaben-Abschlusszeit
- Qualität der Ergebnisse (im Wiki)
- Häufigkeit der Aktivität

## 🚨 Troubleshooting:

### Agenten reagieren nicht:
1. Web UI prüfen - sind sie online?
2. Wiki-Tasks prüfen - sind Aufgaben sichtbar?
3. Manuelles @mention im Web UI versuchen

### Aufgaben werden nicht erstellt:
1. Orchestrator-Logs prüfen
2. OpenRouter API Key prüfen
3. Wiki-Verzeichnis berechtigungen prüfen

### Ergebnisse fehlen:
1. Agenten-Verzeichnisse prüfen
2. Wiki-Änderungen prüfen
3. Manuelle Intervention erwägen