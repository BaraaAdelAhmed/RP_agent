#!/usr/bin/env python3
"""Claude Code hooks for the research-paper skill.

  UserPromptSubmit: saves the user's latest message so `rp.py approve` can check that an approval
                    quote really comes from the user.
  PreToolUse (Write|Edit|MultiEdit): blocks writing a paper's .tex files before the user has approved
                    novelty and structure, and blocks hand-editing references.bib.
Exit code 2 blocks the tool call and shows stderr to Claude.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAPERS = ROOT / "papers"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    event = data.get("hook_event_name")

    if event == "UserPromptSubmit":
        (ROOT / ".claude").mkdir(exist_ok=True)
        (ROOT / ".claude" / "last_user_prompt.txt").write_text(data.get("prompt", ""))
        return

    if event != "PreToolUse":
        return
    path = (data.get("tool_input") or {}).get("file_path")
    if not path:
        return
    p = Path(path)
    if not p.is_absolute():
        p = Path(data.get("cwd") or ROOT) / p
    p = p.resolve()
    try:
        rel = p.relative_to(PAPERS.resolve())
    except ValueError:
        return  # not inside papers/
    if len(rel.parts) < 2:
        return
    project = PAPERS / rel.parts[0]

    if p.name == "references.bib":
        print("references.bib is managed only with `python3 scripts/rp.py addref/rmref`, so that every entry is "
              "real BibTeX fetched from doi.org, arXiv or OpenAlex.", file=sys.stderr)
        sys.exit(2)

    if p.suffix == ".tex":
        state_file = project / ".session" / "state.json"
        state = json.loads(state_file.read_text()) if state_file.exists() else {}
        if not (state.get("novelty_approved") and state.get("structure_approved")):
            print("The paper's LaTeX is locked until the user approves (1) the novelty assessment and (2) the titles "
                  f"and structure. Current: novelty={state.get('novelty_approved', False)}, "
                  f"structure={state.get('structure_approved', False)}. Ask the user, then record their words with "
                  "`python3 scripts/rp.py approve <project> <gate> --quote \"...\"`.", file=sys.stderr)
            sys.exit(2)


if __name__ == "__main__":
    main()
