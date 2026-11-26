@'
# AI Career Assistant

An AI-powered application designed to analyze CVs, compare candidate
profiles with job descriptions, identify skill gaps, and generate
personalized career recommendations.

## Features

- PDF CV and job description extraction
- NLP-based skill extraction
- CV-job matching and similarity scoring
- Local LLM integration with Ollama
- AI-powered career recommendations
- Automated evaluation framework
- LLM-as-a-Judge
- Evaluation benchmarking

## Tech Stack

- Python
- Streamlit
- PyMuPDF
- Scikit-learn
- Ollama
- Pytest

## Architecture

The application is organized into independent modules:

- document: PDF processing
- extraction: skill extraction
- matching: candidate-job matching
- llm: LLM integration
- evaluation: automated evaluation and benchmarking

## Installation

```bash
git clone https://github.com/SihamBouzagrar/ai-career-assistant.git
cd ai-career-assistant

python -m venv venv