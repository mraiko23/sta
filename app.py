from flask import Flask, send_file, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Главная страница - AI Vibe Coder"""
    return send_file('ai-vibe-coder-puter.html')

@app.route('/api/status')
def status():
    """Статус сервера"""
    return jsonify({
        "status": "online",
        "service": "AI Vibe Coder",
        "method": "Puter.js (Frontend)",
        "features": [
            "✅ Бесплатный доступ к Claude через Puter.js",
            "✅ Работает полностью в браузере",
            "✅ Лимит: 100 запросов/час на модель",
            "✅ Не требует API ключей"
        ],
        "models": [
            "Claude 3.5 Sonnet",
            "Claude 3 Opus",
            "Claude 3 Haiku"
        ]
    })

@app.route('/api/health')
def health():
    """Health check для Render"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
