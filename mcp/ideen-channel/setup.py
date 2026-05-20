#!/usr/bin/env python3
"""
Setup script for Ideen Channel MCP Server
Explicit setup to avoid Railway build issues
"""

from setuptools import setup, find_packages

setup(
    name="ideen-channel",
    version="0.1.0",
    description="MCP Server for Ideen Channel integration with WUPHF",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        "httpx>=0.27.0",
        "fastmcp>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "ideen-channel-server=ideen_channel.server:main",
        ],
    },
)