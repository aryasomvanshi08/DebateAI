VERDICTS = ["SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED"]

def is_exact_match(predicted: str, expected: str) -> bool:
    return predicted == expected

def is_hallucination(predicted: str, expected: str) -> bool:
    opposite_pairs = {
        ("SUPPORTED", "UNSUPPORTED"),
        ("UNSUPPORTED", "SUPPORTED"),
    }
    return (predicted, expected) in opposite_pairs

def compute_metrics(results: list[dict]) -> dict:
    total = len(results)
    if total == 0:
        return {"error": "No results to evaluate."}

    exact_matches = sum(is_exact_match(r["predicted_verdict"], r["expected_verdict"]) for r in results)
    hallucinations = sum(is_hallucination(r["predicted_verdict"], r["expected_verdict"]) for r in results)

    correct_confidences = [r["confidence"] for r in results if is_exact_match(r["predicted_verdict"], r["expected_verdict"])]
    wrong_confidences = [r["confidence"] for r in results if not is_exact_match(r["predicted_verdict"], r["expected_verdict"])]
    avg_conf_correct = sum(correct_confidences) / len(correct_confidences) if correct_confidences else None
    avg_conf_wrong = sum(wrong_confidences) / len(wrong_confidences) if wrong_confidences else None

    categories = set(r["category"] for r in results)
    per_category = {}
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        cat_correct = sum(is_exact_match(r["predicted_verdict"], r["expected_verdict"]) for r in cat_results)
        per_category[cat] = {
            "total": len(cat_results),
            "correct": cat_correct,
            "accuracy": round(cat_correct / len(cat_results), 3)
        }

    return {
        "total_claims": total,
        "exact_match_accuracy": round(exact_matches / total, 3),
        "hallucination_count": hallucinations,
        "hallucination_rate": round(hallucinations / total, 3),
        "avg_confidence_when_correct": round(avg_conf_correct, 3) if avg_conf_correct is not None else None,
        "avg_confidence_when_wrong": round(avg_conf_wrong, 3) if avg_conf_wrong is not None else None,
        "per_category": per_category
    }