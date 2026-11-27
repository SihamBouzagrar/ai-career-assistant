
import re


class JobRequirementsExtractor:
    """
    Classifies detected job skills using the surrounding text.

    Skills explicitly identified as preferred are classified
    separately. Other skills remain unclassified and are handled
    conservatively by the SkillMatcher.
    """

    REQUIRED_PATTERNS = [
        r"\brequired\b",
        r"\bmust have\b",
        r"\bmust[- ]have\b",
        r"\bmandatory\b",
        r"\bessential\b",
        r"\bminimum requirements?\b",
        r"\bcompétences obligatoires\b",
        r"\bcompétences requises\b",
        r"\bexigé(?:e)?s?\b",
        r"\bindispensable(?:s)?\b",
        r"\bmaîtrise de\b",
        r"\bmaitrise de\b",
        r"\bvous devez\b",
        r"\bdoit maîtriser\b",
    ]

    PREFERRED_PATTERNS = [
        r"\bpreferred\b",
        r"\bnice to have\b",
        r"\bgood to have\b",
        r"\bdesirable\b",
        r"\ba plus\b",
        r"\batout\b",
        r"\bbonus\b",
        r"\bwould be an advantage\b",
        r"\bis a plus\b",
        r"\bserait un plus\b",
        r"\bserait apprécié\b",
        r"\bsouhaité(?:e)?s?\b",
        r"\bde préférence\b",
        r"\bconstituent un avantage\b",
    ]

    @staticmethod
    def _normalize(text):
        return re.sub(r"\s+", " ", text.lower())

    @classmethod
    def _contains_pattern(cls, text, patterns):
        return any(
            re.search(pattern, text, re.IGNORECASE)
            for pattern in patterns
        )

    @classmethod
    def extract(cls, job_text, detected_skills):
        if not isinstance(job_text, str) or not job_text.strip():
            return {
                "required": [],
                "preferred": [],
                "unclassified": [],
                "classification_complete": False,
            }

        normalized_text = cls._normalize(job_text)

        required = []
        preferred = []
        unclassified = []

        for item in detected_skills or []:
            skill = item.get("skill", "")

            if not skill:
                continue

            # Find the skill's evidence snippets in the original text.
            evidence = item.get("evidence", [])
            contexts = [cls._normalize(e) for e in evidence if e]

            # Use the full text if no evidence is available.
            if not contexts:
                contexts = [normalized_text]

            preferred_match = any(
                cls._contains_pattern(context, cls.PREFERRED_PATTERNS)
                for context in contexts
            )

            required_match = any(
                cls._contains_pattern(context, cls.REQUIRED_PATTERNS)
                for context in contexts
            )

            # Preferred takes priority when both cues appear
            # in the same evidence context.
            if preferred_match:
                preferred.append(skill)
            elif required_match:
                required.append(skill)
            else:
                unclassified.append(skill)

        return {
            "required": sorted(set(required)),
            "preferred": sorted(set(preferred)),
            "unclassified": sorted(set(unclassified)),
            "classification_complete": len(unclassified) == 0,
        }
