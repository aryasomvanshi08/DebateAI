import json
import time
from pathlib import Path
from evaluation.dataset import get_dataset
from evaluation.metrics import compute_metrics


class Evaluator:
    def __init__(self, fact_checker):
        self.fact_checker = fact_checker

    def run(self, save_path: str = "evaluation/results.json") -> dict:
        dataset = get_dataset()
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # Resume: load any results saved by a previous run
        results = []
        if Path(save_path).exists():
            with open(save_path, encoding="utf-8") as f:
                results = json.load(f).get("detailed_results", [])
        done_ids = {r["id"] for r in results}
        print(f"Resuming: {len(done_ids)} of {len(dataset)} claims already done.")

        for i, item in enumerate(dataset):
            if item["id"] in done_ids:
                continue

            print(f"[{i + 1}/{len(dataset)}] Checking: {item['claim'][:60]}...")
            output = self.fact_checker.fact_check(item["claim"])

            results.append({
                "id": item["id"],
                "claim": item["claim"],
                "category": item["category"],
                "expected_verdict": item["expected_verdict"],
                "predicted_verdict": output["verdict"],
                "confidence": output["confidence"],
                "explanation": output["explanation"],
                "sources": output["sources"]
            })

            # Save after every claim so a crash or quota hit never loses work
            self._save(results, save_path)
            time.sleep(13)  # stay under the free-tier per-minute limit

        report = self._save(results, save_path)
        print(f"\nSaved full report to {save_path}")
        return report

    def _save(self, results: list, save_path: str) -> dict:
        report = {
            "metrics": compute_metrics(results),
            "detailed_results": results
        }
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return report


def print_summary(report: dict):
    m = report["metrics"]
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Total claims tested: {m['total_claims']}")
    print(f"Exact match accuracy: {m['exact_match_accuracy'] * 100:.1f}%")
    print(f"Hallucination rate: {m['hallucination_rate'] * 100:.1f}% ({m['hallucination_count']} cases)")
    print(f"Avg confidence when correct: {m['avg_confidence_when_correct']}")
    print(f"Avg confidence when wrong: {m['avg_confidence_when_wrong']}")

    print("\nPer-category accuracy:")
    for cat, stats in m["per_category"].items():
        print(f"  {cat}: {stats['correct']}/{stats['total']} ({stats['accuracy'] * 100:.1f}%)")

    print("\n=== MISSES ===")
    for r in report["detailed_results"]:
        if r["predicted_verdict"] != r["expected_verdict"]:
            print(f"[{r['id']}] {r['claim']}")
            print(f"  expected: {r['expected_verdict']} | predicted: {r['predicted_verdict']} ({r['confidence']})")
            print(f"  reason: {r['explanation']}\n")