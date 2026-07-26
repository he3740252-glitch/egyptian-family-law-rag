"""
07_prompting.py
------------------
الخطوة السابعة: بناء الـ prompt من السياق المسترجع، واستدعاء الـ LLM
عبر OpenRouter عشان يصيغ إجابة طبيعية مبنية على المواد بس.

مهم: متكتبيش مفتاح API حقيقي هنا. المفتاح بييجي من متغير بيئة
OPENROUTER_API_KEY أو من Streamlit secrets وقت الديبلوي (شوفي streamlit_app.py)
"""
import os
from openai import OpenAI

# فاضيين افتراضياً - بيتعبّوا من env var أو من st.secrets
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = (
    "أنت مساعد قانوني متخصص في قانون الأسرة المصري. "
    "أجب على سؤال المستخدم بالاعتماد فقط على المواد القانونية المرفقة في السياق أدناه. "
    "لو السياق مش كافي للإجابة، قولي ذلك صراحة ولا تخترعي معلومات من عندك. "
    "لازم تذكري رقم المادة ومصدرها اللي استندتي عليه في كل جزء من إجابتك."
)


def build_prompt(query: str, context_chunks):
    context_text = "\n\n".join(
        f"[مصدر: {c['source']} - مادة {c['article_number']}]\n{c['text']}"
        for c in context_chunks
    )
    user_prompt = (
        f"السياق (مواد قانونية مسترجعة):\n{context_text}\n\n"
        f"سؤال المستخدم: {query}\n\n"
        "جاوبي بالاعتماد على السياق أعلاه فقط، واذكري رقم المادة مع كل معلومة تستخدميها."
    )
    return user_prompt


def generate_answer(query: str, context_chunks):
    if not OPENROUTER_API_KEY:
        return (
            "⚠️ مفيش OPENROUTER_API_KEY متظبط. "
            "لو شغالة محلياً حطيه كـ متغير بيئة، ولو ديبلوي على Streamlit حطيه في Secrets."
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    user_prompt = build_prompt(query, context_chunks)

    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    import importlib.util

    def _load_module(filename, modname):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        spec = importlib.util.spec_from_file_location(modname, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    retrieve_mod = _load_module("06_retrieve_context.py", "retrieve_mod")
    q = "هل يحق للزوجة طلب الخلع؟"
    context = retrieve_mod.retrieve_context(q)
    print(generate_answer(q, context))
