from __future__ import annotations

import os
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

BOOK_TITLE = "Symbiotic Minds"
WAVE = 44
WRITER_ID = "df-symbiotic-minds-writer"

OUTLINE = [
    "Die symbiotische Beziehung - Definition + Abgrenzung",
    "Mensch als Phronesis-Traeger - Was nur Menschen koennen",
    "AI als Pattern-Recognizer - Was AI kann, Mensch nicht",
    "Trinity-Pattern - Conservative/Aggressive/Contrarian-Synthese",
    "Hamilton-Optimierung - H = u + lambda*f als Lebensformel",
    "Working Memory - Wie symbiotische Systeme Information teilen",
    "Bounded Veto - Wer hat Veto-Rechte wann?",
    "Cognitive Load Distribution - Aufteilung mentaler Last",
    "Failure Modes - Wenn Symbiose kippt",
    "Wisdom Cultivation - Mindfulness als Symbiose-Training",
    "Family-Office als Test-Case - K_0/Q_0-Schutz",
    "Hotel-Operations als Test-Case - HeyLou Trinity",
    "Praxis-Patterns - 50 konkrete Symbiose-Patterns",
    "Ausblick - Wo geht Mensch-AI-Symbiose hin?",
]

STRICT_CONDITIONS = {
    "real_llm_env": "DF_BOOK_REAL_ENABLED",
    "ticket_env": "PHRONESIS_TICKET",
    "real_llm_required_value": "true",
}

DEFAULT_STUB_TEMPLATE = (
    "Kapitel {number}: {title}\n\n"
    "These:\n"
    "Mensch und KI werden hier nicht als Gegner beschrieben, sondern als Arbeitspartner "
    "mit ungleichen Staerken.\n\n"
    "Rollenbild:\n"
    "- Mensch: Phronesis, Urteil, Verantwortung, Sinn\n"
    "- KI: Mustererkennung, Verdichtung, Variantenraum\n\n"
    "Trinity-Frage:\n"
    "Welche konservative, aggressive und kontrariaere Lesart entstehen aus diesem Kapitel?\n\n"
    "Praxisfokus:\n"
    "Das Kapitel endet mit einem klaren Arbeitsmuster statt mit einem Technikmythos."
)


@dataclass(frozen=True)
class ChapterDraft:
    chapter_number: int
    title: str
    mode: str
    content: str
    real_llm_allowed: bool

    def as_dict(self) -> Dict[str, object]:
        return asdict(self)


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _is_truthy_true(value: Optional[str]) -> bool:
    return (value or "").strip().lower() == STRICT_CONDITIONS["real_llm_required_value"]


def real_llm_enabled(env: Optional[Dict[str, str]] = None) -> bool:
    env = env or os.environ
    return _is_truthy_true(env.get(STRICT_CONDITIONS["real_llm_env"]))


def has_valid_phronesis_ticket(ticket: Optional[str]) -> bool:
    if not ticket:
        return False
    return bool(re.fullmatch(r"PHR-[A-Z0-9]{6,}", ticket.strip()))


def real_llm_allowed(
    env: Optional[Dict[str, str]] = None,
    ticket: Optional[str] = None,
) -> bool:
    env = env or os.environ
    effective_ticket = ticket if ticket is not None else env.get(STRICT_CONDITIONS["ticket_env"])
    return real_llm_enabled(env) and has_valid_phronesis_ticket(effective_ticket)


def chapter_title(chapter_number: int) -> str:
    if chapter_number < 1 or chapter_number > len(OUTLINE):
        raise IndexError(f"chapter_number must be between 1 and {len(OUTLINE)}")
    return OUTLINE[chapter_number - 1]


def generate_chapter_stub(chapter_number: int) -> ChapterDraft:
    title = chapter_title(chapter_number)
    content = _normalize_text(DEFAULT_STUB_TEMPLATE.format(number=chapter_number, title=title))
    return ChapterDraft(
        chapter_number=chapter_number,
        title=title,
        mode="mock",
        content=content,
        real_llm_allowed=False,
    )


def generate_chapter_draft(
    chapter_number: int,
    env: Optional[Dict[str, str]] = None,
    ticket: Optional[str] = None,
) -> ChapterDraft:
    """
    Kernlogik:
    - Standard ist Mock.
    - Real-LLM-Modus ist nur freigegeben, wenn ENV und Ticket passen.
    - Auch im freigegebenen Fall erzeugt dieses Modul absichtlich keinen externen Call,
      sondern markiert nur die Ausfuehrung als 'real-eligible'.
    """
    title = chapter_title(chapter_number)
    if not real_llm_allowed(env=env, ticket=ticket):
        return generate_chapter_stub(chapter_number)

    content = _normalize_text(
        f"Kapitel {chapter_number}: {title}\n\n"
        "Real-LLM waere hier freigegeben, aber dieses stdlib-Modul fuehrt absichtlich "
        "keinen externen Modellaufruf aus. Der naechste Orchestrator-Schritt kann "
        "diese Freigabe pruefbar weiterverwenden."
    )
    return ChapterDraft(
        chapter_number=chapter_number,
        title=title,
        mode="real-eligible",
        content=content,
        real_llm_allowed=True,
    )


def generate_book_skeleton(
    env: Optional[Dict[str, str]] = None,
    ticket: Optional[str] = None,
) -> List[ChapterDraft]:
    return [
        generate_chapter_draft(i, env=env, ticket=ticket)
        for i in range(1, len(OUTLINE) + 1)
    ]
# [CRUX-MK]
