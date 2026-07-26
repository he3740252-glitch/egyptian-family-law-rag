"""
01_documents.py
----------------
الخطوة الأولى في السلسلة: تحميل المستندات الخام (نصوص قانون الأسرة)
من مجلد data/. كل ملف .txt جوه data/ بيتحمل كمستند منفصل.
"""
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_documents(data_dir: str = DATA_DIR):
    """
    بيقرأ كل ملفات .txt في data_dir ويرجعهم كقائمة مستندات.
    كل مستند عبارة عن: {"source": اسم الملف, "text": المحتوى الخام}
    """
    documents = []
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".txt"):
            path = os.path.join(data_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({"source": filename, "text": text})
    return documents


if __name__ == "__main__":
    docs = load_documents()
    print(f"تم تحميل {len(docs)} مستند:")
    for d in docs:
        print(f" - {d['source']} ({len(d['text'])} حرف)")
