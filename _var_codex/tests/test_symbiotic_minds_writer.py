import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# [CRUX-MK]
from symbiotic_minds_writer import (
    OUTLINE,
    generate_book_skeleton,
    generate_chapter_draft,
    generate_chapter_stub,
    real_llm_allowed,
)


def test_mock_is_default_without_env_or_ticket():
    draft = generate_chapter_draft(1, env={})
    assert draft.mode == "mock"
    assert draft.real_llm_allowed is False
    assert "Phronesis" in draft.content
    assert "Mustererkennung" in draft.content


def test_real_mode_requires_both_env_and_valid_ticket():
    assert real_llm_allowed(env={"DF_BOOK_REAL_ENABLED": "true"}, ticket=None) is False
    assert real_llm_allowed(env={"DF_BOOK_REAL_ENABLED": "false"}, ticket="PHR-ABC123") is False
    assert real_llm_allowed(env={"DF_BOOK_REAL_ENABLED": "true"}, ticket="bad-ticket") is False
    assert real_llm_allowed(env={"DF_BOOK_REAL_ENABLED": "true"}, ticket="PHR-ABC123") is True

    draft = generate_chapter_draft(
        4,
        env={"DF_BOOK_REAL_ENABLED": "true"},
        ticket="PHR-ABC123",
    )
    assert draft.mode == "real-eligible"
    assert draft.real_llm_allowed is True
    assert "keinen externen Modellaufruf" in draft.content


def test_book_skeleton_covers_full_outline_and_keeps_mock_default():
    book = generate_book_skeleton(env={})
    assert len(book) == len(OUTLINE)
    assert all(ch.mode == "mock" for ch in book)
    assert book[0].chapter_number == 1
    assert book[-1].chapter_number == len(OUTLINE)
    assert book[-1].title == OUTLINE[-1]


def test_generate_chapter_stub_rejects_invalid_chapter_numbers():
    draft = generate_chapter_stub(2)
    assert draft.title == OUTLINE[1]

    try:
        generate_chapter_stub(0)
    except IndexError as exc:
        assert "chapter_number must be between" in str(exc)
    else:
        raise AssertionError("Expected IndexError for invalid chapter number")
