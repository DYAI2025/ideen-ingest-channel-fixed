# Sprint 1: Slack App Setup

## Sprint-Ziel
**Slack App erstellen und ersten Webhook Endpoint implementieren, der Slack Messages empfangen und loggen kann.**

## Success Criteria (Definition of Done)
- ✅ Slack App im Slack Dashboard erstellt
- ✅ Bot Token und Signing Secret generiert
- ✅ Event Subscriptions konfiguriert (message.channels)
- ✅ Webhook Endpoint im FastAPI Backend implementiert
- ✅ Slack Signature Verifier implementiert
- ✅ Erste Slack Message erfolgreich empfangen und geloggt
- ✅ Environment Variables konfiguriert
- ✅ Unit Tests für Webhook Endpoint (Mock Slack Events)
- ✅ Code Review durchgeführt
- ✅ Requirements Check bestanden
- ✅ Code committed & gepusht

## Sprint-Backlog (TDD-Entwicklungsreihenfolge)

### 1. User Story 1: Slack App erstellen (MANUELL - Voraussetzung)
**Als** System-Administrator  
**Ich möchte** eine Slack App erstellen  
**Damit** ich Events aus Slack empfangen kann

**Akzeptanzkriterien:**
- [ ] Slack App im Slack Dashboard erstellt
- [ ] Bot Token generiert
- [ ] Signing Secret generiert
- [ ] Permissions konfiguriert (channels:read, channels:history, chat:write)
- [ ] Event Subscriptions aktiviert (message.channels)
- [ ] OAuth & Permissions konfiguriert

**Aufgaben:**
1. Slack Developer Account öffnen (api.slack.com/apps)
2. "Create New App" auswählen
3. App Name: "Ideen Ingest Channel"
4. Workspace auswählen
5. Bot Permissions konfigurieren:
   - `channels:read`
   - `channels:history`
   - `chat:write`
   - `files:read`
   - `files:write`
6. Event Subscriptions hinzufügen:
   - `message.channels`
7. OAuth & Permissions setup
8. Bot Token und Signing Secret kopieren

**Hinweis**: Dies ist ein manueller Schritt im Slack Dashboard und muss VOR der Entwicklung abgeschlossen sein.

---

### 2. User Story 2: Unit Tests für Webhook (TDD - RED PHASE)
**Als** Entwickler  
**Ich möchte** Unit Tests für den Webhook Endpoint  
**Damit** ich sicherstellen kann, dass Slack Events korrekt verarbeitet werden

**Akzeptanzkriterien:**
- [ ] Mock Slack Events erstellen
- [ ] Test für Signature Verification
- [ ] Test für Challenge Response
- [ ] Test für Message Event Processing
- [ ] Test für Error Handling
- [ ] Test Coverage > 80%

**Aufgaben:**
1. `backend/tests/test_slack.py` erstellen
2. Mock Slack Event Objects erstellen
3. Signature Verification Tests (failing)
4. Challenge Response Tests (failing)
5. Message Event Tests (failing)
6. Error Handling Tests (failing)

**TDD-Status**: 🔴 RED - Tests schreiben, alle müssen fehlschlagen

---

### 3. User Story 3: Webhook Endpoint implementieren (TDD - GREEN PHASE)
**Als** Entwickler  
**Ich möchte** einen Webhook Endpoint im FastAPI Backend  
**Damit** Slack Events HTTP POST Requests senden kann

**Akzeptanzkriterien:**
- [ ] POST `/api/slack/events` Endpoint erstellt
- [ ] Slack Signature Verifier implementiert
- [ ] Request Body validieren
- [ ] Slack Challenge Response implementieren
- [ ] Error Handling implementiert
- [ ] Logging für eingehende Requests
- [ ] CORS konfiguriert

**Aufgaben:**
1. Slack SDK installieren (`slack-sdk>=3.27.0`)
2. `backend/src/api/slack.py` erstellen
3. Signature Verifier implementieren
4. POST Endpoint erstellen
5. Challenge Response implementieren
6. Logging hinzufügen
7. Error Handling hinzufügen

**TDD-Status**: 🟢 GREEN - Implementation bis alle Tests bestehen

---

### 4. User Story 4: Environment Configuration
**Als** System-Administrator  
**Ich möchte** Slack Credentials als Environment Variables  
**Damit** sie sicher konfiguriert sind

**Akzeptanzkriterien:**
- [ ] `SLACK_BOT_TOKEN` Environment Variable
- [ ] `SLACK_SIGNING_SECRET` Environment Variable
- [ ] `SLACK_APP_ID` Environment Variable
- [ ] Backend Configuration erweitern
- [ ] Validation der Environment Variables
- [ ] Fallback für Development (optional)

**Aufgaben:**
1. `backend/.env.template` erstellen
2. `backend/src/core/config.py` erweitern
3. Environment Variablen validieren
4. Documentation für Setup erstellen

---

## Technische Anforderungen

### Dependencies
```python
# backend/pyproject.toml
dependencies = [
    # ... existing
    "slack-sdk>=3.27.0",
]
```

### API Endpoints
```
POST /api/slack/events
- Body: Slack Event Payload
- Headers: X-Slack-Signature, X-Slack-Request-Timestamp
- Response: 200 OK (Challenge) oder 200 OK (Event Acknowledged)
```

### Database
Keine Database Änderungen in diesem Sprint (nur Logging).

### File Structure
```
backend/
├── src/
│   ├── api/
│   │   └── slack.py (neu)
│   ├── services/
│   │   └── slack_service.py (neu)
│   └── core/
│       └── config.py (erweitern)
├── tests/
│   └── test_slack.py (neu)
└── .env.template (neu)
```

## Zeitplan
- **Tage 1**: User Story 1 (Slack App Dashboard) + US2 TDD-RED (Tests)
- **Tag 2**: User Story 3 TDD-GREEN (Implementation) + US4 (Config)
- **Tag 3**: Code Review + Requirements Check + Commit

## TDD-Prozess
1. **RED**: Tests schreiben (US2) - alle müssen fehlschlagen
2. **GREEN**: Implementation schreiben (US3) - bis alle Tests bestehen
3. **REFACTOR**: Code optimieren (optional)
4. **REVIEW**: Code Review durchführen
5. **CHECK**: Requirements Check gegen Sprint-Ziel
6. **COMMIT**: Nur wenn DoD erfüllt

## Risiken
- **Slack API Rate Limits**: In diesem Sprint nur lesend, kein Risiko
- **CORS Issues**: CORS bereits im Backend konfiguriert
- **Environment Variables**: Need Documentation für Setup

## Dependencies
- Slack Developer Account
- Slack Workspace Admin Rights
- Railway Deployment (für spätere Sprints)