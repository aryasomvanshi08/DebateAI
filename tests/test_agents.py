import pytest

from agents.moderator import load_moderator_prompt, validate_topic
from agents.pro_agent import load_pro_prompt, validate_pro_inputs


# Moderator Agent tests


def test_moderator_prompt_loads():
    prompt = load_moderator_prompt()

    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_valid_topic():
    result = validate_topic(
        "  Should artificial intelligence replace teachers?  "
    )

    assert result == "Should artificial intelligence replace teachers?"


def test_extra_spaces_are_removed():
    result = validate_topic("Should   college   education be free?")

    assert result == "Should college education be free?"


def test_empty_topic_raises_error():
    with pytest.raises(ValueError):
        validate_topic("   ")


def test_short_topic_raises_error():
    with pytest.raises(ValueError):
        validate_topic("AI")


def test_non_string_topic_raises_error():
    with pytest.raises(TypeError):
        validate_topic(123)


# Pro Agent tests


def test_pro_prompt_loads():
    prompt = load_pro_prompt()

    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_valid_pro_inputs():
    topic, instruction = validate_pro_inputs(
        "  Should   college education be free?  ",
        "  Present arguments   supporting free education.  ",
    )

    assert topic == "Should college education be free?"
    assert instruction == (
        "Present arguments supporting free education."
    )


def test_empty_pro_topic_raises_error():
    with pytest.raises(ValueError):
        validate_pro_inputs(
            "   ",
            "Present arguments supporting the topic.",
        )


def test_empty_pro_instruction_raises_error():
    with pytest.raises(ValueError):
        validate_pro_inputs(
            "Should college education be free?",
            "   ",
        )


def test_short_pro_instruction_raises_error():
    with pytest.raises(ValueError):
        validate_pro_inputs(
            "Should college education be free?",
            "Pro",
        )


def test_non_string_pro_input_raises_error():
    with pytest.raises(TypeError):
        validate_pro_inputs(
            123,
            "Present arguments supporting the topic.",
        )