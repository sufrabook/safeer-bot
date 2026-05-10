"""
خادم API خفيف لخدمة Chat Widget
يمكن دمجه في أي موقع إلكتروني
"""

import os
import uuid
from typing import Optional
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from openai import OpenAI

# تثبيت flask-cors إذا لم تكن موجودة
try:
    from flask_cors import CORS
except ImportError:
    os.system("pip install flask-cors -q")
    from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # السماح لأي موقع بالاتصال

# ذاكرة المحادثات (مؤقتة في الذاكرة)
conversations = {}

SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي رسمي لجمعية سفراء الكتاب.
اسمك هو "سفير" وهو اسمك الشخصي الذي تعرّف به دائماً عند تقديم نفسك.
مهمتك الإجابة على استفسارات الزوار والأعضاء حول الجمعية وأنشطتها وخدماتها.
إذا لم تعرف الإجابة، قل بأدب: "عذراً، لا تتوفر لديّ هذه المعلومة حالياً، يمكنك التواصل مع الجمعية مباشرة."
تحدث دائماً باللغة العربية بأسلوب ودي ومحترف."""


@app.route("/api/chat", methods=["POST"])
def chat():
    """نقطة نهاية الدردشة الرئيسية"""
    data = request.json
    message = data.get("message", "")
    session_id = data.get("session_id", str(uuid.uuid4()))
    api_key = data.get("api_key") or os.environ.get("OPENAI_API_KEY", "")
    model = data.get("model", "gpt-4o-mini")

    if not message:
        return jsonify({"error": "الرسالة فارغة"}), 400
    if not api_key:
        return jsonify({"error": "مفتاح API مطلوب"}), 401

    # تهيئة سجل المحادثة
    if session_id not in conversations:
        conversations[session_id] = []

    conversations[session_id].append({"role": "user", "content": message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversations[session_id][-20:]

    try:
        client = OpenAI(api_key=api_key)

        def generate():
            full_response = ""
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                max_tokens=1024,
                temperature=0.7,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    yield f"data: {text}\n\n"

            conversations[session_id].append(
                {"role": "assistant", "content": full_response}
            )
            yield "data: [DONE]\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "AI Chatbot API"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
