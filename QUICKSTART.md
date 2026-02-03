# 🚀 Quick Start Guide

Get your Nebari RAG agent running in 5 minutes!

## ✅ Setup Steps

### Step 1: Environment Setup (2 minutes)

**Option A: Conda (Recommended)**

```bash
cd /path/to/nebari-docs-rag-demo

# Create conda environment
conda env create -f environment.yml
conda activate nebari-rag
```

**Option B: Pip**

```bash
cd /path/to/nebari-docs-rag-demo

# Create virtual environment with Python 3.11+
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 minute)

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-...
NEBARI_DOCS_PATH=/path/to/nebari-docs
DEMO_USERNAME=demo
DEMO_PASSWORD=your_password
```

**Get API Key**: https://console.anthropic.com/

### Step 3: Ingest Documentation (2 minutes)

```bash
python ingest_docs.py --docs-path /path/to/nebari-docs

# Expected output:
# 📚 Found 65 files (64 docs + 1 homepage)
# ✂️  Created ~730 chunks
# ✨ Successfully ingested to ChromaDB
```

### Step 4: Launch App (10 seconds)

```bash
streamlit run app.py
```

Opens at `http://localhost:8501` 🎉

**Login with credentials from `.env` file**

---

## 🧪 Quick Test

Try these questions:

1. **"Why should we use Nebari?"**
   - ✅ Should return homepage content (GitOps, Collaboration, Dask features)
   - ✅ Sources should show `index.jsx` (website)
   - ✅ Tests homepage content boosting for "why" questions

2. **"How do I deploy Nebari on AWS?"**
   - ✅ Should return deployment guide
   - ✅ Sources should show `how-tos/` category

3. **"What is Nebari?"**
   - ✅ Should explain Nebari's purpose
   - ✅ Sources should show `get-started/` category

4. **Test Features:**
   - 👍👎 Rate an answer with feedback buttons
   - 📊 Check sidebar stats update immediately
   - 📥 Export conversation as markdown or zip
   - 🔄 Refresh page - should stay logged in on deployed version (cookie auth)

---

## 🎯 Key Features to Demo

### Core RAG Functionality

- **Semantic Chunking**: By markdown headers (preserves structure)
- **Homepage Content**: "Why Choose Nebari?" with relevance boosting
- **Query Expansion**: "why" questions → multiple search variations
- **Source Citations**: With relevance scores and categories

### Advanced Features (New!)

- **🔐 Cookie Auth**: 7-day persistent login (HTTPS only)
- **👍👎 Feedback**: Rate answer quality
- **💰 Cost Tracking**: Real-time token usage + cost (Claude Sonnet 4 pricing)
- **⏱️ Performance**: Response time, retrieval time, LLM time
- **📊 Retrieval Quality**: Relevance scores for each source
- **📥 Export**: Markdown or Zip+Images with downloaded images
- **🔄 Real-Time Stats**: Sidebar updates immediately

---

## 📊 Key Metrics

| Metric                     | Value      |
| -------------------------- | ---------- |
| Documents Indexed          | 65 (64 docs + homepage) |
| Vector Chunks              | ~730       |
| Average Query Time         | <10 seconds |
| Retrieval Time             | <1 second  |
| LLM Time                   | ~8 seconds |
| Retrieval Accuracy (Top-5) | >85% (>90% for "why") |
| Database Size              | ~15 MB     |
| Cost per Query             | ~$0.01-0.02 |

**Model**: Claude Sonnet 4 (2025-05-14)
**Embeddings**: all-MiniLM-L6-v2 (384 dims, local)

---

## 🚢 Deploy to Streamlit Cloud

```bash
# 1. Commit vector database
git add chroma_db/
git commit -m "Add pre-built vector database"
git push

# 2. Go to share.streamlit.io
# 3. New app → Select repo → Main file: app.py
# 4. Add secrets:
#    ANTHROPIC_API_KEY = "sk-ant-..."
#    DEMO_USERNAME = "your_username"
#    DEMO_PASSWORD = "your_password"
# 5. Deploy!
```

**Test Cookie Auth**: Login → Refresh page → Should stay logged in ✅

---

## ⚡ Troubleshooting

### "Collection not found" error

```bash
python ingest_docs.py --docs-path /path/to/nebari-docs
```

### "ANTHROPIC_API_KEY not found"

Check `.env` file has:

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### Cookie not persisting on localhost

**Expected behavior**: Cookies only work on HTTPS (Streamlit Cloud), not `localhost`.

### "Why should we use Nebari?" returns wrong answer

Re-run ingestion to ensure homepage content is indexed:

```bash
python ingest_docs.py --force-refresh
```

---

## 🎬 Interview Demo Tips

### Opening (30 seconds)

> "I built a production-ready RAG agent for Nebari documentation with Claude Sonnet 4, ChromaDB, and Streamlit. It includes advanced features like cookie auth, feedback system, cost tracking, and export with image downloads."

### Demo Flow (5 minutes)

1. **Show Login** (30 sec) - Cookie-based auth with 7-day persistence
2. **Ask "Why Nebari?"** (1 min) - Highlight homepage content retrieval
3. **Show Feedback** (30 sec) - Rate answer, show stats update immediately
4. **Export Conversation** (1 min) - Download as zip with images
5. **Code Walkthrough** (2 min) - Show query expansion, homepage boosting, cost tracking

### Key Talking Points

**Technical:**
- Semantic chunking by headers (not arbitrary character splits)
- Query expansion for "why" questions (3x retrieval with boosting)
- Homepage content relevance boosting (0.6x distance = 40% better ranking)
- Real-time stats with `st.rerun()` for immediate updates

**Production:**
- Cookie auth with SHA-256 hashing (7-day expiration)
- Pre-built vector DB (no cold start on Streamlit Cloud)
- Cost tracking ($3/$15 per million tokens for Sonnet 4)
- Export with image downloads (httpx + in-memory zip)

---

## ✨ You're Ready!

- ✅ Production-ready code
- ✅ Advanced features (auth, feedback, export, stats)
- ✅ Comprehensive documentation
- ✅ Working demo
- ✅ Clear metrics

**Good luck!** 🚀
