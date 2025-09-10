#!/usr/bin/env python3
"""
Setup script for Slack Message Analytics Dashboard
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="slack-message-analyzer",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@assistant.com",
    description="Interactive dashboard for analyzing and categorizing Slack messages with ticket similarity matching",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/slack-message-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
    },
    entry_points={
        "console_scripts": [
            "slack-analyzer=src.app:main",
            "slack-loader=src.slack_data_loader:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.css", "*.js", "*.html"],
    },
)