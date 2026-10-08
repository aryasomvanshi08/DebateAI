import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from graph.state import create_initial_state
from graph.debate_graph import build_debate_graph
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from fact_checker.fact_checker import FactChecker, fact_check_debate
from agents.judge import judge
from guardrails.input_guardrail import check_input
from guardrails.output_guardrail import check_output

EMBEDDING_DIM = 384
INDEX_FOLDER = str(ROOT / "Data" / "index")


@st.cache_resource
def get_graph():
    return build_debate_graph()


@st.cache_resource
def get_checker():
    store = VectorStore.load(INDEX_FOLDER, EMBEDDING_DIM)
    retriever = Retriever(store)
    return FactChecker(retriever, k=3)


def as_text(item) -> str:
    """Turn one argument entry into plain text."""
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        for key in ("claim", "argument", "text", "point"):
            if isinstance(item.get(key), str):
                return item[key].strip()
    return str(item)


def safe(text: str) -> str:
    """Run model-generated text through the output guardrail."""
    return check_output(text)["text"]


def run_debate(topic: str) -> dict:
    state = get_graph().invoke(create_initial_state(topic))

    if state.get("error"):
        raise RuntimeError(state["error"])

    pro = state["pro_argument"]
    con = state["con_argument"]
    reb = state.get("rebuttals", {})

    return {
        "topic": state.get("topic", topic),
        "pro_arguments": [as_text(a) for a in pro["arguments"]],
        "con_arguments": [as_text(a) for a in con["arguments"]],
        "pro_opening": pro.get("opening_statement", ""),
        "con_opening": con.get("opening_statement", ""),
        "pro_conclusion": pro.get("conclusion", ""),
        "con_conclusion": con.get("conclusion", ""),
        "pro_rebuttals": reb.get("pro_rebuttals", []),
        "con_rebuttals": reb.get("con_rebuttals", []),
    }


def show_fact_checks(results: list):
    for r in results:
        st.markdown(f"**{r['verdict']}** ({r['confidence']:.2f}) — {r['claim']}")
        sources = ", ".join(r.get("sources", [])) or "none"
        st.caption(f"{r['explanation']}  |  Sources: {sources}")


st.set_page_config(page_title="DebateAI", layout="wide")
st.title("DebateAI")

topic = st.text_input("Enter a debate topic:")

if st.button("Start Debate"):
    guard = check_input(topic)
    if not guard["allowed"]:
        st.error(f"Blocked: {guard['reason']}")
        st.stop()

    try:
        with st.spinner("Running the debate (this takes a minute)..."):
            debate = run_debate(guard["cleaned"])

        with st.spinner("Fact-checking claims..."):
            payload = {
                "topic": debate["topic"],
                "pro_arguments": debate["pro_arguments"],
                "con_arguments": debate["con_arguments"],
            }
            fact = fact_check_debate(payload, get_checker())

        rebuttal_text = " ".join(debate["pro_rebuttals"] + debate["con_rebuttals"])
        verdict = judge(payload, fact, rebuttal_text)
    except Exception as error:
        st.error(f"Something went wrong: {error}")
        st.stop()

    n_pro = len(debate["pro_arguments"])
    results = fact["fact_check_results"]

    st.subheader(f"Topic: {debate['topic']}")

    col_pro, col_con = st.columns(2)
    with col_pro:
        st.header("Pro")
        st.write(safe(debate["pro_opening"]))
        for a in debate["pro_arguments"]:
            st.write("•", safe(a))
        st.caption(safe(debate["pro_conclusion"]))
    with col_con:
        st.header("Con")
        st.write(safe(debate["con_opening"]))
        for a in debate["con_arguments"]:
            st.write("•", safe(a))
        st.caption(safe(debate["con_conclusion"]))

    st.subheader("Rebuttals")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Pro responds to Con**")
        for r in debate["pro_rebuttals"]:
            st.write("•", safe(r))
    with col_b:
        st.markdown("**Con responds to Pro**")
        for r in debate["con_rebuttals"]:
            st.write("•", safe(r))

    st.subheader("Fact check")
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown("**Pro claims**")
        show_fact_checks(results[:n_pro])
    with col_d:
        st.markdown("**Con claims**")
        show_fact_checks(results[n_pro:])

    st.subheader("Judge decision")
    final = check_output(f"Winner: {verdict['winner']}\n\n{verdict['reason']}")
    st.success(final["text"])
    st.json(verdict["score"])