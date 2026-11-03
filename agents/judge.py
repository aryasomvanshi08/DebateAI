VERDICT_SCORE = {"SUPPORTED": 1.0, "PARTIALLY_SUPPORTED": 0.5, "UNSUPPORTED": 0.0}

def _score(results):
    valid = [r for r in results if r.get("verdict") in VERDICT_SCORE]
    if not valid:
        return 0.0, 0
    total = sum(VERDICT_SCORE[r["verdict"]] * r.get("confidence", 0.5) for r in valid)
    return total / len(valid), len(valid)

def judge(payload: dict, fact_result: dict, rebuttal: str = "") -> dict:
    n_pro = len(payload.get("pro_arguments", []))
    results = fact_result["fact_check_results"]
    pro_res, con_res = results[:n_pro], results[n_pro:]   # Pro first, then Con

    pro_score, pro_n = _score(pro_res)
    con_score, con_n = _score(con_res)

    if abs(pro_score - con_score) < 0.05:
        winner = "Tie"
    else:
        winner = "Pro" if pro_score > con_score else "Con"

    reason = (f"Pro: {pro_n} checkable claims, avg weighted score {pro_score:.2f}. "
              f"Con: {con_n} checkable claims, avg weighted score {con_score:.2f}. "
              f"Winner is decided by how well each side's claims are backed by evidence.")
    return {
        "winner": winner,
        "reason": reason,
        "score": {"pro": round(pro_score, 3), "con": round(con_score, 3)},
    }