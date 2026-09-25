# Demo Video Script: Context-Aware Personal Assistant MCP Server for Alexa+
**Duration: 2:45** | **Target: Amazon Developer Hackathon 2026 Submission**

---

## [0:00-0:15] Hook & Problem Statement
**Visual**: Split screen - Left: User asking Alexa "What did I say about the project yesterday?" → Alexa: "I don't have that context." Right: Same question → Alexa: "You mentioned the quarterly review is due Friday and you wanted to prepare slides tonight."

**Audio**: "Alexa+ is powerful, but it has a critical limitation: no persistent memory across conversations. Every session starts fresh. We built an MCP server that changes that."

---

## [0:15-0:30] Solution Overview
**Visual**: Architecture diagram animation showing Alexa+ → MCP HTTP → Context-Aware Assistant → Persistent Storage

**Audio**: "Our Context-Aware Personal Assistant is a Model Context Protocol server implementing the 2025-11-25 Streamable HTTP spec. It gives Alexa+ persistent memory, task management, calendar integration, and proactive assistance - all self-hosted, privacy-first."

---

## [0:30-0:55] Live Demo: Memory & Context
**Visual**: Terminal showing HTTP requests + Alexa+ simulator/voice interaction

**Action 1**: Store a memory
```bash
curl -X POST localhost:8000/mcp \
  -H "Mcp-Session-Id: demo" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"add_memory","arguments":{"content":"Quarterly review due Friday, need to prepare slides tonight","tags":["work","urgent"],"importance":0.9}}}'
```

**Action 2**: Ask Alexa (simulated)
> **User**: "Alexa, what did I tell you about the quarterly review?"
> **Alexa**: "You mentioned the quarterly review is due Friday and you wanted to prepare slides tonight. That was marked as urgent."

**Audio**: "Memories persist across sessions with importance scoring and semantic search. Alexa can now recall context from days or weeks ago."

---

## [0:55-1:20] Live Demo: Tasks & Proactive Assistance
**Visual**: Create task → Get context → Proactive suggestion

**Action 1**: Create task
```bash
curl -X POST localhost:8000/mcp \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"create_task","arguments":{"title":"Prepare Q3 slides"," "priority":5,"due_date":"2026-10-25T18:00:00","tags":["work"]}}}'
```

**Action 2**: Get proactive suggestions
```bash
curl -X POST localhost:8000/mcp \
  -d '{"jsonrpc":"2.0","id":"3","method":"tools/call","params":{"name":"get_proactive_suggestions","arguments":{}}}'
```
**Response**: `["You have 'Prepare Q3 slides' due in 2 days (high priority).", "You have a meeting with Sarah at 2 PM today."]`

**Alexa Interaction**:
> **User**: "Alexa, what should I focus on today?"
> **Alexa**: "You have 'Prepare Q3 slides' due in 2 days - that's high priority. Also, your meeting with Sarah is at 2 PM."

---

## [1:20-1:45] Live Demo: Calendar Integration
**Visual**: Add event → Get upcoming → Context summary

**Action**: Add calendar event
```bash
curl -X POST localhost:8000/mcp \
  -d '{"jsonrpc":"2.0","id":"4","method":"tools/call","params":{"name":"add_event","arguments":{"title":"Team Sync","start_time":"2026-10-24T14:00:00","end_time":"2026-10-24T14:30:00","attendees":["Sarah","Mike"]}}}'
```

**Context Summary**:
```bash
curl -X POST localhost:8000/mcp \
  -d '{"jsonrpc":"2.0","id":"5","method":"tools/call","params":{"name":"get_context","arguments":{}}}'
```
**Response shows**: current time, upcoming events, pending tasks, high-priority items, recent memories

---

## [1:45-2:10] Technical Highlights
**Visual**: Code snippets + architecture callouts

**Key Points**:
- **Full MCP 2025-11-25 Compliance**: Streamable HTTP + SSE, proper initialization, session management
- **Production Ready**: Docker multi-stage build, health checks, non-root user, CORS for Alexa+
- **Extensible**: Add new tools/resources without breaking changes
- **Privacy-First**: Local JSON storage, no external API calls, your data stays yours

---

## [2:10-2:30] Alexa+ Integration Demo
**Visual**: Alexa Developer Console → Add MCP Server endpoint → Test in simulator

**Audio**: "Integration is simple: add your MCP server URL to Alexa+ developer console. The server handles initialization, capability negotiation, and all tool calls. Works with any Alexa+ device."

---

## [2:30-2:45] Call to Action & Close
**Visual**: GitHub repo URL + QR code + "Built for Amazon Developer Hackathon 2026"

**Audio**: "Context-Aware Personal Assistant - giving Alexa+ the memory it deserves. GitHub link in description. Vote for us in the Alexa+ track!"

---

## Production Notes

### Recording Setup
- Screen recording: 1920x1080, 30fps
- Audio: Clear narration, background music (low)
- Terminal: Large font, high contrast theme
- Alexa simulator: Use Alexa Developer Console simulator

### Key Messages to Emphasize
1. **MCP 2025-11-25 Streamable HTTP** - Exactly what Alexa+ requires
2. **Persistent Context** - Solves the #1 Alexa+ limitation
3. **Self-Hosted & Private** - Enterprise/privacy ready
4. **Production Quality** - Not a prototype, deployable today

### Judging Criteria Mapping
| Demo Segment | Judging Criterion |
|--------------|-------------------|
| Architecture + Code | Tech Implementation |
| UX Flow + Proactive | Design |
| Real Use Cases | Potential Impact |
| Novel MCP Application | Quality of Idea |

---

## Backup: Shorter Version (60 seconds)
If time constrained, cut to: Hook → Memory Demo → Task/Proactive → Technical Highlights → Close