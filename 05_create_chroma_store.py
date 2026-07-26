"""
05_create_chroma_store.py
----------------------------
الخطوة الخامسة: بناء الـ Vector Store (ChromaDB) وتخزين المواد فيه
مع الـ embeddings بتاعتهم، عشان نقدر نسترجعهم بعدين بسرعة.
"""
import os
import importlib.util
import chromadb

CHROMA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
COLLECTION_NAME = "family_law"


def _load_module(filename, modname):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


def build_store():
    documents_mod = _load_module("01_documents.py", "documents_mod")
    preprocessing_mod = _load_module("02_preprocessing.py", "preprocessing_mod")
    chunking_mod = _load_module("03_chunking.py", "chunking_mod")
    vector_mod = _load_module("04_vector_representation.py", "vector_mod")

    docs = documents_mod.load_documents()
    cleaned_docs = preprocessing_mod.preprocess_documents(docs)
    chunks = chunking_mod.chunk_documents(cleaned_docs)

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [
        {"source": c["source"], "article_number": c["article_number"]}
        for c in chunks
    ]

    print(f"بنعمل embeddings لـ {len(texts)} مادة ...")
    embeddings = vector_mod.embed_texts(texts)

    client = get_chroma_client()
    # نمسح الكولكشن القديم لو موجود عشان نبني نسخة جديدة نضيفة كل مرة
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)

    collection.add(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)

    print(f"تم تخزين {len(chunks)} مادة في ChromaDB بمجلد: {CHROMA_DIR}")
    return collection


if __name__ == "__main__":
    build_store()
