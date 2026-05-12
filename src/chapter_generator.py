"""Chapter-Generator. Mock-Default + Real-LLM via ENV-Var-Gate. [CRUX-MK]

Lambda-Honesty-Caveat (Welle-44):
- Real-LLM-Pfad ist STUB (kein _df_common.real_llm_wrappers Import in Skeleton)
- Mock-Default produziert deterministische Chapter-Stubs
- ENV-Var-Aktivierung wirft NotImplementedError bis Real-Integration in Welle-45+
"""

import os
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, List

from .outline_manager import Chapter
from .style_guide import StyleGuide, StyleReport


@dataclass
class GeneratedChapter:
    """Output eines Chapter-Generation-Runs."""
    chapter_number: int
    chapter_title: str
    text: str
    word_count: int
    source: str  # "mock" | "real-llm" | "stub"
    iso_timestamp: str
    style_passes: bool
    activation_gate_id: Optional[str] = None
    style_violations_count: int = 0


def _iso_now() -> str:
    """ISO timestamp UTC."""
    return datetime.now(timezone.utc).isoformat()


class ChapterGenerator:
    """Erzeugt Chapter-Texte (Mock-Default oder Real-LLM via ENV-Gate)."""

    def __init__(self,
                 book_title: str = "Symbiotic Minds",
                 style_guide: Optional[StyleGuide] = None):
        self.book_title = book_title
        self.style_guide = style_guide or StyleGuide()

    def _check_real_mode(self) -> bool:
        """Prueft ENV-Var fuer Real-LLM-Aktivierung. String-compare per ENV-Var-Gated-Rule."""
        return os.environ.get("DF_BOOK_REAL_ENABLED", "false") == "true"

    def _phronesis_ticket(self) -> Optional[str]:
        """PHRONESIS_TICKET aus ENV (Pflicht bei Real-Mode)."""
        ticket = os.environ.get("PHRONESIS_TICKET", "")
        return ticket if ticket else None

    def generate_mock(self, chapter: Chapter) -> GeneratedChapter:
        """Mock-Generation: deterministischer Stub-Text."""
        stub_text = (
            f"# Kapitel {chapter.number}: {chapter.title}\n\n"
            f"[MOCK STUB - Buch '{self.book_title}']\n\n"
            f"Dieses Kapitel ist ein Mock-Stub. Real-Generation erfordert "
            f"DF_BOOK_REAL_ENABLED=true + PHRONESIS_TICKET.\n\n"
            f"Target-Words: {chapter.target_words}\n"
            f"Status: {chapter.status}\n\n"
            f"Mock-Inhalt: Das Kapitel behandelt das Thema '{chapter.title}'. "
            f"Im Mock-Modus wird hier deterministischer Platzhalter-Text erzeugt. "
            f"Echter Inhalt entsteht nur bei aktivierter Real-LLM-Integration.\n"
        )

        report = self.style_guide.audit(stub_text)

        return GeneratedChapter(
            chapter_number=chapter.number,
            chapter_title=chapter.title,
            text=stub_text,
            word_count=len(stub_text.split()),
            source="mock",
            iso_timestamp=_iso_now(),
            style_passes=report.passes,
            style_violations_count=len(report.violations),
        )

    def generate_real(self, chapter: Chapter) -> GeneratedChapter:
        """Real-LLM-Generation. Skeleton stub - raises until Welle-45+."""
        # Pre-Action-Verification (K13-PAV)
        ticket = self._phronesis_ticket()
        if not ticket:
            raise RuntimeError(
                "Real-Mode erfordert PHRONESIS_TICKET ENV-Var. "
                "Phronesis-Pflicht Martin: K_0/Q_0-Approval-Decision-Card."
            )

        # SKELETON: real-llm not integrated yet
        raise NotImplementedError(
            "df-symbiotic-minds-writer Real-LLM-Mode ist Welle-45+-Pflicht. "
            "Skeleton-DF (Welle-44) liefert Mock-Default. "
            f"Ticket erkannt: {ticket}"
        )

    def generate_chapter(self, chapter: Chapter) -> GeneratedChapter:
        """Hauptmethode: dispatch to mock/real basierend auf ENV."""
        if self._check_real_mode():
            return self.generate_real(chapter)
        return self.generate_mock(chapter)
