"""
سفير - الواجهة الرئيسية
مبني بـ Python + Streamlit
"""

import os
import uuid
import time
import streamlit as st
from pathlib import Path

from config import (
    AVAILABLE_MODELS,
    SUPPORTED_FILE_TYPES,
    MAX_FILE_SIZE_MB,
    APP_TITLE,
    APP_ICON,
    DEFAULT_SYSTEM_PROMPT,
    UPLOADS_DIR,
)
from chatbot_engine import ChatbotEngine
from file_processor import KnowledgeBase

# ===== إعداد الصفحة =====
st.set_page_config(
    page_title="سفير",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "شات بوت ذكاء اصطناعي متكامل مبني بـ Python + Streamlit",
    },
)

# ===== CSS مخصص =====
st.markdown("""
<style>
    /* الخط والاتجاه العام */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Cairo', 'Segoe UI', sans-serif !important;
    }
    
    /* الخلفية الرئيسية */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }
    
    /* الشريط الجانبي */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    /* بطاقات الرسائل */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        direction: rtl;
        text-align: right;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white !important;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
        float: left;
        clear: both;
        box-shadow: 0 4px 15px rgba(30, 60, 114, 0.4);
        direction: rtl;
        text-align: right;
    }
    
    .message-container {
        overflow: hidden;
        margin-bottom: 10px;
    }
    
    /* حاوية الدردشة */
    .chat-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
    }
    
    /* العنوان الرئيسي */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .subtitle {
        text-align: center;
        color: rgba(255,255,255,0.6);
        font-size: 1rem;
        margin-bottom: 30px;
    }
    
    /* الأزرار */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* حقل الإدخال */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        direction: rtl;
    }
    
    /* القائمة المنسدلة */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* بطاقة الإحصائيات */
    .stat-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 5px 0;
    }
    
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #f093fb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        color: rgba(255,255,255,0.6);
        font-size: 0.85rem;
    }
    
    /* شريط الحالة */
    .status-bar {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 8px 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* الرسائل */
    [data-testid="stChatMessage"] {
        background: transparent !important;
    }
    
    /* تحسين مربع الدردشة */
    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 25px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* تحسين الشريط الجانبي */
    .sidebar-section {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-title {
        color: #667eea !important;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(102, 126, 234, 0.3);
        padding-bottom: 8px;
    }
    
    /* تحسين الألوان العامة */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #e0e0e0;
    }
    
    /* مؤشر الكتابة */
    .typing-indicator {
        display: inline-flex;
        gap: 4px;
        padding: 10px 15px;
        background: rgba(30, 60, 114, 0.5);
        border-radius: 18px;
        margin: 5px 0;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        background: #667eea;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1.2); opacity: 1; }
    }
    
    /* تحسين رفع الملفات */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        border: 2px dashed rgba(102, 126, 234, 0.5) !important;
        padding: 10px !important;
    }
    
    /* تحسين شريط التقدم */
    .stProgress > div > div {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-radius: 10px !important;
    }
    
    /* تحسين الـ expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
    }
    
    /* إخفاء عناصر Streamlit الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* تحسين الـ chat messages */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
    }
    
    /* تحسين الـ info/success/error boxes */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)


# ===== تهيئة حالة الجلسة =====
def init_session_state():
    """تهيئة متغيرات الجلسة"""
    defaults = {
        "messages": [],
        "session_id": str(uuid.uuid4()),
        "api_key": "",
        "selected_model": "GPT-4o Mini",
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
        "chatbot": None,
        "knowledge_base": None,
        "uploaded_files": [],
        "api_validated": False,
        "total_messages": 0,
        "use_knowledge_base": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_or_create_chatbot() -> ChatbotEngine:
    """الحصول على أو إنشاء محرك الشات بوت"""
    if st.session_state.chatbot is None:
        st.session_state.chatbot = ChatbotEngine(
            api_key=st.session_state.api_key,
            model_name=st.session_state.selected_model,
            system_prompt=st.session_state.system_prompt,
        )
    return st.session_state.chatbot


def get_or_create_knowledge_base() -> KnowledgeBase:
    """الحصول على أو إنشاء قاعدة المعرفة"""
    if st.session_state.knowledge_base is None:
        st.session_state.knowledge_base = KnowledgeBase(
            api_key=st.session_state.api_key,
            session_id=st.session_state.session_id,
        )
    return st.session_state.knowledge_base


# ===== الشريط الجانبي =====
def render_sidebar():
    """رسم الشريط الجانبي"""
    with st.sidebar:
        # الشعار والعنوان
        st.markdown("""
        <div style="text-align: center; padding: 20px 0 10px 0;">
            <div style="font-size: 3rem;">🤖</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #667eea;">سفير</div>
            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5);">مساعدك الذكي من جمعية سفراء الكتاب</div>
        </div>
        <hr style="border-color: rgba(255,255,255,0.1);">
        """, unsafe_allow_html=True)

        # ===== قسم الإعدادات =====
        st.markdown('<div class="sidebar-title">⚙️ الإعدادات</div>', unsafe_allow_html=True)

        # مفتاح API
        api_key_input = st.text_input(
            "🔑 مفتاح API",
            value=st.session_state.api_key,
            type="password",
            placeholder="أدخل مفتاح API هنا...",
            help="أدخل مفتاح API الخاص بالنموذج المختار",
        )

        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
            st.session_state.api_validated = False
            st.session_state.chatbot = None
            st.session_state.knowledge_base = None

        # اختيار النموذج
        model_options = list(AVAILABLE_MODELS.keys())
        selected_model = st.selectbox(
            "🧠 النموذج",
            options=model_options,
            index=model_options.index(st.session_state.selected_model)
            if st.session_state.selected_model in model_options
            else 1,
            help="اختر نموذج الذكاء الاصطناعي",
        )

        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.session_state.chatbot = None
            st.session_state.api_validated = False

        # معلومات النموذج
        model_info = AVAILABLE_MODELS.get(selected_model, {})
        st.caption(f"ℹ️ {model_info.get('description', '')}")

        # زر التحقق من API
        if st.button("✅ تحقق من مفتاح API", use_container_width=True):
            if st.session_state.api_key:
                with st.spinner("جاري التحقق..."):
                    chatbot = get_or_create_chatbot()
                    valid, msg = chatbot.validate_api_key()
                    if valid:
                        st.session_state.api_validated = True
                        st.success(msg)
                    else:
                        st.session_state.api_validated = False
                        st.error(msg)
            else:
                st.warning("⚠️ أدخل مفتاح API أولاً")

        # مؤشر الحالة
        if st.session_state.api_validated:
            st.markdown(
                '<div style="color: #4CAF50; text-align: center; font-size: 0.85rem;">🟢 متصل</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.api_key:
            st.markdown(
                '<div style="color: #FF9800; text-align: center; font-size: 0.85rem;">🟡 لم يتم التحقق</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="color: #f44336; text-align: center; font-size: 0.85rem;">🔴 غير متصل</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ===== قسم الـ System Prompt =====
        with st.expander("📝 تخصيص شخصية البوت", expanded=False):
            new_prompt = st.text_area(
                "System Prompt",
                value=st.session_state.system_prompt,
                height=150,
                help="حدد شخصية وسلوك البوت",
            )
            if new_prompt != st.session_state.system_prompt:
                st.session_state.system_prompt = new_prompt
                if st.session_state.chatbot:
                    st.session_state.chatbot.update_system_prompt(new_prompt)
            if st.button("🔄 إعادة تعيين", use_container_width=True):
                st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT
                if st.session_state.chatbot:
                    st.session_state.chatbot.update_system_prompt(DEFAULT_SYSTEM_PROMPT)
                st.rerun()

        st.markdown("---")

        # ===== قسم رفع الملفات =====
        st.markdown('<div class="sidebar-title">📁 قاعدة المعرفة</div>', unsafe_allow_html=True)

        use_kb = st.toggle(
            "استخدام قاعدة المعرفة",
            value=st.session_state.use_knowledge_base,
            help="عند التفعيل، سيبحث البوت في الملفات المرفوعة",
        )
        st.session_state.use_knowledge_base = use_kb

        uploaded_files = st.file_uploader(
            "رفع ملفات",
            type=SUPPORTED_FILE_TYPES,
            accept_multiple_files=True,
            help=f"الأنواع المدعومة: {', '.join(SUPPORTED_FILE_TYPES)} | الحد الأقصى: {MAX_FILE_SIZE_MB}MB",
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name not in st.session_state.uploaded_files:
                    if not st.session_state.api_key:
                        st.warning("⚠️ أدخل مفتاح API أولاً لمعالجة الملفات")
                        break

                    file_size = uploaded_file.size / (1024 * 1024)
                    if file_size > MAX_FILE_SIZE_MB:
                        st.error(f"❌ الملف {uploaded_file.name} أكبر من {MAX_FILE_SIZE_MB}MB")
                        continue

                    with st.spinner(f"⏳ معالجة {uploaded_file.name}..."):
                        os.makedirs(UPLOADS_DIR, exist_ok=True)
                        file_path = os.path.join(UPLOADS_DIR, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        kb = get_or_create_knowledge_base()
                        success, msg = kb.add_file(file_path, uploaded_file.name)

                        if success:
                            st.session_state.uploaded_files.append(uploaded_file.name)
                            st.success(f"✅ {uploaded_file.name}: {msg}")
                        else:
                            st.error(f"❌ {uploaded_file.name}: {msg}")

        # عرض الملفات المرفوعة
        if st.session_state.uploaded_files:
            st.markdown(f"**📚 الملفات المرفوعة ({len(st.session_state.uploaded_files)}):**")
            for fname in st.session_state.uploaded_files:
                st.markdown(f"• 📄 `{fname}`")

            if st.button("🗑️ مسح قاعدة المعرفة", use_container_width=True):
                if st.session_state.knowledge_base:
                    st.session_state.knowledge_base.clear()
                st.session_state.knowledge_base = None
                st.session_state.uploaded_files = []
                st.success("تم مسح قاعدة المعرفة")
                st.rerun()

        st.markdown("---")

        # ===== الإحصائيات =====
        st.markdown('<div class="sidebar-title">📊 الإحصائيات</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(st.session_state.messages)}</div>
                <div class="stat-label">رسالة</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{len(st.session_state.uploaded_files)}</div>
                <div class="stat-label">ملف</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ===== أزرار التحكم =====
        if st.button("🗑️ مسح المحادثة", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.chatbot:
                st.session_state.chatbot.clear_history()
            st.rerun()

        if st.button("🔄 إعادة تعيين الكل", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        # معلومات التطوير
        st.markdown("""
        <hr style="border-color: rgba(255,255,255,0.1);">
        <div style="text-align: center; color: rgba(255,255,255,0.3); font-size: 0.75rem;">
            🤖 سفير v1.0<br>
            Python + Streamlit
        </div>
        """, unsafe_allow_html=True)


# ===== المنطقة الرئيسية =====
def render_main():
    """رسم المنطقة الرئيسية"""

    # العنوان
    st.markdown("""
    <div class="main-title">🤖 سفير</div>
    <div class="subtitle">مساعدك الذكي من جمعية سفراء الكتاب المدعوم بأحدث نماذج الذكاء الاصطناعي</div>
    """, unsafe_allow_html=True)

    # شريط الحالة
    model_name = st.session_state.selected_model
    has_docs = (
        st.session_state.knowledge_base is not None
        and st.session_state.knowledge_base.has_documents()
    )
    docs_count = len(st.session_state.uploaded_files)

    status_color = "#4CAF50" if st.session_state.api_validated else "#FF9800"
    status_text = "متصل" if st.session_state.api_validated else "غير متصل"
    kb_status = f"📚 {docs_count} ملف" if has_docs else "لا توجد ملفات"

    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 10px 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        direction: rtl;
    ">
        <span>🧠 <strong>{model_name}</strong></span>
        <span style="color: {status_color};">● {status_text}</span>
        <span>📁 {kb_status}</span>
        <span>💬 {len(st.session_state.messages)} رسالة</span>
    </div>
    """, unsafe_allow_html=True)

    # رسائل الترحيب إذا لم تكن هناك محادثة
    if not st.session_state.messages:
        render_welcome_screen()

    # عرض المحادثة
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # حقل الإدخال
    if prompt := st.chat_input(
        "💬 اكتب رسالتك هنا...",
        disabled=not st.session_state.api_key,
    ):
        if not st.session_state.api_key:
            st.error("⚠️ يرجى إدخال مفتاح API في الشريط الجانبي أولاً")
            return

        # إضافة رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # الحصول على الرد
        with st.chat_message("assistant", avatar="🤖"):
            response_placeholder = st.empty()
            full_response = ""

            try:
                chatbot = get_or_create_chatbot()

                # البحث في قاعدة المعرفة
                context_docs = None
                if (
                    st.session_state.use_knowledge_base
                    and st.session_state.knowledge_base is not None
                    and st.session_state.knowledge_base.has_documents()
                ):
                    context_docs = st.session_state.knowledge_base.search(prompt, k=4)

                # الحصول على الرد مع البث
                for chunk in chatbot.chat(prompt, context_docs=context_docs, stream=True):
                    full_response += chunk
                    response_placeholder.markdown(full_response + "▌")

                response_placeholder.markdown(full_response)

            except Exception as e:
                full_response = f"❌ حدث خطأ: {str(e)}"
                response_placeholder.error(full_response)

        # حفظ رد المساعد
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.total_messages += 1


def render_welcome_screen():
    """عرض شاشة الترحيب"""
    st.markdown("""
    <div style="
        text-align: center;
        padding: 40px 20px;
        background: rgba(255,255,255,0.03);
        border-radius: 20px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.08);
    ">
        <div style="font-size: 4rem; margin-bottom: 15px;">🤖</div>
        <h2 style="color: #667eea; margin-bottom: 10px;">مرحباً بك في سفير!</h2>
        <p style="color: rgba(255,255,255,0.6); max-width: 600px; margin: 0 auto 25px auto;">
            يمكنني مساعدتك في الإجابة على أسئلتك، تحليل الوثائق، وتقديم المعلومات بدقة واحترافية.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # بطاقات الميزات
    col1, col2, col3 = st.columns(3)
    features = [
        ("💬", "محادثة ذكية", "تحدث مع أحدث نماذج الذكاء الاصطناعي بطلاقة"),
        ("📁", "تحليل الملفات", "ارفع PDF أو Word أو CSV وتحدث عن محتواها"),
        ("🧠", "ذاكرة المحادثة", "يتذكر البوت سياق المحادثة كاملاً"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3], features):
        with col:
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.05);
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.1);
                height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
                <div style="font-weight: 700; color: #667eea; margin-bottom: 5px;">{title}</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5);">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # اقتراحات للبدء
    st.markdown("""
    <div style="margin-top: 25px; text-align: center;">
        <p style="color: rgba(255,255,255,0.5); font-size: 0.9rem;">💡 جرب أحد هذه الأسئلة للبدء:</p>
    </div>
    """, unsafe_allow_html=True)

    suggestions = [
        "ما هي أحدث تطورات الذكاء الاصطناعي؟",
        "ساعدني في كتابة بريد إلكتروني احترافي",
        "اشرح لي مفهوم التعلم الآلي ببساطة",
        "ما هي أفضل ممارسات برمجة Python؟",
    ]
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(f"💬 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()


# ===== نقطة الدخول الرئيسية =====
def main():
    init_session_state()
    render_sidebar()
    render_main()


if __name__ == "__main__":
    main()
