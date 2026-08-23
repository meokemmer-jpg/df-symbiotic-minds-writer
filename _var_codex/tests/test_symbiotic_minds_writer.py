import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# [CRUX-MK]
from symbiotic_minds_writer import (
    ChapterDraft,
    build_book_skeleton,
    can_use_real_llm,
    resolve_generation_mode,
)


def test_book_skeleton_defaults_to_mock_and_builds_all_chapters():
    book = build_book_skeleton(env={})

    assert book["book_title"] == "Symbiotic Minds"
    assert book["effective_mode"] == "mock"
    assert len(book["chapters"]) == 14
    assert all(isinstance(chapter, ChapterDraft) for chapter in book["chapters"])

    first = book["chapters"][0]
    assert first.number == 1
    assert first.title == "Die symbiotische Beziehung"
    assert first.mode == "mock"
    assert "Mensch + AI > Mensch allein > AI allein." in first.content
    assert "\n" in first.content


def test_real_mode_requires_both_env_flags():
    assert can_use_real_llm({}) is False
    assert can_use_real_llm({"DF_BOOK_REAL_ENABLED": "true"}) is False
    assert can_use_real_llm(
        {"DF_BOOK_REAL_ENABLED": "true", "PHRONESIS_TICKET": "TICKET-44"}
    ) is True
    assert resolve_generation_mode(
        "auto",
        {"DF_BOOK_REAL_ENABLED": "true", "PHRONESIS_TICKET": "TICKET-44"},
    ) == "real-ready"


def test_real_mode_without_ticket_raises_permission_error():
    try:
        build_book_skeleton(requested_mode="real", env={"DF_BOOK_REAL_ENABLED": "true"})
    except PermissionError as exc:
        assert "PHRONESIS_TICKET" in str(exc)
    else:
        raise AssertionError("PermissionError expected for forbidden real mode")
