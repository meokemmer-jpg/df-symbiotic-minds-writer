"""Tests fuer style_guide. [CRUX-MK]"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.style_guide import StyleGuide, StyleReport


def test_style_guide_init():
    sg = StyleGuide()
    assert sg.max_sentence_words == 25
    assert sg.max_paragraph_sentences == 5


def test_audit_short_text_passes():
    """Short Kaestner-style text should pass."""
    sg = StyleGuide()
    text = "Das ist ein kurzer Satz. Hier ist noch einer. Gut so."
    report = sg.audit(text)
    assert report.passes is True
    assert report.sentences_checked == 3


def test_audit_long_sentence_warns():
    """Long sentence triggers kaestner_sentence_length warn."""
    sg = StyleGuide(max_sentence_words=5)
    text = "Dies ist ein sehr langer Satz mit vielen Worten."
    report = sg.audit(text)
    assert any(v.rule == "kaestner_sentence_length" for v in report.violations)


def test_split_sentences_handles_empty():
    sg = StyleGuide()
    assert sg.split_sentences("") == []
    assert sg.split_sentences("   ") == []
