import os
import json
import re
import time
from dotenv import load_dotenv
from google import genai
from rag.retriever import Retriever

load_dotenv()

client_genai = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "gemini-3-flash-preview"

VALID_VERDICTS = {"SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED"}


class FactChecker:
    def __init__(self, retriever: Retriever, k: int = 5):
        self.retriever = retriever
        self.k = k

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def fact_check(self, claim: str) -> dict:
        evidence_chunks = self.retriever.retrieve(claim, k=self.k)

        if not evidence_chunks:
            return {
                "claim": claim,
                "verdict": "UNSUPPORTED",
                "confidence": 0.0,
                "evidence": [],
                "sources": [],
                "explanation": "No evidence was retrieved from the document collection."
            }

        evidence_text = "\n\n".join(
            f"[Source: {c['source']}]\n{c['text']}" for c in evidence_chunks
        )

        prompt = f"""You are a strict fact-checking assistant. You must judge the CLAIM using ONLY the EVIDENCE provided below. Do not use any outside knowledge you may have. If the evidence does not clearly support or contradict the claim, say so honestly.

CLAIM:
{claim}

EVIDENCE:
{evidence_text}

Respond ONLY with a JSON object in this exact format, with no extra text, no markdown code fences, before or after it:
{{
  "verdict": "SUPPORTED" | "PARTIALLY_SUPPORTED" | "UNSUPPORTED",
  "confidence": <float between 0 and 1>,
  "explanation": "<one or two sentences explaining your verdict, referencing the evidence>"
}}

Rules:
- "SUPPORTED" means the evidence clearly backs the claim.
- "PARTIALLY_SUPPORTED" means the evidence is related but incomplete, mixed, or only partially backs the claim.
- "UNSUPPORTED" means the evidence contradicts the claim, or is irrelevant/insufficient to judge it.
- If sources disagree with each other, say so in the explanation and lower your confidence.
- Never invent evidence that isn't in the EVIDENCE section."""

        raw_text = self._call_with_retry(prompt)

        if raw_text is None:
            return {
                "claim": claim,
                "verdict": "ERROR",
                "confidence": 0.0,
                "evidence": [c["text"] for c in evidence_chunks],
                "sources": [c["source"] for c in evidence_chunks],
                "explanation": "The LLM API was unavailable after multiple retries."
            }

        parsed = self._parse_response(raw_text)

        return {
            "claim": claim,
            "verdict": parsed["verdict"],
            "confidence": parsed["confidence"],
            "evidence": [c["text"] for c in evidence_chunks],
            "sources": [c["source"] for c in evidence_chunks],
            "explanation": parsed["explanation"]
        }

    # ------------------------------------------------------------------
    # API call with retry
    # ------------------------------------------------------------------
    def _call_with_retry(self, prompt: str, max_retries: int = 6) -> str | None:
        for attempt in range(max_retries):
            try:
                response = client_genai.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt,
                    config={"max_output_tokens": 3000}
                )
                return response.text.strip()
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    wait_time = 40
                else:
                    wait_time = 5 * (attempt + 1)
                print(f"Gemini call failed ({str(e)[:80]}...), retrying in {wait_time}s...")
                time.sleep(wait_time)
        print("Gave up after all retries — marking this claim as ERROR.")
        return None

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------
    @staticmethod
    def _parse_response(raw_text: str) -> dict:
        """Extract and validate the JSON verdict from the model output."""
        default = {
            "verdict": "UNSUPPORTED",
            "confidence": 0.0,
            "explanation": f"Could not parse LLM response: {raw_text[:500]}"
        }

        # Strip markdown fences if present, then grab the first {...} block —
        # this handles cases where the model adds stray text before/after the JSON.
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip())
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if not match:
            print(f"JSON PARSE FAILURE (no {{...}} block found) — full raw response was:\n{raw_text}\n")
            return default

        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print(f"JSON PARSE FAILURE ({e}) — full raw response was:\n{raw_text}\n")
            return default

        if not isinstance(parsed, dict):
            return default

        verdict = str(parsed.get("verdict", "UNSUPPORTED")).strip().upper().replace(" ", "_")
        if verdict not in VALID_VERDICTS:
            verdict = "UNSUPPORTED"

        try:
            confidence = float(parsed.get("confidence", 0.0))
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))

        return {
            "verdict": verdict,
            "confidence": confidence,
            "explanation": str(parsed.get("explanation", ""))
        }


def fact_check_debate(payload: dict, checker: "FactChecker") -> dict:
    """
    Takes Member 1's handoff payload — {"topic", "pro_arguments", "con_arguments"} —
    and fact-checks every argument on both sides.

    Returns the exact interface shape agreed in the team's integration doc:
      {"claims": [...], "evidence": [...], "fact_check_results": [...]}
    so Member 3's Judge Agent can consume it directly.
    """
    all_claims = payload["pro_arguments"] + payload["con_arguments"]
    all_results = [checker.fact_check(claim) for claim in all_claims]

    return {
        "claims": [r["claim"] for r in all_results],
        "evidence": [r["evidence"] for r in all_results],
        "fact_check_results": [
            {
                "claim": r["claim"],
                "verdict": r["verdict"],
                "confidence": r["confidence"],
                "sources": r["sources"],
                "explanation": r["explanation"]
            }
            for r in all_results
        ]
    }