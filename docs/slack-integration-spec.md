# Slack Integration - Technische Spezifikation

## 1. Datenmodelle

### 1.1 Slack Messages Tabelle
```sql
CREATE TABLE slack_messages (
    id SERIAL PRIMARY KEY,
    slack_message_id VARCHAR(50) UNIQUE NOT NULL,
    slack_channel_id VARCHAR(50) NOT NULL,
    slack_user_id VARCHAR(50),
    slack_team_id VARCHAR(50),
    text TEXT,
    thread_ts VARCHAR(50),
    parent_ts VARCHAR(50),
    message_type VARCHAR(20) DEFAULT 'message',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    slack_timestamp VARCHAR(50) NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_slack_channel_id (slack_channel_id),
    INDEX idx_slack_user_id (slack_user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_processed (processed)
);
```

### 1.2 Slack Files Tabelle
```sql
CREATE TABLE slack_files (
    id SERIAL PRIMARY KEY,
    slack_file_id VARCHAR(50) UNIQUE NOT NULL,
    slack_message_id INTEGER REFERENCES slack_messages(id),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    mime_type VARCHAR(100),
    size_bytes INTEGER,
    url_private VARCHAR(500),
    url_private_download VARCHAR(500),
    storage_path VARCHAR(500),
    downloaded BOOLEAN DEFAULT FALSE,
    download_attempted_at TIMESTAMP WITH TIME ZONE,
    downloaded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_slack_message_id (slack_message_id),
    INDEX idx_downloaded (downloaded)
);
```

### 1.3 Slack Channels Tabelle
```sql
CREATE TABLE slack_channels (
    id SERIAL PRIMARY KEY,
    slack_channel_id VARCHAR(50) UNIQUE NOT NULL,
    slack_team_id VARCHAR(50),
    channel_name VARCHAR(100),
    channel_type VARCHAR(20), -- 'public', 'private', 'mpim', 'im'
    is_archived BOOLEAN DEFAULT FALSE,
    category VARCHAR(50), -- 'ideas', 'general', 'projects', etc.
    auto_process BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_category (category),
    INDEX idx_auto_process (auto_process)
);
```

### 1.4 Slack Users Tabelle
```sql
CREATE TABLE slack_users (
    id SERIAL PRIMARY KEY,
    slack_user_id VARCHAR(50) UNIQUE NOT NULL,
    slack_team_id VARCHAR(50),
    username VARCHAR(100),
    display_name VARCHAR(100),
    email VARCHAR(255),
    is_bot BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    profile_image_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX idx_slack_user_id (slack_user_id),
    INDEX idx_username (username)
);
```

## 2. API Schemas

### 2.1 Slack Message Response
```json
{
    "id": 1,
    "slack_message_id": "1234567890.123456",
    "slack_channel_id": "C123456",
    "slack_user_id": "U123456",
    "text": "This is a test message",
    "timestamp": "2024-01-15T10:30:00Z",
    "slack_timestamp": "1234567890.123456",
    "processed": true,
    "files": [],
    "user": {
        "username": "john.doe",
        "display_name": "John Doe"
    },
    "channel": {
        "channel_name": "ideas",
        "category": "ideas"
    }
}
```

### 2.2 Slack File Response
```json
{
    "id": 1,
    "slack_file_id": "F123456",
    "filename": "document.pdf",
    "file_type": "pdf",
    "mime_type": "application/pdf",
    "size_bytes": 1024000,
    "downloaded": true,
    "storage_path": "/storage/slack/files/2024/01/15/document.pdf",
    "downloaded_at": "2024-01-15T10:35:00Z"
}
```

### 2.3 Channel Configuration Request
```json
{
    "slack_channel_id": "C123456",
    "category": "ideas",
    "auto_process": true
}
```

### 2.4 Real-time Message Event (WebSocket)
```json
{
    "type": "slack_message",
    "data": {
        "slack_message_id": "1234567890.123456",
        "text": "New idea from Slack",
        "channel": "ideas",
        "user": "john.doe",
        "timestamp": "2024-01-15T10:30:00Z",
        "files": []
    }
}
```

## 3. State Machine für Message Processing

### 3.1 Message Processing States
```
[RECEIVED] → [VALIDATED] → [STORED] → [PROCESSED] → [SYNCHRONIZED]
     ↓            ↓           ↓            ↓              ↓
  [ERROR]     [ERROR]     [ERROR]     [ERROR]        [ERROR]
```

### 3.2 State Transitions
- **RECEIVED**: Webhook empfangen, Signature verifiziert
- **VALIDATED**: Timestamp validiert, Schema validiert
- **STORED**: In Datenbank persistiert
- **PROCESSED**: Semantic Analysis angewendet, Kategorisiert
- **SYNCHRONIZED**: Zu Obsidian/GBrain synchronisiert

### 3.3 Error Handling
Jeder State hat Error-Handler mit:
- Error Logging
- Retry-Logik (exponential backoff)
- Dead Letter Queue für permanente Fehler
- Admin-Benachrichtigung bei kritischen Fehlern

## 4. Schnittstellen-Definitionen

### 4.1 Backend API Endpoints

#### Message Management
```
GET /api/slack/messages
  Query Params: channel_id, user_id, processed, limit, offset
  Response: Paginated message list

GET /api/slack/messages/{id}
  Response: Single message with files

POST /api/slack/messages/{id}/process
  Trigger: Manual re-processing
  Response: Processing status

DELETE /api/slack/messages/{id}
  Response: Deletion confirmation
```

#### File Management
```
GET /api/slack/files
  Query Params: message_id, downloaded, limit, offset
  Response: Paginated file list

GET /api/slack/files/{id}/download
  Response: File download

POST /api/slack/files/{id}/retry-download
  Trigger: Retry file download
  Response: Download status
```

#### Channel Management
```
GET /api/slack/channels
  Response: Channel list with configuration

POST /api/slack/channels/configure
  Body: Channel configuration
  Response: Configuration confirmation

GET /api/slack/channels/{id}/messages
  Response: Messages for specific channel
```

#### Real-time Events
```
WS /api/slack/events
  Events: message_received, file_downloaded, processing_complete
```

### 4.2 Frontend Components

#### Components
```
SlackChannelList.tsx
  - Listet alle konfigurierten Channels
  - Zeigt Status (aktiv/inaktiv)
  - Ermöglicht Konfiguration

SlackMessageFeed.tsx
  - Real-time Message Feed
  - Filter nach Channel/User
  - Semantic highlighting

SlackFileGallery.tsx
  - Zeigt heruntergeladene Files
  - Download/Preview Funktionen
  - Filter nach Typ/Zeitraum

SlackAnalytics.tsx
  - Message Statistiken
  - User Activity
  - Channel Performance
```

## 5. Performance Requirements

### 5.1 Response Times
- Webhook Response: < 200ms (async processing)
- API Endpoints: < 500ms (p95)
- WebSocket Events: < 100ms latency
- File Downloads: < 5s für < 10MB Files

### 5.2 Throughput
- Webhook Events: 100 events/second
- Database Writes: 50 writes/second
- Concurrent WebSocket Connections: 100

### 5.3 Storage
- File Storage: 100GB initial
- Database: 10GB initial
- Backup: Daily backups, 30-day retention

## 6. Security Requirements

### 6.1 Authentication
- Slack Signature Verification (mandatory)
- API Key Authentication für interne Endpoints
- JWT Tokens für WebSocket Verbindungen

### 6.2 Authorization
- Channel-based Access Control
- User-based Permissions
- Admin-only Endpoints

### 6.3 Data Protection
- File Encryption at Rest
- HTTPS-only für alle Verbindungen
- PII Handling für User Data
- Audit Logging für alle Aktionen

## 7. Monitoring & Alerting

### 7.1 Metrics
- Webhook Success Rate
- Message Processing Latency
- File Download Success Rate
- Database Connection Pool Health
- WebSocket Connection Health

### 7.2 Alerts
- Webhook Failure Rate > 5%
- Processing Queue Depth > 1000
- File Download Failure Rate > 10%
- Database Connection Errors
- API Response Time > 2s

### 7.3 Logging
- Structured JSON Logging
- Log Levels: DEBUG, INFO, WARNING, ERROR
- Centralized Log Aggregation
- Sensitive Data Masking