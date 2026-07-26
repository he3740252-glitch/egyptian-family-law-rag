"""
06_retrieve_context.py
-------------------------
الخطوة السادسة: استرجاع أقرب المواد القانونية (context) لسؤال معين
من الـ ChromaDB اللي بنيناه في الخطوة السابقة.

تحديث: بنستخدم Hybrid Search (بحث هجين) - بنجمع بين:
1. البحث بالمعنى (semantic search عبر embeddings)
2. البحث بالكلمة المفتاحية الحرفية (keyword matching)
عشان لو موديل الـ embeddings الصغير مقصّر في مصطلح قانوني معين
(زي "الخلع")، التطابق الحرفي للكلمة يعوض الفرق ويطلع المادة الصح.
"""
import os
import re
import importlib.util
import chromadb

CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
COLLECTION_NAME = "family_law"

# كلمات وقفة بسيطة بنتجاهلها في مطابقة الكلمات المفتاحية
STOPWORDS = {
    "هل", "من", "في", "على", "الى", "إلى", "أن", "ان", "التي", "الذي",
    "و", "أو", "او", "ما", "لا", "لم", "يحق", "حق", "بشكل", "عن",
}


def _load_module(filename, modname):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(COLLECTION_NAME)


def _keyword_score(query: str, text: str) -> int:
    """بيحسب عدد كلمات السؤال (غير كلمات الوقف) اللي ظهرت حرفياً في النص"""
    # نستخدم مدى حروف عربية بس (بدون علامات ترقيم زي "؟" أو تشكيل) عشان مايتلزقش
    # بالكلمة ويبوظ المطابقة الحرفية
    words = [w for w in re.findall(r"[\u0621-\u064A]+", query) if w not in STOPWORDS and len(w) > 2]
    score = 0
    for w in words:
        if w in text:
            score += 1
    return score


def retrieve_context(query: str, top_k: int = 3):
    vector_mod = _load_module("04_vector_representation.py", "vector_mod")
    query_embedding = vector_mod.embed_texts([query])[0]

    collection = get_collection()
    total = collection.count()

    # بنجيب كل المواد مرتبة بالمعنى (semantic) عشان نعيد ترتيبها هجينياً بعد كده
    results = collection.query(query_embeddings=[query_embedding], n_results=total)

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    candidates = []
    max_dist = max(dists) if dists else 1.0
    for text, meta, dist in zip(docs, metas, dists):
        # نطبع درجة التشابه الدلالي بين صفر وواحد (كل ما قلت الـ distance زادت الدرجة)
        semantic_score = 1 - (dist / max_dist if max_dist else 0)
        keyword_score = _keyword_score(query, text)
        # بونص كبير لكل كلمة مفتاحية متطابقة حرفياً، عشان يتغلب على ضعف الـ embeddings المحتمل
        combined_score = semantic_score + (keyword_score * 0.5)
        candidates.append({
            "text": text,
            "source": meta.get("source"),
            "article_number": meta.get("article_number"),
            "distance": dist,
            "keyword_score": keyword_score,
            "combined_score": combined_score,
        })

    candidates.sort(key=lambda c: c["combined_score"], reverse=True)
    return candidates[:top_k]


if __name__ == "__main__":
    results = retrieve_context("هل يحق للزوجة طلب الخلع؟")
    for r in results:
        print(
            f"[{r['source']} - مادة {r['article_number']}] "
            f"(distance={r['distance']:.3f}, keyword_score={r['keyword_score']}, "
            f"combined={r['combined_score']:.3f})"
        )
        print(r["text"][:150])
        print()
