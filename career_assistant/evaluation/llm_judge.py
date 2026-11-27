
import json
import re


class LLMJudge:

    CRITERIA = [
        "relevance",
        "faithfulness",
        "completeness",
        "accuracy",
    ]

    @staticmethod
    def _extract_json(text):
        """Extract a JSON object from the model response."""

        if not isinstance(text, str):
            raise ValueError("Judge response must be a string.")

        text = text.strip()

        # Remove Markdown code fences if present.
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            raise ValueError("No valid JSON found in judge response.")

        return json.loads(match.group(0))

    @classmethod
    def evaluate(cls, client, question, context, answer, expected_points):

        prompt = f"""
You are an independent evaluator of an AI career assistant.

Evaluate the answer using ONLY the supplied context and expected points.

QUESTION:
{question}

CONTEXT:
{context}

EXPECTED POINTS:
{json.dumps(expected_points, ensure_ascii=False)}

GENERATED ANSWER:
{answer}

Score each criterion from 1 to 5:
1 = Very poor
2 = Poor
3 = Acceptable
4 = Good
5 = Excellent

Criteria:
- relevance: Does the answer address the question?
- faithfulness: Are factual claims supported by the context?
- completeness: Does it cover the expected points?
- accuracy: Does it avoid unsupported or incorrect claims?

Do not reward invented candidate skills or job requirements.
If information is unavailable in the context, the answer should say so.

Return ONLY valid JSON using this exact structure:
{{
  "relevance": 1,
  "faithfulness": 1,
  "completeness": 1,
  "accuracy": 1,
  "explanation": "Short explanation of the evaluation",
  "strengths": ["strength 1"],
  "issues": ["issue 1"]
}}
"""

        raw_response = client.generate(prompt)
        result = cls._extract_json(raw_response)

        scores = {}

        for criterion in cls.CRITERIA:

            value = result.get(criterion)

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"Invalid judge score for {criterion}."
                )

            if value < 1 or value > 5:
                raise ValueError(
                    f"{criterion} score must be between 1 and 5."
                )

            scores[criterion] = round(float(value) * 20, 2)

        overall = round(
            sum(scores.values()) / len(scores),
            2
        )

        return {
            "scores": scores,
            "overall_score": overall,
            "explanation": str(result.get("explanation", "")),
            "strengths": result.get("strengths", []),
            "issues": result.get("issues", []),
        }
