"""
streamlit_app.py
-----------------
واجهة Streamlit للمساعد القانوني - قانون الأسرة المصري (RAG)
بتربط كل الخطوات (retrieval + prompting) في تطبيق واحد.
"""
import os
import importlib.util
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_module(filename, modname):
    path = os.path.join(BASE_DIR, filename)
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


retrieve_mod = load_module("06_retrieve_context.py", "retrieve_mod")
prompting_mod = load_module("07_prompting.py", "prompting_mod")

# --- قراءة مفتاح OpenRouter من Streamlit secrets وقت الديبلوي ---
try:
    if not prompting_mod.OPENROUTER_API_KEY:
        prompting_mod.OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    prompting_mod.OPENROUTER_MODEL = st.secrets.get(
        "OPENROUTER_MODEL", prompting_mod.OPENROUTER_MODEL
    )
except Exception:
    pass

st.set_page_config(page_title="مساعد قانون الأسرة", page_icon="⚖️")
st.title("⚖️ مساعد قانون الأسرة المصري (RAG)")
st.caption(
    "الإجابات مبنية على نصوص قانون الأحوال الشخصية ومحاكم الأسرة "
    "(قوانين 25/1920، 25/1929، 10/2004)"
)

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input(
    "اسألي سؤالك عن قانون الأسرة:",
    placeholder="مثال: هل يحق للزوجة طلب الخلع؟",
)

top_k = st.sidebar.slider("عدد المواد المسترجعة (top_k)", 1, 5, 3)

if st.button("إسأل") and query.strip():
    with st.spinner("بندور على المواد القانونية المتعلقة بسؤالك..."):
        context_chunks = retrieve_mod.retrieve_context(query, top_k=top_k)

    with st.spinner("بنصيغ الإجابة..."):
        answer = prompting_mod.generate_answer(query, context_chunks)

    st.session_state.history.append(
        {"query": query, "answer": answer, "context": context_chunks}
    )

for item in reversed(st.session_state.history):
    st.markdown(f"### ❓ {item['query']}")
    st.markdown(item["answer"])
    with st.expander("📚 المواد القانونية المستخدمة (المصدر)"):
        for c in item["context"]:
            st.markdown(f"**{c['source']} - مادة {c['article_number']}**")
            st.write(c["text"])
            st.divider()
