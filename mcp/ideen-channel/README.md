# Ideen Channel MCP Server

MCP (Model Context Protocol) server for integrating WUPHF agents with the Ideen Ingest Channel system. This server exposes Ideen Channel APIs as MCP tools, enabling WUPHF agents to interact with ideas and Kanban boards.

## Features

- **Idea Management**: List, search, create, update, and delete ideas
- **Kanban Integration**: View and manage Kanban boards and tasks
- **Caching**: Built-in TTL-based caching to reduce API load
- **Rate Limiting**: Token bucket rate limiting to prevent API abuse
- **Mock Testing**: Full mock support for testing without real server
- **Configuration Validation**: Runtime config validation with health checks

## Installation

```bash
cd mcp/ideen-channel
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Configuration

Configure via environment variables:

```bash
export IDEEN_CHANNEL_API_URL="http://localhost:8002"
export IDEEN_CHANNEL_TIMEOUT=30
export IDEEN_CHANNEL_CACHE_TTL=300
export IDEEN_CHANNEL_RATE_LIMIT_MAX_REQUESTS=60
export IDEEN_CHANNEL_RATE_LIMIT_WINDOW_SECONDS=60
export IDEEN_CHANNEL_MOCK_CLIENT=false
```

Or create a `.env` file:

```env
IDEEN_CHANNEL_API_URL=http://localhost:8002
IDEEN_CHANNEL_TIMEOUT=30
IDEEN_CHANNEL_CACHE_TTL=300
IDEEN_CHANNEL_RATE_LIMIT_MAX_REQUESTS=60
IDEEN_CHANNEL_RATE_LIMIT_WINDOW_SECONDS=60
IDEEN_CHANNEL_MOCK_CLIENT=false
```

## Running the Server

```bash
# Using the entry point
ideen-channel-server

# Or directly with Python
python -m ideen_channel.server

# Or using the run script
python run_server.py
```

## MCP Tools

The server exposes the following MCP tools:

### Idea Management

- **`list_ideas`**: List ideas from the Ideen Ingest Channel
  - Parameters: `phase` (optional), `limit` (default: 50), `offset` (default: 0)

- **`search_ideas`**: Search ideas by query text
  - Parameters: `query` (required), `phase` (optional), `limit` (default: 50)

- **`get_idea`**: Get a specific idea by ID
  - Parameters: `idea_id` (required)

- **`create_idea`**: Create a new idea
  - Parameters: `title` (required), `description` (required), `phase` (default: "discovery"), `tags` (optional)

- **`update_idea`**: Update an existing idea
  - Parameters: `idea_id` (required), `title` (optional), `description` (optional), `phase` (optional), `tags` (optional)

- **`delete_idea`**: Delete an idea
  - Parameters: `idea_id` (required)

### Kanban Management

- **`get_kanban_board`**: Get the complete Kanban board with all tasks
  - Parameters: none

- **`create_kanban_task`**: Create a new Kanban task
  - Parameters: `title` (required), `description` (required), `column` (default: "backlog"), `priority` (default: "medium")

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ideen_channel --cov-report=html

# Run specific test file
pytest src/tests/test_cache.py -v

# Run with verbose output
pytest -v
```

## Development

This project follows Test-Driven Development (TDD) methodology:

1. **Red**: Write failing tests first
2. **Green**: Implement minimal code to pass tests
3. **Refactor**: Improve code while keeping tests passing

Current test coverage: 32 tests passing

### Test Structure

```
src/tests/
├── test_cache.py          # Caching layer tests (8 tests)
├── test_client_mock.py    # Mock client tests (5 tests)
├── test_config.py         # Configuration tests (10 tests)
└── test_rate_limiter.py   # Rate limiting tests (9 tests)
```

## Architecture

```
┌─────────────────┐
│   MCP Server    │
│  (FastMCP)      │
└────────┬────────┘
         │
         ├─────────────────────────────────┐
         │                                 │
         ▼                                 ▼
┌─────────────────┐              ┌─────────────────┐
│  IdeenClient    │              │  RateLimiter    │
│  (HTTP Client)  │              │  (Token Bucket) │
└────────┬────────┘              └─────────────────┘
         │
         ▼
┌─────────────────┐
│   IdeaCache     │
│  (TTL Cache)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Ideen API      │
│  (External)     │
└─────────────────┘
```

## Integration with WUPHF

To integrate this MCP server with WUPHF agents:

1. Add to WUPHF MCP configuration:
```json
{
  "mcpServers": {
    "ideen-channel": {
      "command": "python",
      "args": ["-m", "ideen_channel.server"],
      "env": {
        "IDEEN_CHANNEL_API_URL": "http://localhost:8002"
      }
    }
  }
}
```

2. Agents can now use the tools:
```python
# Agent can call MCP tools
ideas = await mcp_call("list_ideas", {"phase": "discovery"})
```

## Project Structure

```
mcp/ideen-channel/
├── src/
│   ├── ideen_channel/
│   │   ├── __init__.py
│   │   ├── cache.py          # Caching layer
│   │   ├── client.py         # HTTP client
│   │   ├── config.py         # Configuration
│   │   ├── mocks.py          # Mock API for testing
│   │   ├── rate_limiter.py   # Rate limiting
│   │   └── server.py         # MCP server
│   └── tests/
│       ├── test_cache.py
│       ├── test_client_mock.py
│       ├── test_config.py
│       └── test_rate_limiter.py
├── pyproject.toml
├── README.md
└── run_server.py
```

## License

Part of the WUPHF project. See main project license for details.