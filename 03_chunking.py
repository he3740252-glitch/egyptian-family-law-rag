"""
03_chunking.py
---------------
الخطوة الثالثة: تقسيم النص المنظف لمواد قانونية (chunks).
كل "مادة" في القانون بتتحول لـ chunk منفصل عشان يبقى أدق في الاسترجاع.
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


# بيلقط "مادة 1:" أو "مادة رقم 1" أو "مادة (1)" مع لواحق زي "مكررا"/"مكررا ثانيا"
ARTICLE_PATTERN = re.compile(
    r"(مادة\s*(?:رقم\s*)?\(?\d+\)?(?:\s*مكرر[ًا]?"
    r"(?:\s*(?:ثاني[ةا]|ثالث[ةا]|رابع[ةا])?)?)?\s*[:\.\-]?)",
    re.UNICODE,
)


def chunk_text(text: str, source: str):
    parts = ARTICLE_PATTERN.split(text)
    chunks = []
    current_header = None
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if ARTICLE_PATTERN.fullmatch(part):
            current_header = part
        else:
            if current_header:
                num_match = re.search(r"\d+", current_header)
                article_num = num_match.group() if num_match else str(len(chunks) + 1)
                clean_source = source.replace(".txt", "")
                chunks.append({
                    "id": f"{clean_source}_art{article_num}_{len(chunks)}",
                    "source": source,
                    "article_number": article_num,
                    "text": f"{current_header} {part}".strip(),
                })
                current_header = None
            else:
                if len(part) > 30:
                    clean_source = source.replace(".txt", "")
                    chunks.append({
                        "id": f"{clean_source}_preamble_{len(chunks)}",
                        "source": source,
                        "article_number": "0",
                        "text": part,
                    })
    return chunks


def chunk_documents(documents):
    """بياخد قائمة مستندات منظفة من 02_preprocessing.py ويرجع كل المواد مقسمة"""
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_text(doc["text"], doc["source"]))
    return all_chunks


if __name__ == "__main__":
    documents_mod = _load_module("01_documents.py", "documents_mod")
    preprocessing_mod = _load_module("02_preprocessing.py", "preprocessing_mod")

    docs = documents_mod.load_documents()
    cleaned_docs = preprocessing_mod.preprocess_documents(docs)
    chunks = chunk_documents(cleaned_docs)

    print(f"تم استخراج {len(chunks)} مادة/جزء")
    for c in chunks[:5]:
        print(f"- {c['id']}: {c['text'][:70]}...")
