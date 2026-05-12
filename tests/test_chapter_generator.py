"""Tests fuer chapter_generator. [CRUX-MK]"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chapter_generator import ChapterGenerator, GeneratedChapter
from src.outline_manager import Chapter, OutlineManager


def test_generator_init():
    gen = ChapterGenerator()
    assert gen.book_title == "Symbiotic Minds"


def test_default_mock_mode():
    """Without ENV-Var, defaults to mock."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("DF_BOOK_REAL_ENABLED", None)
        gen = ChapterGenerator()
        assert gen._check_real_mode() is False


def test_mock_chapter_generation():
    gen = ChapterGenerator()
    ch = Chapter(1, "Test Chapter")
    result = gen.generate_chapter(ch)
    assert result.source == "mock"
    assert result.chapter_number == 1
    assert result.chapter_title == "Test Chapter"
    assert "MOCK STUB" in result.text
    assert result.word_count > 0


def test_real_mode_without_ticket_raises():
    """Real-Mode ohne PHRONESIS_TICKET raises RuntimeError."""
    with patch.dict(os.environ, {"DF_BOOK_REAL_ENABLED": "true"}, clear=False):
        os.environ.pop("PHRONESIS_TICKET", None)
        gen = ChapterGenerator()
        ch = Chapter(1, "Test")
        try:
            gen.generate_chapter(ch)
            raise AssertionError("Should have raised RuntimeError")
        except RuntimeError as e:
            assert "PHRONESIS_TICKET" in str(e)


def test_real_mode_with_ticket_raises_not_implemented():
    """Skeleton: Real-Mode mit Ticket raises NotImplementedError."""
    with patch.dict(os.environ, {
        "DF_BOOK_REAL_ENABLED": "true",
        "PHRONESIS_TICKET": "PT-2026-05-11-001",
    }, clear=False):
        gen = ChapterGenerator()
        ch = Chapter(1, "Test")
        try:
            gen.generate_chapter(ch)
            raise AssertionError("Should raise NotImplementedError")
        except NotImplementedError as e:
            assert "Welle-45+" in str(e)


def test_env_var_truthy_strict_check():
    """ENV-Var-Pattern: nur '=true' aktiviert. '=1' / '=yes' / '=True' bleibt mock."""
    for val in ["1", "yes", "True", "TRUE", "y"]:
        with patch.dict(os.environ, {"DF_BOOK_REAL_ENABLED": val}, clear=False):
            gen = ChapterGenerator()
            assert gen._check_real_mode() is False, f"Value '{val}' should NOT activate real mode"


def test_source_field_in_output():
    """Property-3 (ENV-Var-Gated-Real-Integration-Default Rule)."""
    gen = ChapterGenerator()
    ch = Chapter(1, "Test")
    result = gen.generate_chapter(ch)
    assert result.source in ("mock", "real-llm", "stub")
    assert result.iso_timestamp is not None
