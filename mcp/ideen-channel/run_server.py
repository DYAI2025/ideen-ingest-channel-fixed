#!/usr/bin/env python3
"""
Entry point for Ideen Channel MCP Server
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ideen_channel.server import mcp

if __name__ == "__main__":
    mcp.run()