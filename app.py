"""Nebari Documentation Assistant - Streamlit UI.

A RAG-powered chatbot for answering questions about Nebari documentation.
"""

import hashlib
import os
import re
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import httpx
import streamlit as st
from dotenv import load_dotenv

# Optional: Cookie authentication (requires extra-streamlit-components)
try:
    from extra_streamlit_components import CookieManager

    COOKIES_AVAILABLE = True
except ImportError:
    COOKIES_AVAILABLE = False
    CookieManager = None

from agent import NebariAgent

# Load environment variables
load_dotenv()

# Base directory for all file paths (configurable via BASE_DIR env var)
BASE_DIR = Path(os.getenv("BASE_DIR", Path(__file__).parent))

# Authentication enabled only if both username and password are set
AUTH_ENABLED = bool(os.getenv("DEMO_USERNAME") and os.getenv("DEMO_PASSWORD"))

# Page configuration
st.set_page_config(
    page_title="Nebari Documentation Assistant",
    page_icon=str(BASE_DIR / "static" / "nebari-logo.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize cookie manager at module level with unique key (if available)
cookie_manager = CookieManager(key="nebari_cookie_manager") if COOKIES_AVAILABLE else None


def check_password() -> bool:
    """Check login credentials with username and password.

    Uses cookies to persist authentication for 7 days.

    Returns
    -------
    bool
        True if user is authenticated
    """
    # Skip authentication entirely if credentials not configured
    if not AUTH_ENABLED:
        return True

    # Get credentials from Streamlit secrets or environment variables
    correct_username = None
    correct_password = None

    try:
        if "DEMO_USERNAME" in st.secrets and "DEMO_PASSWORD" in st.secrets:
            correct_username = st.secrets["DEMO_USERNAME"]
            correct_password = st.secrets["DEMO_PASSWORD"]
    except (FileNotFoundError, KeyError):
        # Secrets file doesn't exist (local development) - try environment variables
        pass

    # Fall back to environment variables if not in secrets
    if not correct_username or not correct_password:
        correct_username = os.getenv("DEMO_USERNAME")
        correct_password = os.getenv("DEMO_PASSWORD")

    # Fail securely if credentials are not configured
    if not correct_username or not correct_password:
        st.error("❌ Authentication credentials not configured")
        st.info(
            "Please set DEMO_USERNAME and DEMO_PASSWORD in:\n"
            "- Streamlit Cloud: App Settings → Secrets\n"
            "- Local development: .env file"
        )
        st.code(
            'DEMO_USERNAME = "your_username"\n' 'DEMO_PASSWORD = "your_password"',
            language="toml",
        )
        st.stop()
        raise RuntimeError("Missing credentials")  # For type checker

    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Check cookie for existing auth (only works on HTTPS/deployed, not localhost)
    if cookie_manager is not None:
        cookies = cookie_manager.get_all()
        auth_cookie = cookies.get("nebari_auth") if cookies else None
        if auth_cookie and not st.session_state.authenticated:
            # Verify cookie hash
            expected_hash = hashlib.sha256(
                f"{correct_username}:{correct_password}".encode()
            ).hexdigest()
            if auth_cookie == expected_hash:
                st.session_state.authenticated = True
                return True

    # If already authenticated, return True
    if st.session_state.authenticated:
        return True

    # Show login page
    st.markdown(
        """
    <style>
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        background-color: #262730;
        border-radius: 10px;
        border: 1px solid #FF6B6B;
    }
    .login-title {
        text-align: center;
        color: #FF6B6B;
        font-size: 2em;
        margin-bottom: 30px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(str(BASE_DIR / "static" / "nebari-logo.png"), width=150)
        st.markdown("<h1 class='login-title'>Nebari Docs Assistant</h1>", unsafe_allow_html=True)
        st.markdown("###  Login Required")
        st.caption("Please enter your credentials to access the demo")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("Login", width="stretch")

            if submit:
                if username == correct_username and password == correct_password:
                    st.session_state.authenticated = True
                    # Set cookie for 7 days (max_age in seconds, requires HTTPS)
                    if cookie_manager is not None:
                        auth_hash = hashlib.sha256(f"{username}:{password}".encode()).hexdigest()
                        cookie_manager.set("nebari_auth", auth_hash, max_age=7 * 24 * 60 * 60)
                    st.success(" Login successful!")
                    st.rerun()
                else:
                    st.error(" Invalid username or password")

        st.markdown("---")
        st.caption("Demo credentials are available from the presenter")

    return False


# Custom CSS
st.markdown(
    """
<style>
.source-card {
    background-color: #262730;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
    border-left: 3px solid #FF6B6B;
}
.source-title {
    font-weight: bold;
    color: #FF6B6B;
    margin-bottom: 5px;
}
.source-meta {
    font-size: 0.9em;
    color: #888;
}
.relevance-high {
    color: #4CAF50;
}
.relevance-medium {
    color: #FFC107;
}
.relevance-low {
    color: #888;
}

/* Sidebar scroll indicator - gradient fade at bottom */
section[data-testid="stSidebar"] > div:first-child {
    position: relative;
}

section[data-testid="stSidebar"] > div:first-child::after {
    content: "↓ Scroll for more ↓";
    position: sticky;
    bottom: 0;
    left: 0;
    right: 0;
    height: 60px;
    background: linear-gradient(
        to bottom,
        transparent 0%,
        rgba(14, 17, 23, 0.95) 50%,
        rgba(14, 17, 23, 1) 100%
    );
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 10px;
    font-size: 0.85em;
    color: #FF6B6B;
    pointer-events: none;
    z-index: 999;
}

/* Hide scroll indicator when scrolled to bottom */
section[data-testid="stSidebar"] > div:first-child:not(:hover)::after {
    animation: fadeInOut 3s ease-in-out infinite;
}

@keyframes fadeInOut {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource  # type: ignore[misc]
def load_agent() -> NebariAgent:
    """Load the RAG agent with caching.

    Returns
    -------
    NebariAgent
        Initialized RAG agent instance
    """
    # Get API key from Streamlit secrets (cloud) or .env (local)
    api_key = None

    # Try Streamlit secrets first (for cloud deployment)
    try:
        if "ANTHROPIC_API_KEY" in st.secrets:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
    except (FileNotFoundError, KeyError):
        # Secrets file doesn't exist (local development)
        pass

    # Fall back to environment variable
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        st.error("ANTHROPIC_API_KEY not found.")
        st.info("Please set it in your `.env` file:")
        st.code("ANTHROPIC_API_KEY=sk-ant-your-key-here")
        st.info("Get your API key from: https://console.anthropic.com/")
        st.stop()
        raise RuntimeError("No API key")  # For type checker

    try:
        agent = NebariAgent(anthropic_api_key=api_key)
        return agent
    except (ValueError, RuntimeError) as e:
        st.error(f"Error loading agent: {e}")
        st.info("Make sure you've run `python ingest_docs.py` first to create the vector database.")
        st.stop()
        raise  # For type checker


def display_sources(sources: list[dict[str, Any]]) -> None:
    """Display source citations with clickable links to nebari.dev.

    Parameters
    ----------
    sources : list[dict[str, Any]]
        List of source dictionaries with metadata
    """
    if not sources:
        return

    with st.expander(f"Sources ({len(sources)} documents)", expanded=False):
        for i, source in enumerate(sources):
            relevance = source.get("relevance", 0)

            # Color code relevance
            if relevance > 0.7:
                relevance_class = "relevance-high"
                relevance_emoji = "🟢"
            elif relevance > 0.5:
                relevance_class = "relevance-medium"
                relevance_emoji = "🟡"
            else:
                relevance_class = "relevance-low"
                relevance_emoji = ""

            # Get URL - website sources have 'url', docs have 'file_path'
            if "url" in source:
                # Website source - use URL directly
                doc_url = source["url"]
            else:
                # Documentation source - convert file path to URL
                file_path = source.get("file_path", "")
                # Remove .md or .mdx extension and convert to URL
                doc_path = file_path.replace(".mdx", "").replace(".md", "")
                doc_url = f"https://nebari.dev/docs/{doc_path}"

            title = source.get("title", "Unknown")
            heading_text = f"→ {source.get('heading', '')}" if source.get("heading") else ""
            st.markdown(
                f"""
            <div class="source-card">
                <div class="source-title">
                     <a href="{doc_url}" target="_blank"
                        style="color: #FF6B6B; text-decoration: none;">{title}</a>
                    {heading_text}
                </div>
                <div class="source-meta">
                    Category: {source.get('category', 'unknown')} |
                    <a href="{doc_url}" target="_blank"
                       style="color: #FF6B6B;"> View full page</a> |
                    Relevance: <span class="{relevance_class}">
                    {relevance_emoji} {relevance:.1%}</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


def export_conversation_to_markdown() -> str:
    """Export conversation history to Markdown format.

    Returns
    -------
    str
        Formatted Markdown string of the conversation
    """
    lines = ["# Nebari Documentation Chat Export\n"]
    lines.append(f"*Exported: {st.session_state.get('export_time', 'Unknown')}*\n")
    lines.append("---\n\n")

    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            lines.append(f"## Question {i//2 + 1}\n")
            lines.append(f"{msg['content']}\n\n")
        else:
            lines.append("### Answer\n")
            lines.append(f"{msg['content']}\n\n")

            if msg.get("sources"):
                lines.append("**Sources:**\n")
                for source in msg["sources"]:
                    title = source.get("title", "Unknown")
                    category = source.get("category", "unknown")
                    lines.append(f"- {title} ({category})\n")
                lines.append("\n")

            if msg.get("metrics"):
                metrics = msg["metrics"]
                lines.append(f"*Response time: {metrics['total_time']:.2f}s | ")
                lines.append(f"Tokens: {metrics['tokens']['total']} | ")
                lines.append(f"Cost: ${metrics['cost']:.4f}*\n\n")

            lines.append("---\n\n")

    return "".join(lines)


def export_conversation_with_images() -> bytes:
    """Export conversation as a zip file with markdown and images.

    Downloads all images referenced in the conversation and packages them
    with the chat markdown in a folder structure.

    Returns
    -------
    bytes
        Zip file contents as bytes
    """
    # Extract all image URLs from messages
    image_pattern = r"!\[([^\]]*)\]\((https://[^\)]+\.(?:png|jpg|jpeg|gif|svg))\)"
    image_urls = set()

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            images = re.findall(image_pattern, msg["content"])
            for _, url in images:
                image_urls.add(url)

    # Create markdown content with local image paths
    lines = ["# Nebari Documentation Chat Export\n"]
    lines.append(f"*Exported: {st.session_state.get('export_time', 'Unknown')}*\n")
    lines.append("---\n\n")

    # Map URLs to local filenames
    url_to_filename: dict[str, str] = {}
    for idx, url in enumerate(sorted(image_urls)):
        ext = Path(url).suffix or ".png"
        filename = f"image_{idx + 1}{ext}"
        url_to_filename[url] = filename

    # Build markdown with local image references
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            lines.append(f"## Question {i//2 + 1}\n")
            lines.append(f"{msg['content']}\n\n")
        else:
            lines.append("### Answer\n")
            # Replace image URLs with local paths
            content = msg["content"]
            for url, filename in url_to_filename.items():
                content = content.replace(url, f"images/{filename}")
            lines.append(f"{content}\n\n")

            if msg.get("sources"):
                lines.append("**Sources:**\n")
                for source in msg["sources"]:
                    title = source.get("title", "Unknown")
                    category = source.get("category", "unknown")
                    lines.append(f"- {title} ({category})\n")
                lines.append("\n")

            if msg.get("metrics"):
                metrics = msg["metrics"]
                lines.append(f"*Response time: {metrics['total_time']:.2f}s | ")
                lines.append(f"Tokens: {metrics['tokens']['total']} | ")
                lines.append(f"Cost: ${metrics['cost']:.4f}*\n\n")

            lines.append("---\n\n")

    markdown_content = "".join(lines)

    # Create zip file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add markdown file
        zip_file.writestr("chat.md", markdown_content)

        # Download and add images
        if image_urls:
            with httpx.Client(timeout=30.0) as client:
                for url, filename in url_to_filename.items():
                    try:
                        response = client.get(url)
                        response.raise_for_status()
                        zip_file.writestr(f"images/{filename}", response.content)
                    except Exception:  # nosec B110
                        # Skip images that fail to download silently
                        pass

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def main() -> None:
    """Run the main Streamlit application."""
    # Check authentication first
    if not check_password():
        st.stop()

    # Initialize session state FIRST
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    if "feedback" not in st.session_state:
        st.session_state.feedback = {}

    if "total_tokens" not in st.session_state:
        st.session_state.total_tokens = 0

    if "total_cost" not in st.session_state:
        st.session_state.total_cost = 0.0

    if "agent" not in st.session_state:
        with st.spinner("Loading agent..."):
            st.session_state.agent = load_agent()

    # Title with Nebari logo
    col1, col2 = st.columns([1, 8])
    with col1:
        st.image(str(BASE_DIR / "static" / "nebari-logo.png"), width=120)
    with col2:
        st.markdown(
            "<h1 style='margin-top: 20px;'>Nebari Documentation Assistant</h1>",
            unsafe_allow_html=True,
        )
    st.caption("Ask questions about deploying and managing Nebari - powered by Claude & RAG")

    # Sidebar
    with st.sidebar:
        st.title("Settings")

        # Retrieval settings
        top_k = st.slider(
            "Sources to retrieve",
            min_value=3,
            max_value=10,
            value=5,
            help="Number of documentation chunks to use as context",
        )

        temperature = st.slider(
            "Creativity",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Higher values make responses more creative but less factual",
        )

        # Category filter
        category_filter_select = st.selectbox(
            "Filter by category",
            options=[
                "All",
                "get-started",
                "tutorials",
                "how-tos",
                "explanations",
                "references",
            ],
            index=0,
            help="Narrow search to specific documentation category",
        )
        category_filter = None if category_filter_select == "All" else category_filter_select

        st.markdown("---")

        # Session stats
        st.title("📊 Session Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tokens", f"{st.session_state.total_tokens:,}")
            helpful_count = sum(1 for f in st.session_state.feedback.values() if f == "helpful")
            st.metric("👍 Helpful", helpful_count)
        with col2:
            st.metric("Total Cost", f"${st.session_state.total_cost:.4f}")
            not_helpful_count = sum(
                1 for f in st.session_state.feedback.values() if f == "not_helpful"
            )
            st.metric("👎 Not Helpful", not_helpful_count)

        # Export conversation
        if st.session_state.messages:
            st.session_state.export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create two columns for export buttons
            export_col1, export_col2 = st.columns(2)

            with export_col1:
                # Simple markdown export
                markdown_content = export_conversation_to_markdown()
                st.download_button(
                    label="📄 Markdown",
                    data=markdown_content,
                    file_name=f"nebari_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    width="stretch",
                    help="Download as markdown file only",
                )

            with export_col2:
                # Zip export with images
                with st.spinner("Preparing zip..."):
                    zip_content = export_conversation_with_images()
                st.download_button(
                    label="📦 Zip+Images",
                    data=zip_content,
                    file_name=f"nebari_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    width="stretch",
                    help="Download zip with markdown and images",
                )

        st.markdown("---")

        # Example questions
        st.title("Quick Start")
        st.caption("Try these example questions:")

        example_questions = [
            "Why should we use Nebari?",
            "Show me the Nebari architecture diagram",
            "How do I deploy Nebari on AWS?",
            "What is the difference between local and cloud deployment?",
            "How do I configure authentication with Keycloak?",
        ]

        for question in example_questions:
            if st.button(question, key=f"example_{hash(question)}"):
                st.session_state.example_query = question

        st.markdown("---")

        # Recent queries history
        st.title("Recent Queries")
        if "query_history" in st.session_state and st.session_state.query_history:
            st.caption("Click to re-ask:")
            for query in reversed(st.session_state.query_history[-5:]):  # Show last 5
                if st.button(f"↩ {query[:40]}...", key=f"history_{hash(query)}", width="stretch"):
                    st.session_state.example_query = query
        else:
            st.caption("No recent queries yet")

        st.markdown("---")

        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.query_history = []
            if "agent" in st.session_state:
                st.session_state.agent.clear_history()
            st.rerun()

        # Info
        st.markdown("---")
        st.caption("""
        **About this app:**

        This RAG-powered assistant uses the official Nebari documentation
        to answer your questions. It retrieves relevant sections and uses
        Claude Sonnet 4 to synthesize helpful answers.

        Built with Streamlit, ChromaDB, and Anthropic Claude

        **GitHub Repository:**
        [github.com/goanpeca/nabari-docs-rag-demo](https://github.com/goanpeca/nabari-docs-rag-demo)

        Built by [@goanpeca](https://www.linkedin.com/in/goanpeca) | © 2026
        """)

        # Logout button (only show if authentication is enabled)
        if AUTH_ENABLED:
            st.markdown("---")
            if st.button("Logout", width="stretch"):
                # Clear cookie (if available)
                if cookie_manager is not None:
                    try:
                        cookie_manager.delete("nebari_auth")
                    except KeyError:
                        # Cookie doesn't exist, that's fine
                        pass
                # Clear session
                st.session_state.authenticated = False
                st.session_state.messages = []
                st.session_state.query_history = []
                if "agent" in st.session_state:
                    del st.session_state.agent
                st.rerun()

    # Display chat history
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            # Display text
            st.markdown(message["content"])

            # Render images if present in message
            if message["role"] == "assistant":
                image_pattern = r"!\[([^\]]*)\]\((https://[^\)]+\.(?:png|jpg|jpeg|gif|svg))\)"
                images = re.findall(image_pattern, message["content"])
                if images:
                    st.markdown("---")
                    for alt_text, img_url in images:
                        st.image(
                            img_url,
                            caption=alt_text or "Nebari Documentation Image",
                            width="stretch",
                        )

                # Display metrics and feedback for assistant messages
                if message.get("metrics"):
                    metrics = message["metrics"]
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
                    with col1:
                        st.caption(f"⚡ {metrics['total_time']:.2f}s")
                    with col2:
                        st.caption(f"🔢 {metrics['tokens']['total']} tokens")
                    with col3:
                        st.caption(f"💰 ${metrics['cost']:.4f}")
                    with col4:
                        # Feedback buttons
                        feedback_col1, feedback_col2 = st.columns(2)
                        with feedback_col1:
                            if st.button("👍 Helpful", key=f"helpful_{idx}"):
                                st.session_state.feedback[idx] = "helpful"
                                st.rerun()
                        with feedback_col2:
                            if st.button("👎 Not Helpful", key=f"not_helpful_{idx}"):
                                st.session_state.feedback[idx] = "not_helpful"
                                st.rerun()

                        # Show current feedback
                        if idx in st.session_state.feedback:
                            if st.session_state.feedback[idx] == "helpful":
                                st.success("✓ Marked as helpful")
                            else:
                                st.warning("✓ Marked as not helpful")

                # Display retrieval quality visualization
                if message.get("retrieval_scores"):
                    with st.expander("🎯 Retrieval Quality", expanded=False):
                        st.caption("Semantic similarity scores (lower = better match)")
                        for i, score_info in enumerate(message["retrieval_scores"]):
                            # Color code by relevance
                            if score_info["distance"] < 0.4:
                                icon = "🟢"
                                quality = "High"
                            elif score_info["distance"] < 0.7:
                                icon = "🟡"
                                quality = "Medium"
                            else:
                                icon = "⚪"
                                quality = "Low"

                            st.markdown(
                                f"{icon} **{score_info['title']}** - "
                                f"Distance: {score_info['distance']:.3f} ({quality})"
                            )

            if message.get("sources"):
                display_sources(message["sources"])

    # Handle example question click
    if "example_query" in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query
    else:
        query = st.chat_input("Ask about Nebari...")

    # Process query
    if query:
        # Add to query history
        if query not in st.session_state.query_history:
            st.session_state.query_history.append(query)

        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("user"):
            st.markdown(query)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.agent.answer_question(
                    query=query,
                    top_k=top_k,
                    temperature=temperature,
                    category_filter=category_filter,
                )

            # Display answer with embedded images
            answer_text = result["answer"]

            # Extract and render images
            image_pattern = r"!\[([^\]]*)\]\((https://[^\)]+\.(?:png|jpg|jpeg|gif|svg))\)"
            images = re.findall(image_pattern, answer_text)

            # Display the text answer
            st.markdown(answer_text)

            # Render images below the text
            if images:
                st.markdown("---")
                for alt_text, img_url in images:
                    st.image(
                        img_url,
                        caption=alt_text or "Nebari Documentation Image",
                        width="stretch",
                    )

            # Display metrics
            if result.get("tokens"):
                metrics = {
                    "total_time": result.get("total_time", 0),
                    "tokens": result["tokens"],
                    "cost": result.get("cost", 0),
                }

                # Update session totals
                st.session_state.total_tokens += metrics["tokens"]["total"]
                st.session_state.total_cost += metrics["cost"]

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.caption(f"⚡ {metrics['total_time']:.2f}s")
                    st.caption(f"  ├─ Retrieval: {result.get('retrieval_time', 0):.2f}s")
                    st.caption(f"  └─ LLM: {result.get('llm_time', 0):.2f}s")
                with col2:
                    st.caption(f"🔢 {metrics['tokens']['total']} tokens")
                    st.caption(f"  ├─ Input: {metrics['tokens']['input']}")
                    st.caption(f"  └─ Output: {metrics['tokens']['output']}")
                with col3:
                    st.caption(f"💰 ${metrics['cost']:.4f}")

            # Display retrieval quality
            if result.get("sources"):
                retrieval_scores = [
                    {
                        "title": s.get("title", "Unknown"),
                        "distance": 1 - s.get("relevance", 0),  # Convert relevance to distance
                    }
                    for s in result["sources"]
                ]

                with st.expander("🎯 Retrieval Quality", expanded=False):
                    st.caption("Semantic similarity scores (lower = better match)")
                    for score_info in retrieval_scores:
                        # Color code by relevance
                        if score_info["distance"] < 0.4:
                            icon = "🟢"
                            quality = "High"
                        elif score_info["distance"] < 0.7:
                            icon = "🟡"
                            quality = "Medium"
                        else:
                            icon = "⚪"
                            quality = "Low"

                        st.markdown(
                            f"{icon} **{score_info['title']}** - "
                            f"Distance: {score_info['distance']:.3f} ({quality})"
                        )

                display_sources(result["sources"])

            # Add to chat history
            message_data = {
                "role": "assistant",
                "content": result["answer"],
                "sources": result.get("sources", []),
            }

            if result.get("tokens"):
                message_data["metrics"] = {
                    "total_time": result.get("total_time", 0),
                    "tokens": result["tokens"],
                    "cost": result.get("cost", 0),
                }
                message_data["retrieval_scores"] = retrieval_scores

            st.session_state.messages.append(message_data)

            # Force rerun to update sidebar stats immediately
            st.rerun()


if __name__ == "__main__":
    main()
