
# K12+K13+K16 Trinity-CONTRARIAN 2026-05-17 (Cross-LLM-validated)
def k12_provenance(payload: bytes, key: bytes = b"df-trinity-contrarian-v1") -> dict:
    import hashlib, hmac
    return {
        "payload_hash": hashlib.sha256(payload).hexdigest(),
        "hmac_sha256": hmac.new(key, payload, hashlib.sha256).hexdigest(),
    }

def k13_anchor(payload_hash: str) -> dict:
    from datetime import datetime, timezone
    return {
        "anchor_type": "rfc3161-mock",
        "iso_ts": datetime.now(timezone.utc).isoformat(),
        "payload_hash": payload_hash,
    }

def k16_lock_or_exit(df_name: str):
    import fcntl, os, sys
    lock_path = f"/tmp/df-trinity-{df_name}.lock"
    fd = os.open(lock_path, os.O_CREAT | os.O_WRONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd
    except BlockingIOError:
        sys.exit(3)

"""Tests fuer adapter_orchestrator. [CRUX-MK]"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.adapter_orchestrator import AdapterOrchestrator, OrchestratorRunResult


def test_orchestrator_init_default():
    with tempfile.TemporaryDirectory() as tmp:
        orch = AdapterOrchestrator(audit_log_dir=Path(tmp))
        assert orch.book_title == "Symbiotic Minds"
        assert orch.quota_max == 5


def test_run_default_quota_5_chapters():
    """Default-run generates min(quota_max, len(numbers)) chapters."""
    with tempfile.TemporaryDirectory() as tmp:
        orch = AdapterOrchestrator(audit_log_dir=Path(tmp), quota_max=3)
        result = orch.run()
        assert isinstance(result, OrchestratorRunResult)
        assert result.chapters_generated == 3
        assert result.source_mode == "mock"


def test_run_with_specific_chapter_numbers():
    """Specific chapter numbers respected up to quota."""
    with tempfile.TemporaryDirectory() as tmp:
        orch = AdapterOrchestrator(audit_log_dir=Path(tmp), quota_max=10)
        result = orch.run(chapter_numbers=[1, 3, 5])
        assert result.chapters_generated == 3
