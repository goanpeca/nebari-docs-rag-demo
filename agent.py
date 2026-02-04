"""RAG agent for Nebari documentation Q&A.

Handles query understanding, context retrieval from ChromaDB,
and answer generation using Claude.
"""

import os
import time
from pathlib import Path
from typing import Any

import chromadb
from anthropic import Anthropic
from chromadb.config import Settings
from dotenv import load_dotenv

from utils.prompts import SYSTEM_PROMPT

load_dotenv()

# Base directory for ChromaDB (configurable via BASE_DIR env var)
BASE_DIR = Path(os.getenv("BASE_DIR", Path(__file__).parent))


class NebariAgent:
    """RAG agent for answering questions about Nebari documentation.

    Parameters
    ----------
    chroma_path : str, default "./chroma_db"
        Path to ChromaDB persistence directory
    collection_name : str, default "nebari_docs"
        Name of the Chroma collection
    anthropic_api_key : str, optional
        Anthropic API key. Uses ANTHROPIC_API_KEY environment variable if not provided

    Attributes
    ----------
    client : chromadb.PersistentClient
        ChromaDB client instance
    collection : chromadb.Collection
        ChromaDB collection for document storage
    anthropic : anthropic.Anthropic
        Anthropic client for Claude API
    conversation_history : list
        History of question-answer pairs

    Raises
    ------
    ValueError
        If collection not found or API key not provided
    """

    def __init__(
        self,
        chroma_path: str = str(BASE_DIR / "chroma_db"),
        collection_name: str = "nebari_docs",
        anthropic_api_key: str | None = None,
    ) -> None:
        self.client = chromadb.PersistentClient(
            path=chroma_path, settings=Settings(anonymized_telemetry=False)
        )

        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception as e:
            raise ValueError(
                f"Collection '{collection_name}' not found. "
                f"Run ingest_docs.py first. Error: {e}"
            )

        api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it in .env or pass as parameter.")

        self.anthropic = Anthropic(api_key=api_key)
        self.conversation_history: list[dict[str, str]] = []

    def expand_query(self, query: str) -> list[str]:
        """Expand user query into multiple search variations for better retrieval.

        Parameters
        ----------
        query : str
            Original user question

        Returns
        -------
        list[str]
            List of query variations including the original, limited to 3
        """
        queries: list[str] = [query]
        query_lower = query.lower()

        # Handle "why" questions about benefits and value proposition
        if any(word in query_lower for word in ["why", "should i use", "benefits", "advantages"]):
            queries.append("why choose nebari benefits features advantages")
            queries.append("gitops collaboration dask open source platform")

        if any(word in query_lower for word in ["show", "see", "view", "display", "what"]):
            for remove_word in [
                "show me",
                "let me see",
                "can you show",
                "i want to see",
                "what is",
                "what are",
            ]:
                if remove_word in query_lower:
                    focused = query_lower.replace(remove_word, "").strip()
                    if focused and focused not in [q.lower() for q in queries]:
                        queries.append(focused)

        if "architecture" in query_lower:
            queries.append("architecture diagram infrastructure")
            queries.append("system design components")

        if "deploy" in query_lower:
            if "aws" in query_lower:
                queries.append("AWS deployment configuration terraform")
            elif "gcp" in query_lower or "google" in query_lower:
                queries.append("GCP deployment google cloud")
            elif "azure" in query_lower:
                queries.append("Azure deployment configuration")
            else:
                queries.append("cloud deployment steps")

        if "install" in query_lower or "setup" in query_lower:
            queries.append("installation requirements setup")

        if "auth" in query_lower or "login" in query_lower or "keycloak" in query_lower:
            queries.append("authentication keycloak configuration")

        return queries[:3]

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        category_filter: str | None = None,
        use_query_expansion: bool = True,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant context from ChromaDB with query expansion.

        Parameters
        ----------
        query : str
            User question
        top_k : int, default 5
            Number of chunks to retrieve
        category_filter : str, optional
            Category filter (e.g., "how-tos")
        use_query_expansion : bool, default True
            Whether to use multiple query variations

        Returns
        -------
        list[dict[str, Any]]
            Retrieved chunks with metadata and relevance scores
        """
        where: dict[str, str] | None = None
        if category_filter:
            where = {"category": category_filter}

        # Detect if this is a "why/benefits" question to boost homepage content
        query_lower = query.lower()
        is_why_question = any(
            word in query_lower
            for word in ["why", "should i use", "benefits", "advantages", "choose"]
        )

        queries = self.expand_query(query) if use_query_expansion else [query]
        all_results: dict[str, dict[str, Any]] = {}

        for q in queries:
            results = self.collection.query(
                query_texts=[q],
                n_results=top_k,
                where=where,
                include=["documents", "metadatas", "distances"],
            )

            if results["documents"] and len(results["documents"][0]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i]
                    distance = results["distances"][0][i] if "distances" in results else None

                    # Boost homepage content for "why" questions
                    if is_why_question and metadata.get("source") == "website":
                        distance = distance * 0.6 if distance is not None else 0.3

                    chunk_key = f"{metadata.get('file_path', '')}:{metadata.get('heading', '')}"

                    if chunk_key not in all_results or (
                        distance is not None and distance < all_results[chunk_key]["distance"]
                    ):
                        relevance = 1 / (1 + distance) if distance is not None else 0.5
                        all_results[chunk_key] = {
                            "text": doc,
                            "metadata": metadata,
                            "relevance": relevance,
                            "distance": distance,
                        }

        retrieved: list[dict[str, Any]] = [
            {
                "text": item["text"],
                "metadata": item["metadata"],
                "relevance": item["relevance"],
            }
            for item in all_results.values()
        ]
        retrieved.sort(key=lambda x: x["relevance"], reverse=True)

        return retrieved[:top_k]

    def generate_answer(
        self,
        query: str,
        context: list[dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 2000,
    ) -> dict[str, Any]:
        """Generate answer using Claude with retrieved context.

        Parameters
        ----------
        query : str
            User question
        context : list of dict
            Retrieved context chunks
        temperature : float, default 0.3
            LLM temperature (0.0-1.0)
        max_tokens : int, default 2000
            Maximum tokens in response

        Returns
        -------
        dict[str, Any]
            Dictionary with answer, sources, and metadata
        """
        context_str = "\n\n".join(
            [
                f"[Source: {chunk['metadata'].get('file_path', 'unknown')}]\n{chunk['text']}"
                for chunk in context
            ]
        )

        prompt = SYSTEM_PROMPT.format(context=context_str, question=query)

        try:
            # Time the LLM call
            llm_start = time.time()
            message = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            llm_time = time.time() - llm_start

            answer = message.content[0].text

            # Extract token usage
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            total_tokens = input_tokens + output_tokens

            # Calculate cost (Claude Sonnet 4 pricing as of Feb 2025)
            # Input: $3.00 per million tokens, Output: $15.00 per million tokens
            input_cost = (input_tokens / 1_000_000) * 3.00
            output_cost = (output_tokens / 1_000_000) * 15.00
            total_cost = input_cost + output_cost

            sources: list[dict[str, Any]] = []
            for chunk in context:
                source_info: dict[str, Any] = {
                    "file_path": chunk["metadata"].get("file_path", "unknown"),
                    "category": chunk["metadata"].get("category", "unknown"),
                    "title": chunk["metadata"].get("title", "unknown"),
                    "heading": chunk["metadata"].get("heading", ""),
                    "relevance": chunk["relevance"],
                }
                if source_info not in sources:
                    sources.append(source_info)

            return {
                "answer": answer,
                "sources": sources,
                "query": query,
                "model": "claude-sonnet-4-20250514",
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens,
                },
                "cost": total_cost,
                "llm_time": llm_time,
            }

        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "query": query,
                "error": str(e),
            }

    def answer_question(
        self,
        query: str,
        top_k: int = 5,
        temperature: float = 0.3,
        category_filter: str | None = None,
    ) -> dict[str, Any]:
        """Answer questions about Nebari documentation.

        Parameters
        ----------
        query : str
            User question
        top_k : int, default 5
            Number of context chunks to retrieve
        temperature : float, default 0.3
            LLM creativity (0.0-1.0)
        category_filter : str, optional
            Category filter

        Returns
        -------
        dict[str, Any]
            Dictionary with answer and metadata
        """
        # Time the entire operation
        total_start = time.time()

        # Time retrieval
        retrieval_start = time.time()
        context = self.retrieve_context(query=query, top_k=top_k, category_filter=category_filter)
        retrieval_time = time.time() - retrieval_start

        if not context:
            return {
                "answer": (
                    "I couldn't find relevant information in the Nebari documentation "
                    "to answer this question. Please try rephrasing or ask about a different topic."
                ),
                "sources": [],
                "query": query,
            }

        result = self.generate_answer(query=query, context=context, temperature=temperature)

        # Add timing information
        total_time = time.time() - total_start
        result["retrieval_time"] = retrieval_time
        result["total_time"] = total_time

        self.conversation_history.append({"query": query, "answer": result["answer"]})

        return result

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []


if __name__ == "__main__":
    agent = NebariAgent()

    test_query = "How do I deploy Nebari on AWS?"
    print(f"\nQuestion: {test_query}\n")

    result = agent.answer_question(test_query, top_k=3)

    print(f"Answer:\n{result['answer']}\n")
    print("\nSources:")
    for source in result["sources"]:
        print(f"  - {source['file_path']} (relevance: {source['relevance']:.2%})")
