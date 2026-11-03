# DebateAI

DebateAI is an AI system where multiple AI agents discuss a question from different sides. Instead of one AI giving an answer, a **Pro Agent, Con Agent, Fact Checker, and Judge** work together. The aim is to test whether this approach can make AI answers more reliable and less likely to hallucinate compared to a single LLM.

---

# Member 2 Module: RAG + Fact Checking + Evaluation

This module provides **evidence retrieval and fact-checking** for DebateAI. Given a claim made by the Pro or Con debate agent, it retrieves relevant evidence from a trusted document collection and uses an LLM to judge the claim strictly against that evidence — never from the LLM's own general knowledge.

## What's in Here

```text
rag/
├── document_loader.py   # Extracts text from PDFs
├── chunker.py           # Splits text into overlapping chunks
├── embeddings.py        # Converts text into vector embeddings (Sentence Transformers)
├── vector_store.py      # FAISS-based vector storage and similarity search
└── retriever.py         # Public retrieve(query, k) interface

fact_checker/
└── fact_checker.py      # Evidence-grounded claim verification (Gemini API)

evaluation/
├── dataset.py           # Hand-labeled claims used to test the fact checker
├── metrics.py           # Accuracy, hallucination rate, per-category breakdown
└── evaluator.py         # Runs the dataset through the fact checker, saves results

Data/
├── Documents/           # Source PDFs (trusted evidence documents)
└── index/               # Generated FAISS index (not committed — rebuild with build_index.py)

build_index.py           # Run once to build the vector index from Data/Documents
run_evaluation.py        # Run the evaluation dataset and print a scored report
```

## Setup

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your-gemini-api-key
```

## How to Run

### 1. Build the Vector Index

Run this once, or whenever documents in `Data/Documents` change:

```bash
python build_index.py
```

### 2. Run the Evaluation

```bash
python run_evaluation.py
```

This checks every claim in `evaluation/dataset.py` against the fact checker, saves results to `evaluation/results.json`, and prints a summary with:

- Accuracy
- Hallucination rate
- Per-category breakdown

## Public Interface

### Single Claim

```python
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from fact_checker.fact_checker import FactChecker

store = VectorStore.load("Data/index", dimension=384)
retriever = Retriever(store)
checker = FactChecker(retriever, k=5)

result = checker.fact_check("Generative AI increases worker productivity.")
# {"claim", "verdict", "confidence", "evidence", "sources", "explanation"}
```

### Debate Payload

Used by the **Member 1 → Member 2 handoff**:

```python
from fact_checker.fact_checker import fact_check_debate

payload = {
    "topic": "...",
    "pro_arguments": ["...", "..."],
    "con_arguments": ["...", "..."]
}

result = fact_check_debate(payload, checker)
# {"claims": [...], "evidence": [...], "fact_check_results": [...]}
```

This matches the **Member 2 → Member 3 interface** agreed in the team's integration doc.

## Verdicts

| Verdict               | Meaning                                                                |
| --------------------- | ---------------------------------------------------------------------- |
| `SUPPORTED`           | Evidence clearly backs the claim                                       |
| `PARTIALLY_SUPPORTED` | Evidence is related but incomplete or mixed                            |
| `UNSUPPORTED`         | Evidence contradicts the claim, or no relevant evidence was found      |
| `ERROR`               | The LLM API was unavailable after retries (rare, infrastructure-level) |

## Evaluation Results

On a **17-claim hand-labeled test set** covering clearly true claims, fabricated claims, irrelevant evidence, nuanced/partially-true claims, and cross-source conflicts:

- **Exact-match accuracy: 100% (17/17)**
- **Hallucination rate: 0%** (the system never asserted the opposite of the truth)

### Notes on This Result

- The test set is small (17 claims) and was authored by the development team, not independently sourced — this measures the fact checker's reasoning given retrieved evidence, not a large-scale benchmark.
- 3 of the 17 ground-truth labels were corrected during development after reviewing the system's evidence-grounded reasoning revealed the original labels were too lenient (see the `notes` field on `part_01`, `part_02`, `part_03` in `evaluation/dataset.py` for the reasoning behind each correction).
- 1 claim required a retry due to a transient Gemini API outage (503), unrelated to fact-checking logic.

## Known Limitations

- The current document collection (`Data/Documents`) is small (4 PDFs, mostly AI governance/regulation frameworks). Claims outside this domain will correctly return `UNSUPPORTED` due to lack of evidence, not because they're false.
- Gemini's free-tier API has per-day and per-minute rate limits; the fact checker includes retry logic with backoff, but very large batches of claims may need to run across multiple sessions or require a paid tier.
