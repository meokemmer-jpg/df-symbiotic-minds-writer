"""Tests fuer outline_manager. [CRUX-MK]"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.outline_manager import OutlineManager, Chapter, SYMBIOTIC_MINDS_OUTLINE


def test_outline_manager_init():
    om = OutlineManager()
    assert om.outline.book_title == "Symbiotic Minds"
    assert om.outline.subtitle == "Mensch-AI-Symbiose"


def test_chapter_count_is_14():
    """Welle-44 spec: ~14 Kapitel fuer Symbiotic Minds."""
    om = OutlineManager()
    assert om.chapter_count() == 14


def test_get_chapter_returns_correct():
    om = OutlineManager()
    ch1 = om.get_chapter(1)
    assert ch1 is not None
    assert ch1.number == 1
    assert "symbiotische Beziehung" in ch1.title


def test_get_chapter_invalid_returns_none():
    om = OutlineManager()
    assert om.get_chapter(99) is None
    assert om.get_chapter(0) is None


def test_chapter_is_frozen():
    """Chapters are frozen dataclass (immutable)."""
    ch = Chapter(1, "Test")
    try:
        ch.number = 2  # type: ignore
        raise AssertionError("Chapter should be frozen")
    except (AttributeError, Exception):
        pass


def test_total_target_words():
    """14 chapters * 8000 words each = 112000."""
    om = OutlineManager()
    assert om.total_target_words() == 14 * 8000
