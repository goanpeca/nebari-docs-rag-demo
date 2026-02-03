# Installation Guide

## Quick Install with Conda (Recommended)

Conda handles binary dependencies better than pip, especially on Apple Silicon (M1/M2/M3).

### Step 1: Create Conda Environment

```bash
# Navigate to project
cd /Users/goanpeca/Desktop/develop/datalayer/nebari-docs-rag-demo

# Create environment from file
conda env create -f environment.yml

# Activate environment
conda activate nebari-rag
```

### Step 2: Configure API Key

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use any editor
```

Add to `.env`:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
NEBARI_DOCS_PATH=/Users/goanpeca/Desktop/develop/datalayer/nebari-docs
DEMO_USERNAME=demo
DEMO_PASSWORD=your_password
```

### Step 3: Verify Installation

```bash
# Check Python version
python --version  # Should be 3.11.x

# Check installed packages
conda list | grep -E "streamlit|chromadb|anthropic"
```

### Step 4: Run Application

```bash
# Ingest documentation (one-time)
python ingest_docs.py

# Launch app
streamlit run app.py
```

---

## Alternative: Virtual Environment with Pip

If you prefer pip or encounter conda issues:

### Option A: Use Python 3.11 specifically

```bash
# Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages one by one (more reliable)
pip install streamlit
pip install chromadb
pip install anthropic
pip install python-dotenv markdown-it-py pymdown-extensions pyyaml
pip install httpx extra-streamlit-components watchdog
```

### Option B: Install ChromaDB without onnxruntime (lighter)

If you don't need onnxruntime for embeddings:

```bash
# Install ChromaDB without ML dependencies
pip install chromadb-client  # Lighter client-only version

# Or use specific version that works
pip install 'chromadb>=0.4.0,<0.5.0' --no-deps
pip install -r requirements.txt --no-deps
pip install $(cat requirements.txt | grep -v chromadb)
```

---

## Platform-Specific Issues

### Apple Silicon (M1/M2/M3)

ChromaDB depends on `onnxruntime` which doesn't have pre-built wheels for ARM64 macOS.

**Solution 1: Use Conda (Recommended)**

```bash
conda env create -f environment.yml
```

**Solution 2: Use Rosetta**

```bash
# Install x86_64 Python via Homebrew
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
arch -x86_64 brew install python@3.11

# Create venv with x86_64 Python
arch -x86_64 /usr/local/bin/python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Solution 3: Skip onnxruntime**

Edit `requirements.txt` to remove version constraints:

```
chromadb  # Remove >= version
```

Then install:

```bash
pip install --no-deps chromadb
pip install -r requirements.txt
```

### Linux

Should work with standard pip:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

If onnxruntime fails on Windows, try:

```bash
pip install onnxruntime-directml  # For DirectML support
```

---

## Troubleshooting

### "No matching distribution for onnxruntime"

**Cause**: Your platform doesn't have pre-built onnxruntime wheels.

**Fix**: Use conda or build from source:

```bash
# Install build tools
conda install -c conda-forge onnxruntime

# Or use conda environment
conda env create -f environment.yml
```

### "Conflicting dependencies"

**Cause**: Package version conflicts.

**Fix**: Install packages individually:

```bash
pip install streamlit chromadb anthropic python-dotenv httpx extra-streamlit-components
```

### "ImportError: cannot import name 'Anthropic'"

**Cause**: Wrong package installed.

**Fix**:

```bash
pip uninstall anthropic
pip install anthropic>=0.18.0
```

### ChromaDB fails to start

**Cause**: Missing SQLite or DuckDB dependencies.

**Fix** (macOS):

```bash
brew install sqlite
```

**Fix** (Linux):

```bash
sudo apt-get install libsqlite3-dev
```

---

## Verify Installation

Run this test script to verify everything works:

```bash
python -c "
import streamlit
import chromadb
import anthropic
import httpx
print('✅ All packages imported successfully!')
print(f'Streamlit: {streamlit.__version__}')
print(f'ChromaDB: {chromadb.__version__}')
print(f'Anthropic: {anthropic.__version__}')
print(f'HTTPX: {httpx.__version__}')
"
```

Expected output:

```
✅ All packages imported successfully!
Streamlit: 1.31.0
ChromaDB: 0.4.24
Anthropic: 0.18.1
HTTPX: 0.27.0
```

---

## Clean Install (Reset)

If you need to start fresh:

**Conda**:

```bash
conda deactivate
conda env remove -n nebari-rag
conda env create -f environment.yml
conda activate nebari-rag
```

**Pip**:

```bash
deactivate
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Next Steps

Once installation is complete:

1. **Configure API key**: Edit `.env` file
2. **Ingest docs**: `python ingest_docs.py`
3. **Run app**: `streamlit run app.py`

See [QUICKSTART.md](QUICKSTART.md) for detailed usage instructions.
