"""Nebari Documentation Assistant - Streamlit UI.

A RAG-powered chatbot for answering questions about Nebari documentation.
"""

import os
import re
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from agent import NebariAgent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Nebari Documentation Assistant",
    page_icon="static/nebari-logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


def check_password() -> bool:
    """Check login credentials with username and password.

    Returns
    -------
    bool
        True if user is authenticated
    """
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
        st.image("static/nebari-logo.png", width=150)
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


def main() -> None:
    """Run the main Streamlit application."""
    # Check authentication first
    if not check_password():
        st.stop()

    # Title with Nebari logo
    col1, col2 = st.columns([1, 8])
    with col1:
        st.image("static/nebari-logo.png", width=120)
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

        # Logout button
        st.markdown("---")
        if st.button("Logout", width="stretch"):
            st.session_state.authenticated = False
            st.session_state.messages = []
            st.session_state.query_history = []
            if "agent" in st.session_state:
                del st.session_state.agent
            st.rerun()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    if "agent" not in st.session_state:
        with st.spinner("Loading agent..."):
            st.session_state.agent = load_agent()

    # Display chat history
    for message in st.session_state.messages:
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

            # Display sources
            if result.get("sources"):
                display_sources(result["sources"])

            # Add to chat history
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result.get("sources", []),
                }
            )


if __name__ == "__main__":
    main()
