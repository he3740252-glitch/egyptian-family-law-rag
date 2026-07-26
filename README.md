# مساعد قانون الأسرة المصري - مشروع RAG

## السلسلة (Pipeline)
```
data/family_law.txt
   -> 01_documents.py         (تحميل المستندات)
   -> 02_preprocessing.py     (تنظيف النص)
   -> 03_chunking.py          (تقسيم لمواد قانونية)
   -> 04_vector_representation.py  (embeddings)
   -> 05_create_chroma_store.py   (تخزين في ChromaDB)
   -> 06_retrieve_context.py      (استرجاع أقرب المواد)
   -> 07_prompting.py             (بناء الـ prompt + استدعاء LLM عبر OpenRouter)
   -> streamlit_app.py            (الواجهة)
```

## البيانات
`data/family_law.txt` فيه النص الكامل لـ 3 قوانين: 25/1920 (النفقة)، 25/1929 (الطلاق والتطليق
والحضانة)، 10/2004 (محاكم الأسرة). 60 مادة إجمالاً.

---

## 1) التشغيل محلياً

```bash
pip install -r requirements.txt
python 01_documents.py        # اختباري - يعرض عدد المستندات
python 03_chunking.py         # اختباري - يعرض عدد المواد المستخرجة (يشغل 01+02 تلقائياً)
python 05_create_chroma_store.py   # بيبني الـ vector store (هيحمل موديل embeddings أول مرة)
```

بعد كده، عشان تجربي بدون Streamlit:
```bash
set OPENROUTER_API_KEY=sk-or-v1-...
python 07_prompting.py
```
(على PowerShell: `$env:OPENROUTER_API_KEY="sk-or-v1-..."`)

وأخيراً شغّلي الواجهة:
```bash
streamlit run streamlit_app.py
```

---

## 2) مفتاح OpenRouter (مجاني للتسجيل)
1. سجّلي في https://openrouter.ai
2. اعملي API key من https://openrouter.ai/keys
3. **متكتبيهوش أبداً جوه أي ملف Python** - استخدمي متغير بيئة محلياً، أو Streamlit secrets وقت الديبلوي.

---

## 3) رفع المشروع على GitHub
```bash
git init
git add .
git commit -m "Family law RAG project"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```
⚠️ **قبل الـ push** تأكدي إن:
- مفيش ملف `.streamlit/secrets.toml` حقيقي في المشروع (بس `secrets.toml.example` مسموح)
- مفيش `.env` فيه مفتاح حقيقي
- ملف `.gitignore` موجود (متضاف بالفعل ومعمول عليه إعداد لاستبعاد المفاتيح والـ chroma_db)

---

## 4) الديبلوي على Streamlit Cloud
1. روحي على https://share.streamlit.io وسجلي دخول بحساب GitHub
2. New app → اختاري الـ repo بتاعك → الملف الرئيسي: `streamlit_app.py`
3. بعد ما يتعمل الـ app، من فوق دوسي **Manage app** → **Settings** → **Secrets**
4. حطي بالظبط:
```toml
OPENROUTER_API_KEY = "sk-or-v1-...المفتاح الحقيقي بتاعك..."
OPENROUTER_MODEL = "openai/gpt-4o-mini"
```
5. احفظي، والتطبيق هيعيد التشغيل تلقائياً ويقرأ المفتاح من الـ secrets.

---

## 5) الـ Checklist النهائي
- [x] كل ملفات الـ pipeline المطلوبة موجودة (01 → 07 + streamlit_app.py)
- [x] requirements.txt موجود
- [ ] اتأكدي إن مفتاحك الحقيقي مش موجود في الـ ZIP ولا الـ GitHub repo
- [ ] Secrets متظبطة بصيغة TOML صحيحة على Streamlit Cloud
- [ ] التطبيق شغال بنجاح على الرابط المنشور
- [ ] الإجابة فعلاً بتستخدم الـ context المسترجع
- [ ] الإجابة بتذكر مصدر/رقم المادة (citation)
