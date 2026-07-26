"""
04_vector_representation.py
-----------------------------
الخطوة الرابعة: تحويل النصوص لمتجهات (embeddings) عشان نقدر نقيس التشابه بينهم.
بنستخدم موديل multilingual مجاني شغال محلياً (مش محتاج API key).
"""
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts):
    """بيرجع embeddings كـ list of lists (الصيغة اللي محتاجاها ChromaDB)"""
    model = get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return embeddings.tolist()


if __name__ == "__main__":
    sample = ["هل يحق للزوجة طلب الخلع؟", "نفقة الأولاد على الأب"]
    vectors = embed_texts(sample)
    print(f"تم عمل embeddings لـ {len(sample)} جملة، أبعاد كل متجه: {len(vectors[0])}")
