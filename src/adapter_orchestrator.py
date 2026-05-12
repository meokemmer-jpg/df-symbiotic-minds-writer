"""Adapter-Orchestrator: LaunchAgent-Entry-Point. [CRUX-MK]"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .outline_manager import OutlineManager
from .chapter_generator import ChapterGenerator, GeneratedChapter
from .style_guide import StyleGuide
from .audit_logger import AuditLogger


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class OrchestratorRunResult:
    """Aggregated result of one orchestrator run."""
    iso_started: str
    iso_completed: str
    chapters_generated: int
    chapters_failed: int
    source_mode: str  # "mock" | "real-llm"
    audit_log_path: str
    quota_used: int


class AdapterOrchestrator:
    """LaunchAgent-Entry. Orchestriert Chapter-Generation pro Run."""

    def __init__(self,
                 book_title: str = "Symbiotic Minds",
                 audit_log_dir: Optional[Path] = None,
                 quota_max_per_run: int = 5):
        self.book_title = book_title
        self.outline = OutlineManager(book_title=book_title)
        self.style = StyleGuide()
        self.generator = ChapterGenerator(book_title=book_title, style_guide=self.style)
        self.quota_max = quota_max_per_run

        log_dir = Path(audit_log_dir) if audit_log_dir else Path.home() / ".df-state"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.audit = AuditLogger(log_dir / "df-symbiotic-minds-writer-audit.jsonl")

    def _check_stop_flag(self) -> bool:
        """Pre-Run Check: STOP.flag aktiv?"""
        flag_path = Path.home() / ".df-state" / "df-symbiotic-minds-writer.STOP.flag"
        return flag_path.exists()

    def _detect_source_mode(self) -> str:
        """ENV-Var-Gate Check."""
        return "real-llm" if os.environ.get("DF_BOOK_REAL_ENABLED", "false") == "true" else "mock"

    def run(self, chapter_numbers: Optional[List[int]] = None) -> OrchestratorRunResult:
        """Hauptmethode. chapter_numbers=None laedt 1..quota_max sequentiell."""
        iso_start = _iso_now()
        source_mode = self._detect_source_mode()

        # Pre-Action-Verification (K13-PAV)
        self.audit.append("run_start", {
            "iso_timestamp": iso_start,
            "source_mode": source_mode,
            "quota_max": self.quota_max,
            "chapter_request": chapter_numbers,
        })

        if self._check_stop_flag():
            self.audit.append("run_stopped", {"reason": "STOP.flag detected"})
            return OrchestratorRunResult(
                iso_started=iso_start,
                iso_completed=_iso_now(),
                chapters_generated=0,
                chapters_failed=0,
                source_mode=source_mode,
                audit_log_path=str(self.audit.log_path),
                quota_used=0,
            )

        # Determine chapters to generate
        if chapter_numbers is None:
            chapter_numbers = list(range(1, self.quota_max + 1))
        chapter_numbers = chapter_numbers[: self.quota_max]  # cap at quota

        # K11.b Pipeline-Cost-Estimate
        if len(chapter_numbers) > self.quota_max:
            self.audit.append("quota_exceeded", {
                "requested": len(chapter_numbers),
                "quota_max": self.quota_max,
                "action": "warn_and_truncate",
            })

        generated = 0
        failed = 0

        for ch_num in chapter_numbers:
            chapter = self.outline.get_chapter(ch_num)
            if not chapter:
                self.audit.append("chapter_not_found", {"chapter_number": ch_num})
                failed += 1
                continue

            try:
                result = self.generator.generate_chapter(chapter)
                self.audit.append("chapter_generated", {
                    "chapter_number": result.chapter_number,
                    "chapter_title": result.chapter_title,
                    "word_count": result.word_count,
                    "source": result.source,
                    "style_passes": result.style_passes,
                })
                generated += 1
            except (NotImplementedError, RuntimeError) as e:
                self.audit.append("chapter_generation_failed", {
                    "chapter_number": ch_num,
                    "error": str(e),
                })
                failed += 1

        self.audit.append("run_complete", {
            "chapters_generated": generated,
            "chapters_failed": failed,
        })

        return OrchestratorRunResult(
            iso_started=iso_start,
            iso_completed=_iso_now(),
            chapters_generated=generated,
            chapters_failed=failed,
            source_mode=source_mode,
            audit_log_path=str(self.audit.log_path),
            quota_used=generated,
        )


def main():
    """LaunchAgent-Entry-Point."""
    orchestrator = AdapterOrchestrator()
    result = orchestrator.run()
    print(f"DF-symbiotic-minds-writer run complete: "
          f"{result.chapters_generated} generated, {result.chapters_failed} failed, "
          f"mode={result.source_mode}")
    sys.exit(0 if result.chapters_failed == 0 else 1)


if __name__ == "__main__":
    main()
