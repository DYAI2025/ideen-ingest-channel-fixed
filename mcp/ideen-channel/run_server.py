#!/usr/bin/env python3
"""
Entry point for Ideen Channel MCP Server
"""

from ideen_channel.server import mcp

if __name__ == "__main__":
    mcp.run()