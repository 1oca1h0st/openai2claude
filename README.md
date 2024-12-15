# OpenAI-to-Claude Proxy Server

A lightweight Flask-based proxy server that converts OpenAI API response to Claude API format with streaming support.

Blog: [https://blog.mrtlobs.net/
](https://blog.mrtblogs.net/openai2claude-converter)
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
```

## Or use Docker

```bash
docker build -t openai2claude .
docker run -d -p 5001:5001 --name openai2claude -restart=always openai2claude
```
