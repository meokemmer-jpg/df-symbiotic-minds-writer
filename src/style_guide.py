"""Style-Guide-Enforcement: Kaestner-Stil + Dyslexie-friendly. [CRUX-MK]"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple


# Kaestner-Stil-Heuristiken (vereinfacht)
KAESTNER_MAX_SENTENCE_WORDS = 25  # Lange Saetze splitten
KAESTNER_PREFER_AKTIVE_STIMME = True  # Aktiv > Passiv
KAESTNER_MAX_NESTED_CLAUSES = 2  # Verschachtelung begrenzen

# Dyslexie-friendly
DYSLEXIA_PREFERRED_SENTENCE_LEN_AVG = 15  # Worte/Satz Schnitt
DYSLEXIA_MAX_PARAGRAPH_SENTENCES = 5  # Absaetze kurz


@dataclass
class StyleViolation:
    """Eine Style-Verletzung."""
    rule: str
    severity: str  # info | warn | error
    message: str
    line_offset: int = 0


@dataclass
class StyleReport:
    """Style-Audit-Report."""
    violations: List[StyleViolation] = field(default_factory=list)
    sentences_checked: int = 0
    paragraphs_checked: int = 0
    avg_sentence_len: float = 0.0
    passes: bool = True


class StyleGuide:
    """Kaestner-Stil + Dyslexie-Friendly Linter."""

    def __init__(self,
                 max_sentence_words: int = KAESTNER_MAX_SENTENCE_WORDS,
                 max_paragraph_sentences: int = DYSLEXIA_MAX_PARAGRAPH_SENTENCES):
        self.max_sentence_words = max_sentence_words
        self.max_paragraph_sentences = max_paragraph_sentences

    def split_sentences(self, text: str) -> List[str]:
        """Naive sentence splitter (period/exclam/question)."""
        if not text:
            return []
        parts = re.split(r"(?<=[.!?])\s+", text.strip())
        return [p for p in parts if p]

    def split_paragraphs(self, text: str) -> List[str]:
        """Paragraphs separated by blank lines."""
        if not text:
            return []
        paragraphs = re.split(r"\n\s*\n", text.strip())
        return [p.strip() for p in paragraphs if p.strip()]

    def count_words(self, sentence: str) -> int:
        """Naive word count."""
        return len(sentence.split())

    def audit(self, text: str) -> StyleReport:
        """Audit Text gegen Style-Guide. Returns Report."""
        report = StyleReport()
        sentences = self.split_sentences(text)
        paragraphs = self.split_paragraphs(text)

        report.sentences_checked = len(sentences)
        report.paragraphs_checked = len(paragraphs)

        # Sentence-Length Check
        for i, sent in enumerate(sentences):
            wc = self.count_words(sent)
            if wc > self.max_sentence_words:
                report.violations.append(StyleViolation(
                    rule="kaestner_sentence_length",
                    severity="warn",
                    message=f"Sentence {i+1}: {wc} words (max {self.max_sentence_words})",
                    line_offset=i,
                ))

        # Paragraph-Sentence-Count Check
        for i, para in enumerate(paragraphs):
            para_sentences = self.split_sentences(para)
            if len(para_sentences) > self.max_paragraph_sentences:
                report.violations.append(StyleViolation(
                    rule="dyslexia_paragraph_length",
                    severity="info",
                    message=f"Paragraph {i+1}: {len(para_sentences)} sentences (max {self.max_paragraph_sentences})",
                    line_offset=i,
                ))

        # Avg Sentence-Length
        if sentences:
            total_words = sum(self.count_words(s) for s in sentences)
            report.avg_sentence_len = total_words / len(sentences)

        # Pass/Fail
        errors = [v for v in report.violations if v.severity == "error"]
        report.passes = len(errors) == 0

        return report
