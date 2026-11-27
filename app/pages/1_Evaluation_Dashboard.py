
import sys
import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from career_assistant.llm.client import OllamaClient
from career_assistant.evaluation.runner import EvaluationRunner


st.set_page_config(
    page_title="Evaluation Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Evaluation Dashboard")
st.caption(
    "Monitor LLM response quality, evaluate test cases "
    "and inspect evaluation history."
)

client = OllamaClient()

# --------------------------------------------------
# MODEL STATUS
# --------------------------------------------------

if client.health_check():
    st.success(f"Connected model: {client.model}")
else:
    st.error("Ollama is unavailable.")

# --------------------------------------------------
# RUN EVALUATION
# --------------------------------------------------

st.header("1. Automated Evaluation")

st.write(
    "Run the evaluation dataset against the configured Ollama model."
)

if st.button(
    "Run Evaluation",
    type="primary",
    disabled=not client.health_check()
):

    try:

        with st.spinner("Running evaluation cases..."):

            report = EvaluationRunner.run(client)

        st.session_state["latest_evaluation"] = report

        st.success(
            f"Evaluation completed: {report['total_cases']} test cases."
        )

    except Exception as error:

        st.error(f"Evaluation failed: {error}")


# --------------------------------------------------
# LATEST RESULTS
# --------------------------------------------------

report = st.session_state.get("latest_evaluation")

if report:

    st.divider()
    st.header("2. Latest Evaluation Results")

    st.caption(
        f"Run: {report['run_id']} | "
        f"Generator: {report['model']} | "
        f"Judge: {report['judge_model']}"
    )

    # LLM-as-a-Judge
    st.subheader("LLM-as-a-Judge Results")

    judge = report["judge_averages"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Relevance", f"{judge['relevance']}%")
    col2.metric("Faithfulness", f"{judge['faithfulness']}%")
    col3.metric("Completeness", f"{judge['completeness']}%")
    col4.metric("Accuracy", f"{judge['accuracy']}%")

    st.metric(
        "Judge Overall Score",
        f"{judge['overall_score']}%"
    )

    st.info(
        "The judge scores are model-generated evaluations. "
        "They should be interpreted as estimates, not objective proof."
    )

    # Lexical metrics
    with st.expander("View lexical evaluation metrics"):

        lexical = report["lexical_averages"]

        st.json(lexical)

    # Individual results
    st.subheader("Test Case Results")

    rows = []

    for result in report["results"]:

        rows.append({
            "Test ID": result["id"],
            "Relevance": result["judge_evaluation"]["scores"]["relevance"],
            "Faithfulness": result["judge_evaluation"]["scores"]["faithfulness"],
            "Completeness": result["judge_evaluation"]["scores"]["completeness"],
            "Accuracy": result["judge_evaluation"]["scores"]["accuracy"],
            "Overall": result["judge_evaluation"]["overall_score"]
        })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True
    )

    for result in report["results"]:

        with st.expander(
            f"Test {result['id']} — "
            f"{result['judge_evaluation']['overall_score']}%"
        ):

            st.markdown("**Question**")
            st.write(result["question"])

            st.markdown("**Generated answer**")
            st.write(result["answer"])

            st.markdown("**Judge explanation**")
            st.write(result["judge_evaluation"]["explanation"])

            st.markdown("**Strengths**")
            st.write(result["judge_evaluation"]["strengths"])

            st.markdown("**Issues detected**")
            st.write(result["judge_evaluation"]["issues"])

            st.markdown("**Detailed scores**")
            st.json(result["judge_evaluation"]["scores"])



# --------------------------------------------------
# EVALUATION HISTORY
# --------------------------------------------------

st.divider()
st.header("3. Evaluation History")

history_file = ROOT / "reports" / "evaluations" / "history.jsonl"

if history_file.exists():

    history = []

    with history_file.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                run = json.loads(line)

                if isinstance(run, dict):
                    history.append(run)

            except json.JSONDecodeError:
                continue

    if history:

        history_rows = []
        legacy_count = 0

        for run in history:

            judge = run.get("judge_averages")

            # Ignore old reports without LLM-as-a-Judge metrics
            if not isinstance(judge, dict):
                legacy_count += 1
                continue

            history_rows.append({
                "Run ID": run.get("run_id", "Unknown"),
                "Date": run.get("created_at", "Unknown"),
                "Generator": run.get("model", "Unknown"),
                "Judge": run.get("judge_model", "Unknown"),
                "Test cases": run.get("total_cases", 0),
                "Relevance": judge.get("relevance", 0),
                "Faithfulness": judge.get("faithfulness", 0),
                "Completeness": judge.get("completeness", 0),
                "Accuracy": judge.get("accuracy", 0),
                "Overall": judge.get("overall_score", 0)
            })

        if history_rows:

            history_df = pd.DataFrame(history_rows)

            st.dataframe(
                history_df.sort_values(
                    "Date",
                    ascending=False
                ),
                use_container_width=True
            )

            st.download_button(
                "Download Evaluation History",
                data=history_file.read_text(encoding="utf-8"),
                file_name="evaluation_history.jsonl",
                mime="application/json"
            )

        else:
            st.info(
                "No evaluation runs with LLM-as-a-Judge metrics yet. "
                "Run a new evaluation to generate compatible reports."
            )

        if legacy_count > 0:
            st.caption(
                f"{legacy_count} older evaluation(s) without "
                "LLM-as-a-Judge metrics were skipped."
            )

    else:
        st.info("No valid evaluation runs found.")

else:
    st.info(
        "No evaluation history yet. Run your first evaluation above."
    )


# --------------------------------------------------
# MODEL COMPARISON
# --------------------------------------------------

st.divider()
st.header("4. Model Comparison")

st.write(
    "Compare Qwen 2.5 3B and Llama 3.2 3B "
    "using the same evaluation dataset and a fixed judge."
)

if st.button(
    "Run Model Comparison",
    type="primary",
    disabled=not client.health_check()
):

    try:
        with st.spinner(
            "Comparing models... This may take several minutes."
        ):

            comparison = EvaluationRunner.compare_models(
                client=client,
                models=[
                    "qwen2.5:3b",
                    "llama3.2:3b"
                ],
                judge_model="qwen2.5:3b"
            )

        st.session_state["model_comparison"] = comparison

        st.success("Model comparison completed.")

    except Exception as error:
        st.error(f"Model comparison failed: {error}")


comparison = st.session_state.get("model_comparison")

if comparison:

    st.subheader("Comparison Results")

    rows = []

    for model_name, model_data in comparison[
        "comparison_results"
    ].items():

        judge = model_data["judge_averages"]
        lexical = model_data["lexical_averages"]

        rows.append({
            "Model": model_name,
            "Relevance": judge["relevance"],
            "Faithfulness": judge["faithfulness"],
            "Completeness": judge["completeness"],
            "Accuracy": judge["accuracy"],
            "Judge Overall": judge["overall_score"],
            "Lexical Overall": lexical["overall_score"]
        })

    comparison_df = pd.DataFrame(rows)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    best_model = max(
        comparison["comparison_results"].items(),
        key=lambda item: item[1]["judge_averages"]["overall_score"]
    )

    st.success(
        f"Highest Judge Overall Score: {best_model[0]} "
        f"({best_model[1]['judge_averages']['overall_score']}%)"
    )

    for model_name, model_data in comparison[
        "comparison_results"
    ].items():

        with st.expander(f"Detailed results — {model_name}"):

            st.markdown("**Judge metrics**")
            st.json(model_data["judge_averages"])

            st.markdown("**Lexical metrics**")
            st.json(model_data["lexical_averages"])

            detail_rows = []

            for result in model_data["results"]:

                detail_rows.append({
                    "Test ID": result["id"],
                    "Relevance": result["judge_evaluation"]["scores"]["relevance"],
                    "Faithfulness": result["judge_evaluation"]["scores"]["faithfulness"],
                    "Completeness": result["judge_evaluation"]["scores"]["completeness"],
                    "Accuracy": result["judge_evaluation"]["scores"]["accuracy"],
                    "Overall": result["judge_evaluation"]["overall_score"]
                })

            st.dataframe(
                pd.DataFrame(detail_rows),
                use_container_width=True,
                hide_index=True
            )

    st.download_button(
        "Download Model Comparison (JSON)",
        data=json.dumps(
            comparison,
            ensure_ascii=False,
            indent=4
        ),
        file_name="model_comparison.json",
        mime="application/json"
    )
