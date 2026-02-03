# API Keys Guide

## What You Need ✅

### 1. Anthropic API Key (REQUIRED)

**Purpose**: Powers Claude Sonnet 4 (2025-05-14) for generating answers

**How to get it**:

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to "API Keys" section
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-...`)

**Cost**:

- $3 per 1M input tokens
- $15 per 1M output tokens
- **Average cost per query**: ~$0.009 (less than 1 cent)
- Free trial credits available for new accounts

**Add to `.env`**:

```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

---

## What You DON'T Need ❌

### Voyage API Key (NOT NEEDED)

**Why it's mentioned**: In the original plan, I considered Voyage AI as a potential embedding provider for advanced use cases.

**Reality**: The app uses **FREE local embeddings** that run on your computer. No API key needed!

**How embeddings work in this app**:

```
Your Question
    ↓
ChromaDB (uses Sentence Transformers locally - FREE)
    ↓
Converts text to vectors (embeddings)
    ↓
Finds similar documentation chunks
    ↓
Sends chunks to Claude (requires ANTHROPIC_API_KEY)
    ↓
Claude generates answer
```

**What is Voyage AI?**

- An embedding service (like OpenAI's embedding API)
- Provides high-quality text embeddings
- Costs ~$0.10 per 1M tokens
- **NOT used in this app by default**

**When would you use Voyage AI?**

- Only if you want to experiment with different embedding models
- Only for advanced optimization (>95% accuracy not enough)
- **For this demo, you don't need it!**

---

## Summary

### Minimal Setup (Recommended)

Your `.env` file only needs:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your-key-here
NEBARI_DOCS_PATH=/Users/goanpeca/Desktop/develop/datalayer/nebari-docs
DEMO_USERNAME=demo
DEMO_PASSWORD=your_password
```

That's it! Just **one API key**.

---

## How the App Works (Technical Details)

### Embedding Generation (FREE)

**What happens during `python ingest_docs.py`**:

1. Reads Nebari documentation files
2. Chunks them by markdown headers
3. **ChromaDB automatically uses Sentence Transformers** (`all-MiniLM-L6-v2`)
4. Generates 384-dimensional vectors
5. Stores in local database (`./chroma_db/`)

**Cost**: $0 (runs on your computer)

### Query Processing (Costs ~$0.009)

**What happens when you ask a question**:

1. Your question → ChromaDB (free local embedding)
2. ChromaDB searches for similar chunks (free)
3. Top 5 chunks sent to Claude API (costs money)
4. Claude generates answer (costs money)
5. Answer displayed with sources (free)

**Total cost**: Only the Claude API call (~$0.009 per query)

---

## Cost Estimation

### For Interview Demo (1 hour)

- Questions asked: ~20-30
- Cost: ~$0.18 - $0.27
- **Basically free** 💰

### For Development (1 week)

- Questions asked: ~100-200
- Cost: ~$0.90 - $1.80
- **Still very cheap** 💰

### For Production (1000 queries/day)

- Monthly queries: ~30,000
- Cost: ~$270/month
- **Scales with usage** 📈

---

## Alternative: Use OpenAI Instead

If you prefer OpenAI:

**For Embeddings** (optional, not recommended for demo):

```bash
OPENAI_API_KEY=sk-...
```

**For LLM** (instead of Claude):

- Would require code changes
- Not implemented by default
- Claude is better for this use case

---

## FAQ

**Q: Why does the code mention Voyage AI if we don't use it?**

A: The original plan considered multiple embedding providers. The final implementation uses free local embeddings, but the infrastructure supports swapping providers if needed.

**Q: Can I use this without any API keys?**

A: No, you need the Anthropic API key for Claude. However, embeddings are free (local).

**Q: Is there a completely free option?**

A: You could use a local LLM (like Llama 3 via Ollama) instead of Claude, but:

- Requires code changes
- Slower responses
- Lower quality answers
- Not recommended for interview demo

**Q: Do I need an OpenAI API key?**

A: No! The app doesn't use OpenAI by default.

---

## Quick Start Checklist

- [ ] Get Anthropic API key from https://console.anthropic.com/
- [ ] Create `.env` file: `cp .env.example .env`
- [ ] Add API key to `.env`
- [ ] ~~Get Voyage API key~~ ❌ NOT NEEDED
- [ ] ~~Get OpenAI API key~~ ❌ NOT NEEDED
- [ ] Run `conda activate nebari-rag`
- [ ] Run `python ingest_docs.py`
- [ ] Run `streamlit run app.py`

**That's it!** Just one API key needed. 🎉
