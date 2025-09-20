import pytest
import sys
import os

# Add the backend directory to the path so we can import from MCP
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from MCP.server import server, hello

def test_hello_direct():
    """Test the hello function directly from the server module"""
    result = hello(name="Alice")
    assert result == "Hello, Alice!"

def test_server_instance():
    """Test that the server instance exists and is properly configured"""
    # Check if the server is a FastMCP instance
    from mcp.server.fastmcp import FastMCP
    assert isinstance(server, FastMCP)
    assert server.name == "demo-mcp"
    
def test_hello_with_different_names():
    """Test hello function with various names"""
    test_cases = [
        ("Alice", "Hello, Alice!"),
        ("Bob", "Hello, Bob!"),
        ("Charlie", "Hello, Charlie!"),
        ("", "Hello, !"),
    ]
    
    for name, expected in test_cases:
        result = hello(name=name)
        assert result == expected
