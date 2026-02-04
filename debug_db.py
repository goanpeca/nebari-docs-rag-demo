#!/usr/bin/env python3
"""Debug script to check what's in ChromaDB for architecture content."""

import os
from pathlib import Path

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

# Base directory for ChromaDB (configurable via BASE_DIR env var)
BASE_DIR = Path(os.getenv("BASE_DIR", Path(__file__).parent))

# Initialize ChromaDB client
client = chromadb.PersistentClient(
    path=str(BASE_DIR / "chroma_db"), settings=Settings(anonymized_telemetry=False)
)

# Get collection
collection = client.get_collection("nebari_docs")

print("=" * 60)
print("CHROMADB DIAGNOSTICS")
print("=" * 60)

# Get total count
count = collection.count()
print(f"\n Total chunks in database: {count}")

# Search for architecture-related content
print("\n" + "=" * 60)
print("SEARCHING FOR 'architecture'")
print("=" * 60)

results = collection.query(
    query_texts=["architecture diagram infrastructure"],
    n_results=10,
    include=["documents", "metadatas", "distances"],
)

if results["documents"] and len(results["documents"][0]) > 0:
    print(f"\n Found {len(results['documents'][0])} results\n")

    for i, (doc, meta, dist) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ):
        print(f"\n{'='*60}")
        print(f"RESULT {i+1}")
        print(f"{'='*60}")
        print(f"File: {meta.get('file_path', 'unknown')}")
        print(f"Title: {meta.get('title', 'unknown')}")
        print(f"Category: {meta.get('category', 'unknown')}")
        print(f"Heading: {meta.get('heading', 'N/A')}")
        print(f"Distance: {dist:.4f}")
        print(f"\nDocument length: {len(doc)} chars")
        print(f"Contains '![': {'![' in doc}")
        print(f"Contains '<': {'<' in doc}")
        print(f"Contains 'TabItem': {'TabItem' in doc}")

        # Extract image references
        import re

        images = re.findall(r"!\[([^\]]*)\]\(([^\)]+)\)", doc)
        if images:
            print(f"\n Images found ({len(images)}):")
            for alt, url in images:
                print(f"  - [{alt}]({url})")

        # Show first 500 chars
        print("\n Content preview:")
        print("-" * 60)
        print(doc[:500])
        print("-" * 60)
else:
    print("\n No results found!")

# Also check if architecture.mdx file exists in any chunk
print("\n" + "=" * 60)
print("CHECKING FOR architecture.mdx FILE")
print("=" * 60)

all_data = collection.get(include=["documents", "metadatas"])

arch_chunks = [
    (doc, meta)
    for doc, meta in zip(all_data["documents"], all_data["metadatas"])
    if "architecture" in meta.get("file_path", "").lower()
]

print(f"\n Found {len(arch_chunks)} chunks from architecture.mdx")

if arch_chunks:
    print("\nFirst architecture chunk:")
    print("-" * 60)
    print(f"File: {arch_chunks[0][1].get('file_path')}")
    print(f"Heading: {arch_chunks[0][1].get('heading', 'N/A')}")
    print(f"Contains images: {'![' in arch_chunks[0][0]}")
    print(f"Contains HTML: {'<' in arch_chunks[0][0]}")
    print("\nContent preview:")
    print(arch_chunks[0][0][:500])
