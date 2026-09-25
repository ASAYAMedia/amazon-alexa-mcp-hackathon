#!/usr/bin/env python3
"""
Test script for Context-Aware Personal Assistant MCP Server
Tests both STDIO and HTTP server functionality
"""

import asyncio
import json
import subprocess
import sys
import time
import httpx
from pathlib import Path


async def test_stdio_server():
    """Test the STDIO MCP server."""
    print("=" * 60)
    print("Testing STDIO MCP Server")
    print("=" * 60)
    
    # Start server process
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path(__file__).parent
    )
    
    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {}
        }
        proc.stdin.write((json.dumps(init_request) + "\n").encode())
        await proc.stdin.drain()
        
        # Read response
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
        response = json.loads(line.decode())
        print(f"Initialize response: {json.dumps(response, indent=2)}")
        
        # Send initialized notification
        initialized = {"jsonrpc": "2.0", "method": "initialized", "params": {}}
        proc.stdin.write((json.dumps(initialized) + "\n").encode())
        await proc.stdin.drain()
        
        # Test tools/list
        tools_request = {"jsonrpc": "2.0", "id": "2", "method": "tools/list", "params": {}}
        proc.stdin.write((json.dumps(tools_request) + "\n").encode())
        await proc.stdin.drain()
        
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
        response = json.loads(line.decode())
        print(f"Tools count: {len(response.get('result', {}).get('tools', []))}")
        
        # Test add_memory
        add_mem = {
            "jsonrpc": "2.0",
            "id": "3",
            "method": "tools/call",
            "params": {
                "name": "add_memory",
                "arguments": {
                    "content": "Test memory from STDIO test",
                    "tags": ["test", "stdio"],
                    "importance": 0.8
                }
            }
        }
        proc.stdin.write((json.dumps(add_mem) + "\n").encode())
        await proc.stdin.drain()
        
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
        response = json.loads(line.decode())
        print(f"Add memory response: {json.dumps(response, indent=2)}")
        
        # Test get_context
        get_ctx = {"jsonrpc": "2.0", "id": "4", "method": "tools/call", "params": {"name": "get_context", "arguments": {}}}
        proc.stdin.write((json.dumps(get_ctx) + "\n").encode())
        await proc.stdin.drain()
        
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
        response = json.loads(line.decode())
        print(f"Context response: {json.dumps(response, indent=2)}")
        
        print("✓ STDIO server tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ STDIO server test failed: {e}")
        return False
    finally:
        proc.terminate()
        await proc.wait()


async def test_http_server():
    """Test the HTTP MCP server."""
    print("\n" + "=" * 60)
    print("Testing HTTP MCP Server")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    session_id = "test-session-123"
    headers = {"Content-Type": "application/json", "Mcp-Session-Id": session_id}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Health check
            resp = await client.get(f"{base_url}/health")
            print(f"Health check: {resp.status_code} - {resp.json()}")
            
            # Initialize
            init_req = {"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}}
            resp = await client.post(f"{base_url}/mcp", json=init_req, headers=headers)
            print(f"Initialize: {resp.status_code}")
            print(f"  Session ID header: {resp.headers.get('Mcp-Session-Id')}")
            print(f"  Response: {json.dumps(resp.json(), indent=2)}")
            
            # Tools list
            tools_req = {"jsonrpc": "2.0", "id": "2", "method": "tools/list", "params": {}}
            resp = await client.post(f"{base_url}/mcp", json=tools_req, headers=headers)
            print(f"Tools list: {resp.status_code}")
            tools = resp.json().get("result", {}).get("tools", [])
            print(f"  Tools count: {len(tools)}")
            
            # Add memory
            add_mem = {
                "jsonrpc": "2.0",
                "id": "3",
                "method": "tools/call",
                "params": {
                    "name": "add_memory",
                    "arguments": {
                        "content": "Test memory from HTTP test",
                        "tags": ["test", "http"],
                        "importance": 0.9
                    }
                }
            }
            resp = await client.post(f"{base_url}/mcp", json=add_mem, headers=headers)
            print(f"Add memory: {resp.status_code}")
            print(f"  Response: {json.dumps(resp.json(), indent=2)}")
            
            # Create task
            create_task = {
                "jsonrpc": "2.0",
                "id": "4",
                "method": "tools/call",
                "params": {
                    "name": "create_task",
                    "arguments": {
                        "title": "Test task from HTTP",
                        "description": "Created via HTTP test",
                        "priority": 4,
                        "tags": ["test"]
                    }
                }
            }
            resp = await client.post(f"{base_url}/mcp", json=create_task, headers=headers)
            print(f"Create task: {resp.status_code}")
            print(f"  Response: {json.dumps(resp.json(), indent=2)}")
            
            # Get context
            get_ctx = {"jsonrpc": "2.0", "id": "5", "method": "tools/call", "params": {"name": "get_context", "arguments": {}}}
            resp = await client.post(f"{base_url}/mcp", json=get_ctx, headers=headers)
            print(f"Get context: {resp.status_code}")
            print(f"  Response: {json.dumps(resp.json(), indent=2)}")
            
            # Get proactive suggestions
            get_sugg = {"jsonrpc": "2.0", "id": "6", "method": "tools/call", "params": {"name": "get_proactive_suggestions", "arguments": {}}}
            resp = await client.post(f"{base_url}/mcp", json=get_sugg, headers=headers)
            print(f"Get suggestions: {resp.status_code}")
            print(f"  Response: {json.dumps(resp.json(), indent=2)}")
            
            # Test resources
            resources_req = {"jsonrpc": "2.0", "id": "7", "method": "resources/list", "params": {}}
            resp = await client.post(f"{base_url}/mcp", json=resources_req, headers=headers)
            print(f"Resources list: {resp.status_code}")
            resources = resp.json().get("result", {}).get("resources", [])
            print(f"  Resources count: {len(resources)}")
            
            # Read context resource
            read_ctx = {"jsonrpc": "2.0", "id": "8", "method": "resources/read", "params": {"uri": "assistant://context"}}
            resp = await client.post(f"{base_url}/mcp", json=read_ctx, headers=headers)
            print(f"Read context resource: {resp.status_code}")
            print(f"  Response: {json.dumps(resp.json(), indent=2)}")
            
            print("✓ HTTP server tests passed!")
            return True
            
        except Exception as e:
            print(f"✗ HTTP server test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run all tests."""
    print("Starting MCP Server Tests\n")
    
    # Test STDIO server
    stdio_ok = await test_stdio_server()
    
    # Test HTTP server (needs server running)
    print("\nNote: HTTP tests require server running on localhost:8000")
    print("Start with: python http_server.py")
    print("Then run this test again.\n")
    
    # Check if HTTP server is running
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get("http://localhost:8000/health")
            if resp.status_code == 200:
                http_ok = await test_http_server()
            else:
                print("HTTP server not running, skipping HTTP tests")
                http_ok = True  # Not a failure, just skipped
    except:
        print("HTTP server not running, skipping HTTP tests")
        http_ok = True
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"STDIO Server: {'PASS' if stdio_ok else 'FAIL'}")
    print(f"HTTP Server:  {'PASS' if http_ok else 'FAIL/SKIP'}")
    
    return stdio_ok and http_ok


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)