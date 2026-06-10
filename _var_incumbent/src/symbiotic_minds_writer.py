"""
df-symbiotic-minds-writer: Foundation-DF fuer "Symbiotic Minds" Kapitel-Generierung.
Mock-Default: kein Real-LLM-Call ohne ENV DF_BOOK_REAL_ENABLED=true + PHRONESIS_TICKET.
[CRUX-MK]
"""

import os
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Optional

BOOK_TITLE = "Symbiotic Minds"
BOOK_SUBTITLE = "Mensch-AI-Symbiose: Warum beide Seiten klare Rollen brauchen"

CHAPTER_REGISTRY: dict = {
    1:  {"title": "Die symbiotische Beziehung",      "subtitle": "Definition + Abgrenzung",                          "core_thesis": "AI + Mensch > Mensch allein > AI allein",                                    "keywords": ["Symbiose", "Komplementaritaet", "Rollenverteilung"],          "target_words": 4000},
    2:  {"title": "Mensch als Phronesis-Traeger",     "subtitle": "Was nur Menschen koennen",                         "core_thesis": "Praktische Weisheit (Phronesis) ist nicht delegierbar",                      "keywords": ["Phronesis", "Aristoteles", "Werte", "Urteil"],                "target_words": 5000},
    3:  {"title": "AI als Pattern-Recognizer",        "subtitle": "Was AI kann, Mensch nicht",                        "core_thesis": "AI erkennt Muster in Millionen Datenpunkten – kein Mensch kann das",          "keywords": ["Pattern-Recognition", "Skalierung", "Mustererkennung"],       "target_words": 4500},
    4:  {"title": "Trinity-Pattern",                  "subtitle": "Conservative/Aggressive/Contrarian-Synthese",      "core_thesis": "Drei Perspektiven zusammen schlagen jede einzelne",                           "keywords": ["Trinity", "Conservative", "Aggressive", "Contrarian"],        "target_words": 4000},
    5:  {"title": "Hamilton-Optimierung",             "subtitle": "H = u + lambda*f als Lebensformel",                "core_thesis": "Jede Entscheidung hat Gegenwartswert und Zukunftswert",                       "keywords": ["Hamilton", "Pontryagin", "Optimierung", "Zeitwert"],          "target_words": 4500},
    6:  {"title": "Working Memory",                   "subtitle": "Wie symbiotische Systeme Information teilen",      "core_thesis": "Geteiltes Working Memory ist Grundlage effektiver Mensch-AI-Zusammenarbeit", "keywords": ["Working-Memory", "Context-Engineering", "Persistenz"],        "target_words": 4000},
    7:  {"title": "Bounded Veto",                     "subtitle": "Wer hat Veto-Rechte wann?",                        "core_thesis": "Klare Veto-Regeln verhindern AI-Diktat und Human-Blockade",                   "keywords": ["Bounded-Veto", "COSMOS", "MHC", "Meaningful-Human-Control"], "target_words": 4500},
    8:  {"title": "Cognitive Load Distribution",      "subtitle": "Aufteilung mentaler Last",                         "core_thesis": "Symbiotische Systeme verteilen Kognition nach komparativen Vorteilen",        "keywords": ["Cognitive-Load", "Spezialisierung", "Engpass", "TOC"],        "target_words": 4000},
    9:  {"title": "Failure Modes",                    "subtitle": "Wenn Symbiose kippt",                              "core_thesis": "Replit-Incident und Algorithmic Shield sind Symptome zerbrochener Symbiose",  "keywords": ["Failure-Modes", "Replit", "Algorithmic-Shield", "Sycophancy"],"target_words": 5000},
    10: {"title": "Wisdom Cultivation",               "subtitle": "Mindfulness als Symbiose-Training",               "core_thesis": "Wisdom ist trainierbar – und verbessert Mensch-AI-Interaktion messbar",      "keywords": ["Wisdom", "Mindfulness", "Non-Attachment", "Training"],        "target_words": 4000},
    11: {"title": "Family-Office als Test-Case",      "subtitle": "K_0/Q_0-Schutz in der Praxis",                    "core_thesis": "Familienvermoegens-Management braucht Phronesis-Reservate",                   "keywords": ["Family-Office", "K_0", "Q_0", "KPM", "Kapitalschutz"],       "target_words": 4500},
    12: {"title": "Hotel-Operations als Test-Case",   "subtitle": "HeyLou Trinity in der Praxis",                    "core_thesis": "7 AI-first Hotels zeigen: Symbiose skaliert operational",                     "keywords": ["HeyLou", "Hotel-AI", "GSA", "SAE", "Trinity"],               "target_words": 4500},
    13: {"title": "Praxis-Patterns",                  "subtitle": "50 konkrete Symbiose-Patterns",                   "core_thesis": "Symbiose ist erlernbar durch konkrete, wiederholbare Patterns",                "keywords": ["Patterns", "Praxis", "Methodik"],                             "target_words": 8000},
    14: {"title": "Ausblick",                         "subtitle": "Wo geht Mensch-AI-Symbiose hin?",                 "core_thesis": "Symbiose wird tiefer und breiter – Phronesis bleibt menschlich",               "keywords": ["Zukunft", "AGI", "Phronesis", "Langfrist"],                   "target_words": 3000},
}


@dataclass
class StyleCheckResult:
    passed: bool
    warnings: list
    word_count: int
    avg_sentence_length: float


@dataclass
class ChapterDraft:
    chapter_id: int
    title: str
    content: str
    source: str           # "mock" | "real-llm" | "stub"
    word_count: int
    iso_timestamp: str
    phronesis_ticket: Optional[str]
    style_warnings: list
    content_hash: str = field(default="")

    def __post_init__(self) -> None:
        if not self.content_hash:
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]


def get_chapter_spec(chapter_id: int) -> dict:
    """Returns chapter spec. Raises ValueError for unknown IDs."""
    if chapter_id not in CHAPTER_REGISTRY:
        raise ValueError(
            f"Kapitel-ID {chapter_id} unbekannt. Gueltig: 1-{len(CHAPTER_REGISTRY)}"
        )
    return {"chapter_id": chapter_id, **CHAPTER_REGISTRY[chapter_id]}


def check_kaestner_style(text: str) -> StyleCheckResult:
    """
    Kaestner-Stil-Pruefung: klar, kurz, integer.
    Warnt bei langen Saetzen, Floskeln, leerem Text.
    """
    warnings: list = []

    normalized = text.replace("!", ".").replace("?", ".")
    sentences = [s.strip() for s in normalized.split(".") if s.strip()]

    if not sentences:
        return StyleCheckResult(passed=False, warnings=["Kein Text vorhanden"], word_count=0, avg_sentence_length=0.0)

    words = text.split()
    word_count = len(words)

    lengths = [len(s.split()) for s in sentences]
    avg_len = sum(lengths) / len(lengths)

    if avg_len > 25:
        warnings.append(f"Durchschnittliche Satzlaenge {avg_len:.1f} Worte (Kaestner: max 20)")

    floskeln = ["grundsaetzlich", "sozusagen", "gewissermassen", "irgendwie", "quasi"]
    found = [f for f in floskeln if f in text.lower()]
    if found:
        warnings.append(f"Floskel-Verdacht: {', '.join(found)}")

    if word_count < 100:
        warnings.append(f"Sehr kurz ({word_count} Worte) – Stub-Status")

    return StyleCheckResult(
        passed=len(warnings) == 0,
        warnings=warnings,
        word_count=word_count,
        avg_sentence_length=avg_len,
    )


def _mock_chapter_content(chapter_id: int, spec: dict) -> str:
    """Generiert Mock-Stub-Content ohne Real-LLM-Call."""
    keywords_str = ", ".join(spec.get("keywords", []))
    return (
        f"# Kapitel {chapter_id}: {spec['title']}\n"
        f"## {spec['subtitle']}\n\n"
        f"[MOCK-STUB – kein Real-LLM-Call]\n\n"
        f"Kernthese: {spec['core_thesis']}\n\n"
        f"Schlagwoerter: {keywords_str}\n\n"
        f"Ziel-Wortanzahl: {spec['target_words']}\n\n"
        f"---\n\n"
        f"Dieser Stub ist Platzhalter fuer den Real-LLM-generierten Kapitel-Entwurf.\n"
        f"Aktivierung: ENV DF_BOOK_REAL_ENABLED=true plus PHRONESIS_TICKET setzen.\n\n"
        f"Im Real-Modus entsteht hier ein vollstaendiger Entwurf im Kaestner-Stil:\n"
        f"direkt, praezise, ohne Floskel, mit konkreten Beispielen.\n\n"
        f"[CRUX-MK]\n"
    )


def generate_chapter_draft(
    chapter_id: int,
    backend: Optional[str] = None,
    phronesis_ticket: Optional[str] = None,
) -> ChapterDraft:
    """
    Generiert Kapitel-Draft mit ENV-Var-Gate.

    Mock-Default: ENV DF_BOOK_REAL_ENABLED != 'true' -> source='mock'.
    Real-Modus: DF_BOOK_REAL_ENABLED=true + PHRONESIS_TICKET Pflicht.
    Fehlendes Ticket -> graceful Mock-Fallback (per env-var-gated-real-integration-default.md).

    Args:
        chapter_id:        Kapitel-Nummer 1-14.
        backend:           'mock' (default) | 'real-llm'. None = ENV-Var-Routing.
        phronesis_ticket:  Pflicht bei backend='real-llm'.

    Returns:
        ChapterDraft mit source-Tracking.
    """
    spec = get_chapter_spec(chapter_id)
    now = datetime.now(timezone.utc).isoformat()

    if backend is None:
        backend = "real-llm" if os.environ.get("DF_BOOK_REAL_ENABLED") == "true" else "mock"

    if backend == "real-llm":
        ticket = phronesis_ticket or os.environ.get("PHRONESIS_TICKET")
        if not ticket:
            # Graceful Mock-Fallback: kein Ticket vorhanden
            content = _mock_chapter_content(chapter_id, spec)
            style = check_kaestner_style(content)
            return ChapterDraft(
                chapter_id=chapter_id,
                title=spec["title"],
                content=content,
                source="mock",
                word_count=style.word_count,
                iso_timestamp=now,
                phronesis_ticket=None,
                style_warnings=["PHRONESIS_TICKET fehlt – Mock-Fallback aktiviert"],
            )

        # Real-LLM-Pfad: hier wuerde _df_common.real_llm_wrappers aufgerufen.
        # Im Skeleton: Stub-Content mit Ticket-Nachweis.
        content = _mock_chapter_content(chapter_id, spec)
        style = check_kaestner_style(content)
        return ChapterDraft(
            chapter_id=chapter_id,
            title=spec["title"],
            content=content,
            source="stub",
            word_count=style.word_count,
            iso_timestamp=now,
            phronesis_ticket=ticket,
            style_warnings=style.warnings,
        )

    # Mock-Default
    content = _mock_chapter_content(chapter_id, spec)
    style = check_kaestner_style(content)
    return ChapterDraft(
        chapter_id=chapter_id,
        title=spec["title"],
        content=content,
        source="mock",
        word_count=style.word_count,
        iso_timestamp=now,
        phronesis_ticket=None,
        style_warnings=style.warnings,
    )


def get_book_toc() -> list:
    """Gibt Inhaltsverzeichnis als geordnete Liste zurueck."""
    return [
        {
            "chapter_id": cid,
            "title": spec["title"],
            "subtitle": spec["subtitle"],
            "target_words": spec["target_words"],
        }
        for cid, spec in sorted(CHAPTER_REGISTRY.items())
    ]


def generate_all_stubs(backend: str = "mock") -> list:
    """Generiert Mock-Stubs fuer alle 14 Kapitel."""
    return [generate_chapter_draft(cid, backend=backend) for cid in sorted(CHAPTER_REGISTRY)]
# [CRUX-MK]
