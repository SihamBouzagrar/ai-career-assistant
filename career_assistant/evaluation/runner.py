
import json
from datetime import datetime, timezone
from pathlib import Path

from career_assistant.evaluation.evaluator import ResponseEvaluator
from career_assistant.evaluation.llm_judge import LLMJudge


class EvaluationRunner:

    @staticmethod
    def _load_dataset(dataset_path):
        dataset_file = Path(dataset_path)

        if not dataset_file.exists():
            raise FileNotFoundError(
                f"Evaluation dataset not found: {dataset_file}"
            )

        with dataset_file.open("r", encoding="utf-8") as file:
            dataset = json.load(file)

        if not isinstance(dataset, list) or not dataset:
            raise ValueError(
                "Evaluation dataset must be a non-empty list."
            )

        return dataset

    @staticmethod
    def _evaluate_case(generator, judge, item):

        question = item["question"]
        context = item["context"]
        expected_points = item["expected_points"]

        prompt = f"""
You are an AI Career Assistant.

Answer the user's question using only the context below.
Do not invent information.
If the context does not contain enough information, say so.

CONTEXT:
{context}

QUESTION:
{question}

Provide a concise and useful answer.
"""

        answer = generator.generate(prompt)

        lexical_evaluation = ResponseEvaluator.evaluate(
            question=question,
            answer=answer,
            context=context,
            expected_points=expected_points
        )

        judge_evaluation = LLMJudge.evaluate(
            client=judge,
            question=question,
            context=context,
            answer=answer,
            expected_points=expected_points
        )

        return {
            "id": item["id"],
            "question": question,
            "answer": answer,
            "lexical_evaluation": lexical_evaluation["metrics"],
            "judge_evaluation": judge_evaluation
        }

    @staticmethod
    def _calculate_averages(results):

        if not results:
            raise ValueError("No evaluation results to summarize.")

        lexical_names = [
            "relevance",
            "groundedness",
            "hallucination_proxy",
            "completeness",
            "overall_score"
        ]

        judge_names = [
            "relevance",
            "faithfulness",
            "completeness",
            "accuracy"
        ]

        lexical_averages = {}

        for name in lexical_names:
            values = [
                result["lexical_evaluation"][name]
                for result in results
            ]

            lexical_averages[name] = round(
                sum(values) / len(values), 2
            )

        judge_averages = {}

        for name in judge_names:
            values = [
                result["judge_evaluation"]["scores"][name]
                for result in results
            ]

            judge_averages[name] = round(
                sum(values) / len(values), 2
            )

        judge_averages["overall_score"] = round(
            sum(
                result["judge_evaluation"]["overall_score"]
                for result in results
            ) / len(results),
            2
        )

        return lexical_averages, judge_averages

    @staticmethod
    def _save_report(report, output_dir):

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        report_file = (
            output_path / f"evaluation_{report['run_id']}.json"
        )

        with report_file.open("w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                ensure_ascii=False,
                indent=4
            )

        history_file = output_path / "history.jsonl"

        with history_file.open("a", encoding="utf-8") as file:
            file.write(
                json.dumps(report, ensure_ascii=False) + "\n"
            )

        return report

    @staticmethod
    def run(
        client,
        dataset_path="data/evaluation/evaluation_dataset.json",
        output_dir="reports/evaluations"
    ):

        dataset = EvaluationRunner._load_dataset(dataset_path)

        results = []

        for item in dataset:
            results.append(
                EvaluationRunner._evaluate_case(
                    generator=client,
                    judge=client,
                    item=item
                )
            )

        lexical_averages, judge_averages = (
            EvaluationRunner._calculate_averages(results)
        )

        now = datetime.now(timezone.utc)

        report = {
            "run_id": now.strftime("%Y%m%d_%H%M%S"),
            "created_at": now.isoformat(),
            "model": getattr(client, "model", "unknown"),
            "judge_model": getattr(client, "model", "unknown"),
            "total_cases": len(results),
            "lexical_averages": lexical_averages,
            "judge_averages": judge_averages,
            "results": results
        }

        return EvaluationRunner._save_report(
            report,
            output_dir
        )

    @staticmethod
    def compare_models(
        client,
        models=None,
        judge_model="qwen2.5:3b",
        dataset_path="data/evaluation/evaluation_dataset.json",
        output_dir="reports/evaluations"
    ):

        if models is None:
            models = [
                "qwen2.5:3b",
                "llama3.2:3b"
            ]

        if len(models) < 2:
            raise ValueError(
                "At least two models are required for comparison."
            )

        if len(set(models)) != len(models):
            raise ValueError(
                "Duplicate model names are not allowed."
            )

        dataset = EvaluationRunner._load_dataset(dataset_path)

        comparison_results = {}

        for model_name in models:

            print(f"Evaluating generator: {model_name}")

            generator = type(client)(model=model_name)
            judge = type(client)(model=judge_model)

            if not generator.health_check():
                raise ConnectionError(
                    f"Ollama is unavailable for model: {model_name}"
                )

            model_results = []

            for index, item in enumerate(dataset, start=1):

                print(
                    f"[{model_name}] "
                    f"Test {index}/{len(dataset)}: {item['id']}"
                )

                result = EvaluationRunner._evaluate_case(
                    generator=generator,
                    judge=judge,
                    item=item
                )

                model_results.append(result)

            lexical_averages, judge_averages = (
                EvaluationRunner._calculate_averages(
                    model_results
                )
            )

            comparison_results[model_name] = {
                "model": model_name,
                "judge_model": judge_model,
                "total_cases": len(model_results),
                "lexical_averages": lexical_averages,
                "judge_averages": judge_averages,
                "results": model_results
            }

        now = datetime.now(timezone.utc)

        report = {
            "run_id": now.strftime("%Y%m%d_%H%M%S"),
            "created_at": now.isoformat(),
            "type": "model_comparison",
            "models": models,
            "judge_model": judge_model,
            "total_cases": len(dataset),
            "comparison_results": comparison_results
        }

        return EvaluationRunner._save_report(
            report,
            output_dir
        )
