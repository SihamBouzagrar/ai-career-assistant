
import re


class SkillMatcher:

    @staticmethod
    def _normalize(skill: str) -> str:
        return re.sub(r"\s+", " ", skill.strip().lower())

    @classmethod
    def _extract_skill_names(cls, skills: list) -> set:
        result = set()

        for item in skills or []:
            if isinstance(item, str):
                name = item
            elif isinstance(item, dict):
                name = item.get("skill", "")
            else:
                continue

            if isinstance(name, str) and name.strip():
                result.add(cls._normalize(name))

        return result

    @staticmethod
    def _safe_percentage(numerator, denominator):
        if denominator == 0:
            return 0.0

        return round(numerator / denominator * 100, 2)

    @classmethod
    def match(
        cls,
        cv_skills,
        job_skills,
        required_skills=None,
        preferred_skills=None
    ):

        cv_set = cls._extract_skill_names(cv_skills)
        job_set = cls._extract_skill_names(job_skills)

        required_set = cls._extract_skill_names(required_skills or [])
        preferred_set = cls._extract_skill_names(preferred_skills or [])

        if not required_set and not preferred_set:
            required_set = job_set

        required_set &= job_set
        preferred_set &= job_set

        # Unclassified job skills are considered required.
        unclassified = job_set - required_set - preferred_set
        required_set |= unclassified

        matched = cv_set & job_set
        missing = job_set - cv_set
        additional = cv_set - job_set

        matched_required = matched & required_set
        matched_preferred = matched & preferred_set

        missing_required = required_set - cv_set
        missing_preferred = preferred_set - cv_set

        # Required skills have weight 2.
        # Preferred skills have weight 1.
        total_weight = (
            len(required_set) * 2 +
            len(preferred_set)
        )

        matched_weight = (
            len(matched_required) * 2 +
            len(matched_preferred)
        )

        weighted_score = cls._safe_percentage(
            matched_weight,
            total_weight
        )

        coverage_score = cls._safe_percentage(
            len(matched),
            len(job_set)
        )

        precision = cls._safe_percentage(
            len(matched),
            len(cv_set)
        )

        recall = coverage_score

        f1_score = (
            round(2 * precision * recall / (precision + recall), 2)
            if precision + recall > 0
            else 0.0
        )

        metrics = {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }

        return {
            # New format
            "matched": sorted(matched),
            "missing": sorted(missing),
            "additional": sorted(additional),

            "matched_required": sorted(matched_required),
            "matched_preferred": sorted(matched_preferred),
            "missing_required": sorted(missing_required),
            "missing_preferred": sorted(missing_preferred),

            "coverage_score": coverage_score,
            "weighted_score": weighted_score,

            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,

            "total_cv_skills": len(cv_set),
            "total_job_skills": len(job_set),
            "total_matched_skills": len(matched),

            "total_required_skills": len(required_set),
            "total_preferred_skills": len(preferred_set),

            # Backward compatibility with the previous application
            "cv_skill_count": len(cv_set),
            "job_skill_count": len(job_set),

            "common_skills": sorted(matched),
            "missing_skills": sorted(missing),
            "extra_skills": sorted(additional),

            "metrics": metrics
        }
