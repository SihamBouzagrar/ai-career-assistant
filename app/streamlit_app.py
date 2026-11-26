import sys
from pathlib import Path

import streamlit as st

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from career_assistant.llm.client import OllamaClient


st.set_page_config(
    page_title="AI Career Assistant",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Career Assistant")

st.caption(
    "An AI-powered application for CV analysis and job matching."
)

client = OllamaClient()

st.subheader("LLM Backend Status")

if client.health_check():
    st.success(f"Ollama connected | Model: {client.model}")
else:
    st.error("Ollama is not available. Start the Ollama service.")

st.divider()

st.subheader("Test the AI Assistant")

prompt = st.text_area(
    "Enter your question",
    placeholder="How can I improve my CV for an AI Engineer position?"
)

if st.button("Generate response"):

    if not prompt.strip():
        st.warning("Please enter a question.")

    elif not client.health_check():
        st.error("Ollama is unavailable.")

    else:
        with st.spinner("Generating response..."):

            try:
                answer = client.generate(prompt)

                st.markdown("### AI Response")
                st.write(answer)

            except Exception as error:
                st.error(f"Generation failed: {error}")