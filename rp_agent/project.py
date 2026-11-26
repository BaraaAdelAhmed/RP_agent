"""A paper project on disk: its files, workflow state and saved conversation."""

from __future__ import annotations

import io
import json
import re
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .config import PAPERS_DIR

STAGES = ["idea", "novelty", "structure", "drafting", "review"]
STAGE_LABELS = {
    "idea": "1. Discuss the idea",
    "novelty": "2. Verify novelty",
    "structure": "3. Titles & structure",
    "drafting": "4. Write LaTeX + .bib",
    "review": "5. Check & hand over",
}

# Files the agent may create with write_file.
WRITABLE_SUFFIXES = {".tex", ".md", ".py", ".csv", ".txt", ".dat", ".sty", ".cls"}


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return slug[:60] or "untitled"


@dataclass
class ProjectState:
    stage: str = "idea"
    novelty_approved: bool = False
    structure_approved: bool = False
    working_title: str = ""
    novelty_verdict: str = ""
    approvals: list[dict] = field(default_factory=list)
    # 1st-draft skill: "" (not started) -> "audit" (edits locked) -> "editing" -> "done"
    draft1_status: str = ""


class Project:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.session_dir = self.root / ".session"
        for d in (self.root, self.session_dir, self.root / "sections", self.root / "figures",
                  self.root / "notes", self.root / "inputs"):
            d.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    # ---------- construction ----------
    @classmethod
    def open(cls, name: str) -> "Project":
        return cls(PAPERS_DIR / slugify(name))

    @staticmethod
    def list_all() -> list[str]:
        if not PAPERS_DIR.exists():
            return []
        return sorted(p.name for p in PAPERS_DIR.iterdir() if p.is_dir() and not p.name.startswith("."))

    @property
    def name(self) -> str:
        return self.root.name

    # ---------- paths ----------
    def resolve(self, rel_path: str) -> Path:
        """Resolve a path inside the project, refusing anything that escapes it."""
        rel_path = rel_path.strip().lstrip("/\\")
        p = (self.root / rel_path).resolve()
        if p != self.root and self.root not in p.parents:
            raise ValueError(f"Path '{rel_path}' is outside the project folder.")
        if ".session" in p.relative_to(self.root).parts:
            raise ValueError("The .session folder is private to the app.")
        return p

    def list_files(self) -> list[str]:
        out = []
        for p in sorted(self.root.rglob("*")):
            if p.is_file() and ".session" not in p.relative_to(self.root).parts:
                out.append(str(p.relative_to(self.root)))
        return out

    # ---------- state ----------
    def _load_state(self) -> ProjectState:
        f = self.session_dir / "state.json"
        if f.exists():
            data = json.loads(f.read_text())
            return ProjectState(**{k: v for k, v in data.items() if k in ProjectState.__dataclass_fields__})
        return ProjectState()

    def save_state(self) -> None:
        (self.session_dir / "state.json").write_text(json.dumps(asdict(self.state), indent=2))

    # ---------- conversation ----------
    def load_messages(self) -> list[dict]:
        f = self.session_dir / "messages.json"
        return json.loads(f.read_text()) if f.exists() else []

    def save_messages(self, messages: list[dict]) -> None:
        tmp = self.session_dir / "messages.json.tmp"
        tmp.write_text(json.dumps(messages))
        tmp.replace(self.session_dir / "messages.json")

    def load_chat(self) -> list[dict]:
        f = self.session_dir / "chat.json"
        return json.loads(f.read_text()) if f.exists() else []

    def save_chat(self, chat: list[dict]) -> None:
        (self.session_dir / "chat.json").write_text(json.dumps(chat, indent=1))

    # ---------- export ----------
    def zip_bytes(self) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for rel in self.list_files():
                zf.write(self.root / rel, arcname=f"{self.name}/{rel}")
        return buf.getvalue()
