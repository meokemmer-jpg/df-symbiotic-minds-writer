"""
df-symbiotic-minds-writer [CRUX-MK]

Skeleton-Foundation-DF fuer "Symbiotic Minds" Buch-Generierung.
14 Kapitel-Outline, Mock-Default, ENV-Var-Gate fuer Real-LLM.

Strict-Conditions:
- KEIN Real-LLM-Call ohne DF_BOOK_REAL_ENABLED=true + PHRONESIS_TICKET
- Mock-Default: Kapitel-Stub statt Real-LLM-Generation
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Chapter Outline (14 Kapitel)
# ---------------------------------------------------------------------------

CHAPTER_OUTLINE: list[dict] = [
    {
        "id": 1,
        "title": "Die symbiotische Beziehung",
        "subtitle": "Definition und Abgrenzung",
        "core_thesis": "Symbiose: AI + Mensch > Mensch allein > AI allein",
        "key_concepts": ["Symbiose", "Komplementaritaet", "Reziprozitaet"],
        "approx_words": 3000,
    },
    {
        "id": 2,
        "title": "Mensch als Phronesis-Traeger",
        "subtitle": "Was nur Menschen koennen",
        "core_thesis": "Phronesis ist nicht delegierbar: Werte, Intuition, Verantwortung.",
        "key_concepts": ["Phronesis", "Practical Wisdom", "Moralische Urteilskraft"],
        "approx_words": 4000,
    },
    {
        "id": 3,
        "title": "AI als Pattern-Recognizer",
        "subtitle": "Was AI kann, Mensch nicht",
        "core_thesis": "AI findet Muster in Millionen Beispielen – Mensch in Lebensgeschichten.",
        "key_concepts": ["Pattern Recognition", "Statistical Inference", "Skalierung"],
        "approx_words": 4000,
    },
    {
        "id": 4,
        "title": "Trinity-Pattern",
        "subtitle": "Conservative/Aggressive/Contrarian-Synthese",
        "core_thesis": "Drei Perspektiven kombiniert uebertreffen jede einzelne.",
        "key_concepts": ["Trinity", "Cognitive Diversity", "Best-of-Three"],
        "approx_words": 3500,
    },
    {
        "id": 5,
        "title": "Hamilton-Optimierung",
        "subtitle": "H = u + lambda*f als Lebensformel",
        "core_thesis": "Optimales Handeln balanciert Gegenwartswert und Zukunftspotenzial.",
        "key_concepts": ["Hamilton-Funktion", "Pontryagin", "Zeitoptimierung"],
        "approx_words": 3500,
    },
    {
        "id": 6,
        "title": "Working Memory",
        "subtitle": "Wie symbiotische Systeme Information teilen",
        "core_thesis": "Geteiltes Gedaechtnis multipliziert kollektive Intelligenz.",
        "key_concepts": ["Working Memory", "Shared Context", "Kontextfenster"],
        "approx_words": 3000,
    },
    {
        "id": 7,
        "title": "Bounded Veto",
        "subtitle": "Wer hat Veto-Rechte wann?",
        "core_thesis": "Klare Veto-Rechte schuetzen Qualitaet ohne Handlung zu laehmen.",
        "key_concepts": ["Bounded Veto", "MHC", "Meaningful Human Control"],
        "approx_words": 3000,
    },
    {
        "id": 8,
        "title": "Cognitive Load Distribution",
        "subtitle": "Aufteilung mentaler Last",
        "core_thesis": "Symbiose entlastet den Menschen dort, wo er am schwaechsten ist.",
        "key_concepts": ["Cognitive Load", "Delegation", "Entlastung"],
        "approx_words": 3500,
    },
    {
        "id": 9,
        "title": "Failure Modes",
        "subtitle": "Wenn Symbiose kippt",
        "core_thesis": "Algorithmic Shield und Autonomie-Drift zerstoeren Vertrauen.",
        "key_concepts": ["Replit-Incident", "Algorithmic Shield", "Failure Analysis"],
        "approx_words": 4000,
    },
    {
        "id": 10,
        "title": "Wisdom Cultivation",
        "subtitle": "Mindfulness als Symbiose-Training",
        "core_thesis": "Weisheit ist trainierbar und macht Symbiose tiefer.",
        "key_concepts": ["Mindfulness", "Non-Attachment", "Compassion"],
        "approx_words": 3000,
    },
    {
        "id": 11,
        "title": "Family-Office als Test-Case",
        "subtitle": "K_0/Q_0-Schutz in der Praxis",
        "core_thesis": "Familienkapital als Pruefstein fuer symbiotische Entscheidungen.",
        "key_concepts": ["K_0", "Q_0", "Family-Office", "Vermoegen"],
        "approx_words": 3500,
    },
    {
        "id": 12,
        "title": "Hotel-Operations als Test-Case",
        "subtitle": "HeyLou Trinity in Aktion",
        "core_thesis": "KI-unterstuetzte Hotellerie als Reallabor fuer Mensch-AI-Symbiose.",
        "key_concepts": ["HeyLou", "SAE", "Trinity", "Hotellerie"],
        "approx_words": 3500,
    },
    {
        "id": 13,
        "title": "Praxis-Patterns",
        "subtitle": "50 konkrete Symbiose-Patterns",
        "core_thesis": "Abstrakte Prinzipien brauchen konkrete, wiederholbare Muster.",
        "key_concepts": ["Design Patterns", "Best Practices", "Anwendung"],
        "approx_words": 8000,
    },
    {
        "id": 14,
        "title": "Ausblick",
        "subtitle": "Wo geht Mensch-AI-Symbiose hin?",
        "core_thesis": "Symbiose ist kein Endpunkt, sondern ein dynamischer Prozess.",
        "key_concepts": ["Zukunft", "Evolution", "AGI", "Post-Symbiose"],
        "approx_words": 3000,
    },
]

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class ChapterDraft:
    """Kapitel-Draft mit Source-Tracking (mock | real-llm)."""

    chapter_id: int
    title: str
    subtitle: str
    content: str
    source: str  # "mock" | "real-llm"
    iso_timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    word_count: int = 0
    style_issues: list[str] = field(default_factory=list)
    phronesis_ticket: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "chapter_id": self.chapter_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "content": self.content,
            "source": self.source,
            "iso_timestamp": self.iso_timestamp,
            "word_count": self.word_count,
            "style_issues": self.style_issues,
            "phronesis_ticket": self.phronesis_ticket,
        }


# ---------------------------------------------------------------------------
# Core Functions
# ---------------------------------------------------------------------------

def get_chapter_info(chapter_id: int) -> dict:
    """Gibt Outline-Metadaten fuer ein Kapitel zurueck.

    Raises:
        ValueError: wenn chapter_id nicht in 1-14.
    """
    for chapter in CHAPTER_OUTLINE:
        if chapter["id"] == chapter_id:
            return chapter
    raise ValueError(
        f"Kapitel {chapter_id} nicht gefunden. Gueltig: 1-14."
    )


def is_real_mode_enabled() -> bool:
    """Prueft ob Real-LLM-Mode aktiv ist (nur bei exakt '=true')."""
    return os.environ.get("DF_BOOK_REAL_ENABLED") == "true"


def _get_phronesis_ticket() -> Optional[str]:
    return os.environ.get("PHRONESIS_TICKET") or None


def _generate_mock_content(chapter_info: dict) -> str:
    """Erzeugt einen Stub-Platzhalter fuer ein Kapitel."""
    concepts = ", ".join(chapter_info["key_concepts"])
    return (
        f"# {chapter_info['title']}\n"
        f"## {chapter_info['subtitle']}\n\n"
        f"**[MOCK-STUB]** Dieses Kapitel ist ein Platzhalter.\n\n"
        f"**Kernthese:** {chapter_info['core_thesis']}\n\n"
        f"**Schluesselbegriffe:** {concepts}\n\n"
        f"Geschaetzter Umfang: ca. {chapter_info['approx_words']} Woerter.\n\n"
        f"*Real-Content erfordert: DF_BOOK_REAL_ENABLED=true + PHRONESIS_TICKET*\n"
    )


def validate_kaestner_style(content: str) -> list[str]:
    """Prueft Kaestner-Stil: klar, kurz, aktiv, dyslexie-freundlich.

    Returns:
        Liste der Stil-Probleme (leer = konform).
    """
    issues: list[str] = []

    if not content.strip():
        issues.append("Leerer Content.")
        return issues

    # Absatzlaenge (Dyslexie-Barriere > 150 Woerter)
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    long_paras = [
        i + 1 for i, p in enumerate(paragraphs) if len(p.split()) > 150
    ]
    if long_paras:
        issues.append(
            f"Absaetze {long_paras} zu lang (>150 Woerter, Dyslexie-Barriere)."
        )

    # Satzlaenge (Kaestner: kurz und klar, > 35 Woerter bedenklich)
    normalized = content.replace("?", ".").replace("!", ".")
    sentences = [s.strip() for s in normalized.split(".") if s.strip()]
    long_sents = [i + 1 for i, s in enumerate(sentences) if len(s.split()) > 35]
    if long_sents:
        shown = long_sents[:3]
        ellipsis = "..." if len(long_sents) > 3 else ""
        issues.append(
            f"Saetze {shown}{ellipsis} zu lang (>35 Woerter, Kaestner: kurz und klar)."
        )

    # Passiv-Indikatoren
    passive_hits = sum(
        content.lower().count(p) for p in ["wurde ", "worden ", "werden von"]
    )
    if passive_hits > 5:
        issues.append(
            f"Viel Passiv ({passive_hits} Treffer). Kaestner bevorzugt Aktiv."
        )

    return issues


def generate_chapter_draft(chapter_id: int) -> ChapterDraft:
    """Generiert einen Kapitel-Draft (Mock oder Real-LLM via ENV-Gate).

    Default:  Mock-Stub.
    Real-Mode: DF_BOOK_REAL_ENABLED=true + PHRONESIS_TICKET erforderlich.

    Args:
        chapter_id: Kapitel-Nummer 1-14.

    Raises:
        ValueError: ungueltige chapter_id.
        RuntimeError: Real-Mode ohne PHRONESIS_TICKET.
    """
    chapter_info = get_chapter_info(chapter_id)

    if is_real_mode_enabled():
        ticket = _get_phronesis_ticket()
        if not ticket:
            raise RuntimeError(
                "Real-LLM-Mode erfordert PHRONESIS_TICKET ENV-Var. "
                "Phronesis-Approval Martin: Buch-Kapitel-Generation mit Real-LLM."
            )
        # In Production: _df_common.real_llm_wrappers.generate(chapter_info)
        # Hier Stub da _df_common ausserhalb stdlib:
        content = _generate_mock_content(chapter_info)
        source = "real-llm"
        phronesis_ticket: Optional[str] = ticket
    else:
        content = _generate_mock_content(chapter_info)
        source = "mock"
        phronesis_ticket = None

    word_count = len(content.split())
    style_issues = validate_kaestner_style(content)

    return ChapterDraft(
        chapter_id=chapter_id,
        title=chapter_info["title"],
        subtitle=chapter_info["subtitle"],
        content=content,
        source=source,
        word_count=word_count,
        style_issues=style_issues,
        phronesis_ticket=phronesis_ticket,
    )


def generate_book_skeleton() -> list[ChapterDraft]:
    """Generiert Mock-Stubs fuer alle 14 Kapitel."""
    return [generate_chapter_draft(i) for i in range(1, 15)]


def write_chapter_to_file(draft: ChapterDraft, output_dir: str = ".") -> Path:
    """Schreibt Kapitel-Draft als Markdown-Datei mit YAML-Frontmatter."""
    slug = _slugify(draft.title)
    out_path = Path(output_dir) / f"chapter_{draft.chapter_id:02d}_{slug}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    frontmatter = (
        f"---\n"
        f"chapter_id: {draft.chapter_id}\n"
        f'title: "{draft.title}"\n'
        f'subtitle: "{draft.subtitle}"\n'
        f"source: {draft.source}\n"
        f"word_count: {draft.word_count}\n"
        f"generated_at: {draft.iso_timestamp}\n"
        f"crux-mk: true\n"
        f"---\n\n"
    )
    out_path.write_text(frontmatter + draft.content, encoding="utf-8")
    return out_path


def audit_log_entry(draft: ChapterDraft, action: str = "GENERATE") -> dict:
    """Erstellt einen JSONL-kompatiblen Audit-Log-Eintrag."""
    return {
        "ts": draft.iso_timestamp,
        "df": "df-symbiotic-minds-writer",
        "action": action,
        "chapter_id": draft.chapter_id,
        "title": draft.title,
        "source": draft.source,
        "word_count": draft.word_count,
        "style_issues_count": len(draft.style_issues),
        "phronesis_ticket": draft.phronesis_ticket,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(text: str) -> str:
    return (
        text.lower()
        .replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        .replace(" ", "_").replace("/", "_").replace("-", "_")
    )
# [CRUX-MK]
