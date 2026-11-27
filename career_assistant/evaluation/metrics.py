
import re
import unicodedata


STOPWORDS = {
    "the", "and", "for", "with", "from", "that", "this",
    "your", "you", "are", "was", "were", "have", "has",
    "les", "des", "une", "dans", "pour", "avec", "sur",
    "est", "sont", "qui", "que", "par", "pas", "plus",
    "du", "de", "la", "le", "un", "et", "en", "au",
}


def tokenize(text):
    """Normalize text and return meaningful tokens."""

    if not isinstance(text, str):
        return set()

    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )

    tokens = re.findall(r"\b[a-zA-Z0-9+#.]+\b", text)

    return {
        token
        for token in tokens
        if len(token) > 1 and token not in STOPWORDS
    }


def calculate_relevance(answer, expected_points):
    """Measure coverage of expected concepts in the answer."""

    expected = [
        tokenize(point)
        for point in expected_points
        if tokenize(point)
    ]

    if not expected:
        return 0.0

    answer_tokens = tokenize(answer)

    scores = []

    for point_tokens in expected:
        overlap = answer_tokens.intersection(point_tokens)
        score = len(overlap) / len(point_tokens)
        scores.append(score)

    return round(sum(scores) / len(scores) * 100, 2)


def calculate_groundedness(answer, context):
    """Estimate how much answer vocabulary appears in the context."""

    answer_tokens = tokenize(answer)
    context_tokens = tokenize(context)

    if not answer_tokens:
        return 0.0

    supported = answer_tokens.intersection(context_tokens)

    return round(
        len(supported) / len(answer_tokens) * 100,
        2
    )


def calculate_hallucination_proxy(answer, context):
    """
    Estimate unsupported vocabulary.

    This is only a lexical proxy, not a semantic
    hallucination detector.
    """

    groundedness = calculate_groundedness(answer, context)

    return round(100 - groundedness, 2)


def calculate_completeness(answer, expected_points):
    """Measure the percentage of expected concepts covered."""

    if not expected_points:
        return 0.0

    answer_tokens = tokenize(answer)

    covered = 0

    for point in expected_points:

        point_tokens = tokenize(point)

        if not point_tokens:
            continue

        overlap = answer_tokens.intersection(point_tokens)

        if len(overlap) / len(point_tokens) >= 0.5:
            covered += 1

    valid_points = sum(
        1 for point in expected_points
        if tokenize(point)
    )

    if valid_points == 0:
        return 0.0

    return round(covered / valid_points * 100, 2)
