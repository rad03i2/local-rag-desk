# Local RAG Desk

A privacy-first, dependency-free local retrieval workspace for indexing text/Markdown documents and finding source-grounded context with BM25 ranking.

> **Status:** functional CLI and Python library. Retrieval is local and deterministic; this project does not pretend to generate AI answers without a configured model.

## English

### Why it exists
Local RAG Desk provides the retrieval half of a RAG workflow without uploading documents or requiring API keys. It is useful for notes, documentation, research exports, and other UTF-8 text collections where you need fast, inspectable source passages.

### Features
- Recursively ingest `.txt` and `.md` files.
- Chunk documents with configurable size and overlap.
- Unicode-aware tokenization that works with English and Arabic text.
- BM25 ranking with document-frequency statistics stored in a portable JSON index.
- Search with scores, source paths, and line ranges.
- `context` output suitable for pasting into an LLM prompt while retaining citations.
- JSON output for automation.
- No network calls, telemetry, API keys, database, or runtime dependencies.
- Safe indexing: symbolic links are skipped and files outside the selected root are never followed.

### Preview
```text
$ local-rag index ./docs -o .rag/index.json
Indexed 12 chunks from 4 files -> .rag/index.json

$ local-rag search "water treatment" -i .rag/index.json -k 2
1. docs/process.md:18-29  score=2.841
   ...coagulation and filtration are common water treatment stages...
```

### Requirements & installation
Python 3.10+.

```bash
python -m pip install -e .
local-rag --version
```

No `.env` file is required.

### Usage
```bash
# Build/rebuild an index
local-rag index ./documents -o .rag/index.json --chunk-size 180 --overlap 30

# Human-readable search
local-rag search "groundwater contamination" -i .rag/index.json -k 5

# Machine-readable search
local-rag search "معالجة المياه" -i .rag/index.json --json

# Prompt-ready source context
local-rag context "activated sludge" -i .rag/index.json -k 3

# Validate an existing index
local-rag validate -i .rag/index.json
```

Python API:
```python
from local_rag_desk import build_index, load_index, search

build_index("documents", ".rag/index.json")
index = load_index(".rag/index.json")
for hit in search(index, "water quality", limit=3):
    print(hit.source, hit.start_line, hit.score)
```

### Configuration
`--chunk-size` and `--overlap` are measured in tokens. Chunk size must be at least 20; overlap must be smaller than chunk size. The index stores relative source paths, text chunks, token counts, and corpus statistics. Re-run `index` after source files change.

### Project structure
```text
src/local_rag_desk/   library, BM25 engine and CLI
tests/                automated unit/integration tests
examples/             small bilingual sample corpus
.github/workflows/    CI
```

### Testing
```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```
CI runs these checks on Python 3.10, 3.12 and 3.13 on Ubuntu, Windows and macOS.

### Security & privacy
All processing is local. The tool does not execute document content, follow symlinks, make network requests, or collect telemetry. Treat generated indexes as sensitive when source documents are sensitive because chunk text is stored verbatim. See `SECURITY.md`.

### Limitations
This is lexical retrieval, not embedding/vector semantic search. It indexes UTF-8 plain text and Markdown only, not PDF/DOCX/OCR. It does not generate answers or verify factual truth. BM25 quality depends on the wording shared between the query and documents. The JSON index is optimized for portability and modest personal collections rather than millions of chunks.

### Optional roadmap
Optional future work may add pluggable local embeddings, additional document parsers, and an opt-in local-model answer adapter without changing the offline-first default.

### Contributing
See `CONTRIBUTING.md`. Contributions should preserve safe local defaults and include tests for behavioral changes.

### License
MIT — see `LICENSE`.

### Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

## العربية

### نظرة عامة
**Local RAG Desk** مساحة استرجاع محلية تحافظ على الخصوصية، تفهرس ملفات النص وMarkdown ثم تستخرج المقاطع الأكثر صلة باستخدام ترتيب BM25. تعمل دون إرسال المستندات إلى أي خدمة خارجية ودون مفاتيح API.

### لماذا المشروع؟
يوفر المشروع جزء الاسترجاع من منظومة RAG بصورة بسيطة وقابلة للفحص. يفيد للملاحظات والوثائق والبحوث والمجموعات النصية التي تحتاج منها مقاطع موثقة بالمصدر قبل استخدامها مع نموذج لغوي.

### الميزات
- فهرسة متكررة لملفات `.txt` و`.md`.
- تقسيم المستندات إلى مقاطع بحجم وتداخل قابلين للضبط.
- تحليل Unicode يدعم النص العربي والإنجليزي.
- ترتيب BM25 وإحصاءات corpus محفوظة في ملف JSON محمول.
- إظهار المسار وأرقام الأسطر والدرجة لكل نتيجة.
- أمر `context` لإنشاء سياق يحتفظ بإشارات المصدر.
- إخراج JSON للأتمتة.
- لا شبكة ولا telemetry ولا مفاتيح سرية ولا اعتماديات تشغيل خارجية.
- تجاهل الروابط الرمزية وعدم الخروج من جذر المجلد المحدد.

### التثبيت
يتطلب Python 3.10 أو أحدث:
```bash
python -m pip install -e .
local-rag --version
```

### الاستخدام
```bash
local-rag index ./documents -o .rag/index.json --chunk-size 180 --overlap 30
local-rag search "معالجة المياه" -i .rag/index.json -k 5
local-rag search "تلوث المياه الجوفية" -i .rag/index.json --json
local-rag context "الحمأة المنشطة" -i .rag/index.json -k 3
local-rag validate -i .rag/index.json
```
يمكن كذلك استخدام دوال `build_index` و`load_index` و`search` مباشرة من Python كما في المثال الإنجليزي أعلاه.

### الإعداد
يقاس `chunk-size` و`overlap` بعدد الكلمات/الرموز المحللة. يجب ألا يقل حجم المقطع عن 20 وأن يكون التداخل أصغر منه. بعد تعديل الملفات الأصلية أعد بناء الفهرس.

### بنية المشروع
المصدر داخل `src/local_rag_desk`، والاختبارات داخل `tests`، والعينات داخل `examples`، وإعداد CI داخل `.github/workflows`.

### الاختبارات
```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
```
ويشغّل CI هذه الفحوصات على عدة أنظمة وإصدارات Python.

### الأمان والخصوصية
المعالجة محلية بالكامل، ولا ينفذ البرنامج محتوى الملفات أو يتبع الروابط الرمزية أو يجري اتصالات شبكية. ملف الفهرس يحتوي نص المقاطع نفسه؛ لذلك يجب حمايته إذا كانت المصادر حساسة. راجع `SECURITY.md`.

### القيود
البحث معجمي وليس بحث embeddings دلاليًا. يدعم UTF-8 Text وMarkdown فقط، ولا يقرأ PDF أو DOCX ولا يجري OCR. لا يولد إجابات ولا يضمن صحة الحقائق. ملف JSON مناسب للمجموعات الشخصية والمتوسطة وليس لملايين المقاطع.

### تطوير اختياري
يمكن مستقبلًا إضافة embeddings محلية اختيارية، وقارئات صيغ إضافية، ومحول اختياري لنموذج محلي مع الحفاظ على الوضع المحلي الافتراضي.

### المساهمة والترخيص
راجع `CONTRIBUTING.md`. المشروع مرخص برخصة MIT الموجودة في `LICENSE`.

### المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
