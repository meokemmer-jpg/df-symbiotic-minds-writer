import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# [CRUX-MK]
from datetime import datetime, timezone

import pytest

from symbiotic_minds_writer import (
    CHAPTER_OUTLINE,
    build_book_skeleton,
    generate_chapter_draft,
    load_config,
)


def test_mock_default_returns_stub_without_real_permissions():
    draft = generate_chapter_draft(
        1,
        now=datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc),
    )

    assert draft.mode == "mock"
    assert draft.title == CHAPTER_OUTLINE[0]
    assert "Phronesis" in draft.content
    assert draft.metadata["real_llm_called"] is False
    assert draft.slug.startswith("01-")


def test_real_mode_requires_both_env_flag_and_ticket():
    with pytest.raises(PermissionError):
        generate_chapter_draft(
            2,
            prefer_real_llm=True,
            env={"DF_BOOK_REAL_ENABLED": "true"},
        )

    draft = generate_chapter_draft(
        2,
        prefer_real_llm=True,
        env={
            "DF_BOOK_REAL_ENABLED": "true",
            "PHRONESIS_TICKET": "approved-123",
        },
    )

    assert draft.mode == "real-ready"
    assert draft.metadata["phronesis_ticket_present"] is True
    assert "keinen externen API-Call" in draft.content


def test_book_skeleton_builds_selected_chapters_with_real_mock_default():
    skeleton = build_book_skeleton([1, 14])

    assert len(skeleton) == 2
    assert skeleton[0]["chapter_number"] == 1
    assert skeleton[1]["chapter_number"] == 14
    assert skeleton[0]["mode"] == "mock"
    assert skeleton[1]["title"] == CHAPTER_OUTLINE[13]


def test_load_config_interprets_env_gate_correctly():
    blocked = load_config({"DF_BOOK_REAL_ENABLED": "true", "PHRONESIS_TICKET": ""})
    allowed = load_config(
        {"DF_BOOK_REAL_ENABLED": "true", "PHRONESIS_TICKET": "ticket-xyz"}
    )

    assert blocked.may_call_real_llm is False
    assert blocked.mode == "mock"
    assert allowed.may_call_real_llm is True
    assert allowed.mode == "real"
