# Workflow Orchestrator Skill

Automatischer Workflow-Orchestrator, der Tasks zwischen WUPHF und Open Design weiterleitet basierend auf Aufgaben-Typ.

## Fähigkeiten

- **Task-Klassifikation**: Analysiert Aufgaben und leitet sie an das optimale System weiter
- **Design-Tasks**: Leitet an Open Design weiter (UI/UX, Grafiken, Präsentationen)
- **Development-Tasks**: Leitet an WUPHF weiter (Code, Architektur, Debugging)
- **Hybrid-Tasks**: Koordiniert beide Systeme für komplexe Projekte

## Trigger

Wird automatisch aufgerufen bei:
- Neue Aufgaben im System
- Agent-Anfragen für Design oder Development
- Projekt-Koordinations-Anforderungen

## Verwendung

Der Orchestrator wird automatisch aktiviert und entscheidet basierend auf der Aufgabe:
- Design-Keywords → Open Design
- Development-Keywords → WUPHF
- Gemischte Anforderungen → Kombinierter Workflow