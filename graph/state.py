from typing import Any, NotRequired, TypedDict


class DebateState(TypedDict):
    """Shared state passed between the debate agents."""

    # Original topic entered by the user
    user_topic: str

    # Values produced by the Moderator Agent
    topic: NotRequired[str]
    pro_instruction: NotRequired[str]
    con_instruction: NotRequired[str]

    # Opening arguments
    pro_argument: NotRequired[dict[str, Any]]
    con_argument: NotRequired[dict[str, Any]]

    # Responses produced by the Rebuttal Agent
    rebuttals: NotRequired[dict[str, Any]]

    # Optional workflow error
    error: NotRequired[str]


def create_initial_state(user_topic: str) -> DebateState:
    """Validate a user topic and create the initial debate state."""

    if not isinstance(user_topic, str):
        raise TypeError("The user topic must be a string.")

    cleaned_topic = " ".join(user_topic.split())

    if not cleaned_topic:
        raise ValueError("The user topic cannot be empty.")

    if len(cleaned_topic) < 5:
        raise ValueError("The user topic is too short.")

    return DebateState(user_topic=cleaned_topic)