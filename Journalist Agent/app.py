"""Streamlit entry point for AI Journalist Agent."""

from __future__ import annotations

import streamlit as st

from workflows import generate_article


st.set_page_config(page_title="AI Journalist Agent", page_icon="🗞️", layout="wide")

st.title("AI Journalist Agent")
st.caption("Research, draft, and edit structured articles with a coordinated multi agent workflow.")

with st.sidebar:
    st.header("Configuration")
    openai_api_key = st.text_input("OpenAI API key", type="password")
    serpapi_api_key = st.text_input("SerpAPI key", type="password")
    model_id = st.text_input("Model", value="gpt-4o")
    article_length = st.selectbox("Article length", options=("short", "balanced", "long"), index=1)

st.subheader("Article request")
topic = st.text_area(
    "What should the journalist agent write about?",
    placeholder="Example: The impact of AI agents on small business operations in 2026",
    height=120,
)

if st.button("Generate article", type="primary"):
    if not topic.strip():
        st.warning("Please enter an article topic.")
    elif not openai_api_key.strip() or not serpapi_api_key.strip():
        st.warning("Please enter both API keys in the sidebar.")
    else:
        with st.spinner("Researching, drafting, and editing the article..."):
            try:
                article = generate_article(
                    topic=topic,
                    openai_api_key=openai_api_key,
                    serpapi_api_key=serpapi_api_key,
                    model_id=model_id,
                    article_length=article_length,
                )
            except Exception as exc:
                st.error(f"The agent could not complete the article: {exc}")
            else:
                st.success("Article generated successfully.")
                st.markdown(article)
                st.download_button(
                    label="Download article as Markdown",
                    data=article,
                    file_name="ai_journalist_article.md",
                    mime="text/markdown",
                )
