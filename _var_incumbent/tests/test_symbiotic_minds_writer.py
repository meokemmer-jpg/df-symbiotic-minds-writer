import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
# [CRUX-MK]
import os
import pytest
from symbiotic_minds_writer import (
    CHAPTER_OUTLINE,
    ChapterDraft,
    audit_log_entry,
    generate_book_skeleton,
    generate_chapter_draft,
    get_chapter_info,
    is_real_mode_enabled,
    validate_kaestner_style,
    write_chapter_to_file,
)


# --- Outline ---

def test_outline_has_14_chapters():
    assert len(CHAPTER_OUTLINE) == 14


def test_outline_ids_sequential():
    ids = [c["id"] for c in CHAPTER_OUTLINE]
    assert ids == list(range(1, 15))


def test_outline_required_fields():
    required = {"id", "title", "subtitle", "core_thesis", "key_concepts", "approx_words"}
    for chapter in CHAPTER_OUTLINE:
        missing = required - set(chapter.keys())
        assert not missing, f"Kapitel {chapter['id']} fehlt Felder: {missing}"


def test_outline_titles_unique():
    titles = [c["title"] for c in CHAPTER_OUTLINE]
    assert len(titles) == len(set(titles))


def test_outline_key_concepts_nonempty():
    for chapter in CHAPTER_OUTLINE:
        assert chapter["key_concepts"], f"Kapitel {chapter['id']}: key_concepts leer"


# --- get_chapter_info ---

def test_get_chapter_info_chapter_1():
    info = get_chapter_info(1)
    assert info["id"] == 1
    assert "symbiotisch" in info["title"].lower()


def test_get_chapter_info_chapter_14():
    info = get_chapter_info(14)
    assert info["id"] == 14
    assert "ausblick" in info["title"].lower()


def test_get_chapter_info_invalid_raises():
    with pytest.raises(ValueError, match="15"):
        get_chapter_info(15)


def test_get_chapter_info_zero_raises():
    with pytest.raises(ValueError, match="0"):
        get_chapter_info(0)


# --- ENV-Var Gate ---

def test_real_mode_disabled_by_default():
    os.environ.pop("DF_BOOK_REAL_ENABLED", None)
    assert not is_real_mode_enabled()


def test_real_mode_enabled_only_for_exact_true():
    os.environ["DF_BOOK_REAL_ENABLED"] = "true"
    assert is_real_mode_enabled()
    os.environ.pop("DF_BOOK_REAL_ENABLED")


@pytest.mark.parametrize("val", ["1", "yes", "True", "TRUE", "on", "false", ""])
def test_real_mode_not_enabled_for_other_values(val):
    os.environ["DF_BOOK_REAL_ENABLED"] = val
    assert not is_real_mode_enabled()
    os.environ.pop("DF_BOOK_REAL_ENABLED")


# --- generate_chapter_draft (Mock) ---

def test_draft_mock_default_source():
    os.environ.pop("DF_BOOK_REAL_ENABLED", None)
    draft = generate_chapter_draft(1)
    assert draft.source == "mock"


def test_draft_mock_no_phronesis_ticket():
    os.environ.pop("DF_BOOK_REAL_ENABLED", None)
    draft = generate_chapter_draft(1)
    assert draft.phronesis_ticket is None


def test_draft_mock_contains_stub_marker():
    os.environ.pop("DF_BOOK_REAL_ENABLED", None)
    draft = generate_chapter_draft(4)
    assert "MOCK-STUB" in draft.content


def test_draft_chapter_id_correct():
    for cid in [1, 7, 14]:
        draft = generate_chapter_draft(cid)
        assert draft.chapter_id == cid


def test_draft_has_title_and_subtitle():
    draft = generate_chapter_draft(2)
    assert draft.title
    assert draft.subtitle


def test_draft_word_count_positive():
    draft = generate_chapter_draft(3)
    assert draft.word_count > 0


def test_draft_style_issues_is_list():
    draft = generate_chapter_draft(5)
    assert isinstance(draft.style_issues, list)


def test_draft_iso_timestamp_present():
    draft = generate_chapter_draft(6)
    assert draft.iso_timestamp
    assert "T" in draft.iso_timestamp  # ISO 8601 format


# --- generate_chapter_draft (Real-Mode) ---

def test_real_mode_without_ticket_raises():
    os.environ["DF_BOOK_REAL_ENABLED"] = "true"
    os.environ.pop("PHRONESIS_TICKET", None)
    try:
        with pytest.raises(RuntimeError, match="PHRONESIS_TICKET"):
            generate_chapter_draft(1)
    finally:
        os.environ.pop("DF_BOOK_REAL_ENABLED", None)


def test_real_mode_with_ticket_sets_source():
    os.environ["DF_BOOK_REAL_ENABLED"] = "true"
    os.environ["PHRONESIS_TICKET"] = "PT-TEST-001"
    try:
        draft = generate_chapter_draft(1)
        assert draft.source == "real-llm"
    finally:
        os.environ.pop("DF_BOOK_REAL_ENABLED", None)
        os.environ.pop("PHRONESIS_TICKET", None)


def test_real_mode_with_ticket_records_ticket():
    os.environ["DF_BOOK_REAL_ENABLED"] = "true"
    os.environ["PHRONESIS_TICKET"] = "PT-TEST-002"
    try:
        draft = generate_chapter_draft(2)
        assert draft.phronesis_ticket == "PT-TEST-002"
    finally:
        os.environ.pop("DF_BOOK_REAL_ENABLED", None)
        os.environ.pop("PHRONESIS_TICKET", None)


# --- generate_book_skeleton ---

def test_skeleton_has_14_drafts():
    os.environ.pop("DF_BOOK_REAL_ENABLED", None)
    skeleton = generate_book_skeleton()
    assert len(skeleton) == 14


def test_skeleton_all_ids_present():
    os.environ.pop("DF_BOOK_REAL_ENABLED", None)
    skeleton = generate_book_skeleton()
    assert [d.chapter_id for d in skeleton] == list(range(1, 15))


def test_skeleton_all_mock_source():
    os.environ.pop("DF_BOOK_REAL_ENABLED", None)
    for draft in generate_book_skeleton():
        assert draft.source == "mock"


# --- validate_kaestner_style ---

def test_style_clean_text_no_issues():
    text = (
        "AI erkennt Muster. Menschen entscheiden.\n\n"
        "Das ist der Kern der Symbiose. Beide brauchen einander.\n\n"
        "Kein Wettbewerb. Keine Hierarchie. Nur Partnerschaft."
    )
    assert validate_kaestner_style(text) == []


def test_style_empty_content_reported():
    issues = validate_kaestner_style("")
    assert len(issues) > 0
    assert any("leer" in i.lower() for i in issues)


def test_style_whitespace_only_reported():
    issues = validate_kaestner_style("   \n  ")
    assert len(issues) > 0


def test_style_long_sentence_detected():
    long = "Dies ist " + " ".join(["ein weiteres Wort"] * 20) + "."
    issues = validate_kaestner_style(long)
    assert any("lang" in i.lower() or "woerter" in i.lower() for i in issues)


def test_style_long_paragraph_detected():
    # 200 words in one paragraph
    long_para = " ".join(["Wort"] * 200)
    issues = validate_kaestner_style(long_para)
    assert any("absaetz" in i.lower() or "absatz" in i.lower() for i in issues)


def test_style_excessive_passive_detected():
    passive_text = " ".join(["Es wurde gemacht."] * 10)
    issues = validate_kaestner_style(passive_text)
    assert any("passiv" in i.lower() for i in issues)


# --- ChapterDraft.to_dict ---

def test_to_dict_has_required_keys():
    draft = generate_chapter_draft(8)
    d = draft.to_dict()
    for key in ("chapter_id", "title", "subtitle", "content", "source",
                "iso_timestamp", "word_count", "style_issues", "phronesis_ticket"):
        assert key in d


def test_to_dict_chapter_id_matches():
    draft = generate_chapter_draft(9)
    assert draft.to_dict()["chapter_id"] == 9


def test_to_dict_source_is_mock():
    os.environ.pop("DF_BOOK_REAL_ENABLED", None)
    assert generate_chapter_draft(10).to_dict()["source"] == "mock"


# --- audit_log_entry ---

def test_audit_log_required_keys():
    draft = generate_chapter_draft(11)
    log = audit_log_entry(draft)
    for key in ("ts", "df", "action", "chapter_id", "source", "word_count",
                "style_issues_count", "phronesis_ticket"):
        assert key in log


def test_audit_log_df_name():
    draft = generate_chapter_draft(12)
    assert audit_log_entry(draft)["df"] == "df-symbiotic-minds-writer"


def test_audit_log_chapter_id_correct():
    draft = generate_chapter_draft(13)
    assert audit_log_entry(draft)["chapter_id"] == 13


def test_audit_log_default_action():
    draft = generate_chapter_draft(14)
    assert audit_log_entry(draft)["action"] == "GENERATE"


def test_audit_log_custom_action():
    draft = generate_chapter_draft(1)
    assert audit_log_entry(draft, action="REVIEW")["action"] == "REVIEW"


def test_audit_log_mock_no_ticket():
    os.environ.pop("DF_BOOK_REAL_ENABLED", None)
    draft = generate_chapter_draft(2)
    assert audit_log_entry(draft)["phronesis_ticket"] is None


# --- write_chapter_to_file ---

def test_write_creates_file(tmp_path):
    draft = generate_chapter_draft(1)
    out = write_chapter_to_file(draft, output_dir=str(tmp_path))
    assert out.exists()


def test_write_file_contains_frontmatter(tmp_path):
    draft = generate_chapter_draft(3)
    out = write_chapter_to_file(draft, output_dir=str(tmp_path))
    text = out.read_text(encoding="utf-8")
    assert "crux-mk: true" in text
    assert "chapter_id:" in text


def test_write_file_contains_content(tmp_path):
    draft = generate_chapter_draft(4)
    out = write_chapter_to_file(draft, output_dir=str(tmp_path))
    assert "MOCK-STUB" in out.read_text(encoding="utf-8")


def test_write_filename_contains_chapter_id(tmp_path):
    draft = generate_chapter_draft(5)
    out = write_chapter_to_file(draft, output_dir=str(tmp_path))
    assert "05" in out.name

