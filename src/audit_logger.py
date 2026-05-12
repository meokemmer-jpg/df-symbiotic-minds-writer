"""Audit-Logger mit HMAC-SHA256-Hash-Chain. [CRUX-MK]"""

import hmac
import hashlib
import json
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AuditEntry:
    """Single audit log entry."""
    iso_timestamp: str
    event_type: str
    payload: Dict
    sequence_no: int
    prev_hash: str
    chain_hash: str = ""


class AuditLogger:
    """HMAC-SHA256 Hash-Chain Audit-Logger (Concurrent-Safe via Lock)."""

    def __init__(self, log_path: Path, hmac_key: Optional[bytes] = None):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._hmac_key = hmac_key or os.urandom(32)
        self._lock = threading.Lock()
        self._sequence_no = 0
        self._last_hash = "GENESIS"

        # Recover state if log exists
        if self.log_path.exists():
            self._recover_state()

    def _recover_state(self):
        """Recover sequence_no + last_hash from existing log."""
        with self.log_path.open("r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    self._sequence_no = entry["sequence_no"] + 1
                    self._last_hash = entry["chain_hash"]
                except (json.JSONDecodeError, KeyError):
                    continue

    def _compute_chain_hash(self, prev_hash: str, payload_json: str) -> str:
        """HMAC-SHA256 over (prev_hash || payload_json)."""
        msg = (prev_hash + payload_json).encode("utf-8")
        return hmac.new(self._hmac_key, msg, hashlib.sha256).hexdigest()

    def append(self, event_type: str, payload: Dict) -> AuditEntry:
        """Append audit entry. Concurrent-safe via lock."""
        with self._lock:
            payload_json = json.dumps(payload, sort_keys=True)
            chain_hash = self._compute_chain_hash(self._last_hash, payload_json)

            entry = AuditEntry(
                iso_timestamp=_iso_now(),
                event_type=event_type,
                payload=payload,
                sequence_no=self._sequence_no,
                prev_hash=self._last_hash,
                chain_hash=chain_hash,
            )

            with self.log_path.open("a") as f:
                f.write(json.dumps({
                    "iso_timestamp": entry.iso_timestamp,
                    "event_type": entry.event_type,
                    "payload": entry.payload,
                    "sequence_no": entry.sequence_no,
                    "prev_hash": entry.prev_hash,
                    "chain_hash": entry.chain_hash,
                }) + "\n")

            self._sequence_no += 1
            self._last_hash = chain_hash

            return entry

    def verify_chain(self) -> bool:
        """Verify hash chain integrity end-to-end."""
        if not self.log_path.exists():
            return True

        prev_hash = "GENESIS"
        with self.log_path.open("r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    payload_json = json.dumps(entry["payload"], sort_keys=True)
                    expected = self._compute_chain_hash(prev_hash, payload_json)
                    if expected != entry["chain_hash"]:
                        return False
                    if entry["prev_hash"] != prev_hash:
                        return False
                    prev_hash = entry["chain_hash"]
                except (json.JSONDecodeError, KeyError):
                    return False
        return True
