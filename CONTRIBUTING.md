# Contributing to Nebari RAG Demo

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Quick Links

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

**Before submitting a bug report:**

- Check the [existing issues](https://github.com/yourusername/nebari-docs-rag-demo/issues)
- Verify the bug in the latest version
- Collect relevant information (error messages, logs, environment)

**Submitting a bug report:**

1. Use the bug report template
2. Provide a clear, descriptive title
3. Include steps to reproduce
4. Describe expected vs actual behavior
5. Add screenshots if applicable
6. Specify your environment (OS, Python version, dependencies)

### Suggesting Enhancements

**Enhancement suggestions are welcome!**

- Use the feature request template
- Explain the problem your enhancement would solve
- Describe the proposed solution
- Consider alternative solutions
- Explain why this would be useful to most users

### Code Contributions

**Areas for contribution:**

- Improve retrieval accuracy (hybrid search, multi-query retrieval)
- Add conversation memory (future feature)
- Implement streaming responses (future feature)
- Enhance UI/UX
- Add tests (currently at ~50% coverage)
- Improve documentation
- Fix bugs

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- Anthropic API key

### Setup Instructions

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/nebari-docs-rag-demo.git
cd nebari-docs-rag-demo

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# Run ingestion
python ingest_docs.py

# Start development server
streamlit run app.py
```

### Development Workflow

1. **Create a branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**:
   - Write code
   - Add tests
   - Update documentation

3. **Test locally**:

   ```bash
   # Run tests
   pytest

   # Run pre-commit hooks (ruff, pydocstyle, bandit, mypy)
   pre-commit run --all-files
   ```

4. **Commit changes**:

   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   # Open pull request on GitHub
   ```

## Coding Standards

### Python Style Guide

**Follow PEP 8** with these specifics:

- Line length: 100 characters (not 79)
- Use Ruff for linting and formatting
- Use type hints for function signatures
- Use docstrings (Google style)
- Run pre-commit hooks before committing

**Example**:

```python
from typing import List, Dict, Optional

def retrieve_context(
    query: str,
    top_k: int = 5,
    category_filter: Optional[str] = None
) -> List[Dict]:
    """
    Retrieve relevant context from ChromaDB.

    Args:
        query: User question
        top_k: Number of chunks to retrieve
        category_filter: Optional category filter (e.g., "how-tos")

    Returns:
        List of retrieved chunks with metadata and relevance scores

    Raises:
        ValueError: If top_k is less than 1
    """
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    # Implementation...
```

### Code Organization

**File structure**:

```
app.py           # Streamlit UI (main entry point)
agent.py         # RAG agent logic
ingest_docs.py   # Document ingestion
utils/
  chunking.py    # Chunking utilities
  prompts.py     # Prompt templates
tests/
  test_chunking.py
  test_agent.py
```

**Import order**:

1. Standard library
2. Third-party packages
3. Local modules

```python
# Standard library
import os
from typing import List

# Third-party
import chromadb
from anthropic import Anthropic

# Local
from utils.chunking import chunk_by_headers
```

### Documentation Standards

**Docstrings are required** for:

- All public functions
- All classes
- All modules

**Use Google-style docstrings**:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief one-line summary.

    Longer description if needed, explaining what the function does,
    how it works, and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative

    Examples:
        >>> example_function("test", 5)
        True
    """
```

### Testing Standards

**Write tests for**:

- New features
- Bug fixes
- Edge cases
- Performance-critical code

**Test structure**:

```python
import pytest
from agent import NebariAgent

def test_retrieve_context_returns_results():
    """Test that retrieve_context returns expected number of results."""
    agent = NebariAgent()
    results = agent.retrieve_context("How do I deploy?", top_k=3)

    assert len(results) == 3
    assert all('text' in r for r in results)
    assert all('metadata' in r for r in results)

def test_retrieve_context_with_invalid_top_k():
    """Test that retrieve_context raises error for invalid top_k."""
    agent = NebariAgent()

    with pytest.raises(ValueError):
        agent.retrieve_context("test", top_k=0)
```

**Run tests**:

```bash
# All tests
pytest

# Specific file
pytest tests/test_agent.py

# With coverage
pytest --cov=. --cov-report=html
```

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains changes

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

How has this been tested?

## Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests pass
```

### Review Process

1. **Automated checks**: CI runs tests and linting
2. **Code review**: Maintainer reviews code
3. **Feedback**: Address any comments or suggestions
4. **Approval**: Once approved, PR is merged
5. **Cleanup**: Delete branch after merge

### Commit Message Guidelines

**Format**:

```
type(scope): brief description

Longer explanation if needed

Fixes #123
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples**:

```
feat(agent): add conversation memory support

Implements conversation memory to maintain context across
multiple queries using Streamlit session state.

Fixes #45
```

## Areas for Contribution

### High Priority

- [ ] Add streaming support for Claude responses
- [ ] Implement conversation memory (maintain context across multiple queries)
- [ ] Improve test coverage (currently ~50%, target: 80%)
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Add query caching (Redis or in-memory)

### Medium Priority

- [ ] Advanced retrieval (hybrid search, multi-query)
- [ ] Analytics dashboard (expand current sidebar stats)
- [ ] Better error handling and recovery
- [ ] Performance optimization (response time, caching)
- [ ] Add integration tests

### Low Priority

- [ ] Multi-language support
- [ ] Voice input
- [ ] Additional export formats (PDF, JSON)

### Documentation

- [ ] API documentation (automated with TypeDoc/Sphinx)
- [ ] Tutorial videos
- [ ] Architecture diagrams (expand current documentation)
- [ ] Performance benchmarks (automated testing)

## Questions?

- Open a [discussion](https://github.com/yourusername/nebari-docs-rag-demo/discussions)
- Join our community chat (link TBD)
- Email maintainers (link TBD)

---

**Thank you for contributing!** 🎉
