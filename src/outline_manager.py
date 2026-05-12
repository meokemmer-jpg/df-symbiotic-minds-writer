"""Outline-Manager fuer Symbiotic-Minds. Buch-Struktur + Kapitel-Liste. [CRUX-MK]"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass(frozen=True)
class Chapter:
    """Frozen Chapter-Definition (immutable nach Outline-Lock)."""
    number: int
    title: str
    target_words: int = 8000
    status: str = "outlined"  # outlined | drafted | reviewed | final


@dataclass
class BookOutline:
    """Book-Outline mit Kapitel-Liste + Metadata."""
    book_title: str
    subtitle: str
    chapters: List[Chapter] = field(default_factory=list)


# Symbiotic-Minds Outline (14 Kapitel)
SYMBIOTIC_MINDS_OUTLINE: List[Chapter] = [
    Chapter(1, "Die symbiotische Beziehung - Definition + Abgrenzung"),
    Chapter(2, "Mensch als Phronesis-Traeger - Was nur Menschen koennen"),
    Chapter(3, "AI als Pattern-Recognizer - Was AI kann, Mensch nicht"),
    Chapter(4, "Trinity-Pattern - Conservative/Aggressive/Contrarian-Synthese"),
    Chapter(5, "Hamilton-Optimierung - H = u + lambda*f als Lebensformel"),
    Chapter(6, "Working Memory - Wie symbiotische Systeme Information teilen"),
    Chapter(7, "Bounded Veto - Wer hat Veto-Rechte wann?"),
    Chapter(8, "Cognitive Load Distribution - Aufteilung mentaler Last"),
    Chapter(9, "Failure Modes - Wenn Symbiose kippt"),
    Chapter(10, "Wisdom Cultivation - Mindfulness als Symbiose-Training"),
    Chapter(11, "Family-Office als Test-Case - K_0/Q_0-Schutz"),
    Chapter(12, "Hotel-Operations als Test-Case - HeyLou Trinity"),
    Chapter(13, "Praxis-Patterns - 50 konkrete Symbiose-Patterns"),
    Chapter(14, "Ausblick - Wo geht Mensch-AI-Symbiose hin?"),
]


class OutlineManager:
    """Verwaltet Book-Outline (immutable nach Lock)."""

    def __init__(self, book_title: str = "Symbiotic Minds",
                 subtitle: str = "Mensch-AI-Symbiose"):
        self.outline = BookOutline(
            book_title=book_title,
            subtitle=subtitle,
            chapters=list(SYMBIOTIC_MINDS_OUTLINE),
        )

    def get_chapter(self, number: int) -> Optional[Chapter]:
        """Liefert Chapter by number (1-indexed)."""
        for ch in self.outline.chapters:
            if ch.number == number:
                return ch
        return None

    def list_chapters(self) -> List[Chapter]:
        """Liefert alle Kapitel (frozen, sicher fuer Iteration)."""
        return list(self.outline.chapters)

    def chapter_count(self) -> int:
        """Anzahl Kapitel im Outline."""
        return len(self.outline.chapters)

    def total_target_words(self) -> int:
        """Summe aller target_words ueber alle Kapitel."""
        return sum(ch.target_words for ch in self.outline.chapters)

    def metadata(self) -> Dict[str, str]:
        """Buch-Metadata fuer Verlag/Audit."""
        return {
            "title": self.outline.book_title,
            "subtitle": self.outline.subtitle,
            "chapter_count": str(self.chapter_count()),
            "target_total_words": str(self.total_target_words()),
        }
