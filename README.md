# AI Career Assistant

An AI-powered career analysis platform that evaluates the compatibility between a candidate's CV and a job description, identifies skill gaps, and generates personalized career recommendations using Large Language Models (LLMs).

## Features

- **CV Analysis:** Extract text and information from PDF resumes.
- **Job Description Processing:** Upload a PDF, provide a job posting URL, or paste job description text.
- **Skill Extraction:** Identify technical skills using NLP and rule-based extraction.
- **Requirement Classification:** Distinguish required and preferred skills.
- **CV–Job Matching:** Calculate skill coverage, weighted matching scores, and identify missing skills.
- **AI Career Recommendations:** Generate context-aware recommendations using locally hosted LLMs.
- **Response Evaluation:** Assess generated answers using lexical evaluation metrics.
- **LLM-as-a-Judge:** Evaluate relevance, faithfulness, completeness, and accuracy.
- **Model Benchmarking:** Compare different local LLMs using a shared evaluation dataset.
- **Evaluation Dashboard:** Visualize evaluation results, model comparisons, and historical reports.

## Architecture

The project follows a modular Python architecture.

```text
ai-career-assistant/
├── app/
│   ├── streamlit_app.py
│   └── pages/
│       └── 1_Evaluation_Dashboard.py
├── career_assistant/
│   ├── document/
│   ├── extraction/
│   ├── matching/
│   ├── llm/
│   └── evaluation/
├── data/
│   └── evaluation/
├── reports/
│   └── evaluations/
├── tests/
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── README.md
```

### Main Components

| Module | Responsibility |
|---|---|
| `document` | PDF parsing and job URL extraction |
| `extraction` | Skill extraction and job requirement classification |
| `matching` | Candidate–job skill matching and scoring |
| `llm` | Ollama integration and AI-generated recommendations |
| `evaluation` | Evaluation metrics, LLM-as-a-Judge, and model benchmarking |
| `app` | Streamlit user interface and evaluation dashboard |
| `tests` | Automated unit tests |

## Tech Stack

- **Language:** Python 3.13
- **Frontend:** Streamlit
- **PDF Processing:** PyMuPDF
- **NLP / Data Processing:** Scikit-learn, Pandas
- **LLM Runtime:** Ollama
- **Models:** Qwen 2.5 3B, Llama 3.2 3B
- **Containerization:** Docker, Docker Compose
- **Testing:** Pytest

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/SihamBouzagrar/ai-career-assistant.git
cd ai-career-assistant
```

### 2. Install Ollama

Install Ollama from:

https://ollama.com/

Download the models:

```bash
ollama pull qwen2.5:3b
ollama pull llama3.2:3b
```

Verify installed models:

```bash
ollama list
```

### 3. Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

Example configuration:

```env
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b
REQUEST_TIMEOUT=120
```

Do not commit your `.env` file or API credentials.

### 4. Build and launch with Docker

```bash
docker compose up -d --build
```

Access the application:

- Main application: http://localhost:8501
- Evaluation Dashboard: available through the Streamlit navigation menu.

## Evaluation Framework

The project includes two complementary evaluation approaches.

### 1. Lexical Evaluation

The deterministic evaluation module calculates:

- Relevance
- Groundedness
- Hallucination proxy
- Completeness
- Overall score

These metrics are based on lexical overlap and should be interpreted as heuristic indicators rather than factual verification.

### 2. LLM-as-a-Judge

An LLM evaluates generated responses across four dimensions:

- Relevance
- Faithfulness
- Completeness
- Accuracy

Each criterion is scored from 1 to 5 and converted to a percentage.

### 3. Model Benchmarking

Two local models were evaluated using the same three test scenarios:

- Qwen 2.5 3B
- Llama 3.2 3B

Qwen 2.5 3B was used as the fixed evaluator.

#### Experimental Results

| Metric | Qwen 2.5 3B | Llama 3.2 3B |
|---|---:|---:|
| Relevance | 93.33% | 86.67% |
| Faithfulness | 46.67% | 60.00% |
| Completeness | 66.67% | 73.33% |
| Accuracy | 93.33% | 68.33% |
| Judge Overall | **73.33%** | 51.38% |
| Lexical Overall | 53.33% | 46.21% |

Qwen 2.5 3B obtained the highest overall judge score in this initial experiment.

**Evaluation limitations:** The benchmark currently contains only three scenarios. The evaluator is also one of the compared models, so the results are preliminary and may contain evaluator bias. Larger datasets and independent evaluation models are needed for more reliable conclusions.

## Running Tests

Execute the automated test suite inside the Docker container:

```bash
docker exec ai-career-assistant pytest -v
```

Latest test results:

```text
27 passed in 0.89s
```

## Current Project Status

- CV and job description processing
- Skill extraction and classification
- Candidate–job matching
- Local LLM integration
- Context-aware career recommendations
- Lexical response evaluation
- LLM-as-a-Judge
- Automated model comparison
- Streamlit evaluation dashboard
- Automated test suite

## Future Improvements

- Expand the evaluation dataset with more realistic scenarios.
- Introduce an independent LLM evaluator.
- Improve semantic groundedness and factual consistency evaluation.
- Add persistent experiment tracking and richer visualizations.
- Improve skill extraction using semantic NLP techniques.

## Author

**Siham Bouzagrar**

Engineering Student — GIS 

GitHub: [SihamBouzagrar](https://github.com/SihamBouzagrar)

LinkedIn: [Siham Bouzagrar](https://www.linkedin.com/in/siham-bouzagrar-262711251/)
