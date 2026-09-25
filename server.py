#!/usr/bin/env python3
"""
Context-Aware Personal Assistant MCP Server for Alexa+
A Model Context Protocol server that provides persistent memory, 
calendar integration, task management, and proactive assistance.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolResult, ListResourcesResult, ListToolsResult, ReadResourceResult
)
import httpx
from pydantic import BaseModel


# Data models
@dataclass
class MemoryEntry:
    id: str
    content: str
    tags: List[str]
    timestamp: str
    importance: float  # 0.0 to 1.0
    source: str  # "user", "assistant", "system"

@dataclass
class Task:
    id: str
    title: str
    description: str
    status: str  # "pending", "in_progress", "done", "cancelled"
    priority: int  # 1-5
    due_date: Optional[str]
    created_at: str
    completed_at: Optional[str]
    tags: List[str]

@dataclass
class CalendarEvent:
    id: str
    title: str
    description: str
    start_time: str
    end_time: str
    location: Optional[str]
    attendees: List[str]
    recurrence: Optional[str]


class ContextAwareAssistant:
    """Main assistant class with persistent memory and context awareness."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.memories: List[MemoryEntry] = []
        self.tasks: List[Task] = []
        self.events: List[CalendarEvent] = []
        self.user_preferences: Dict[str, Any] = {}
        
        self._load_data()
    
    def _load_data(self):
        """Load all data from disk."""
        for attr, filename in [
            ("memories", "memories.json"),
            ("tasks", "tasks.json"),
            ("events", "events.json"),
            ("user_preferences", "preferences.json")
        ]:
            path = self.data_dir / filename
            if path.exists():
                with open(path) as f:
                    data = json.load(f)
                    if attr == "memories":
                        self.memories = [MemoryEntry(**m) for m in data]
                    elif attr == "tasks":
                        self.tasks = [Task(**t) for t in data]
                    elif attr == "events":
                        self.events = [CalendarEvent(**e) for e in data]
                    else:
                        setattr(self, attr, data)
    
    def _save_data(self):
        """Save all data to disk."""
        for attr, filename in [
            ("memories", "memories.json"),
            ("tasks", "tasks.json"),
            ("events", "events.json"),
            ("user_preferences", "preferences.json")
        ]:
            path = self.data_dir / filename
            data = getattr(self, attr)
            if attr in ["memories", "tasks", "events"]:
                data = [asdict(item) for item in data]
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
    
    # Memory operations
    def add_memory(self, content: str, tags: List[str], importance: float = 0.5, source: str = "user") -> MemoryEntry:
        entry = MemoryEntry(
            id=f"mem_{datetime.now().timestamp()}",
            content=content,
            tags=tags,
            timestamp=datetime.now().isoformat(),
            importance=importance,
            source=source
        )
        self.memories.append(entry)
        self._save_data()
        return entry
    
    def search_memories(self, query: str, tags: Optional[List[str]] = None, limit: int = 10) -> List[MemoryEntry]:
        results = []
        query_lower = query.lower()
        for mem in self.memories:
            if query_lower in mem.content.lower():
                if tags is None or any(t in mem.tags for t in tags):
                    results.append(mem)
        # Sort by importance and recency
        results.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
        return results[:limit]
    
    def get_recent_memories(self, hours: int = 24, limit: int = 20) -> List[MemoryEntry]:
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [m for m in self.memories if datetime.fromisoformat(m.timestamp) > cutoff]
        recent.sort(key=lambda m: m.timestamp, reverse=True)
        return recent[:limit]
    
    # Task operations
    def create_task(self, title: str, description: str = "", priority: int = 3, 
                    due_date: Optional[str] = None, tags: List[str] = None) -> Task:
        task = Task(
            id=f"task_{datetime.now().timestamp()}",
            title=title,
            description=description,
            status="pending",
            priority=priority,
            due_date=due_date,
            created_at=datetime.now().isoformat(),
            completed_at=None,
            tags=tags or []
        )
        self.tasks.append(task)
        self._save_data()
        return task
    
    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        for task in self.tasks:
            if task.id == task_id:
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                if kwargs.get("status") == "done":
                    task.completed_at = datetime.now().isoformat()
                self._save_data()
                return task
        return None
    
    def get_tasks(self, status: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Task]:
        results = self.tasks
        if status:
            results = [t for t in results if t.status == status]
        if tags:
            results = [t for t in results if any(tag in t.tags for tag in tags)]
        return sorted(results, key=lambda t: (-t.priority, t.created_at))
    
    # Calendar operations
    def add_event(self, title: str, start_time: str, end_time: str,
                  description: str = "", location: Optional[str] = None,
                  attendees: List[str] = None, recurrence: Optional[str] = None) -> CalendarEvent:
        event = CalendarEvent(
            id=f"evt_{datetime.now().timestamp()}",
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            attendees=attendees or [],
            recurrence=recurrence
        )
        self.events.append(event)
        self._save_data()
        return event
    
    def get_upcoming_events(self, hours: int = 24) -> List[CalendarEvent]:
        now = datetime.now()
        cutoff = now + timedelta(hours=hours)
        upcoming = []
        for event in self.events:
            start = datetime.fromisoformat(event.start_time)
            if now <= start <= cutoff:
                upcoming.append(event)
        return sorted(upcoming, key=lambda e: e.start_time)
    
    def get_events_for_date(self, date: datetime) -> List[CalendarEvent]:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        return [e for e in self.events 
                if start_of_day <= datetime.fromisoformat(e.start_time) < end_of_day]
    
    # Context awareness
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of current context for the assistant."""
        now = datetime.now()
        upcoming = self.get_upcoming_events(24)
        pending_tasks = self.get_tasks(status="pending")
        recent_memories = self.get_recent_memories(24, 5)
        
        return {
            "current_time": now.isoformat(),
            "upcoming_events_count": len(upcoming),
            "next_event": upcoming[0].title if upcoming else None,
            "pending_tasks_count": len(pending_tasks),
            "high_priority_tasks": [t.title for t in pending_tasks if t.priority >= 4][:3],
            "recent_memories": [m.content[:100] for m in recent_memories],
            "user_preferences": self.user_preferences
        }
    
    def set_preference(self, key: str, value: Any):
        self.user_preferences[key] = value
        self._save_data()
    
    def get_proactive_suggestions(self) -> List[str]:
        """Generate proactive suggestions based on context."""
        suggestions = []
        context = self.get_context_summary()
        
        # Check for upcoming events
        if context["next_event"]:
            suggestions.append(f"You have '{context['next_event']}' coming up soon.")
        
        # Check for overdue tasks
        overdue = [t for t in self.get_tasks(status="pending") 
                   if t.due_date and datetime.fromisoformat(t.due_date) < datetime.now()]
        if overdue:
            suggestions.append(f"You have {len(overdue)} overdue task(s).")
        
        # Check for high priority tasks
        if context["high_priority_tasks"]:
            suggestions.append(f"High priority: {', '.join(context['high_priority_tasks'])}")
        
        return suggestions


# Initialize the assistant
assistant = ContextAwareAssistant()

# Create MCP server
server = Server("context-aware-assistant")


@server.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources."""
    return ListResourcesResult(resources=[
        Resource(
            uri="assistant://context",
            name="Current Context",
            description="Current context summary including events, tasks, and memories",
            mimeType="application/json"
        ),
        Resource(
            uri="assistant://memories",
            name="All Memories",
            description="All stored memories",
            mimeType="application/json"
        ),
        Resource(
            uri="assistant://tasks",
            name="All Tasks",
            description="All tasks",
            mimeType="application/json"
        ),
        Resource(
            uri="assistant://events",
            name="Calendar Events",
            description="All calendar events",
            mimeType="application/json"
        ),
        Resource(
            uri="assistant://preferences",
            name="User Preferences",
            description="User preferences and settings",
            mimeType="application/json"
        ),
    ])


@server.read_resource()
async def read_resource(uri: str) -> ReadResourceResult:
    """Read a resource."""
    if uri == "assistant://context":
        return ReadResourceResult(contents=[
            TextContent(type="text", text=json.dumps(assistant.get_context_summary(), indent=2))
        ])
    elif uri == "assistant://memories":
        return ReadResourceResult(contents=[
            TextContent(type="text", text=json.dumps([asdict(m) for m in assistant.memories], indent=2))
        ])
    elif uri == "assistant://tasks":
        return ReadResourceResult(contents=[
            TextContent(type="text", text=json.dumps([asdict(t) for t in assistant.tasks], indent=2))
        ])
    elif uri == "assistant://events":
        return ReadResourceResult(contents=[
            TextContent(type="text", text=json.dumps([asdict(e) for e in assistant.events], indent=2))
        ])
    elif uri == "assistant://preferences":
        return ReadResourceResult(contents=[
            TextContent(type="text", text=json.dumps(assistant.user_preferences, indent=2))
        ])
    else:
        raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    return ListToolsResult(tools=[
        Tool(
            name="add_memory",
            description="Store a new memory with tags and importance",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Memory content"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for categorization"},
                    "importance": {"type": "number", "description": "Importance 0.0-1.0", "default": 0.5},
                    "source": {"type": "string", "description": "Source of memory", "default": "user"}
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="search_memories",
            description="Search memories by query and optional tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"},
                    "limit": {"type": "integer", "description": "Max results", "default": 10}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_recent_memories",
            description="Get recent memories from the last N hours",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {"type": "integer", "description": "Hours to look back", "default": 24},
                    "limit": {"type": "integer", "description": "Max results", "default": 20}
                }
            }
        ),
        Tool(
            name="create_task",
            description="Create a new task",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description", "default": ""},
                    "priority": {"type": "integer", "description": "Priority 1-5", "default": 3},
                    "due_date": {"type": "string", "description": "ISO format due date", "default": ""},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Task tags", "default": []}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="update_task",
            description="Update an existing task",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID"},
                    "status": {"type": "string", "description": "Task status", "enum": ["pending", "in_progress", "done", "cancelled"]},
                    "priority": {"type": "integer", "description": "Priority 1-5"},
                    "description": {"type": "string", "description": "Task description"}
                },
                "required": ["task_id"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List tasks with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status", "enum": ["pending", "in_progress", "done", "cancelled"]},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Filter by tags"}
                }
            }
        ),
        Tool(
            name="add_event",
            description="Add a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Event title"},
                    "start_time": {"type": "string", "description": "ISO format start time"},
                    "end_time": {"type": "string", "description": "ISO format end time"},
                    "description": {"type": "string", "description": "Event description", "default": ""},
                    "location": {"type": "string", "description": "Event location", "default": ""},
                    "attendees": {"type": "array", "items": {"type": "string"}, "description": "Attendees", "default": []},
                    "recurrence": {"type": "string", "description": "Recurrence rule", "default": ""}
                },
                "required": ["title", "start_time", "end_time"]
            }
        ),
        Tool(
            name="get_upcoming_events",
            description="Get upcoming events within N hours",
            inputSchema={
                "type": "object",
                "properties": {
                    "hours": {"type": "integer", "description": "Hours to look ahead", "default": 24}
                }
            }
        ),
        Tool(
            name="get_context",
            description="Get current context summary",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_proactive_suggestions",
            description="Get proactive suggestions based on current context",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="set_preference",
            description="Set a user preference",
            inputSchema={
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Preference key"},
                    "value": {"type": "string", "description": "Preference value"}
                },
                "required": ["key", "value"]
            }
        ),
    ])


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    try:
        if name == "add_memory":
            entry = assistant.add_memory(
                content=arguments["content"],
                tags=arguments.get("tags", []),
                importance=arguments.get("importance", 0.5),
                source=arguments.get("source", "user")
            )
            return CallToolResult(content=[TextContent(type="text", text=f"Memory added: {entry.id}")])
        
        elif name == "search_memories":
            results = assistant.search_memories(
                query=arguments["query"],
                tags=arguments.get("tags"),
                limit=arguments.get("limit", 10)
            )
            return CallToolResult(content=[TextContent(type="text", text=json.dumps([asdict(r) for r in results], indent=2))])
        
        elif name == "get_recent_memories":
            results = assistant.get_recent_memories(
                hours=arguments.get("hours", 24),
                limit=arguments.get("limit", 20)
            )
            return CallToolResult(content=[TextContent(type="text", text=json.dumps([asdict(r) for r in results], indent=2))])
        
        elif name == "create_task":
            task = assistant.create_task(
                title=arguments["title"],
                description=arguments.get("description", ""),
                priority=arguments.get("priority", 3),
                due_date=arguments.get("due_date") or None,
                tags=arguments.get("tags", [])
            )
            return CallToolResult(content=[TextContent(type="text", text=f"Task created: {task.id} - {task.title}")])
        
        elif name == "update_task":
            task = assistant.update_task(arguments["task_id"], **{k: v for k, v in arguments.items() if k != "task_id"})
            if task:
                return CallToolResult(content=[TextContent(type="text", text=f"Task updated: {task.id}")])
            else:
                return CallToolResult(content=[TextContent(type="text", text="Task not found")], isError=True)
        
        elif name == "list_tasks":
            tasks = assistant.get_tasks(
                status=arguments.get("status"),
                tags=arguments.get("tags")
            )
            return CallToolResult(content=[TextContent(type="text", text=json.dumps([asdict(t) for t in tasks], indent=2))])
        
        elif name == "add_event":
            event = assistant.add_event(
                title=arguments["title"],
                start_time=arguments["start_time"],
                end_time=arguments["end_time"],
                description=arguments.get("description", ""),
                location=arguments.get("location") or None,
                attendees=arguments.get("attendees", []),
                recurrence=arguments.get("recurrence") or None
            )
            return CallToolResult(content=[TextContent(type="text", text=f"Event created: {event.id} - {event.title}")])
        
        elif name == "get_upcoming_events":
            events = assistant.get_upcoming_events(hours=arguments.get("hours", 24))
            return CallToolResult(content=[TextContent(type="text", text=json.dumps([asdict(e) for e in events], indent=2))])
        
        elif name == "get_context":
            context = assistant.get_context_summary()
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(context, indent=2))])
        
        elif name == "get_proactive_suggestions":
            suggestions = assistant.get_proactive_suggestions()
            return CallToolResult(content=[TextContent(type="text", text=json.dumps(suggestions, indent=2))])
        
        elif name == "set_preference":
            assistant.set_preference(arguments["key"], arguments["value"])
            return CallToolResult(content=[TextContent(type="text", text=f"Preference set: {arguments['key']}")])
        
        else:
            return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")], isError=True)
    
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")], isError=True)


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())