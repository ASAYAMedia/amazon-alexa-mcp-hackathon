# Context-Aware Personal Assistant MCP Server for Alexa+

A **Model Context Protocol (MCP) server** built for the **Amazon Developer Hackathon 2026 (Alexa+ Track)** that provides persistent memory, calendar integration, task management, and proactive assistance for Alexa+.

## 🏆 Hackathon Entry

- **Track**: Alexa+ (MCP Server)
- **Division**: New Experience
- **Competition**: Build, Ship, Shape: Amazon Developer Hackathon
- **Deadline**: October 23, 2026

## ✨ Features

### Core Capabilities
- **Persistent Memory**: Store and retrieve memories with tags, importance scoring, and semantic search
- **Task Management**: Create, update, and track tasks with priorities, due dates, and tags
- **Calendar Integration**: Schedule events, get upcoming events, and manage recurrence
- **Proactive Assistance**: Context-aware suggestions based on current time, events, and tasks
- **User Preferences**: Persistent preference storage for personalization

### MCP Protocol Compliance
- **MCP Spec**: 2025-11-25 (Streamable HTTP)
- **Transport**: Streamable HTTP + SSE for real-time updates
- **Capabilities**: Tools, Resources, Prompts
- **Session Management**: Multi-session support with proper initialization

### Alexa+ Integration Ready
- Self-hosted MCP server deployable anywhere
- Streamable HTTP transport as required by Alexa+
- OpenAPI-compatible endpoints
- Health checks and monitoring

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)

### Local Development
```bash
# Clone and setup
git clone <your-repo>
cd amazon-alexa-mcp-hackathon

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run STDIO server (for local testing)
python server.py

# Run HTTP server (for Alexa+ integration)
python http_server.py
```

### Docker Deployment
```bash
# Build and run
docker-compose up --build -d

# Check health
curl http://localhost:8000/health
```

## 📡 MCP Endpoints

### HTTP Transport (Alexa+ Compatible)
- **POST /mcp** - Main MCP endpoint (Streamable HTTP)
- **GET /mcp** - SSE endpoint for real-time updates
- **GET /health** - Health check
- **DELETE /mcp/session/{id}** - Session management

### Available Tools
| Tool | Description |
|------|-------------|
| `add_memory` | Store a new memory with tags and importance |
| `search_memories` | Search memories by query and tags |
| `get_recent_memories` | Get recent memories from last N hours |
| `create_task` | Create a new task with priority and due date |
| `update_task` | Update task status, priority, description |
| `list_tasks` | List tasks with optional filters |
| `add_event` | Add a calendar event |
| `get_upcoming_events` | Get upcoming events within N hours |
| `get_context` | Get current context summary |
| `get_proactive_suggestions` | Get proactive suggestions |
| `set_preference` | Set a user preference |

### Available Resources
| Resource | Description |
|----------|-------------|
| `assistant://context` | Current context summary |
| `assistant://memories` | All stored memories |
| `assistant://tasks` | All tasks |
| `assistant://events` | All calendar events |
| `assistant://preferences` | User preferences |

## 🎯 Use Cases for Alexa+

1. **Morning Briefing**: "Alexa, what's my day look like?" → Gets context summary with events, tasks, suggestions
2. **Memory Recall**: "Alexa, remember I need to call mom about the reunion" → Stores memory with tags
3. **Task Management**: "Alexa, add a task to review the quarterly report by Friday" → Creates task with due date
4. **Proactive Alerts**: "You have a meeting in 15 minutes" → Proactive suggestions
5. **Context Continuity**: Memories persist across sessions, enabling long-term personal assistant behavior

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Alexa+        │────▶│  MCP HTTP Server │────▶│  Context-Aware  │
│   (Client)      │     │  (Streamable HTTP)│     │  Assistant Core │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │  Persistent     │
                                               │  Storage (JSON) │
                                               └─────────────────┘
```

## 📁 Project Structure

```
amazon-alexa-mcp-hackathon/
├── server.py              # STDIO MCP server (local testing)
├── http_server.py         # HTTP MCP server (Alexa+ integration)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Multi-stage Docker build
├── docker-compose.yml     # Container orchestration
├── data/                  # Persistent data (gitignored)
│   ├── memories.json
│   ├── tasks.json
│   ├── events.json
│   └── preferences.json
└── README.md
```

## 🔧 Configuration

Environment variables:
- `PORT` - Server port (default: 8000)
- `PYTHONUNBUFFERED` - Unbuffered output for logging

## 🧪 Testing

### Test STDIO Server
```bash
echo '{"jsonrpc":"2.0","id":"1","method":"initialize","params":{}}' | python server.py
```

### Test HTTP Server
```bash
# Initialize
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"initialize","params":{}}'

# List tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: test-session" \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/list","params":{}}'

# Call tool
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: test-session" \
  -d '{"jsonrpc":"2.0","id":"3","method":"tools/call","params":{"name":"get_context","arguments":{}}}'
```

## 🏅 Hackathon Highlights

### Why This Wins
1. **Complete MCP 2025-11-25 Implementation** - Full Streamable HTTP transport compliance
2. **Real-World Utility** - Solves actual Alexa+ limitation: lack of persistent context
3. **Production Ready** - Docker, health checks, multi-session, CORS
4. **Extensible Design** - Easy to add new tools, resources, integrations
5. **Privacy-First** - Local storage, no external dependencies

### Judging Criteria Alignment
| Criterion | How We Excel |
|-----------|--------------|
| **Tech Implementation** | Full MCP spec compliance, proper session management, error handling |
| **Design** | Clean API, intuitive tool/resource model, proactive UX |
| **Potential Impact** | Enables truly personal Alexa+ assistants with memory |
| **Quality of Idea** | Novel application of MCP for persistent personal context |

## 📝 Submission Checklist

- [x] Working MCP server (STDIO + HTTP)
- [x] MCP 2025-11-25 Streamable HTTP transport
- [x] Self-hosted, deployable anywhere
- [x] GitHub repo with source code
- [x] Demo video (3 min max)
- [x] Product feedback on Amazon Developer tools
- [x] Alexa+ track requirements met

## 📄 License

MIT License - See LICENSE file for details.

## 🤝 Acknowledgments

- Amazon Developer Team for the hackathon opportunity
- MCP Specification authors
- NVIDIA Nemotron team (inspiration for context-aware AI)

---

**Built for the Amazon Developer Hackathon 2026** 🚀