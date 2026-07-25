"""Core mission module for df-symbiotic-minds-writer."""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import Callable, Mapping


BOOK_TITLE = "Symbiotic Minds"
BOOK_SUBTITLE = "Mensch-AI-Symbiose"
DEFAULT_WAVE = 44
DEFAULT_MODE = "mock"
REAL_ENV_FLAG = "DF_BOOK_REAL_ENABLED"
REAL_TICKET_FLAG = "PHRONESIS_TICKET"
TRINITY_ROLES = ("conservative", "aggressive", "contrarian")
MAX_SENTENCE_WORDS = 22

OUTLINE: tuple[tuple[int, str], ...] = (
    (1, "Die symbiotische Beziehung - Definition + Abgrenzung"),
    (2, "Mensch als Phronesis-Traeger - Was nur Menschen koennen"),
    (3, "AI als Pattern-Recognizer - Was AI kann, Mensch nicht"),
    (4, "Trinity-Pattern - Conservative/Aggressive/Contrarian-Synthese"),
    (5, "Hamilton-Optimierung - H = u + lambda*f als Lebensformel"),
    (6, "Working Memory - Wie symbiotische Systeme Information teilen"),
    (7, "Bounded Veto - Wer hat Veto-Rechte wann?"),
    (8, "Cognitive Load Distribution - Aufteilung mentaler Last"),
    (9, "Failure Modes - Wenn Symbiose kippt"),
    (10, "Wisdom Cultivation - Mindfulness als Symbiose-Training"),
    (11, "Family-Office als Test-Case - K_0/Q_0-Schutz"),
    (12, "Hotel-Operations als Test-Case - HeyLou Trinity"),
    (13, "Praxis-Patterns - 50 konkrete Symbiose-Patterns"),
    (14, "Ausblick - Wo geht Mensch-AI-Symbiose hin?"),
)


@dataclass(frozen=True)
class ChapterSpec:
    number: int
    title: str


@dataclass(frozen=True)
class ChapterDraft:
    number: int
    title: str
    mode: str
    body: str
    trinity_roles: tuple[str, ...]
    style_ok: bool
    real_generation_allowed: bool


def get_outline() -> list[ChapterSpec]:
    return [ChapterSpec(number, title) for number, title in OUTLINE]


def mission_manifest() -> dict[str, object]:
    return {
        "book_title": BOOK_TITLE,
        "subtitle": BOOK_SUBTITLE,
        "wave": DEFAULT_WAVE,
        "default_mode": DEFAULT_MODE,
        "strict_conditions": {
            "real_llm_requires_env": REAL_ENV_FLAG,
            "real_llm_requires_ticket": REAL_TICKET_FLAG,
            "auto_push_allowed": False,
            "cashflow_allowed": False,
        },
        "outline": get_outline(),
    }


def real_generation_enabled(env: Mapping[str, str] | None = None) -> bool:
    current_env = os.environ if env is None else env
    return (
        current_env.get(REAL_ENV_FLAG) == "true"
        and bool(current_env.get(REAL_TICKET_FLAG, "").strip())
    )


def require_real_generation(env: Mapping[str, str] | None = None) -> None:
    if not real_generation_enabled(env):
        raise PermissionError(
            "Real-LLM-Calls sind gesperrt. Setze DF_BOOK_REAL_ENABLED=true "
            "und ein nicht-leeres PHRONESIS_TICKET."
        )


def normalize_style(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    normalized = re.sub(r"[ \t]+", " ", normalized)
    paragraphs = [line.strip() for line in normalized.split("\n") if line.strip()]
    return "\n\n".join(paragraphs)


def sentence_word_counts(text: str) -> list[int]:
    counts: list[int] = []
    for fragment in re.split(r"[.!?]+", text):
        words = re.findall(r"\b[\w'-]+\b", fragment)
        if words:
            counts.append(len(words))
    return counts


def is_kaestner_clear(text: str, max_sentence_words: int = MAX_SENTENCE_WORDS) -> bool:
    normalized = normalize_style(text)
    if not normalized or "\n\n" not in normalized:
        return False
    if len(normalized.split()) < 20:
        return False
    return all(count <= max_sentence_words for count in sentence_word_counts(normalized))


def validate_trinity_balance(text: str) -> bool:
    lowered = text.lower()
    return all(role in lowered for role in TRINITY_ROLES)


def _chapter_stub_body(number: int, title: str) -> str:
    paragraphs = (
        f"Kapitel {number} traegt den Titel '{title}'. Es trennt Mensch und KI klar, damit Kooperation nicht zur Ersatzphantasie wird.",
        "Der Mensch bringt Phronesis. Er setzt Richtung, traegt Folgen und urteilt dort, wo Daten allein keine Verantwortung tragen.",
        "Die KI bringt Pattern-Recognition. Sie vergleicht Varianten schnell und zeigt Strukturen, die ein einzelner Kopf leicht verpasst.",
        "Die conservative Stimme schuetzt Substanz. Die aggressive Stimme sucht Hebel. Die contrarian Stimme prueft blinde Flecken.",
        "So gilt die Kernthese dieses Buchs: AI + Mensch > Mensch allein > AI allein. Symbiose braucht Rollen, Grenzen und geteiltes Working Memory.",
    )
    return normalize_style("\n\n".join(paragraphs))


def generate_chapter_stub(number: int, title: str) -> ChapterDraft:
    body = _chapter_stub_body(number, title)
    return ChapterDraft(
        number=number,
        title=title,
        mode=DEFAULT_MODE,
        body=body,
        trinity_roles=TRINITY_ROLES,
        style_ok=is_kaestner_clear(body) and validate_trinity_balance(body),
        real_generation_allowed=False,
    )


def request_chapter_draft(
    number: int,
    env: Mapping[str, str] | None = None,
    mode: str = DEFAULT_MODE,
    llm_callable: Callable[[int, str], str] | None = None,
) -> ChapterDraft:
    chapter_titles = dict(OUTLINE)
    if number not in chapter_titles:
        raise ValueError(f"Unbekannte Kapitelnummer: {number}")

    title = chapter_titles[number]
    if mode == DEFAULT_MODE:
        return generate_chapter_stub(number, title)
    if mode != "real":
        raise ValueError("mode muss 'mock' oder 'real' sein")

    require_real_generation(env)
    if llm_callable is None:
        raise RuntimeError("Real-Mode ist freigeschaltet, aber kein llm_callable wurde uebergeben.")

    body = normalize_style(llm_callable(number, title))
    return ChapterDraft(
        number=number,
        title=title,
        mode="real",
        body=body,
        trinity_roles=TRINITY_ROLES,
        style_ok=is_kaestner_clear(body) and validate_trinity_balance(body),
        real_generation_allowed=True,
    )


def build_book_skeleton(
    env: Mapping[str, str] | None = None,
    mode: str = DEFAULT_MODE,
    llm_callable: Callable[[int, str], str] | None = None,
) -> dict[str, object]:
    manifest = mission_manifest()
    chapters = [
        request_chapter_draft(spec.number, env=env, mode=mode, llm_callable=llm_callable)
        for spec in manifest["outline"]
    ]
    return {
        "book_title": manifest["book_title"],
        "subtitle": manifest["subtitle"],
        "wave": manifest["wave"],
        "mode": mode,
        "chapters": chapters,
        "strict_conditions": manifest["strict_conditions"],
    }
# [CRUX-MK]
