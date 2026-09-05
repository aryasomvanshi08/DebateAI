import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


MODEL_NAME = "gemini-3.5-flash-lite"

PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "prompts"
    / "moderator_prompt.txt"
)


class ModeratedTopic(BaseModel):
    """Structured output produced by the Moderator Agent."""

    topic: str = Field(
        description="A clear and neutral debate question."
    )

    pro_instruction: str = Field(
        description="An instruction asking the Pro Agent to support the topic."
    )

    con_instruction: str = Field(
        description="An instruction asking the Con Agent to oppose the topic."
    )


def load_moderator_prompt() -> str:
    """Load the Moderator Agent instructions from the prompt file."""

    if not PROMPT_PATH.exists():
        raise FileNotFoundError(
            f"Moderator prompt was not found: {PROMPT_PATH}"
        )

    prompt = PROMPT_PATH.read_text(encoding="utf-8").strip()

    if not prompt:
        raise ValueError("The Moderator prompt file is empty.")

    return prompt


def validate_topic(topic: str) -> str:
    """Validate and clean the debate topic."""

    if not isinstance(topic, str):
        raise TypeError("The debate topic must be a string.")

    cleaned_topic = " ".join(topic.split())

    if not cleaned_topic:
        raise ValueError("The debate topic cannot be empty.")

    if len(cleaned_topic) < 5:
        raise ValueError("The debate topic is too short.")

    return cleaned_topic


def create_moderator_model():
    """Create the Gemini model with structured output."""

    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise EnvironmentError(
            "GOOGLE_API_KEY was not found in the .env file."
        )

    model = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        temperature=1.0,
        max_retries=4,
    )

    return model.with_structured_output(
        schema=ModeratedTopic.model_json_schema(),
        method="json_schema",
    )


def moderate_topic(topic: str) -> dict[str, str]:
    """
    Convert a user topic into a neutral debate question and create
    instructions for the Pro and Con agents.
    """

    cleaned_topic = validate_topic(topic)
    moderator_prompt = load_moderator_prompt()
    structured_model = create_moderator_model()

    try:
        result = structured_model.invoke(
            [
                ("system", moderator_prompt),
                ("human", f"User debate topic: {cleaned_topic}"),
            ]
        )
    except Exception as error:
        raise RuntimeError(
            f"The Moderator Agent could not process the topic: {error}"
        ) from error

    validated_result = ModeratedTopic.model_validate(result)

    return validated_result.model_dump()


if __name__ == "__main__":
    sample_topic = "Should artificial intelligence replace teachers?"

    moderated_debate = moderate_topic(sample_topic)

    print("\nModerator Agent output:\n")
    print(json.dumps(moderated_debate, indent=2))