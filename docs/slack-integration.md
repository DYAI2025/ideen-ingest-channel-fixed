# Slack Integration - Iterative Implementierungsplan

## Phase 0: Analyse & Vorbereitung

### Ziel
Slack als Live-Chat Interface für das Ideen-System mit Channels, Kategorisierung, permanenter Speicherung, File Upload, semantischer Analyse und GBrain Sync.

### Aktueller Stack-Analyse
- **Backend**: FastAPI, Python 3.12, Uvicorn
- **Frontend**: React, TypeScript, Vite (Port 5174)
- **Daten**: GBrain (Ideen), SQLite (Kanban), Filesystem (Uploads)
- **Analysis**: TF-IDF Semantic Analysis
- **Agents**: API für Ideen-Anreicherung
- **Infrastruktur**: Railway Deployment möglich

### Technische Lücken
1. ❌ Keine persistente Datenbank für Messages/Chats
2. ❌ Keine Slack App konfiguriert
3. ❌ Kein WebSocket/Realtime-System
4. ❌ Kein File-Storage für Slack-Files
5. ❌ Kein Auth-System für Slack-Users

## Phase 1: Slack App Setup (1-2 Tage)

### 1.1 Slack App erstellen
- Slack Developer Account
- App erstellen mit Permissions:
  - `channels:read` - Channels lesen
  - `channels:history` - Message History
  - `chat:write` - Messages senden
  - `files:read` - Files lesen
  - `files:write` - Files hochladen
  - `reactions:read` - Reactions lesen
  - `reactions:write` - Reactions schreiben
- OAuth & Permissions konfigurieren
- Bot Token generieren

### 1.2 Event Subscriptions
- `message.channels` - Neue Messages
- `file_shared` - File Uploads
- `reaction_added` - Reactions
- `channel_created` - Neue Channels
- Webhook Endpoint konfigurieren

### 1.3 Environment Variables
```env
SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_APP_ID=...
SLACK_CLIENT_ID=...
SLACK_CLIENT_SECRET=...
```

## Phase 2: Backend Slack Integration (3-4 Tage)

### 2.1 Slack Service erstellen
```python
# backend/src/services/slack_service.py
class SlackService:
    def __init__(self, bot_token, signing_secret):
        self.client = WebClient(token=bot_token)
        self.signature_verifier = SignatureVerifier(signing_secret)
    
    async def send_message(self, channel, text, attachments=None)
    async def get_channel_messages(self, channel, limit=100)
    async def upload_file(self, channel, file_path, filename)
    async def create_reaction(self, channel, timestamp, emoji)
```

### 2.2 Webhook Endpoints
```python
# backend/src/api/slack.py
@router.post("/slack/events")
async def slack_events(request: Request)
@router.post("/slack/interactive")
async def slack_interactions(payload: dict)
@router.get("/slack/install")
async def slack_install()
@router.get("/slack/oauth/callback")
async def slack_oauth_callback()
```

### 2.3 Database Schema (SQLite)
```sql
CREATE TABLE slack_messages (
    id INTEGER PRIMARY KEY,
    slack_message_id TEXT UNIQUE,
    channel_id TEXT,
    user_id TEXT,
    username TEXT,
    text TEXT,
    timestamp DATETIME,
    thread_ts TEXT,
    file_id TEXT,
    file_url TEXT,
    file_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE slack_channels (
    id INTEGER PRIMARY KEY,
    slack_channel_id TEXT UNIQUE,
    channel_name TEXT,
    topic TEXT,
    purpose TEXT,
    category TEXT,
    gbrain_synced BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE slack_files (
    id INTEGER PRIMARY KEY,
    slack_file_id TEXT UNIQUE,
    message_id INTEGER,
    filename TEXT,
    file_url TEXT,
    file_type TEXT,
    size INTEGER,
    local_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES slack_messages(id)
);
```

### 2.4 Channel Kategorisierung
- Auto-Kategorisierung basierend auf Channel Name/Topic
- Manuelle Kategorisierung über Slash Commands
- Kategorien: `research`, `development`, `design`, `marketing`, `general`

## Phase 3: Message Processing & Storage (2-3 Tage)

### 3.1 Message Ingest Pipeline
```python
# backend/src/services/message_processor.py
class MessageProcessor:
    async def process_message(self, message_data):
        # 1. Validate message
        # 2. Extract entities (hashtags, mentions, URLs)
        # 3. Store in database
        # 4. Trigger semantic analysis
        # 5. Check for GBrain sync triggers
```

### 3.2 File Download & Storage
```python
async def download_slack_file(file_url, token):
    # Download from Slack
    # Store locally (integration mit bestehendem upload system)
    # Update database
```

### 3.3 Thread Support
- Thread-TS speichern für Message Hierarchie
- Thread-übergreifende Suche ermöglichen

## Phase 4: Semantic Analysis Integration (2-3 Tage)

### 4.1 Chat-Level Analyse
```python
# Erweiterung semantic_analysis.py
class ChatAnalyzer:
    async def analyze_chat(self, channel_id, time_range=None):
        # Alle Messages aus Channel holen
        # TF-IDF Analyse für gesamten Chat
        # Key Topics extrahieren
        # Summary generieren
```

### 4.2 Message-Level Analyse
- Einzelne Messages analysieren
- Sentiment Analysis (optional)
- Entity Recognition (optional)

### 4.3 Analysis Results Storage
```sql
CREATE TABLE chat_analysis (
    id INTEGER PRIMARY KEY,
    channel_id TEXT,
    analysis_date DATETIME,
    key_topics TEXT,
    summary TEXT,
    sentiment_score REAL,
    message_count INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Phase 5: GBrain Sync (2-3 Tage)

### 5.1 Sync Triggers definieren
- Manual: `/gbrain-sync` Slash Command
- Auto: Wöchentliche Syncs für bestimmte Channels
- Keyword: Messages mit `#gbrain` Tag

### 5.2 Chat → GBrain Conversion
```python
class ChatToGBrainConverter:
    async def convert_chat_to_idea(self, channel_id):
        # Chat Summary als Idee
        # Key Messages als Content
        # Files als Attachments
        # Channel Metadata als Tags
```

### 5.3 Bidirectional Sync
- GBrain Ideas → Slack Channel Updates
- Slack Channel → GBrain Idea Creation

## Phase 6: Frontend Integration (3-4 Tage)

### 6.1 Slack Auth UI
- "Connect Slack" Button
- OAuth Flow
- Channel Selection UI

### 6.2 Dashboard Komponenten
```typescript
// Slack Dashboard
- Channel List mit Kategorien
- Message Search
- File Browser
- Analysis Results
- GBrain Sync Status
```

### 6.3 Realtime Updates
- WebSocket Verbindung für Live Messages
- Auto-refresh für Channel Lists

## Phase 7: Testing & Deployment (2-3 Tage)

### 7.1 Unit Tests
- Slack Service Tests
- Message Processor Tests
- Database Tests
- GBrain Sync Tests

### 7.2 Integration Tests
- Slack Webhook Tests
- End-to-End Message Flow
- File Upload Tests

### 7.3 Deployment
- Railway Deployment
- Environment Variables konfigurieren
- Slack App Production konfigurieren

## Kritische Prüfung des Plans

### ✅ Stärken
1. **Iterativ**: Phasen sind klar abgegrenzt
2. **Realistisch**: Basierend auf vorhandenem Stack
3. **Testbar**: Jede Phase kann unabhängig getestet werden
4. **Skalierbar**: SQLite kann später zu PostgreSQL migriert werden

### ❌ Schwächen & Risiken

#### 1. Database Choice (SQLite)
**Problem**: SQLite ist für Production nicht ideal für Concurrency
**Lösung**: 
- Phase 2-4: SQLite für Prototyping
- Phase 7: Migration zu PostgreSQL (Railway hat PostgreSQL)
- Connection Pooling implementieren

#### 2. File Storage
**Problem**: Lokale File Storage ist nicht Production-ready
**Lösung**:
- Phase 2-4: Lokales Filesystem
- Phase 5: Integration mit Railway Volumes oder S3
- Alternativ: Externe File-Storage (Cloudflare R2, AWS S3)

#### 3. Realtime Updates
**Problem**: Aktuell kein WebSocket System
**Lösung**:
- FastAPI WebSocket Support nutzen
- Oder: Server-Sent Events (SSE) für einfachere Implementierung
- Oder: Polling für Phase 1, WebSocket für Phase 2

#### 4. Rate Limiting (Slack API)
**Problem**: Slack hat Rate Limits
**Lösung**:
- Rate Limiting implementieren (bereits in MCP Server vorhanden)
- Caching für häufige Requests
- Queue System für Batch-Operations

#### 5. Auth & User Management
**Problem**: Kein User Mapping zwischen Slack und System
**Lösung**:
- Slack User ID als Primary Key
- Optional: Lokale User Profiles erweitern

## Verbesserter Plan

### Modifizierte Phasen

#### Phase 1: Slack App + Minimal Webhook (1-2 Tage)
- Slack App erstellen
- Nur `message.channels` Event
- Einfacher Webhook Endpoint
- Message Logging (nur Console)

#### Phase 2: PostgreSQL + Basic Storage (2-3 Tage)
- PostgreSQL bei Railway einrichten
- Database Schema erstellen
- Slack Messages persistieren
- File Metadata speichern

#### Phase 3: File Storage Integration (1-2 Tage)
- Railway Volume für File Storage
- Slack Files downloaden
- Basic File Management

#### Phase 4: Message Processing (2-3 Tage)
- Entity Extraction
- Channel Kategorisierung
- Basic Search

#### Phase 5: Semantic Analysis (2-3 Tage)
- Chat-Level TF-IDF Analysis
- Topic Extraction
- Summary Generation

#### Phase 6: GBrain Sync (2-3 Tage)
- Manual Sync Command
- Chat → Idea Conversion
- Basic Bidirectional Sync

#### Phase 7: Frontend (3-4 Tage)
- Slack Auth UI
- Channel Dashboard
- Message Browser
- Analysis Results

#### Phase 8: Realtime & Polish (2-3 Tage)
- WebSocket/SSE Implementation
- Rate Limiting & Error Handling
- Production Deployment

### Technische Anpassungen

#### Database Schema (PostgreSQL)
```sql
-- Enhanced mit proper constraints und indexes
CREATE TABLE slack_messages (
    id SERIAL PRIMARY KEY,
    slack_message_id TEXT UNIQUE NOT NULL,
    channel_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    username TEXT,
    text TEXT,
    timestamp TIMESTAMP WITH TIME ZONE,
    thread_ts TEXT,
    file_id TEXT,
    file_url TEXT,
    file_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_slack_messages_channel ON slack_messages(channel_id);
CREATE INDEX idx_slack_messages_timestamp ON slack_messages(timestamp);
CREATE INDEX idx_slack_messages_user ON slack_messages(user_id);
```

#### Dependencies hinzufügen
```python
# pyproject.toml
dependencies = [
    # ... existing
    "slack-sdk>=3.27.0",
    "asyncpg>=0.29.0",  # PostgreSQL async driver
    "databases[postgresql]>=0.8.0",  # Database connection pooling
]
```

#### File Storage Strategy
```python
# Railway Volume mounten
# /data/slack-files/ für persistente Storage
# Oder: Cloudflare R2 für S3-kompatible Storage
```

### Success Criteria pro Phase

#### Phase 1: ✅ Slack App connected, Messages in Console
#### Phase 2: ✅ Messages in PostgreSQL, Basic Query API
#### Phase 3: ✅ Files downloaded und lokal gespeichert
#### Phase 4: ✅ Channels kategorisiert, Search funktioniert
#### Phase 5: ✅ Chat Analysis verfügbar, Topics extrahiert
#### Phase 6: ✅ Manual GBrain Sync funktioniert
#### Phase 7: ✅ Frontend zeigt Channels, Messages, Analysis
#### Phase 8: ✅ Realtime Updates, Production Deployed

## Geschätzte Gesamtzeit: 18-23 Tage

## Nächste Schritte

1. **Slack Developer Account** erstellen
2. **Railway PostgreSQL** einrichten
3. **Phase 1 starten**: Slack App + Webhook

---

*Erstellt: 2025-05-20*
*Status: Entwurf - Zur Genehmigung*