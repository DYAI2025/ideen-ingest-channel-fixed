# Autonomous Agency Orchestrator

## 🎯 Das Konzept

**Cloud-Intelligenz + Lokale Ausführung = Kostenlose Autonomie**

- **Cloud Orchestrator**: Nutzt OpenRouter Freemium-Modelle für strategische Entscheidungen
- **Lokale Agenten**: Deine WUPHF-Agenten führen die Aufgaben mit lokalen Modellen aus
- **Kosten**: €0 (nur Freemium-Modelle)
- **Autonomie**: Strategische Planung ohne menschliches Eingreifen

## 🚀 Schnellstart

### 1. OpenRouter API Key erhalten (kostenlos)

1. Gehe zu https://openrouter.ai/keys
2. Erstelle einen Account (kostenlos)
3. Generiere einen API Key
4. Keine Kreditkarte nötig für Freemium-Modelle!

### 2. API Key setzen

```bash
export OPENROUTER_API_KEY='your-key-here'
```

Für dauerhafte Nutzung in `~/.bashrc` oder `~/.zshrc`:
```bash
echo 'export OPENROUTER_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. WUPHF starten

Stelle sicher, dass WUPHF läuft:
```bash
./wuphf
```

### 4. Orchestrator nutzen

```bash
# Lead Generation Kampagne starten
python orchestrator.py launch_campaign

# Outreach Sequenz starten
python orchestrator.py outreach

# Projekt Delivery ausführen
python orchestrator.py delivery

# Performance Optimierung
python orchestrator.py optimize

# Custom strategische Entscheidung
python orchestrator.py custom "Analysiere unsere Performance der letzten Woche und schlage Verbesserungen vor"
```

## 🧠 Wie es funktioniert

### Cloud Orchestrator (OpenRouter Freemium)
- **openrouter/free**: Wählt automatisch das beste Freemium-Modell
- **DeepSeek R1**: Schnelles Reasoning für einfache Entscheidungen
- **Trinity Large**: Komplexe strategische Analyse
- **Nemotron 3 Super**: Allzweck-Entscheidungen

### Fallback-Kaskade
Wenn ein Modell fehlschlägt, versucht der Orchestrator automatisch das nächste:
1. openrouter/free (Auto-Selection)
2. deepseek/deepseek-r1:free
3. arcee-ai/trinity-large-thinking:free
4. nvidia/nemotron-3-super:free

### Lokale Agenten (WUPHF + Ollama)
- **PM** (gemma4:e4b): Projektmanagement und Planung
- **Designer** (llama3.1:8b): Visuelles Design und Pitch Decks
- **CMO** (llama3.1:8b): Marketing und Content
- **CRO** (gemma4:e4b): Sales und Closing
- **SDR** (gemma4:e4b): Lead Generation
- **Research** (gemma4:e4b): Marktanalyse
- **Content** (llama3.1:8b): Content Erstellung
- **Analyst** (gemma4:e4b): Performance Analyse

## 📊 Beispiel-Workflow

### Kampagne starten:
```bash
python orchestrator.py launch_campaign
```

**Der Orchestrator:**
1. Analysiert die Situation mit OpenRouter Freemium-Modellen
2. Entscheidet strategisch: "Starte LinkedIn Search nach DACH SaaS Startups"
3. Delegiert an lokalen SDR-Agenten: "Identifiziere 100 qualifizierte Leads"
4. Delegiert an lokalen Research-Agenten: "Analysiere Funding-Status der identifizierten Companies"
5. Delegiert an lokalen CMO-Agenten: "Bereite Outreach Templates vor"

**Die lokalen Agenten:**
- Führen die Aufgaben mit gemma4/llama3.1 aus
- Dokumentieren Ergebnisse im Wiki
- Melden Fortschritt zurück

## 🎛️ Konfiguration

### Umgebungsvariablen:
```bash
export OPENROUTER_API_KEY="your-key"
export WUPHF_BROKER_URL="http://127.0.0.1:7890"  # Optional, Default ist localhost
```

### Anpassung der Agent-Zuweisungen:
Editiere `orchestrator.py` und passe die `system_prompt` Variable an, um:
- Andere Agenten hinzuzufügen
- Prioritäten zu ändern
- Neue Entscheidungstypen zu definieren

## 📈 Monitoring

Der Orchestrator speichert eine Entscheidungs-Historie:
- Zeitstempel jeder Entscheidung
- Welches Modell verwendet wurde
- Confidence-Score der Entscheidung
- Art der Entscheidung

Diese kann für spätere Analyse und Optimierung genutzt werden.

## 🔧 Fehlerbehebung

### "OPENROUTER_API_KEY nicht gesetzt"
```bash
export OPENROUTER_API_KEY="your-key"
```

### "WUPHF Broker nicht erreichbar"
Stelle sicher, dass WUPHF läuft:
```bash
./wuphf
```

### "Alle Cloud-Modelle fehlgeschlagen"
- Überprüfe deine Internetverbindung
- Überprüfe ob OpenRouter verfügbar ist (https://status.openrouter.ai)
- Der Orchestrator verwendet automatisch Fallback

### "Agenten antworten nicht"
- Überprüfe ob WUPHF-Agenten aktiv sind
- Überprüfe die Wiki-Tasks unter `~/.wuphf/wiki/tasks/`
- Manuelle Delegation möglich über Web UI

## 💡 Best Practices

1. **Starte klein**: Beginne mit einer Kampagne und beobachte die Ergebnisse
2. **Überwache die Logs**: Der Orchestrator gibt detaillierte Status-Updates
3. **Kombiniere mit manueller Überwachung**: In der ersten Phase noch menschliche Supervision
4. **Iteriere optimiere**: Passe die Prompts basierend auf Ergebnissen an

## 🚀 Nächste Schritte

1. **Ersten Testlauf**: `python orchestrator.py launch_campaign`
2. **Ergebnisse überwachen**: Wiki und Web UI prüfen
3. **Optimieren**: Basierend auf ersten Ergebnissen anpassen
4. **Skalieren**: Weitere Kampagnen automatisieren

## 💰 Kosten

- **OpenRouter Freemium**: €0 (während der Testphase)
- **Lokale Modelle**: €0 (du hast sie bereits)
- **Gesamt**: €0 für vollautonome Agenten-Firma!

## 🎯 Erfolgs-KPIs

**Woche 1:**
- 5 Orchestrator-Entscheidungen
- 20+ delegierte Aufgaben
- 10+ Wiki-Tasks erstellt
- 80%+ Erfolgsrate der Delegation

**Woche 2-4:**
- Steigerung der autonomen Ausführung
- Reduzierung manueller Intervention
- Erhöhung der Confidence-Scores