import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# [CRUX-MK]
from symbiotic_minds_writer import (
    get_chapter_spec,
    generate_chapter_draft,
    check_kaestner_style,
    get_book_toc,
    generate_all_stubs,
    CHAPTER_REGISTRY,
    ChapterDraft,
    StyleCheckResult,
)

import os
import pytest


# --- Registry ---

def test_chapter_registry_has_14_chapters():
    assert len(CHAPTER_REGISTRY) == 14


def test_chapter_registry_ids_are_1_to_14():
    assert set(CHAPTER_REGISTRY.keys()) == set(range(1, 15))


def test_chapter_registry_required_fields():
    required = {"title", "subtitle", "core_thesis", "keywords", "target_words"}
    for cid, spec in CHAPTER_REGISTRY.items():
        missing = required - set(spec.keys())
        assert not missing, f"Kapitel {cid}: Felder fehlen: {missing}"


def test_chapter_registry_target_words_positive():
    for cid, spec in CHAPTER_REGISTRY.items():
        assert spec["target_words"] > 0, f"Kapitel {cid}: target_words muss > 0 sein"


# --- get_chapter_spec ---

def test_get_chapter_spec_returns_chapter_id():
    spec = get_chapter_spec(1)
    assert spec["chapter_id"] == 1


def test_get_chapter_spec_all_chapters_accessible():
    for i in range(1, 15):
        spec = get_chapter_spec(i)
        assert spec["chapter_id"] == i
        assert spec["title"]


def test_get_chapter_spec_invalid_zero_raises():
    with pytest.raises(ValueError, match="unbekannt"):
        get_chapter_spec(0)


def test_get_chapter_spec_invalid_15_raises():
    with pytest.raises(ValueError):
        get_chapter_spec(15)


def test_get_chapter_spec_invalid_negative_raises():
    with pytest.raises(ValueError):
        get_chapter_spec(-1)


# --- generate_chapter_draft: Mock-Default ---

def test_mock_default_when_no_env(monkeypatch):
    monkeypatch.delenv("DF_BOOK_REAL_ENABLED", raising=False)
    draft = generate_chapter_draft(1)
    assert draft.source == "mock"


def test_explicit_mock_returns_mock():
    draft = generate_chapter_draft(4, backend="mock")
    assert draft.source == "mock"


def test_mock_draft_is_chapter_draft_instance():
    draft = generate_chapter_draft(2, backend="mock")
    assert isinstance(draft, ChapterDraft)


def test_mock_draft_has_correct_chapter_id():
    for cid in [1, 7, 14]:
        draft = generate_chapter_draft(cid, backend="mock")
        assert draft.chapter_id == cid


def test_mock_draft_has_title():
    draft = generate_chapter_draft(3, backend="mock")
    assert draft.title == CHAPTER_REGISTRY[3]["title"]


def test_mock_draft_source_is_valid_string():
    draft = generate_chapter_draft(5, backend="mock")
    assert draft.source in ("mock", "real-llm", "stub")


def test_mock_draft_content_not_empty():
    draft = generate_chapter_draft(6, backend="mock")
    assert len(draft.content) > 0


def test_mock_draft_word_count_positive():
    draft = generate_chapter_draft(8, backend="mock")
    assert draft.word_count > 0


def test_mock_draft_has_iso_timestamp():
    draft = generate_chapter_draft(9, backend="mock")
    assert "T" in draft.iso_timestamp
    # UTC offset or Z
    assert "+" in draft.iso_timestamp or "Z" in draft.iso_timestamp


def test_mock_draft_phronesis_ticket_is_none():
    draft = generate_chapter_draft(10, backend="mock")
    assert draft.phronesis_ticket is None


def test_mock_draft_content_hash_set():
    draft = generate_chapter_draft(11, backend="mock")
    assert draft.content_hash
    assert len(draft.content_hash) == 16


def test_mock_draft_content_includes_chapter_number():
    for cid in range(1, 15):
        draft = generate_chapter_draft(cid, backend="mock")
        assert str(cid) in draft.content


def test_mock_draft_content_includes_crux_marker():
    draft = generate_chapter_draft(1, backend="mock")
    assert "CRUX-MK" in draft.content


def test_mock_draft_style_warnings_is_list():
    draft = generate_chapter_draft(12, backend="mock")
    assert isinstance(draft.style_warnings, list)


# --- ENV-Var Gate ---

def test_env_false_yields_mock(monkeypatch):
    monkeypatch.setenv("DF_BOOK_REAL_ENABLED", "false")
    draft = generate_chapter_draft(2)
    assert draft.source == "mock"


def test_env_truthy_variants_do_not_activate(monkeypatch):
    """Nur exakter String 'true' aktiviert Real-Modus."""
    for non_true in ("1", "yes", "True", "TRUE", "on", "enabled"):
        monkeypatch.setenv("DF_BOOK_REAL_ENABLED", non_true)
        draft = generate_chapter_draft(3)
        assert draft.source == "mock", f"'{non_true}' darf Real-Modus nicht aktivieren"


def test_env_true_without_ticket_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("DF_BOOK_REAL_ENABLED", "true")
    monkeypatch.delenv("PHRONESIS_TICKET", raising=False)
    draft = generate_chapter_draft(4)
    assert draft.source == "mock"


# --- Real-LLM backend: Phronesis-Gate ---

def test_real_llm_without_ticket_falls_back_to_mock(monkeypatch):
    monkeypatch.delenv("PHRONESIS_TICKET", raising=False)
    draft = generate_chapter_draft(7, backend="real-llm", phronesis_ticket=None)
    assert draft.source == "mock"


def test_real_llm_without_ticket_has_phronesis_warning(monkeypatch):
    monkeypatch.delenv("PHRONESIS_TICKET", raising=False)
    draft = generate_chapter_draft(7, backend="real-llm", phronesis_ticket=None)
    assert any("PHRONESIS_TICKET" in w for w in draft.style_warnings)


def test_real_llm_with_explicit_ticket_returns_stub():
    draft = generate_chapter_draft(8, backend="real-llm", phronesis_ticket="PT-TEST-001")
    assert draft.source in ("stub", "real-llm")
    assert draft.phronesis_ticket == "PT-TEST-001"


def test_real_llm_with_env_ticket(monkeypatch):
    monkeypatch.setenv("PHRONESIS_TICKET", "PT-ENV-002")
    draft = generate_chapter_draft(9, backend="real-llm")
    assert draft.phronesis_ticket == "PT-ENV-002"
    assert draft.source in ("stub", "real-llm")


def test_explicit_ticket_overrides_env_ticket(monkeypatch):
    monkeypatch.setenv("PHRONESIS_TICKET", "PT-ENV-003")
    draft = generate_chapter_draft(10, backend="real-llm", phronesis_ticket="PT-EXPLICIT-004")
    assert draft.phronesis_ticket == "PT-EXPLICIT-004"


# --- check_kaestner_style ---

def test_kaestner_style_clean_text_passes():
    text = "KI erkennt Muster. Menschen entscheiden. Diese Arbeitsteilung funktioniert."
    result = check_kaestner_style(text)
    assert isinstance(result, StyleCheckResult)
    assert result.word_count > 0
    assert result.avg_sentence_length < 20


def test_kaestner_style_floskel_triggers_warning():
    text = "Grundsaetzlich ist die Symbiose sozusagen ein wichtiger Prozess."
    result = check_kaestner_style(text)
    assert not result.passed
    assert any("Floskel" in w for w in result.warnings)


def test_kaestner_style_long_sentences_triggers_warning():
    sentence = " ".join(["Wort"] * 30)
    text = f"{sentence}. {sentence}."
    result = check_kaestner_style(text)
    assert any("Satzlaenge" in w for w in result.warnings)


def test_kaestner_style_empty_text_fails():
    result = check_kaestner_style("")
    assert not result.passed
    assert result.word_count == 0


def test_kaestner_style_short_text_warns():
    result = check_kaestner_style("Kurz.")
    assert any("kurz" in w.lower() or "Stub" in w for w in result.warnings)


def test_kaestner_style_word_count_correct():
    text = "Eins zwei drei. Vier fuenf."
    result = check_kaestner_style(text)
    assert result.word_count == 5


def test_kaestner_style_avg_sentence_length():
    # 4 words + 2 words = avg 3.0
    text = "Eins zwei drei vier. Fuenf sechs."
    result = check_kaestner_style(text)
    assert abs(result.avg_sentence_length - 3.0) < 0.1


# --- get_book_toc ---

def test_toc_has_14_entries():
    toc = get_book_toc()
    assert len(toc) == 14


def test_toc_is_ordered():
    toc = get_book_toc()
    ids = [e["chapter_id"] for e in toc]
    assert ids == list(range(1, 15))


def test_toc_entries_have_required_fields():
    toc = get_book_toc()
    for entry in toc:
        assert "chapter_id" in entry
        assert "title" in entry
        assert "subtitle" in entry
        assert "target_words" in entry


def test_toc_first_chapter():
    toc = get_book_toc()
    assert toc[0]["chapter_id"] == 1


def test_toc_last_chapter():
    toc = get_book_toc()
    assert toc[-1]["chapter_id"] == 14


# --- generate_all_stubs ---

def test_all_stubs_returns_14_drafts():
    drafts = generate_all_stubs()
    assert len(drafts) == 14


def test_all_stubs_all_mock_source():
    drafts = generate_all_stubs()
    for d in drafts:
        assert d.source == "mock"


def test_all_stubs_covers_all_chapters():
    drafts = generate_all_stubs()
    assert {d.chapter_id for d in drafts} == set(range(1, 15))


def test_all_stubs_all_have_content():
    drafts = generate_all_stubs()
    for d in drafts:
        assert d.content
        assert d.word_count > 0


def test_all_stubs_content_hashes_unique():
    drafts = generate_all_stubs()
    hashes = [d.content_hash for d in drafts]
    # Alle Kapitel haben unterschiedliche Inhalte → unterschiedliche Hashes
    assert len(set(hashes)) == 14

