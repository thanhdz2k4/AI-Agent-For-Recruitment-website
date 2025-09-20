import pytest
from mcp.server.fastmcp import FastMCP

def test_hello_direct():
    # FastMCP stores tools in a dict: name -> Tool
    assert "hello" in FastMCP._tools

    tool = FastMCP._tools["hello"]
    # tool.func is the original Python callable
    result = tool.func(name="Alice")

    assert result == "Hello, Alice!"
