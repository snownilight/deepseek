from flask import Flask, request, jsonify, render_template
import requests
import json
import re

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama 伺服器 URL
chat_context = []

def clean_response(text):
    return re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL).strip()

@app.route("/")
def index():
    return render_template("index.html")  # 顯示前端頁面

@app.route("/chat", methods=["POST"])
def chat():
    global chat_context

    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"error": "請輸入內容"}), 400

    # 發送請求給 Ollama（DeepSeek-R1）
    payload = {
        "model": "deepseek-r1",
        "prompt": user_input,
        "stream": False,
        "context": chat_context
    }
    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code != 200:
        return jsonify({"error": f"Ollama 伺服器錯誤 (HTTP {response.status_code})"}), 500

    try:
        response_json = json.loads(response.text)
        ai_response = response_json.get("response", "").strip()
        ai_response = clean_response(ai_response)
        chat_context = response_json.get("context", [])
        return jsonify({"response": ai_response})
    except Exception as e:
        print("Ollama回應內容: " + response.text)
        return jsonify({"error": f"解析 JSON 失敗: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)