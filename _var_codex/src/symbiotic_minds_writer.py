from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Sequence, Tuple


BOOK_TITLE = "Symbiotic Minds"
WAVE = 44
BOOK_TYPE = "Foundation-DF"
STYLE = "Sachbuch-Diskurs + Kaestner-klar"
DEFAULT_MODE = "mock"

OUTLINE: Tuple[Tuple[int, str], ...] = (
    (1, "Die symbiotische Beziehung"),
    (2, "Mensch als Phronesis-Traeger"),
    (3, "AI als Pattern-Recognizer"),
    (4, "Trinity-Pattern"),
    (5, "Hamilton-Optimierung"),
    (6, "Working Memory"),
    (7, "Bounded Veto"),
    (8, "Cognitive Load Distribution"),
    (9, "Failure Modes"),
    (10, "Wisdom Cultivation"),
    (11, "Family-Office als Test-Case"),
    (12, "Hotel-Operations als Test-Case"),
    (13, "Praxis-Patterns"),
    (14, "Ausblick"),
)

KB_REFERENCES: Tuple[str, ...] = (
    "[KB: knowledge-diff-mac-architekt-2-martin-direktiven-2026-07-24.md]",
    "[KB: EIGENFEHLER-2026-05-13-CONSERVATIVE-DEFAULT-BIAS-OPTION-C.md]",
    "[KB: knowledge-diff-mac-2026-05-14-SESSION-B-PHASE-B-1-COMPLETE.md]",
)


@dataclass(frozen=True)
class ChapterDraft:
    number: int
    title: str
    mode: str
    content: str
    cues: Tuple[str, ...]


def can_use_real_llm(env: Optional[Mapping[str, str]] = None) -> bool:
    source = os.environ if env is None else env
    return (
        source.get("DF_BOOK_REAL_ENABLED", "").lower() == "true"
        and bool(source.get("PHRONESIS_TICKET", "").strip())
    )


def resolve_generation_mode(
    requested_mode: str = "auto",
    env: Optional[Mapping[str, str]] = None,
) -> str:
    mode = requested_mode.strip().lower()
    if mode not in {"auto", "mock", "real"}:
        raise ValueError(f"unsupported mode: {requested_mode}")
    if mode == "mock":
        return "mock"
    if mode == "real":
        if not can_use_real_llm(env):
            raise PermissionError(
                "Real-LLM-call forbidden without DF_BOOK_REAL_ENABLED=true and PHRONESIS_TICKET."
            )
        return "real-ready"
    return "real-ready" if can_use_real_llm(env) else "mock"


def enforce_style(text: str) -> str:
    cleaned = re.sub(r"[ \t]+", " ", text.strip())
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]
    if not sentences:
        return ""
    compact = " ".join(sentences)
    words = compact.split()
    lines: List[str] = []
    current: List[str] = []
    current_len = 0
    for word in words:
        add_len = len(word) + (1 if current else 0)
        if current and current_len + add_len > 72:
            lines.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += add_len
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def _chapter_cues(number: int, title: str) -> Tuple[str, ...]:
    base = (
        "These: Mensch + AI > Mensch allein > AI allein.",
        "Rollen klar trennen: Phronesis fuer Menschen, Mustererkennung fuer AI.",
        "Trinity-Denken gegen Conservative-Default-Bias absichern.",
    )
    extras = {
        4: ("Synthese aus Conservative, Aggressive und Contrarian sichtbar machen.",),
        5: ("Hamilton-Formel H = u + lambda*f als Entscheidungsgeruest erklaeren.",),
        7: ("Veto-Rechte begrenzen und an Schaden koppeln.",),
        9: ("Failure-Modes konkret, nicht abstrakt, benennen.",),
        13: ("Handlungsnahe Patterns statt wolkiger Prinzipien liefern.",),
    }
    return base + extras.get(number, ()) + (f"Kapitelanker: {title}.",)


def generate_chapter_stub(number: int, title: str) -> ChapterDraft:
    cues = _chapter_cues(number, title)
    raw = f"""
    Kapitel {number}: {title}.

    Dieses Kapitel erklaert die Kernfrage in klarer Sprache.
    Es trennt menschliche Urteilskraft von maschinischer Mustererkennung.
    Daraus entsteht keine Konkurrenz-Erzaehlung, sondern ein Arbeitsbuendnis.

    Der Leser soll drei Dinge mitnehmen.
    Erstens: Symbiose braucht Rollen, keine Romantik.
    Zweitens: Die AI skaliert Suchraum, Tempo und Varianten.
    Drittens: Der Mensch traegt Richtung, Haftung und Sinn.

    Diskurslinie:
    - Problem sauber benennen.
    - Trinity-Spannung offenlegen.
    - Praktische Regel fuer Alltag und Organisation ableiten.

    Leitplanken:
    {cues[0]}
    {cues[1]}
    {cues[2]}
    """
    return ChapterDraft(
        number=number,
        title=title,
        mode="mock",
        content=enforce_style(raw),
        cues=cues,
    )


def build_book_skeleton(
    requested_mode: str = "auto",
    env: Optional[Mapping[str, str]] = None,
    outline: Sequence[Tuple[int, str]] = OUTLINE,
) -> Dict[str, object]:
    mode = resolve_generation_mode(requested_mode, env)
    chapters = [generate_chapter_stub(number, title) for number, title in outline]

    if mode == "real-ready":
        mode_note = (
            "Real-LLM waere erlaubt, wird in diesem Modul aber absichtlich nicht ausgefuehrt. "
            "Mock-Stubs bleiben aktiv."
        )
        effective_mode = "mock"
    else:
        mode_note = "Mock-Default aktiv. Keine Real-LLM-Calls."
        effective_mode = "mock"

    return {
        "book_title": BOOK_TITLE,
        "wave": WAVE,
        "type": BOOK_TYPE,
        "style": STYLE,
        "effective_mode": effective_mode,
        "mode_note": mode_note,
        "strict_conditions": {
            "real_llm_guard": "DF_BOOK_REAL_ENABLED=true and PHRONESIS_TICKET required",
            "auto_push": False,
            "real_money_workflow": False,
        },
        "kb_references": KB_REFERENCES,
        "chapters": chapters,
    }
# [CRUX-MK]
