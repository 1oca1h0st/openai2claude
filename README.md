# OpenAI-to-Claude Proxy Server

A lightweight Flask-based proxy server that converts OpenAI API response to Claude API format with streaming support.

## Key Features

- SSE (Server-Sent Events) streaming support
- Complete error handling and exception catching
- CORS support for cross-origin requests
- Simple API key authentication
- Easy to deploy and use

## Requirements

- Python 3.6+
- Flask
- Flask-CORS
- Requests

## Installation

Install dependencies:
```bash
pip install flask flask-cors requests
