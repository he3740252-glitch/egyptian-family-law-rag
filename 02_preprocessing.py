"""
02_preprocessing.py
--------------------
الخطوة الثانية: تنظيف النص الخام (توحيد الأسطر، إزالة المسافات الزايدة)
قبل ما نقسمه لمواد في خطوة الـ chunking.
"""
import re
import os
import importlib.util


def _load_module(filename, modname):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def preprocess_text(raw_text: str) -> str:
    """تنظيف بسيط للنص العربي: توحيد فواصل الأسطر وإزالة التكرار الزائد"""
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def preprocess_documents(documents):
    """بياخد قائمة مستندات من 01_documents.py ويرجعهم بعد التنظيف"""
    cleaned = []
    for doc in documents:
        cleaned.append({
            "source": doc["source"],
            "text": preprocess_text(doc["text"]),
        })
    return cleaned


if __name__ == "__main__":
    documents_mod = _load_module("01_documents.py", "documents_mod")
    docs = documents_mod.load_documents()
    cleaned_docs = preprocess_documents(docs)
    for d in cleaned_docs:
        print(f"{d['source']}: بعد التنظيف {len(d['text'])} حرف")
