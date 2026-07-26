from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import os
import re
from typing import Iterable, Mapping


BOOK_TITLE = "Symbiotic Minds"
WAVE = 44
DF_TYPE = "Foundation-DF"
DEFAULT_MODE = "mock"
REAL_ENV_FLAG = "DF_BOOK_REAL_ENABLED"
TICKET_ENV_FLAG = "PHRONESIS_TICKET"

CHAPTER_OUTLINE = (
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
)


@dataclass(frozen=True)
class WriterConfig:
    mode: str
    real_llm_enabled: bool
    has_ticket: bool

    @property
    def may_call_real_llm(self) -> bool:
        return self.real_llm_enabled and self.has_ticket


@dataclass(frozen=True)
class ChapterDraft:
    chapter_number: int
    title: str
    slug: str
    mode: str
    content: str
    metadata: dict


def chapter_title(chapter_number: int) -> str:
    if not 1 <= chapter_number <= len(CHAPTER_OUTLINE):
        raise ValueError(f"chapter_number must be between 1 and {len(CHAPTER_OUTLINE)}")
    return CHAPTER_OUTLINE[chapter_number - 1]


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def style_enforce(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean = " ".join(lines)
    clean = re.sub(r"\s+", " ", clean)
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", clean) if part.strip()]
    return "\n".join(sentences)


def load_config(env: Mapping[str, str] | None = None) -> WriterConfig:
    env = os.environ if env is None else env
    enabled = env.get(REAL_ENV_FLAG, "").lower() == "true"
    ticket = bool(env.get(TICKET_ENV_FLAG, "").strip())
    return WriterConfig(
        mode=DEFAULT_MODE if not enabled or not ticket else "real",
        real_llm_enabled=enabled,
        has_ticket=ticket,
    )


def _timestamp_iso(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return now.isoformat()


def build_mock_chapter_stub(chapter_number: int, now: datetime | None = None) -> ChapterDraft:
    title = chapter_title(chapter_number)
    content = style_enforce(
        f"""
        Kapitel {chapter_number}: {title}.

        Kernthese: Mensch und AI werden nur dann besser als jede Seite fuer sich,
        wenn Phronesis beim Menschen bleibt und Pattern-Erkennung sauber an die AI delegiert wird.

        Dieses Mock-Kapitel ist absichtlich ein Stub.
        Es definiert Argument, Test-Case und naechsten Ausbauschritt,
        ohne einen Real-LLM-Call auszufuehren.
        """
    )
    return ChapterDraft(
        chapter_number=chapter_number,
        title=title,
        slug=f"{chapter_number:02d}-{slugify(title)}",
        mode="mock",
        content=content,
        metadata={
            "book_title": BOOK_TITLE,
            "wave": WAVE,
            "type": DF_TYPE,
            "generated_at": _timestamp_iso(now),
            "real_llm_called": False,
        },
    )


def generate_chapter_draft(
    chapter_number: int,
    *,
    prefer_real_llm: bool = False,
    env: Mapping[str, str] | None = None,
    now: datetime | None = None,
) -> ChapterDraft:
    config = load_config(env)

    if not prefer_real_llm:
        return build_mock_chapter_stub(chapter_number, now=now)

    if not config.may_call_real_llm:
        raise PermissionError(
            f"Real LLM call blocked. Require {REAL_ENV_FLAG}=true and non-empty {TICKET_ENV_FLAG}."
        )

    title = chapter_title(chapter_number)
    content = style_enforce(
        f"""
        Kapitel {chapter_number}: {title}.

        Real-LLM-Modus ist freigeschaltet.
        Dieses Modul macht absichtlich keinen externen API-Call.
        Der Hook ist offen fuer _df_common.real_llm_wrappers.
        """
    )
    return ChapterDraft(
        chapter_number=chapter_number,
        title=title,
        slug=f"{chapter_number:02d}-{slugify(title)}",
        mode="real-ready",
        content=content,
        metadata={
            "book_title": BOOK_TITLE,
            "wave": WAVE,
            "type": DF_TYPE,
            "generated_at": _timestamp_iso(now),
            "real_llm_called": False,
            "phronesis_ticket_present": True,
        },
    )


def build_book_skeleton(
    chapters: Iterable[int] | None = None,
    *,
    env: Mapping[str, str] | None = None,
    now: datetime | None = None,
) -> list[dict]:
    chapter_numbers = list(chapters) if chapters is not None else list(range(1, len(CHAPTER_OUTLINE) + 1))
    return [
        asdict(generate_chapter_draft(number, prefer_real_llm=False, env=env, now=now))
        for number in chapter_numbers
    ]


__all__ = [
    "BOOK_TITLE",
    "CHAPTER_OUTLINE",
    "ChapterDraft",
    "WriterConfig",
    "build_book_skeleton",
    "build_mock_chapter_stub",
    "chapter_title",
    "generate_chapter_draft",
    "load_config",
    "slugify",
    "style_enforce",
]
# [CRUX-MK]
