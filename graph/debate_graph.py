import json
from typing import Any

from langgraph.graph import END, START, StateGraph

from agents.con_agent import generate_con_argument
from agents.moderator import moderate_topic
from agents.pro_agent import generate_pro_argument
from agents.rebuttal import generate_rebuttals
from graph.state import DebateState, create_initial_state


def _require_state_value(
    state: DebateState,
    key: str,
) -> Any:
    """Return a required state value or raise a clear error."""

    value = state.get(key)

    if value is None:
        raise ValueError(
            f"The debate state is missing the required value: {key}"
        )

    return value


def moderator_node(state: DebateState) -> dict:
    """Process the user's original topic."""

    user_topic = _require_state_value(state, "user_topic")

    moderated_result = moderate_topic(user_topic)

    return {
        "topic": moderated_result["topic"],
        "pro_instruction": moderated_result["pro_instruction"],
        "con_instruction": moderated_result["con_instruction"],
    }


def pro_node(state: DebateState) -> dict:
    """Generate the opening argument supporting the topic."""

    topic = _require_state_value(state, "topic")
    instruction = _require_state_value(state, "pro_instruction")

    argument = generate_pro_argument(topic, instruction)

    return {"pro_argument": argument}


def con_node(state: DebateState) -> dict:
    """Generate the opening argument opposing the topic."""

    topic = _require_state_value(state, "topic")
    instruction = _require_state_value(state, "con_instruction")

    argument = generate_con_argument(topic, instruction)

    return {"con_argument": argument}


def rebuttal_node(state: DebateState) -> dict:
    """Generate rebuttals after both opening arguments."""

    topic = _require_state_value(state, "topic")
    pro_argument = _require_state_value(state, "pro_argument")
    con_argument = _require_state_value(state, "con_argument")

    rebuttals = generate_rebuttals(
        topic,
        pro_argument,
        con_argument,
    )

    return {"rebuttals": rebuttals}


def build_debate_graph():
    """Build and compile the complete debate workflow."""

    workflow = StateGraph(DebateState)

    workflow.add_node("moderator", moderator_node)
    workflow.add_node("pro", pro_node)
    workflow.add_node("con", con_node)
    workflow.add_node("rebuttal", rebuttal_node)

    workflow.add_edge(START, "moderator")
    workflow.add_edge("moderator", "pro")
    workflow.add_edge("pro", "con")
    workflow.add_edge("con", "rebuttal")
    workflow.add_edge("rebuttal", END)

    return workflow.compile()


debate_graph = build_debate_graph()


def run_debate(user_topic: str) -> dict:
    """Run the complete multi-agent debate workflow."""

    initial_state = create_initial_state(user_topic)
    final_state = debate_graph.invoke(initial_state)

    return dict(final_state)


if __name__ == "__main__":
    print("\nWelcome to DebateAI")

    user_topic = input("Enter a debate topic: ").strip()

    try:
        debate_result = run_debate(user_topic)

        print("\nComplete DebateAI result:\n")
        print(json.dumps(debate_result, indent=2))

    except (TypeError, ValueError) as error:
        print(f"\nInvalid topic: {error}")

    except RuntimeError as error:
        print(f"\nDebate generation failed: {error}")