import os
from pathlib import Path

MODEL = os.environ.get("RP_AGENT_MODEL", "claude-opus-5-5")
DEFAULT_EFFORT = os.environ.get("RP_AGENT_EFFORT", "high")
MAX_TOKENS = 64000          # streaming, so a large ceiling is safe
MAX_AGENT_STEPS = 60        # model calls per user turn before we stop the loop
PAPERS_DIR = Path(os.environ.get("RP_AGENT_PAPERS_DIR", Path(__file__).resolve().parent.parent / "papers"))

# Server-side tools (run on Anthropic's infrastructure).
WEB_SEARCH_MAX_USES = 25
WEB_FETCH_MAX_USES = 20
