import re

SECRET_PATTERNS = [r"AIza[0-9A-Za-z_\-]{30,}", r"sk-[A-Za-z0-9]{20,}", r"(?i)api[_-]?key\s*[:=]\s*\S+"]
LEAK_PHRASES = ["system prompt", "my instructions are", "hidden instructions"]

def check_output(text: str) -> dict:
    issues, cleaned = [], text or ""
    for p in SECRET_PATTERNS:
        if re.search(p, cleaned):
            cleaned = re.sub(p, "[REDACTED]", cleaned)
            issues.append("secret_redacted")
    if any(ph in cleaned.lower() for ph in LEAK_PHRASES):
        issues.append("possible_instruction_leak")
        cleaned = "Response withheld: it may contain internal information."
    if not cleaned.strip():
        issues.append("empty_output")
        cleaned = "No answer could be generated."
    return {"safe": not issues, "text": cleaned, "issues": issues}