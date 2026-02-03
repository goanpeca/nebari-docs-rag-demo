# 🌌 Nebari Documentation Assistant

A production-ready RAG (Retrieval Augmented Generation) chatbot that answers questions about [Nebari](https://www.nebari.dev/) using the official documentation. Built with Streamlit, ChromaDB, and Anthropic Claude Sonnet 4.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**🔗 Live Demo**: [nebari-docs-rag.streamlit.app](https://nebari-docs-rag.streamlit.app)

## 🎯 Features

### Core Functionality
- **Semantic Search**: Retrieves relevant documentation using vector embeddings (all-MiniLM-L6-v2)
- **Intelligent Chunking**: Preserves document structure by splitting at markdown headers
- **Homepage Content**: Includes "Why Choose Nebari?" marketing content with relevance boosting
- **Source Citations**: Every answer includes clickable source references with relevance scores
- **Clean UI**: Dark-themed chat interface with Nebari branding

### Advanced Features
- **🔐 Cookie Authentication**: 7-day persistent login (works on HTTPS/deployed, not localhost)
- **👍👎 Feedback System**: Rate answer quality with thumbs up/down buttons
- **💰 Cost Tracking**: Real-time token usage and cost monitoring (Claude Sonnet 4 pricing)
- **⏱️ Performance Metrics**: Track response time, retrieval time, and LLM time
- **📊 Retrieval Quality**: View relevance scores for each source document
- **📥 Export Options**:
  - **Markdown**: Simple text export with metadata
  - **Zip+Images**: Full export with downloaded images and folder structure
- **🔄 Real-Time Stats**: Sidebar metrics update immediately after each question

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Streamlit Web UI                      │
│  Chat + Login + Feedback + Export + Stats      │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│          RAG Agent (agent.py)                   │
│  Query Expansion → Retrieval → Answer          │
│  - Homepage content boosting                    │
│  - Token & cost tracking                        │
│  - Timing measurements                          │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│       ChromaDB Vector Store                     │
│   ~730 chunks from 64+ docs + homepage         │
│   Metadata: category, source, title            │
└─────────────────────────────────────────────────┘
```

**Technology Stack:**

| Component | Technology | Version |
|-----------|-----------|---------|
| **Frontend** | Streamlit | 1.31+ |
| **Vector DB** | ChromaDB | 0.4+ |
| **Embeddings** | Sentence Transformers | all-MiniLM-L6-v2 (384 dims) |
| **LLM** | Anthropic Claude | Sonnet 4 (2025-05-14) |
| **Auth** | extra-streamlit-components | CookieManager |
| **HTTP Client** | httpx | 0.27+ (for image downloads) |
| **Document Processing** | markdown-it-py, pymdown-extensions | - |

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Anthropic API key** ([get one here](https://console.anthropic.com/))
- **Nebari documentation** repository cloned locally

### Installation

1. **Clone this repository**

   ```bash
   git clone https://github.com/goanpeca/nebari-docs-rag-demo.git
   cd nebari-docs-rag-demo
   ```

2. **Install dependencies (using conda)**

   ```bash
   conda env create -f environment.yml
   conda activate nebari-rag
   ```

   **OR using pip:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set environment variables**

   Create a `.env` file:

   ```bash
   ANTHROPIC_API_KEY=sk-ant-...
   NEBARI_DOCS_PATH=/path/to/nebari-docs
   DEMO_USERNAME=demo
   DEMO_PASSWORD=your_password
   ```

### Running the Application

1. **Ingest documentation** (one-time setup)

   ```bash
   python ingest_docs.py --docs-path /path/to/nebari-docs
   ```

   This will:
   - Scan all markdown/MDX files in nebari-docs
   - Extract homepage marketing content (Why Choose Nebari?)
   - Chunk semantically by headers (max 800 tokens, 100 overlap)
   - Generate embeddings and store in ChromaDB
   - Takes ~2-3 minutes for 64+ documents

   Expected output:
   ```
   📚 Found 65 files (64 docs + 1 homepage)
   ✂️  Created ~730 chunks
   ✨ Successfully ingested to ChromaDB
   ```

2. **Launch Streamlit app**

   ```bash
   streamlit run app.py
   ```

   Opens at `http://localhost:8501`

3. **Login with credentials**

   Use the username/password from your `.env` file

## 💻 Usage

### Example Questions

Try asking:

- **"Why should we use Nebari?"** - Gets homepage marketing content with benefits
- "How do I deploy Nebari on AWS?"
- "What is the difference between local and cloud deployment?"
- "How do I configure authentication with Keycloak?"
- "What are the hardware requirements?"
- "How do I troubleshoot deployment errors?"

### Features Guide

**Sidebar Settings:**
- **Sources to retrieve**: 3-10 sources (more = more context, slower)
- **Creativity**: 0.0-1.0 (lower = factual, higher = creative)

**Feedback & Export:**
- Rate answers with 👍 👎 buttons
- View stats: queries, tokens, cost, feedback
- Export as markdown or zip with images

**Source Citations:**
- Each answer shows 3-5 source documents
- Expandable cards with relevance scores
- Category labels (docs, community, website)

## 🔧 Technical Details

### Query Expansion for "Why" Questions

Special handling for benefits/value proposition questions:

```python
# When user asks "Why should we use Nebari?"
queries = [
    "Why should we use Nebari?",  # Original
    "why choose nebari benefits features advantages",  # Expanded
    "gitops collaboration dask open source platform"  # Keywords
]

# Homepage content gets 0.6x distance boost (better ranking)
if is_why_question and source == "website":
    distance *= 0.6  # Improves relevance by ~40%
```

### Cookie Authentication

- Uses `extra-streamlit-components` CookieManager
- SHA-256 hashed credentials
- 7-day expiration (604800 seconds)
- **Requires HTTPS** - works on Streamlit Cloud, not localhost

### Cost Tracking

Claude Sonnet 4 pricing (as of Feb 2025):
- Input: $3.00 per million tokens
- Output: $15.00 per million tokens

```python
input_cost = (input_tokens / 1_000_000) * 3.00
output_cost = (output_tokens / 1_000_000) * 15.00
```

### Export with Images

Zip export:
1. Extracts all image URLs from markdown (`![alt](https://...)`)
2. Downloads images with `httpx`
3. Creates folder structure: `chat.md` + `images/image_1.png`
4. Replaces URLs with local paths in markdown
5. Returns in-memory zip file

## 🚢 Deployment to Streamlit Cloud

### Step 1: Pre-build Vector Database

**CRITICAL**: Commit `chroma_db/` to Git to avoid build timeouts.

```bash
python ingest_docs.py
git add chroma_db/
git commit -m "Add pre-built vector database"
git push
```

### Step 2: Deploy

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Connect GitHub repository
3. Set main file: `app.py`
4. Add secrets:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   DEMO_USERNAME = "your_username"
   DEMO_PASSWORD = "your_password"
   ```
5. Deploy!

### Step 3: Test Cookie Auth

1. Login with credentials
2. **Refresh page** (Cmd+R)
3. ✅ Should stay logged in (cookie persists for 7 days)

**Note**: Cookie auth only works on HTTPS (Streamlit Cloud), not localhost.

## 📁 Project Structure

```
nebari-docs-rag-demo/
├── app.py                      # Streamlit UI with auth, feedback, export
├── agent.py                    # RAG agent with query expansion & tracking
├── ingest_docs.py              # Doc ingestion + homepage extraction
├── requirements.txt            # pip dependencies
├── environment.yml             # conda environment
├── pyproject.toml             # project config (ruff, pydocstyle, bandit)
├── .pre-commit-config.yaml    # pre-commit hooks
├── utils/
│   ├── chunking.py            # Semantic markdown chunking
│   └── prompts.py             # LLM system prompt
├── .streamlit/
│   └── config.toml            # Theme + CORS settings
├── chroma_db/                 # Vector database (git-committed)
├── tests/                     # pytest tests
└── specifications/            # Architecture & planning docs
```

## 🧪 Testing

Run pre-commit hooks (mypy, ruff, pydocstyle, bandit):

```bash
pre-commit run --all-files
```

Run pytest tests:

```bash
pytest tests/
```

## 📊 Performance Metrics

Based on 64+ Nebari docs + homepage:

| Metric                     | Value      |
| -------------------------- | ---------- |
| Documents Indexed          | 65 (64 docs + homepage) |
| Vector Chunks              | ~730       |
| Average Query Time         | <10 seconds (includes LLM) |
| Retrieval Time             | <1 second  |
| LLM Time                   | ~8 seconds |
| Retrieval Accuracy (Top-5) | >85% (>90% for "why" questions) |
| Database Size              | ~15 MB     |
| Cost per Query             | ~$0.01-0.02 |

## 🐛 Troubleshooting

### "Collection not found" error

**Solution**: Run `python ingest_docs.py` to create the vector database.

### "ANTHROPIC_API_KEY not found"

**Solutions**:
- **Local**: Add to `.env` file
- **Streamlit Cloud**: Add in App Settings → Secrets

### Cookie not persisting on localhost

**Expected behavior**: Cookies only work on HTTPS (Streamlit Cloud), not `localhost`.
**Solution**: Deploy to Streamlit Cloud to test cookie auth.

### "Why should we use Nebari?" returns wrong answer

**Solution**: The agent now includes query expansion and homepage content boosting. Re-run ingestion to ensure homepage content is indexed.

## 🎨 Customization

### Change Theme Colors

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF6B6B"  # Nebari red
backgroundColor = "#0E1117"  # Dark background
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

### Adjust Chunking

Edit `ingest_docs.py`:

```python
chunks = chunk_by_headers(
    doc["content"],
    doc["metadata"],
    max_chunk_size=800,  # Increase for more context
    overlap=100          # Increase for more overlap
)
```

### Add More Query Expansions

Edit `agent.py` `expand_query()` method to add custom query patterns.

## 📄 License

MIT License - see [LICENSE.txt](LICENSE.txt) for details

## 🙏 Acknowledgments

- **Nebari Team** - For excellent documentation
- **Anthropic** - For Claude Sonnet 4
- **Streamlit** - For the framework
- **ChromaDB** - For the vector database

---

**Built for AI Evangelist interview demo** | [LinkedIn](https://www.linkedin.com/in/goanpeca) | [GitHub](https://github.com/goanpeca/nebari-docs-rag-demo)
