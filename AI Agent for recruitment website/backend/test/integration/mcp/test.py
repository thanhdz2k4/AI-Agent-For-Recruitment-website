import subprocess
import sys
import json
import pytest

@pytest.mark.asyncio
async def test_server_via_stdio(tmp_path):
    # Start the server as a subprocess
    proc = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    # A JSON-RPC request the MCP client would send
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call_tool",
        "params": {"name": "hello", "arguments": {"name": "Bob"}}
    }

    # Write request and flush
    proc.stdin.write(json.dumps(request) + "\n")
    proc.stdin.flush()

    # Read one line of response
    response_line = proc.stdout.readline()
    proc.kill()

    response = json.loads(response_line)
    assert response["result"]["output"] == "Hello, Bob!"
