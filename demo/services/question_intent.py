# services/question_intent.py


def detect_intent(question: str) -> str:
    q = question.lower()

    if any(w in q for w in ["trend", "over time", "monthly", "yearly"]):
        return "trend"

    if any(w in q for w in ["compare", "top", "bottom", "highest", "lowest", "vs"]):
        return "comparison"

    if any(w in q for w in ["distribution", "spread", "share", "percentage"]):
        return "distribution"

    if any(w in q for w in ["relationship", "impact", "correlation"]):
        return "correlation"

    return "summary"
