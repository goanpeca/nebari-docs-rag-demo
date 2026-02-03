# Deployment Guide

Complete guide for deploying the Nebari RAG Demo to various environments.

## Table of Contents

- [Local Development](#local-development)
- [Streamlit Cloud (Recommended for Demo)](#streamlit-cloud-recommended-for-demo)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Monitoring & Analytics](#monitoring--analytics)

---

## Local Development

### Prerequisites

- Python 3.11+
- 4GB RAM minimum
- Anthropic API key
- Git

### Quick Setup

```bash
# Clone repository
git clone https://github.com/yourusername/nebari-docs-rag-demo.git
cd nebari-docs-rag-demo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY

# Run ingestion
python ingest_docs.py

# Start app
streamlit run app.py
```

### Development Workflow

**Hot Reload**:
Streamlit auto-reloads on file changes. Keep it running while developing.

**Clear Cache**:

```python
# In app, press 'C' then 'Enter' to clear cache
# Or restart: Ctrl+C, then streamlit run app.py
```

**Testing**:

```bash
# Test ingestion
python ingest_docs.py --force-refresh

# Test agent
python agent.py

# Test specific query
python -c "from agent import NebariAgent; agent = NebariAgent(); print(agent.answer_question('What is Nebari?'))"
```

---

## Streamlit Cloud (Recommended for Demo)

**Best for**: Interview demos, prototypes, sharing with stakeholders

### Step 1: Prepare Repository

1. **Ensure all files are committed**:

   ```bash
   git status
   git add .
   git commit -m "Ready for deployment"
   ```

2. **CRITICAL: Pre-build vector database**:

   ```bash
   # Run ingestion locally
   python ingest_docs.py

   # Commit the database (usually gitignored, but needed for deployment)
   git add -f chroma_db/
   git commit -m "Add pre-built vector database"
   git push
   ```

   **Why?** Streamlit Cloud has a 10-minute build timeout. Building the vector database during deployment will timeout. Pre-building avoids this.

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/nebari-docs-rag-demo.git
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)

2. Sign in with GitHub

3. Click **"New app"**

4. Configure app:
   - **Repository**: Select `nebari-docs-rag-demo`
   - **Branch**: `main`
   - **Main file path**: `app.py`

5. Click **"Advanced settings"**

6. Set **Python version**: `3.11` (or match your local version)

7. Add **Secrets**:

   ```toml
   # Click "Secrets" section
   ANTHROPIC_API_KEY = "sk-ant-your-actual-key-here"
   DEMO_USERNAME = "your_username"
   DEMO_PASSWORD = "your_password"
   ```

8. Click **"Deploy!"**

### Step 3: Verify Deployment

**Expected Timeline**:

- Build: 2-3 minutes
- Initial load: 5-10 seconds
- Subsequent loads: <2 seconds

**Test Checklist**:

- [ ] App loads without errors
- [ ] Chat interface visible
- [ ] Example questions in sidebar
- [ ] Test query: "How do I deploy Nebari on AWS?"
- [ ] Sources display correctly
- [ ] No API errors in logs

**Troubleshooting**:

**Error: "Collection not found"**

- Problem: Vector database not committed to Git
- Solution: Run Step 1.2 again (pre-build and commit database)

**Error: "ANTHROPIC_API_KEY not found"**

- Problem: Secrets not configured
- Solution: Go to App Settings → Secrets → Add key

**Error: "Build timeout"**

- Problem: Trying to build database during deployment
- Solution: Pre-build locally and commit (Step 1.2)

### Step 4: Share Demo

Your app is now live at:

```
https://share.streamlit.io/yourusername/nebari-docs-rag-demo/main/app.py
```

**Tips for Demo**:

- Bookmark the URL
- Test in incognito mode (verifies it works for others)
- Take screenshots as backup
- Record a quick video walkthrough

---

## Docker Deployment

**Best for**: Portable deployment, self-hosting, Kubernetes

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t nebari-rag-demo .

# Run container
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -v $(pwd)/chroma_db:/app/chroma_db \
  nebari-rag-demo
```

**Access**: http://localhost:8501

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped
```

**Run**:

```bash
docker-compose up -d
```

---

## Production Deployment

**Best for**: High-traffic, production use cases

### Architecture

```
┌─────────────────┐
│  Load Balancer  │  (NGINX / Cloudflare)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ App 1│  │ App 2│  (Multiple Streamlit instances)
└───┬──┘  └──┬───┘
    │        │
┌───▼────────▼───┐
│  Pinecone / DB │  (Managed vector database)
└────────────────┘
```

### Requirements

- **Frontend**: Migrate from Streamlit to FastAPI + React
- **Vector DB**: Migrate from ChromaDB to Pinecone or Weaviate
- **Caching**: Add Redis for query caching
- **Monitoring**: Add PostHog/Mixpanel for analytics
- **Auth**: Add user authentication
- **Rate Limiting**: Prevent abuse

### Migration Checklist

#### Phase 1: Backend (1 week)

- [ ] Replace Streamlit with FastAPI
- [ ] Migrate ChromaDB → Pinecone
- [ ] Add Redis caching
- [ ] Add rate limiting
- [ ] Add logging (structured JSON)
- [ ] Add health check endpoints

**Example FastAPI Endpoint**:

```python
from fastapi import FastAPI
from agent import NebariAgent

app = FastAPI()
agent = NebariAgent()

@app.post("/api/query")
async def query(question: str, top_k: int = 5):
    result = agent.answer_question(question, top_k)
    return result
```

#### Phase 2: Frontend (1 week)

- [ ] Build React chat UI
- [ ] Add streaming support
- [ ] Add conversation history
- [x] Add feedback buttons (👍 👎) - Already implemented in Streamlit UI
- [ ] Add analytics tracking

#### Phase 3: Infrastructure (1 week)

- [ ] Deploy to AWS/GCP/Azure
- [ ] Set up CI/CD (GitHub Actions)
- [ ] Configure monitoring (Datadog/New Relic)
- [ ] Set up alerts
- [ ] Configure backups

### Cost Estimation (Production)

| Service             | Monthly Cost | Notes                  |
| ------------------- | ------------ | ---------------------- |
| Pinecone (Starter)  | $70          | 1M vectors, serverless |
| Anthropic API       | $100-500     | Depends on traffic     |
| AWS EC2 (t3.medium) | $30          | Application server     |
| Redis Cache         | $15          | ElastiCache            |
| Monitoring          | $20          | Datadog free tier      |
| **Total**           | **$235-635** | Scales with usage      |

---

## Monitoring & Analytics

### Metrics to Track

**Performance**:

- Query latency (p50, p95, p99)
- ChromaDB search time
- Claude API call time
- Cache hit rate

**Usage**:

- Queries per day
- Unique users
- Popular questions
- Category distribution

**Quality**:

- Feedback score (👍 vs 👎)
- Retrieval accuracy
- Source citation rate
- Empty result rate

### Logging Setup

**Local Development**:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Query: {query}, Latency: {latency}ms")
```

**Production (Structured JSON)**:

```python
import structlog

log = structlog.get_logger()
log.info("query_processed",
    query=query,
    latency_ms=latency,
    sources_count=len(sources),
    category=category
)
```

### Analytics Dashboard

**Recommended Tools**:

- **PostHog**: Product analytics, self-hosted option
- **Mixpanel**: User behavior tracking
- **Plausible**: Privacy-friendly web analytics

**Key Dashboards**:

1. **Overview**: Queries/day, unique users, avg latency
2. **Popular Questions**: Most asked queries
3. **Performance**: Latency over time, error rate
4. **Quality**: Feedback scores, empty results

---

## Security Best Practices

### API Key Management

**Local Development**:

- Use `.env` file (never commit)
- Add `.env` to `.gitignore`

**Streamlit Cloud**:

- Use Streamlit secrets
- Rotate keys every 90 days

**Production**:

- Use AWS Secrets Manager / GCP Secret Manager
- Enable key rotation
- Audit key usage

### Rate Limiting

**Prevent abuse**:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/query")
@limiter.limit("10/minute")  # 10 queries per minute per IP
async def query(request: Request, question: str):
    ...
```

### Input Validation

**Sanitize user input**:

```python
def validate_query(query: str) -> str:
    # Max length
    if len(query) > 500:
        raise ValueError("Query too long")

    # Strip dangerous characters
    query = query.strip()

    # Prevent injection
    if any(c in query for c in ['<', '>', '{', '}']):
        raise ValueError("Invalid characters")

    return query
```

---

## Backup & Recovery

### Database Backups

**ChromaDB (Local)**:

```bash
# Backup
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz chroma_db/

# Restore
tar -xzf chroma_backup_YYYYMMDD.tar.gz
```

**Pinecone (Production)**:

- Enable automatic backups in Pinecone dashboard
- Export vectors to S3 weekly

### Disaster Recovery Plan

1. **Database corruption**: Restore from backup, re-run ingestion
2. **API outage**: Serve cached responses, display status message
3. **Deployment failure**: Rollback to previous version
4. **Data loss**: Re-ingest from source (nebari-docs repo)

**Recovery Time Objective (RTO)**: < 1 hour
**Recovery Point Objective (RPO)**: < 24 hours

---

## Performance Optimization

### Caching Strategy

**Query-level caching**:

```python
import hashlib
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_answer(query_hash: str, top_k: int):
    return agent.answer_question(query, top_k)

# Use
query_hash = hashlib.md5(query.encode()).hexdigest()
result = cached_answer(query_hash, top_k)
```

**Benefits**:

- Reduce Claude API calls (save costs)
- Faster response for common questions
- Lower latency

### Database Optimization

**ChromaDB**:

- Keep database size < 100MB
- Use SSD for storage
- Enable persistence

**Pinecone**:

- Use serverless for variable traffic
- Enable metadata filtering
- Use namespaces for multi-tenancy

### Claude API Optimization

**Reduce costs**:

- Lower temperature for factual queries (0.1-0.3)
- Reduce max_tokens (1000-1500 is often enough)
- Cache frequent queries
- Batch requests if possible

**Improve latency**:

- Enable streaming (show response as it generates)
- Prefetch common follow-ups
- Use async/await for concurrent requests

---

## Troubleshooting

### Common Issues

| Issue              | Cause                 | Solution                            |
| ------------------ | --------------------- | ----------------------------------- |
| Slow queries       | Too many sources      | Reduce top_k to 3-5                 |
| High API costs     | Many unique queries   | Enable caching                      |
| Poor answers       | Low-quality retrieval | Increase top_k, improve chunking    |
| Empty results      | Typos, out-of-domain  | Add query expansion, fuzzy matching |
| Deployment timeout | Building database     | Pre-build and commit database       |

### Debug Mode

Enable verbose logging:

```python
# In agent.py
import logging
logging.basicConfig(level=logging.DEBUG)

# Shows:
# - Query embedding time
# - Search results
# - Prompt sent to Claude
# - Token usage
```

---

## Maintenance

### Weekly Tasks

- [ ] Review error logs
- [ ] Check API usage and costs
- [ ] Monitor query latency trends

### Monthly Tasks

- [ ] Update dependencies (`pip list --outdated`)
- [ ] Review popular queries, add to examples
- [ ] Rotate API keys
- [ ] Re-ingest docs if Nebari docs updated

### Quarterly Tasks

- [ ] Evaluate new LLMs (Claude 4, GPT-5, etc.)
- [ ] Review and update prompts
- [ ] Analyze user feedback, iterate on UX
- [ ] Test with new Nebari releases

---

_For questions or issues, open a GitHub issue or contact the maintainers._
