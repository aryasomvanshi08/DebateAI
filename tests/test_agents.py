import pytest

from agents.moderator import load_moderator_prompt, validate_topic
from agents.pro_agent import load_pro_prompt, validate_pro_inputs
from agents.con_agent import load_con_prompt, validate_con_inputs
from agents.rebuttal import (
    load_rebuttal_prompt,
    validate_rebuttal_inputs,
)

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

def test_con_prompt_loads():
    prompt = load_con_prompt()

    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_valid_con_inputs():
    topic, instruction = validate_con_inputs(
        "  Should college education be free?  ",
        "  Present arguments opposing free college education.  ",
    )

    assert topic == "Should college education be free?"
    assert instruction == (
        "Present arguments opposing free college education."
    )


def test_empty_con_topic_raises_error():
    with pytest.raises(ValueError):
        validate_con_inputs(
            "   ",
            "Present arguments opposing the topic.",
        )


def test_empty_con_instruction_raises_error():
    with pytest.raises(ValueError):
        validate_con_inputs(
            "Should college education be free?",
            "   ",
        )


def test_short_con_instruction_raises_error():
    with pytest.raises(ValueError):
        validate_con_inputs(
            "Should college education be free?",
            "No",
        )


def test_non_string_con_topic_raises_error():
    with pytest.raises(TypeError):
        validate_con_inputs(
            123,
            "Present arguments opposing the topic.",
        )

def make_sample_arguments():
    pro_argument = {
        "position": "pro",
        "opening_statement": "AI can improve access to education.",
        "arguments": [
            "AI can personalize lessons.",
            "AI can operate at any time.",
            "AI can reduce administrative work.",
        ],
        "conclusion": "AI can make education more scalable.",
    }

    con_argument = {
        "position": "con",
        "opening_statement": "Human teachers remain essential.",
        "arguments": [
            "Teachers provide emotional support.",
            "AI can reproduce bias.",
            "Technology is not equally accessible.",
        ],
        "conclusion": "AI should assist rather than replace teachers.",
    }

    return pro_argument, con_argument


def test_rebuttal_prompt_loads():
    prompt = load_rebuttal_prompt()

    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_valid_rebuttal_inputs():
    pro_argument, con_argument = make_sample_arguments()

    topic, validated_pro, validated_con = validate_rebuttal_inputs(
        "  Should AI replace human teachers?  ",
        pro_argument,
        con_argument,
    )

    assert topic == "Should AI replace human teachers?"
    assert validated_pro["position"] == "pro"
    assert validated_con["position"] == "con"


def test_empty_rebuttal_topic_raises_error():
    pro_argument, con_argument = make_sample_arguments()

    with pytest.raises(ValueError):
        validate_rebuttal_inputs(
            "   ",
            pro_argument,
            con_argument,
        )


def test_non_dictionary_pro_argument_raises_error():
    _, con_argument = make_sample_arguments()

    with pytest.raises(TypeError):
        validate_rebuttal_inputs(
            "Should AI replace human teachers?",
            "invalid pro argument",
            con_argument,
        )


def test_empty_con_argument_raises_error():
    pro_argument, _ = make_sample_arguments()

    with pytest.raises(ValueError):
        validate_rebuttal_inputs(
            "Should AI replace human teachers?",
            pro_argument,
            {},
        )


def test_missing_argument_field_raises_error():
    pro_argument, con_argument = make_sample_arguments()
    del pro_argument["conclusion"]

    with pytest.raises(ValueError):
        validate_rebuttal_inputs(
            "Should AI replace human teachers?",
            pro_argument,
            con_argument,
        )


def test_wrong_argument_position_raises_error():
    pro_argument, con_argument = make_sample_arguments()
    con_argument["position"] = "pro"

    with pytest.raises(ValueError):
        validate_rebuttal_inputs(
            "Should AI replace human teachers?",
            pro_argument,
            con_argument,
        )