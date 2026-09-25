#!/usr/bin/env python3
"""
HTTP Server for Context-Aware Personal Assistant MCP Server
Implements Streamable HTTP transport for Alexa+ integration (MCP spec 2025-11-25+)
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from server import assistant, server as mcp_server


# Request/Response models for MCP over HTTP
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


# Session management
class MCPSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.initialized = False
        self.client_info: Optional[Dict] = None
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP request."""
        try:
            if request.method == "initialize":
                return await self.handle_initialize(request)
            elif request.method == "initialized":
                self.initialized = True
                return MCPResponse(id=request.id, result={})
            elif request.method == "tools/list":
                return await self.handle_tools_list(request)
            elif request.method == "tools/call":
                return await self.handle_tool_call(request)
            elif request.method == "resources/list":
                return await self.handle_resources_list(request)
            elif request.method == "resources/read":
                return await self.handle_resource_read(request)
            elif request.method == "prompts/list":
                return MCPResponse(id=request.id, result={"prompts": []})
            else:
                return MCPResponse(
                    id=request.id,
                    error={"code": -32601, "message": f"Method not found: {request.method}"}
                )
        except Exception as e:
            return MCPResponse(
                id=request.id,
                error={"code": -32603, "message": f"Internal error: {str(e)}"}
            )
    
    async def handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """Handle initialize request."""
        self.client_info = request.params or {}
        self.initialized = True
        
        return MCPResponse(
            id=request.id,
            result={
                "protocolVersion": "2025-11-25",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True}
                },
                "serverInfo": {
                    "name": "context-aware-assistant",
                    "version": "1.0.0"
                }
            }
        )
    
    async def handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/list request."""
        from server import list_tools
        result = await list_tools()
        return MCPResponse(id=request.id, result={"tools": [t.model_dump() for t in result.tools]})
    
    async def handle_tool_call(self, request: MCPRequest) -> MCPResponse:
        """Handle tools/call request."""
        from server import call_tool
        params = request.params or {}
        name = params.get("name")
        arguments = params.get("arguments", {})
        result = await call_tool(name, arguments)
        return MCPResponse(
            id=request.id,
            result={
                "content": [c.model_dump() for c in result.content],
                "isError": result.isError
            }
        )
    
    async def handle_resources_list(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/list request."""
        from server import list_resources
        result = await list_resources()
        return MCPResponse(id=request.id, result={"resources": [r.model_dump() for r in result.resources]})
    
    async def handle_resource_read(self, request: MCPRequest) -> MCPResponse:
        """Handle resources/read request."""
        from server import read_resource
        params = request.params or {}
        uri = params.get("uri")
        result = await read_resource(uri)
        return MCPResponse(
            id=request.id,
            result={"contents": [c.model_dump() for c in result.contents]}
        )


# Session storage
sessions: Dict[str, MCPSession] = {}


def get_session(session_id: str) -> MCPSession:
    """Get or create session."""
    if session_id not in sessions:
        sessions[session_id] = MCPSession(session_id)
    return sessions[session_id]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Startup
    print("Starting Context-Aware Assistant MCP Server...")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Context-Aware Personal Assistant MCP Server",
    description="MCP Server with persistent memory, tasks, calendar, and proactive assistance for Alexa+",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for Alexa+ integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": "Context-Aware Personal Assistant MCP Server",
        "version": "1.0.0",
        "protocol": "MCP 2025-11-25",
        "transport": "Streamable HTTP",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Main MCP endpoint for Streamable HTTP transport."""
    # Get session ID from header or create new
    session_id = request.headers.get("Mcp-Session-Id", "default")
    session = get_session(session_id)
    
    # Parse request
    body = await request.json()
    mcp_request = MCPRequest(**body)
    
    # Handle request
    response = await session.handle_request(mcp_request)
    
    # Return with session ID header
    headers = {"Mcp-Session-Id": session_id}
    return Response(
        content=response.model_dump_json(exclude_none=True),
        media_type="application/json",
        headers=headers
    )


@app.get("/mcp")
async def mcp_sse(request: Request):
    """SSE endpoint for server-sent events (optional)."""
    session_id = request.headers.get("Mcp-Session-Id", "default")
    session = get_session(session_id)
    
    async def event_stream():
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'sessionId': session_id})}\n\n"
        
        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield f"data: {json.dumps({'type': 'ping'})}\n\n"
    
    return Response(
        content=event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Mcp-Session-Id": session_id
        }
    )


@app.delete("/mcp/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if session_id in sessions:
        del sessions[session_id]
    return {"status": "deleted"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)