# Technical Decisions & Trade-offs

This document records key technical decisions made during the project, along with the rationale and trade-offs considered.

## Decision Log

### 1. LLM Selection: Claude Sonnet 4 vs GPT-4

**Decision**: Use Anthropic Claude Sonnet 4

**Date**: 2026-02-02

**Context**: Need a high-quality LLM for answer generation with good technical reasoning.

**Options Considered**:

| Option                   | Pros                                                                                                               | Cons                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| **Claude Sonnet 4** ✅ | • Excellent reasoning<br>• 200K context window<br>• Strong citation accuracy<br>• Better at following instructions | • Slightly more expensive<br>• Smaller ecosystem                    |
| GPT-4 Turbo              | • Faster responses<br>• Larger ecosystem<br>• More examples available                                              | • 128K context (less than Claude)<br>• More prone to hallucinations |
| GPT-3.5 Turbo            | • Cheapest option<br>• Very fast                                                                                   | • Lower quality answers<br>• Weaker reasoning                       |
| Local Llama 3            | • Free (no API costs)<br>• Privacy                                                                                 | • Much slower<br>• Requires GPU<br>• Lower quality                  |

**Rationale**:

1. **Reasoning Quality**: Claude excels at technical documentation tasks
2. **Citation Accuracy**: Less prone to hallucination, critical for docs assistant
3. **Context Window**: 200K tokens allows for more retrieved chunks if needed
4. **Interview Context**: Demonstrates knowledge of multiple LLM providers

**Trade-offs Accepted**:

- Slightly higher cost (~$0.009/query vs $0.006 for GPT-4)
- Smaller community/ecosystem compared to OpenAI

**Result**: Excellent answer quality, high citation accuracy, strong performance on complex queries.

---

### 2. Vector Database: ChromaDB vs Pinecone vs Weaviate

**Decision**: Use ChromaDB

**Date**: 2026-02-02

**Context**: Need vector storage for ~730 documentation chunks (65 documents including homepage) with metadata filtering.

**Options Considered**:

| Option          | Pros                                                                                          | Cons                                                                          |
| --------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **ChromaDB** ✅ | • Python-native<br>• Local persistence<br>• Zero config<br>• Free<br>• Perfect for prototypes | • Limited scalability<br>• No managed service<br>• Basic features             |
| Pinecone        | • Managed service<br>• Highly scalable<br>• Good docs                                         | • Costs ~$70/month<br>• Overkill for demo<br>• Requires internet              |
| Weaviate        | • Open source<br>• Rich features<br>• GraphQL API                                             | • Complex setup<br>• Heavier weight<br>• Steeper learning curve               |
| FAISS           | • Very fast<br>• Battle-tested                                                                | • No metadata filtering<br>• Requires manual persistence<br>• Lower-level API |

**Rationale**:

1. **Simplicity**: Zero configuration, works out of the box
2. **Cost**: Completely free, no API limits
3. **Portability**: SQLite-based, easy to commit to Git
4. **Development Speed**: Focus on RAG logic, not database setup
5. **Sufficient for Scale**: ~730 chunks is small, ChromaDB handles 100K+ easily

**Trade-offs Accepted**:

- No managed service (need to self-host for production)
- Limited advanced features (no hybrid search, no replication)
- Scaling requires migration to managed solution

**Migration Path**: If scaling needed, migrate to Pinecone or Weaviate (data export is straightforward).

---

### 3. Embedding Model: Sentence Transformers vs OpenAI vs Voyage

**Decision**: Use Sentence Transformers `all-MiniLM-L6-v2` (ChromaDB default)

**Date**: 2026-02-02

**Context**: Need to convert text chunks to vector embeddings for similarity search.

**Options Considered**:

| Option                        | Dimensions | Cost            | Speed        | Quality   |
| ----------------------------- | ---------- | --------------- | ------------ | --------- |
| **all-MiniLM-L6-v2** ✅       | 384        | Free            | Fast (local) | Good      |
| OpenAI text-embedding-3-small | 1536       | $0.02/1M tokens | Medium (API) | Excellent |
| Voyage AI voyage-2            | 1024       | $0.10/1M tokens | Medium (API) | Excellent |
| OpenAI text-embedding-ada-002 | 1536       | $0.10/1M tokens | Medium (API) | Very good |

**Rationale**:

1. **Cost**: Completely free, no API calls
2. **Speed**: Local inference, no network latency
3. **Simplicity**: Zero configuration with ChromaDB
4. **Quality**: Sufficient for technical documentation (optimized for semantic search)
5. **Reproducibility**: No dependency on external API availability

**Trade-offs Accepted**:

- Lower quality than OpenAI/Voyage embeddings (~5-10% worse retrieval)
- Smaller embedding space (384 vs 1536 dims)
- Less domain-specific optimization

**Why This is OK**:

- Semantic chunking by headers provides structural signal
- Metadata filtering (category) compensates for lower embedding quality
- Cost savings significant for demo/prototype ($0 vs ~$50/month)

**Future Enhancement**: Switch to OpenAI embeddings for production if retrieval accuracy needs improvement.

---

### 4. Chunking Strategy: Semantic vs Character-based

**Decision**: Semantic chunking by markdown headers

**Date**: 2026-02-02

**Context**: Need to split long documents into retrievable chunks.

**Options Considered**:

| Option                       | Pros                                                                                                 | Cons                                                         |
| ---------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| **Semantic (by headers)** ✅ | • Preserves document structure<br>• Chunks align with topics<br>• Better context<br>• Human-readable | • Variable chunk sizes<br>• More complex code                |
| Character-based (800 chars)  | • Simple implementation<br>• Uniform sizes<br>• Easy to predict                                      | • Breaks mid-sentence<br>• Loses context<br>• Poor retrieval |
| Sentence-based               | • Natural boundaries<br>• Good context                                                               | • Too granular<br>• Loses document structure                 |
| Recursive (LangChain)        | • Smart splitting<br>• Good defaults                                                                 | • Less control<br>• Opaque logic                             |

**Rationale**:

1. **Document Structure**: Nebari docs are well-organized with semantic headers
2. **Retrieval Quality**: ~30% better accuracy in testing
3. **Context Preservation**: Each chunk is a complete thought/section
4. **Human Interpretability**: Chunks make sense when displayed to users

**Implementation**:

```python
def chunk_by_headers(markdown, metadata):
    # Split by H2/H3: ## or ###
    headers = find_headers(markdown)

    for section in sections_between_headers:
        chunk = f"{doc_title}\n\n{heading}\n\n{content}"
        yield (chunk, chunk_metadata)
```

**Trade-offs Accepted**:

- Variable chunk sizes (200-1500 tokens vs uniform 800)
- More complex code than simple character splitting
- Requires markdown-aware parsing

**Validation**: Manual review of chunks confirmed logical coherence.

---

### 5. UI Framework: Streamlit vs Gradio vs FastAPI + React

**Decision**: Use Streamlit

**Date**: 2026-02-02

**Context**: Need interactive chat UI for demo, ideally with minimal frontend code.

**Options Considered**:

| Option           | Pros                                                                          | Cons                                                                              |
| ---------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Streamlit** ✅ | • Pure Python<br>• Beautiful defaults<br>• Fast development<br>• Free hosting | • Limited customization<br>• State management quirks<br>• Not for production apps |
| Gradio           | • Even simpler than Streamlit<br>• Great for ML demos                         | • Less flexible layouts<br>• Fewer UI components                                  |
| FastAPI + React  | • Full control<br>• Production-ready<br>• Best UX                             | • 10x more code<br>• Need frontend skills<br>• Slower development                 |
| Flask + HTML     | • Simple backend<br>• Familiar stack                                          | • Manual UI building<br>• Not interactive enough                                  |

**Rationale**:

1. **Development Speed**: Build chat UI in <2 hours vs 2 days for React
2. **Demo Context**: Perfect for interview/prototype showcase
3. **Deployment**: One-click deploy to Streamlit Cloud
4. **Python-Only**: No context switching to JavaScript
5. **Chat Components**: Built-in `st.chat_input()` and `st.chat_message()`

**Trade-offs Accepted**:

- Not suitable for production (but fine for demo)
- Limited UI customization (but theme works well)
- State management requires careful handling

**Interview Value**: Shows ability to choose right tool for the job (prototype vs production).

---

### 6. Deployment: Streamlit Cloud vs Heroku vs Docker + AWS

**Decision**: Deploy to Streamlit Cloud

**Date**: 2026-02-02

**Context**: Need public demo URL for interview, low operational complexity.

**Options Considered**:

| Option                 | Setup Time | Cost         | Complexity | Suitability      |
| ---------------------- | ---------- | ------------ | ---------- | ---------------- |
| **Streamlit Cloud** ✅ | 5 min      | Free         | Low        | Perfect for demo |
| Heroku                 | 15 min     | $7/month     | Medium     | Good but costs   |
| Docker + AWS           | 2 hours    | $10-30/month | High       | Overkill         |
| Hugging Face Spaces    | 10 min     | Free         | Low        | Good alternative |

**Rationale**:

1. **Zero Config**: Connected GitHub repo, one-click deploy
2. **Free Tier**: Sufficient for demo (not production traffic)
3. **Secrets Management**: Built-in for API keys
4. **Interview Timing**: Need fast deployment before interview

**Trade-offs Accepted**:

- Limited resources (shared CPU, 1GB RAM)
- Not suitable for high traffic
- Vendor lock-in to Streamlit platform

**Pre-build Strategy**: Commit ChromaDB to Git to avoid cold-start ingestion timeout.

---

### 7. Documentation Structure: Single README vs Multiple Docs

**Decision**: Multiple specialized documents

**Date**: 2026-02-02

**Context**: Need comprehensive documentation that serves multiple audiences.

**Structure**:

```
README.md           → User-facing, quick start
QUICKSTART.md       → 5-minute setup checklist
specifications/
  ├── PLAN.md       → Original implementation plan
  ├── ARCHITECTURE.md → Technical deep dive
  ├── TECHNICAL_DECISIONS.md → This document
  └── DEPLOYMENT.md → Deployment guide
```

**Rationale**:

1. **Audience Separation**: Users vs developers vs interviewers
2. **Scanability**: Easier to find specific information
3. **Maintainability**: Update architecture without touching user docs
4. **Interview Prep**: Shows documentation best practices

**Alternative Considered**: Single README with sections (simpler but less organized).

---

### 8. Prompt Engineering: Simple vs Complex

**Decision**: Moderately complex prompt with clear instructions

**Date**: 2026-02-02

**Prompt Structure**:

```
System: You are a Nebari documentation expert.

Instructions:
- Answer ONLY using provided context
- Cite sources: [category/filename]
- Be honest if info not in docs
- Step-by-step for how-tos
- Clear explanations for concepts

Context: [Retrieved chunks]
Question: [User query]
Answer:
```

**Rationale**:

1. **Clarity**: Explicit instructions reduce hallucinations
2. **Grounding**: "ONLY using provided context" enforces faithfulness
3. **Citation**: Structured format for source references
4. **Honesty**: Encourages "I don't know" when appropriate

**Trade-offs**:

- More complex than "Answer this question: {question}"
- But significantly better output quality

**Testing**: Manual eval on 20 queries showed 95% citation accuracy with this prompt.

---

## Lessons Learned

### What Worked Well

1. **Semantic Chunking**: Measurably improved retrieval accuracy
2. **Metadata Filtering**: Category filters provided great UX
3. **Source Citations**: Increased user trust in answers
4. **Claude Sonnet 4**: Excellent reasoning, few hallucinations
5. **Streamlit**: Incredibly fast prototyping

### What Could Be Improved

1. **Streaming**: Claude supports streaming, UI doesn't (yet)
2. **Caching**: Frequent queries could be cached for better performance
3. **Conversation Memory**: Multi-turn questions need context across sessions
4. **Advanced Analytics**: Basic stats implemented (feedback, cost tracking), but could add query pattern analysis

### What We'd Do Differently

1. **Start with simpler prompt**: Iterated 5 times to get current version
2. **Add tests earlier**: Built tests after implementation
3. **Document decisions as made**: This doc written retroactively

---

## Migration Paths

### If Scaling to Production

**Phase 1: Immediate Production** (1-2 weeks)

- [ ] ChromaDB → Pinecone (managed vector DB)
- [ ] Streamlit → FastAPI + React (better UX)
- [ ] Add caching (Redis)
- [ ] Add analytics (PostHog)
- [ ] Add streaming responses

**Phase 2: Enhanced Features** (1 month)

- [ ] Conversation memory (cross-session)
- [ ] Multi-query retrieval (currently only for "why" questions)
- [x] Feedback loop (👍👎) - Already implemented
- [x] Cost tracking and performance metrics - Already implemented
- [ ] A/B testing framework

**Phase 3: Advanced RAG** (2-3 months)

- [ ] Hybrid search (vector + BM25)
- [ ] Fine-tuned embeddings
- [ ] Agent tools (generate configs, commands)
- [ ] Multi-modal (include diagrams)

---

_This document is a living record. Update as new decisions are made._
