"""
ملف الإعدادات الرئيسي للشات بوت
"""

import os

# ===== إعدادات النماذج المتاحة =====
AVAILABLE_MODELS = {
    "GPT-4o": {
        "provider": "openai",
        "model_id": "gpt-4o",
        "description": "أقوى نموذج من OpenAI",
        "base_url": None,
    },
    "GPT-4o Mini": {
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "description": "نموذج سريع واقتصادي من OpenAI",
        "base_url": None,
    },
    "GPT-4.1 Mini": {
        "provider": "openai",
        "model_id": "gpt-4.1-mini",
        "description": "نموذج GPT-4.1 Mini",
        "base_url": None,
    },
    "Gemini 2.5 Flash": {
        "provider": "openai_compatible",
        "model_id": "gemini-2.5-flash",
        "description": "نموذج Gemini من Google",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "Claude 3.5 Sonnet": {
        "provider": "anthropic",
        "model_id": "claude-3-5-sonnet-20241022",
        "description": "نموذج Claude من Anthropic",
        "base_url": None,
    },
}

# ===== إعدادات معالجة الملفات =====
SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx", "csv", "md"]
MAX_FILE_SIZE_MB = 50
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ===== إعدادات الذاكرة =====
MAX_HISTORY_MESSAGES = 20
VECTOR_DB_PATH = "/home/ubuntu/ai_chatbot/data/vectorstore"

# ===== إعدادات الواجهة =====
APP_TITLE = "🤖 شات بوت الذكاء الاصطناعي"
APP_ICON = "🤖"
DEFAULT_SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي متخصص ومفيد. تجيب على الأسئلة بدقة واحترافية.
إذا كانت هناك وثائق أو ملفات تم تحميلها، استخدمها كمصدر رئيسي للإجابة.
تحدث باللغة التي يستخدمها المستخدم."""

# ===== System Prompt مخصص لجمعية سفراء الكتاب =====
BOOK_FRIENDS_SYSTEM_PROMPT = """أنت مساعد ذكاء اصطناعي رسمي لجمعية سفراء الكتاب.
اسمك هو "سفير" وهو اسمك الشخصي الذي تعرّف به دائماً عند تقديم نفسك.
مهمتك الإجابة على استفسارات الزوار والأعضاء حول الجمعية وأنشطتها وخدماتها.
إذا كانت هناك وثائق أو ملفات تم تحميلها، استخدمها كمصدر رئيسي للإجابة.
إذا لم تعرف الإجابة، قل بأدب: "عذراً، لا تتوفر لديّ هذه المعلومة حالياً، يمكنك التواصل مع الجمعية مباشرة."
تحدث دائماً باللغة العربية بأسلوب ودي ومحترف."""

# ===== إعدادات Chat Widget (للدمج في المواقع) =====
WIDGET_TITLE = "سفير"
WIDGET_SUBTITLE = "كيف يمكنني مساعدتك؟"
WIDGET_PLACEHOLDER = "اكتب سؤالك هنا..."
WIDGET_PRIMARY_COLOR = "#1a5276"
WIDGET_SECONDARY_COLOR = "#2e86c1"

# ===== مسارات الملفات =====
UPLOADS_DIR = "/home/ubuntu/ai_chatbot/uploads"
DATA_DIR = "/home/ubuntu/ai_chatbot/data"
