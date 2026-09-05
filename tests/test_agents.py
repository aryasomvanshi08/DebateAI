import pytest

from agents.moderator import load_moderator_prompt, validate_topic


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