#!/bin/bash
# K16 Concurrent-Spawn-Mutex Wrapper [CRUX-MK]

set -e

LOCK_DIR="/tmp/df-symbiotic-minds-writer.lock"
LOCK_AGE_LIMIT_S=21600  # 6h

# Stale-Lock-Auto-Claim
if [ -d "$LOCK_DIR" ]; then
  if [ "$(uname)" = "Darwin" ]; then
    LOCK_MTIME=$(stat -f %m "$LOCK_DIR" 2>/dev/null || echo 0)
  else
    LOCK_MTIME=$(stat -c %Y "$LOCK_DIR" 2>/dev/null || echo 0)
  fi
  LOCK_AGE_S=$(( $(date +%s) - LOCK_MTIME ))
  if [ "$LOCK_AGE_S" -gt "$LOCK_AGE_LIMIT_S" ]; then
    echo "Stale lock (age ${LOCK_AGE_S}s > ${LOCK_AGE_LIMIT_S}s) - removing"
    rm -rf "$LOCK_DIR"
  fi
fi

# Atomic mkdir-Lock
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Lock exists - another instance is running. Exiting (K16-VETO)."
  exit 3
fi

echo "$$" > "$LOCK_DIR/pid"
trap 'rm -rf "$LOCK_DIR"' EXIT INT TERM

DF_DIR="/Users/make/Projects/dark-factories/df-symbiotic-minds-writer"
cd "$DF_DIR"

# Run orchestrator
python3 -m src.adapter_orchestrator
EXIT_CODE=$?

echo "df-symbiotic-minds-writer completed with exit code $EXIT_CODE"
exit $EXIT_CODE
