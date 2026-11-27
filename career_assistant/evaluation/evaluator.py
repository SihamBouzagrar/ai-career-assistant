
from career_assistant.evaluation.metrics import (
    calculate_relevance,
    calculate_groundedness,
    calculate_hallucination_proxy,
    calculate_completeness,
)


class ResponseEvaluator:

    @staticmethod
    def evaluate(
        question,
        answer,
        context,
        expected_points
    ):
        """Evaluate one AI-generated response."""

        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Answer must not be empty.")

        if not isinstance(context, str):
            raise ValueError("Context must be a string.")

        if not isinstance(question, str):
            raise ValueError("Question must be a string.")

        if not isinstance(expected_points, list):
            raise ValueError("Expected points must be a list.")

        relevance = calculate_relevance(
            answer,
            expected_points
        )

        groundedness = calculate_groundedness(
            answer,
            context
        )

        hallucination_proxy = calculate_hallucination_proxy(
            answer,
            context
        )

        completeness = calculate_completeness(
            answer,
            expected_points
        )

        overall_score = round(
            (
                relevance
                + groundedness
                + completeness
                + (100 - hallucination_proxy)
            ) / 4,
            2
        )

        return {
            "question": question,
            "answer": answer,
            "metrics": {
                "relevance": relevance,
                "groundedness": groundedness,
                "hallucination_proxy": hallucination_proxy,
                "completeness": completeness,
                "overall_score": overall_score,
            }
        }
