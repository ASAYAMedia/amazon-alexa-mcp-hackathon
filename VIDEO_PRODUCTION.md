# Demo Video Production Package
## Context-Aware Personal Assistant MCP Server

### Video Specifications
- **Duration**: 2:45 max (Amazon) / 5:00 max (Nebius)
- **Format**: MP4, 1920x1080, 30fps
- **Audio**: Clear narration, background music optional
- **Upload**: YouTube (unlisted or public)

---

## Recording Checklist

### Equipment Needed
- [ ] Screen recording software (OBS, QuickTime, Windows Game Bar)
- [ ] Microphone for narration
- [ ] Terminal with large font (16pt+)
- [ ] Browser for Devpost pages
- [ ] Code editor (VS Code) open to project

### Pre-Recording Setup
```bash
# Start the HTTP server
cd /home/asaya/Projects/amazon-alexa-mcp-hackathon
source venv/bin/activate
python http_server.py

# In another terminal, run test script
python test_server.py
```

---

## Scene-by-Scene Recording Guide

### Scene 1: Hook (0:00-0:15)
**Screen**: Split view or quick cuts
**Action**: 
1. Show Alexa+ failing to recall context: "What did I say about the quarterly review?"
2. Show same question working with MCP server

**Narration**: "Alexa+ is powerful but has a critical limitation: no persistent memory. Every session starts fresh. We built an MCP server that changes that."

### Scene 2: Architecture Overview (0:15-0:30)
**Screen**: Architecture diagram (draw.io, Figma, or whiteboard)
**Show**: 
```
User → Alexa+/Client → MCP HTTP Server → Nemotron (Nebius) → Persistent Storage
```

**Narration**: "Our Context-Aware Personal Assistant implements the MCP 2025-11-25 Streamable HTTP spec, giving Alexa+ persistent memory, tasks, calendar, and proactive assistance."

### Scene 3: Live Demo - Memory (0:30-0:55)
**Screen**: Terminal running curl commands
**Commands to run**:
```bash
# Store a memory
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: demo" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"add_memory","arguments":{"content":"Quarterly review due Friday, prepare slides tonight","tags":["work","urgent"],"importance":0.9}}}'

# Query it back
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: demo" \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"search_memories","arguments":{"query":"quarterly review"}}}'
```

**Narration**: "Memories persist across sessions with importance scoring and semantic search."

### Scene 4: Live Demo - Tasks & Proactive (0:55-1:20)
**Screen**: Terminal
**Commands**:
```bash
# Create task
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: demo" \
  -d '{"jsonrpc":"2.0","id":"3","method":"tools/call","params":{"name":"create_task","arguments":{"title":"Prepare Q3 slides","priority":5,"due_date":"2026-10-25T18:00:00","tags":["work"]}}}'

# Get proactive suggestions
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: demo" \
  -d '{"jsonrpc":"2.0","id":"4","method":"tools/call","params":{"name":"get_proactive_suggestions","arguments":{}}}'
```

**Narration**: "Tasks with priorities and due dates. The assistant proactively suggests what to focus on."

### Scene 5: Live Demo - Calendar (1:20-1:45)
**Screen**: Terminal
**Commands**:
```bash
# Add event
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: demo" \
  -d '{"jsonrpc":"2.0","id":"5","method":"tools/call","params":{"name":"add_event","arguments":{"title":"Team Sync","start_time":"2026-10-24T14:00:00","end_time":"2026-10-24T14:30:00","attendees":["Sarah","Mike"]}}}'

# Get context summary
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: demo" \
  -d '{"jsonrpc":"2.0","id":"6","method":"tools/call","params":{"name":"get_context","arguments":{}}}'
```

### Scene 6: Technical Highlights (1:45-2:10)
**Screen**: Code editor showing key files
**Show**:
- `server.py` - MCP tools/resources definitions
- `http_server.py` - Streamable HTTP transport
- `Dockerfile` - Production deployment
- `test_server.py` - Test suite

**Narration**: "Full MCP 2025-11-25 compliance. 11 tools, 5 resources. Docker-ready with health checks. Privacy-first local storage."

### Scene 7: Nebius/NVIDIA Integration (2:10-2:30) [Nebius version]
**Screen**: Architecture diagram + code
**Show**:
- Nemotron 3 Ultra for reasoning
- Nemotron Nano/Super for speed
- Nebius Token Factory API
- Serverless Endpoints/Jobs

**Narration**: "For Nebius track: Nemotron models via Token Factory. Serverless Endpoints for deployment. Serverless Jobs for background processing."

### Scene 8: Call to Action (2:30-2:45)
**Screen**: GitHub repo + Devpost submission pages
**Show**: 
- https://github.com/ASAYAMedia/amazon-alexa-mcp-hackathon
- Devpost submission URLs

**Narration**: "Context-Aware Personal Assistant - giving AI assistants the memory they deserve. Links in description."

---

## Post-Production

### YouTube Upload
- Title: "Context-Aware Personal Assistant MCP Server for Alexa+ | Amazon Developer Hackathon 2026"
- Description: Include GitHub link, Devpost links, tech stack
- Tags: MCP, Alexa+, AI, Hackathon, Nemotron, Nebius
- Playlist: "Hackathon Submissions 2026"

### Update Devpost Submissions
1. Go to each submission edit page
2. Update "Video demo link" field with YouTube URL
3. Save & continue → Submit

---

## Alternative: Animated Demo (if no recording possible)

Create a simple HTML animation showing the flow:

```html
<!-- demo-animation.html -->
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: monospace; background: #1a1a2e; color: #eee; padding: 20px; }
    .terminal { background: #0f0f23; border: 1px solid #333; padding: 20px; border-radius: 8px; }
    .command { color: #0f0; }
    .output { color: #aaa; margin-top: 5px; }
    .highlight { color: #ff6; }
  </style>
</head>
<body>
  <h1>Context-Aware Personal Assistant MCP Server</h1>
  <div class="terminal" id="term"></div>
  <script>
    const commands = [
      {cmd: 'curl -X POST localhost:8000/mcp -d \'{"method":"tools/call","params":{"name":"add_memory","arguments":{"content":"Quarterly review due Friday","tags":["work"],"importance":0.9}}}\'', out: 'Memory added: mem_123'},
      {cmd: 'curl -X POST localhost:8000/mcp -d \'{"method":"tools/call","params":{"name":"search_memories","arguments":{"query":"quarterly"}}}\'', out: '[{"content":"Quarterly review due Friday","tags":["work"],"importance":0.9}]'},
      {cmd: 'curl -X POST localhost:8000/mcp -d \'{"method":"tools/call","params":{"name":"get_proactive_suggestions","arguments":{}}}\'', out: '["Quarterly review due in 2 days (high priority)"]'},
    ];
    const term = document.getElementById('term');
    let i = 0;
    function type() {
      if (i >= commands.length) return;
      term.innerHTML += `<div class="command">$ ${commands[i].cmd}</div><div class="output">${commands[i].output}</div>`;
      i++;
      setTimeout(type, 2000);
    }
    type();
  </script>
</body>
</html>
```

---

## Quick Reference: Devpost Submission URLs

### Amazon Developer Hackathon
- Edit: https://devpost.com/submit-to/30992-build-ship-shape-amazon-developer-hackathon/manage/submissions/1191826-project-x/edit
- Project: https://devpost.com/software/context-aware-personal-assistant-mcp-server-for-alexa

### Nebius x NVIDIA Global AI Hackathon
- Edit: https://devpost.com/submit-to/30790-nebius-x-nvidia-global-ai-hackathon/manage/submissions/[SUBMISSION_ID]/edit
- Project: (will be available after submission)

---

## Timeline
- **Today**: Record video
- **Today**: Upload to YouTube
- **Today**: Update both Devpost submissions
- **Oct 23**: Amazon deadline
- **Oct 30**: Nebius deadline