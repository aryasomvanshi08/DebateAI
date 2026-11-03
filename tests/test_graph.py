import pytest

import graph.debate_graph as debate_graph_module


def test_debate_graph_compiles():
    graph = debate_graph_module.build_debate_graph()

    assert graph is not None


def test_pro_node_requires_moderated_topic():
    state = {
        "user_topic": "Should college education be free?",
    }

    with pytest.raises(ValueError, match="topic"):
        debate_graph_module.pro_node(state)


def test_run_debate_with_mocked_agents(monkeypatch):
    call_order = []

    def fake_moderate_topic(user_topic):
        call_order.append("moderator")

        assert user_topic == "Should college education be free?"

        return {
            "topic": "Should college education be free?",
            "pro_instruction": "Support free college education.",
            "con_instruction": "Oppose free college education.",
        }

    def fake_generate_pro_argument(topic, instruction):
        call_order.append("pro")

        assert topic == "Should college education be free?"
        assert instruction == "Support free college education."

        return {
            "position": "pro",
            "opening_statement": "Education should be accessible.",
            "arguments": [
                "It can improve access.",
                "It can reduce student debt.",
                "It can benefit society.",
            ],
            "conclusion": "College education should be free.",
        }

    def fake_generate_con_argument(topic, instruction):
        call_order.append("con")

        assert topic == "Should college education be free?"
        assert instruction == "Oppose free college education."

        return {
            "position": "con",
            "opening_statement": "Free college has major costs.",
            "arguments": [
                "It requires public funding.",
                "It may increase demand.",
                "Other education levels may need priority.",
            ],
            "conclusion": "College should not be completely free.",
        }

    def fake_generate_rebuttals(
        topic,
        pro_argument,
        con_argument,
    ):
        call_order.append("rebuttal")

        assert topic == "Should college education be free?"
        assert pro_argument["position"] == "pro"
        assert con_argument["position"] == "con"

        return {
            "pro_rebuttals": [
                "Public education is a long-term investment.",
                "Funding models can control costs.",
            ],
            "con_rebuttals": [
                "Benefits do not eliminate funding constraints.",
                "Targeted support may be more sustainable.",
            ],
        }

    monkeypatch.setattr(
        debate_graph_module,
        "moderate_topic",
        fake_moderate_topic,
    )

    monkeypatch.setattr(
        debate_graph_module,
        "generate_pro_argument",
        fake_generate_pro_argument,
    )

    monkeypatch.setattr(
        debate_graph_module,
        "generate_con_argument",
        fake_generate_con_argument,
    )

    monkeypatch.setattr(
        debate_graph_module,
        "generate_rebuttals",
        fake_generate_rebuttals,
    )

    result = debate_graph_module.run_debate(
        "  Should college education be free?  "
    )

    assert call_order == [
        "moderator",
        "pro",
        "con",
        "rebuttal",
    ]

    assert result["topic"] == "Should college education be free?"
    assert result["pro_argument"]["position"] == "pro"
    assert result["con_argument"]["position"] == "con"
    assert len(result["rebuttals"]["pro_rebuttals"]) == 2
    assert len(result["rebuttals"]["con_rebuttals"]) == 2


def test_run_debate_rejects_empty_topic():
    with pytest.raises(ValueError):
        debate_graph_module.run_debate("   ")