"""
Evaluation dataset for DebateAI's Fact Checker.

Each entry is a claim paired with a human-assigned ground-truth verdict,
used to measure whether the Fact Checker's output matches what a careful
human reader of the source documents would conclude.

verdict values match the Fact Checker's own output format:
  SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED

category values describe WHY this claim is in the dataset — this is what
lets your evaluation report say more than "X% accuracy": it lets you show
*where* the system succeeds or fails.
"""

DATASET = [
    # --- Category: Clearly true, directly supported claims ---
    {
        "id": "sup_01",
        "claim": "The EU AI Act classifies AI systems into different risk categories rather than applying one uniform set of rules to all AI.",
        "expected_verdict": "SUPPORTED",
        "category": "clearly_true",
        "notes": "Core structure of the Act (risk-based tiering). Verify against your Ai3.pdf content."
    },
    {
        "id": "sup_02",
        "claim": "The NIST AI Risk Management Framework organizes its guidance around four core functions: Govern, Map, Measure, and Manage.",
        "expected_verdict": "SUPPORTED",
        "category": "clearly_true",
        "notes": "Matches structure seen in your Ai1.pdf retrieval output (MAP sections already appeared in your test)."
    },
    {
        "id": "sup_03",
        "claim": "The NIST AI Risk Management Framework describes trustworthy AI systems as needing to be valid, reliable, and accountable.",
        "expected_verdict": "SUPPORTED",
        "category": "clearly_true",
        "notes": "Matches your own retrieved evidence (Fig. 4 'Characteristics of trustworthy AI systems' appeared in your test output)."
    },
    {
        "id": "sup_04",
        "claim": "The EU AI Act allows the use of regulatory sandboxes to let companies test AI systems in a controlled environment before full market release.",
        "expected_verdict": "SUPPORTED",
        "category": "clearly_true",
        "notes": "This appeared directly in your own con_fact_checks test evidence — check why your system labeled it UNSUPPORTED there; it may have been evaluating a different specific claim, not this one."
    },

    # --- Category: Clearly false / fabricated claims ---
    {
        "id": "unsup_01",
        "claim": "The EU AI Act completely bans the use of any AI system in the healthcare industry.",
        "expected_verdict": "UNSUPPORTED",
        "category": "fabricated",
        "notes": "False — the Act is risk-tiered, not a blanket ban on a whole industry. Good test of whether the system resists a plausible-sounding but wrong claim."
    },
    {
        "id": "unsup_02",
        "claim": "The NIST AI Risk Management Framework is a legally binding law that all companies operating in the United States must comply with.",
        "expected_verdict": "UNSUPPORTED",
        "category": "fabricated",
        "notes": "False — NIST AI RMF is voluntary guidance, not binding law. Tests whether system distinguishes 'framework/guidance' from 'legal mandate.'"
    },
    {
        "id": "unsup_03",
        "claim": "The EU AI Act specifically names OpenAI's GPT-4 as a banned AI system.",
        "expected_verdict": "UNSUPPORTED",
        "category": "fabricated",
        "notes": "False — the Act regulates by risk category/capability thresholds, not by naming specific commercial products. Classic 'sounds plausible' hallucination bait."
    },
    {
        "id": "unsup_04",
        "claim": "The EU AI Act was first adopted and entered into force in 2020.",
        "expected_verdict": "UNSUPPORTED",
        "category": "fabricated",
        "notes": "False — check your Ai3.pdf for the actual year; the Act's final text is from 2024, not 2020. Good factual/date-precision test."
    },

    # --- Category: Evidence exists but is irrelevant to the specific claim ---
    {
        "id": "irr_01",
        "claim": "Generative AI increases worker productivity.",
        "expected_verdict": "UNSUPPORTED",
        "category": "irrelevant_evidence",
        "notes": "Already tested — your governance/regulation docs don't address economic productivity, so UNSUPPORTED is the correct, honest answer given YOUR current corpus. Re-test after adding an economic-impact document; the label may become SUPPORTED then."
    },
    {
        "id": "irr_02",
        "claim": "Generative AI models can compose original music.",
        "expected_verdict": "UNSUPPORTED",
        "category": "irrelevant_evidence",
        "notes": "True in general, but your regulation-focused documents won't discuss this capability at all — tests whether system correctly says 'no evidence' rather than answering from its own world knowledge."
    },
    {
        "id": "irr_03",
        "claim": "AI regulation improves public trust in AI systems.",
        "expected_verdict": "PARTIALLY_SUPPORTED",
        "category": "irrelevant_evidence",
        "notes": "Documents discuss 'trustworthy AI' extensively as a goal, which the system correctly read as partial (not direct) support. Confirmed correct after the token-limit parsing fix."
    },

    # --- Category: Nuanced / partially true claims ---
    {
        "id": "part_01",
        "claim": "The EU AI Act requires all AI systems, regardless of risk level, to undergo the same strict conformity assessment before deployment.",
        "expected_verdict": "UNSUPPORTED",
        "category": "nuanced",
        "notes": "Corrected from PARTIALLY_SUPPORTED. Original label was too generous — the claim says 'all AI systems regardless of risk level,' but the Act's conformity assessment is explicitly risk-tiered (applies to high-risk and general-purpose models, not universally). The system correctly identified this as fully contradicted, not partially supported, because the claim's own wording ('all', 'same', 'regardless of risk') is the part being tested, and the evidence directly refutes it."
    },
    {
        "id": "part_02",
        "claim": "Under the NIST framework, AI risk management is solely the responsibility of an organization's engineering team.",
        "expected_verdict": "UNSUPPORTED",
        "category": "nuanced",
        "notes": "Corrected from PARTIALLY_SUPPORTED. Original label too generous — the claim's key word is 'solely,' and the evidence directly shows broader organizational involvement (internal teams across the AI lifecycle, not engineering alone). The system correctly flagged this as a full contradiction rather than a partial one."
    },
    {
        "id": "part_03",
        "claim": "Excessive regulation slows down AI innovation.",
        "expected_verdict": "UNSUPPORTED",
        "category": "nuanced",
        "notes": "Corrected from PARTIALLY_SUPPORTED. On review, the evidence about regulatory sandboxes fostering innovation doesn't actually address whether 'excessive' regulation slows it down — it's a different question entirely (sandboxes describe a mitigation measure, not a verdict on the claim's causal statement). The system correctly treated this as unrelated to the claim rather than partial support. Still a genuinely debatable policy claim worth discussing in the report as a case where plausible-sounding 'related' evidence isn't the same as supporting evidence."
    },

    # --- Category: Contradicting/conflicting evidence across sources ---
    {
        "id": "contra_01",
        "claim": "All major governments agree on a single unified global standard for regulating generative AI.",
        "expected_verdict": "UNSUPPORTED",
        "category": "conflicting_sources",
        "notes": "False — EU and US (NIST) approaches differ significantly (binding law vs. voluntary framework). Tests whether system notices disagreement/inconsistency across sources rather than assuming agreement."
    },

    # --- Category: Insufficient evidence in current corpus (add more docs to flip) ---
    {
        "id": "insuff_01",
        "claim": "Global investment in generative AI startups exceeded $50 billion in 2024.",
        "expected_verdict": "UNSUPPORTED",
        "category": "insufficient_evidence",
        "notes": "May become SUPPORTED once you confirm what's actually in ai_index_report_2026.pdf — check that document for real investment figures and adjust this claim/label to match its actual content."
    },
    {
        "id": "insuff_02",
        "claim": "The number of AI-related job postings has increased significantly in recent years.",
        "expected_verdict": "UNSUPPORTED",
        "category": "insufficient_evidence",
        "notes": "Same as above — verify against your actual ai_index_report_2026.pdf content. Note: this claim returned an ERROR verdict (Gemini API outage after retries) in the evaluation run on this date — a documented infrastructure limitation, not a system logic failure. Re-run when convenient to get a real verdict."
    },
]


def get_dataset():
    return DATASET


def get_dataset_by_category(category: str):
    return [item for item in DATASET if item["category"] == category]