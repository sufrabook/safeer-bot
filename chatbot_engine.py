"""
نواة الشات بوت - التواصل مع نماذج الذكاء الاصطناعي
"""

import os
from typing import List, Dict, Optional, Generator
from openai import OpenAI
from config import AVAILABLE_MODELS, MAX_HISTORY_MESSAGES, DEFAULT_SYSTEM_PROMPT


class ChatbotEngine:
    """محرك الشات بوت الرئيسي"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "GPT-4o Mini",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.conversation_history: List[Dict] = []
        self._init_client()

    def _init_client(self):
        """تهيئة عميل API"""
        model_config = AVAILABLE_MODELS.get(self.model_name, {})
        provider = model_config.get("provider", "openai")
        base_url = model_config.get("base_url")

        if provider == "anthropic":
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=self.api_key)
                self.client = None
            except ImportError:
                self.client = OpenAI(api_key=self.api_key)
                self.anthropic_client = None
        else:
            kwargs = {"api_key": self.api_key}
            if base_url:
                kwargs["base_url"] = base_url
            self.client = OpenAI(**kwargs)
            self.anthropic_client = None

    def update_model(self, model_name: str, api_key: str = None):
        """تحديث النموذج المستخدم"""
        self.model_name = model_name
        if api_key:
            self.api_key = api_key
        self._init_client()

    def update_system_prompt(self, system_prompt: str):
        """تحديث الـ System Prompt"""
        self.system_prompt = system_prompt

    def clear_history(self):
        """مسح سجل المحادثة"""
        self.conversation_history = []

    def _build_messages(
        self,
        user_message: str,
        context_docs: Optional[List] = None,
    ) -> List[Dict]:
        """بناء قائمة الرسائل للإرسال"""
        messages = [{"role": "system", "content": self.system_prompt}]

        # إضافة السياق من الوثائق إذا وجد
        if context_docs:
            context_text = "\n\n".join([
                f"[مصدر: {doc.metadata.get('source', 'غير معروف')}]\n{doc.page_content}"
                for doc in context_docs
            ])
            context_message = (
                f"فيما يلي معلومات من الوثائق المرفوعة قد تساعدك في الإجابة:\n\n"
                f"{context_text}\n\n"
                f"استخدم هذه المعلومات للإجابة على سؤال المستخدم إذا كانت ذات صلة."
            )
            messages.append({"role": "system", "content": context_message})

        # إضافة سجل المحادثة (آخر N رسالة)
        history = self.conversation_history[-MAX_HISTORY_MESSAGES:]
        messages.extend(history)

        # إضافة رسالة المستخدم الحالية
        messages.append({"role": "user", "content": user_message})

        return messages

    def chat(
        self,
        user_message: str,
        context_docs: Optional[List] = None,
        stream: bool = True,
    ) -> Generator[str, None, None]:
        """إرسال رسالة والحصول على رد (مع دعم البث)"""
        messages = self._build_messages(user_message, context_docs)
        model_config = AVAILABLE_MODELS.get(self.model_name, {})
        model_id = model_config.get("model_id", "gpt-4o-mini")
        provider = model_config.get("provider", "openai")

        full_response = ""

        try:
            if provider == "anthropic" and self.anthropic_client:
                # Claude API
                anthropic_messages = [m for m in messages if m["role"] != "system"]
                system_content = " ".join([
                    m["content"] for m in messages if m["role"] == "system"
                ])
                with self.anthropic_client.messages.stream(
                    model=model_id,
                    max_tokens=4096,
                    system=system_content,
                    messages=anthropic_messages,
                ) as stream_obj:
                    for text in stream_obj.text_stream:
                        full_response += text
                        yield text
            else:
                # OpenAI / Gemini API
                if stream:
                    response = self.client.chat.completions.create(
                        model=model_id,
                        messages=messages,
                        stream=True,
                        max_tokens=4096,
                        temperature=0.7,
                    )
                    for chunk in response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            text = chunk.choices[0].delta.content
                            full_response += text
                            yield text
                else:
                    response = self.client.chat.completions.create(
                        model=model_id,
                        messages=messages,
                        stream=False,
                        max_tokens=4096,
                        temperature=0.7,
                    )
                    full_response = response.choices[0].message.content
                    yield full_response

        except Exception as e:
            error_msg = f"❌ خطأ في الاتصال بالنموذج: {str(e)}"
            yield error_msg
            full_response = error_msg

        # حفظ المحادثة في السجل
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": full_response})

    def validate_api_key(self) -> tuple[bool, str]:
        """التحقق من صحة مفتاح API"""
        try:
            model_config = AVAILABLE_MODELS.get(self.model_name, {})
            provider = model_config.get("provider", "openai")

            if provider == "anthropic":
                try:
                    import anthropic
                    client = anthropic.Anthropic(api_key=self.api_key)
                    client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "Hi"}],
                    )
                    return True, "مفتاح API صحيح ✅"
                except Exception as e:
                    return False, f"مفتاح API غير صحيح: {str(e)}"
            else:
                base_url = model_config.get("base_url")
                kwargs = {"api_key": self.api_key}
                if base_url:
                    kwargs["base_url"] = base_url
                client = OpenAI(**kwargs)
                models = client.models.list()
                return True, "مفتاح API صحيح ✅"
        except Exception as e:
            return False, f"مفتاح API غير صحيح: {str(e)}"
