from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import json
import time

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов

# Puter.js API endpoint
PUTER_API_URL = "https://api.puter.com/drivers/call"

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "service": "AI Vibe Coder API Proxy",
        "message": "Бесплатный безлимитный доступ к Claude API через Puter.js",
        "endpoints": {
            "/api/chat": "POST - Отправить сообщение Claude (обычный режим)",
            "/api/chat/stream": "POST - Отправить сообщение Claude (стриминг)",
            "/api/models": "GET - Список доступных моделей"
        },
        "available_models": [
            "claude-sonnet-4-5",
            "claude-opus-4-5",
            "claude-haiku-4-5",
            "claude-sonnet-4",
            "claude-opus-4",
            "claude-opus-4-1"
        ]
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """Получить список доступных моделей"""
    return jsonify({
        "models": [
            {
                "id": "claude-sonnet-4-5",
                "name": "Claude Sonnet 4.5",
                "description": "Умный и эффективный для повседневных задач"
            },
            {
                "id": "claude-opus-4-5",
                "name": "Claude Opus 4.5",
                "description": "Самая мощная модель для сложных задач"
            },
            {
                "id": "claude-haiku-4-5",
                "name": "Claude Haiku 4.5",
                "description": "Быстрая и легкая модель"
            },
            {
                "id": "claude-sonnet-4",
                "name": "Claude Sonnet 4",
                "description": "Предыдущее поколение Sonnet"
            },
            {
                "id": "claude-opus-4",
                "name": "Claude Opus 4",
                "description": "Предыдущее поколение Opus"
            },
            {
                "id": "claude-opus-4-1",
                "name": "Claude Opus 4.1",
                "description": "Улучшенная версия Opus 4"
            }
        ]
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Обычный режим чата (без стриминга)"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        model = data.get('model', 'claude-sonnet-4-5')
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        # Формируем запрос к Puter.js API
        puter_request = {
            "interface": "puter-chat-completion",
            "driver": "anthropic",
            "method": "complete",
            "args": {
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "model": model
            }
        }
        
        # Отправляем запрос к Puter API
        response = requests.post(
            PUTER_API_URL,
            json=puter_request,
            headers={
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                "success": True,
                "model": model,
                "response": result.get("message", {}).get("content", [{}])[0].get("text", ""),
                "usage": result.get("usage", {}),
                "timestamp": time.time()
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Puter API error: {response.status_code}",
                "details": response.text
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Стриминг режим чата"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        model = data.get('model', 'claude-sonnet-4-5')
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        def generate():
            try:
                # Формируем запрос к Puter.js API с stream: true
                puter_request = {
                    "interface": "puter-chat-completion",
                    "driver": "anthropic",
                    "method": "complete",
                    "args": {
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "model": model,
                        "stream": True
                    }
                }
                
                # Отправляем запрос к Puter API
                response = requests.post(
                    PUTER_API_URL,
                    json=puter_request,
                    headers={
                        "Content-Type": "application/json"
                    },
                    stream=True
                )
                
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        yield f"data: {decoded_line}\n\n"
                        
            except Exception as e:
                error_data = json.dumps({"error": str(e)})
                yield f"data: {error_data}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    })

if __name__ == '__main__':
    # Для Render используется переменная окружения PORT
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
