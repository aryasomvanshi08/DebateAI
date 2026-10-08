from guardrails.injection_detector import detect_injection

MIN_LEN, MAX_LEN = 5, 300
BLOCKED = ["make a bomb", "build a weapon", "how to hack", "self-harm instructions"]

def check_input(user_input: str) -> dict:
    text = (user_input or "").strip()
    if not text:
        return {"allowed": False, "reason": "Topic is empty.", "cleaned": ""}
    if len(text) < MIN_LEN:
        return {"allowed": False, "reason": "Topic is too short.", "cleaned": text}
    if len(text) > MAX_LEN:
        return {"allowed": False, "reason": f"Topic must be under {MAX_LEN} characters.", "cleaned": text}
    inj = detect_injection(text)
    if inj["is_suspicious"]:
        return {"allowed": False, "reason": f"Possible prompt injection ({inj['category']}).", "cleaned": text}
    if any(b in text.lower() for b in BLOCKED):
        return {"allowed": False, "reason": "Topic is outside the allowed scope.", "cleaned": text}
    return {"allowed": True, "reason": "OK", "cleaned": text}