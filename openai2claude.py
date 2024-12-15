from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import requests
import json
import uuid

app = Flask(__name__)
CORS(app)  # 允许所有域名访问


def parse_authorization_header():
    try:
        auth_header = request.headers.get('x-api-key')
        if not auth_header:
            raise ValueError("Authorization header is missing")
        return auth_header
    except Exception as e:
        raise ValueError(str(e))


def send_openai_request(openai_req_body, api_key):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.post('https://{openai_base_url}/v1/chat/completions',
                             headers=headers,
                             json=openai_req_body,
                             stream=True)
    response.raise_for_status()
    return response


@app.route('/v1/messages', methods=['POST'])
def proxy_from_claude_stream():
    claude_req = request.json
    try:
        api_key = parse_authorization_header()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    try:
        resp = send_openai_request(claude_req, api_key)
    except requests.RequestException as e:
        return jsonify({"error": "Failed to send request to OpenAI API"}), 500

    def generate():
        content = ""
        message_started = False
        for line in resp.iter_lines():
            if line:
                line_str = line.decode('utf-8').strip()
                if not message_started:
                    yield f'event: message_start\ndata: {json.dumps({
                        "type": "message_start",
                        "message": {
                            "id": str(uuid.uuid4()),
                            "type": "message",
                            "model": claude_req["model"],
                            "usage": {"input_tokens": 8, "output_tokens": 0},
                            "role": "assistant"
                        }
                    })}\n\n'
                    yield f'event: content_block_start\ndata: {json.dumps({"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})}\n\n'
                    yield f'event: ping\ndata: {json.dumps({"type": "ping"})}\n\n'
                    message_started = True
                if line_str.startswith("data:"):
                    data_str = line_str[5:].strip()
                    if data_str and data_str != "[DONE]":  # 检查数据是否为空
                        try:
                            data = json.loads(data_str)
                        except json.JSONDecodeError as e:
                            print(f"Failed to decode JSON: {data_str}")
                            continue
                        if data.get("object") == "chat.completion.chunk":
                            choices = data.get("choices", [])
                            if choices:
                                delta = choices[0].get("delta", {})
                                content_str = delta.get("content")
                                if content_str:
                                    content += content_str
                                    yield f'event: content_block_delta\ndata: {json.dumps({"type": "content_block_delta", "delta": {"type": "text_delta", "text": content_str}})}\n\n'
                elif line_str.startswith("event: message_stop"):
                    yield f'event: message_stop\ndata: {json.dumps({"type": "message_stop"})}\n\n'
                    break
        # Ensure to send the final message stop if it wasn't caught in the loop
        if content:
            yield f'event: message_stop\ndata: {json.dumps({"type": "message_stop"})}\n\n'

    return Response(generate(), content_type='text/event-stream')


if __name__ == '__main__':
    app.run(debug=True, port=5001, host="0.0.0.0")
