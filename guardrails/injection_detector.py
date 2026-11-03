import re

PATTERNS = {
    "instruction_override": r"\b(ignore|forget|disregard)\b.{0,30}\b(previous|prior|above|all|your)\b.{0,20}\b(instructions?|rules?|prompts?)\b",
    "prompt_extraction": r"\b(show|reveal|print|repeat|tell)\b.{0,30}\b(system prompt|hidden (prompt|instructions?)|internal instructions?)\b",
    "secret_extraction": r"\b(api[ _-]?key|secret|password|token|environment variables?|\.env)\b.{0,20}\b(show|reveal|give|print|leak)\b|\b(show|reveal|give|print|leak)\b.{0,20}\b(api[ _-]?key|secrets?|passwords?|tokens?|environment variables?|\.env)\b",
    "role_manipulation": r"\b(you are no longer|act as an? (unrestricted|unfiltered)|pretend (to be|you are)|developer mode|DAN mode)\b",
    "jailbreak": r"\b(jailbreak|bypass (your )?(safety|restrictions|guardrails))\b",
}

def detect_injection(text: str) -> dict:
    for name, pattern in PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            return {"is_suspicious": True, "category": name}
    return {"is_suspicious": False, "category": None}