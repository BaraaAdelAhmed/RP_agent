# RP Agent

This repository helps an academic author turn a research idea into a structured LaTeX paper.

- When the user wants to start, continue or revise a paper (or shares an idea, a PDF or an image of one), use the
  `research-paper` skill (`.claude/skills/research-paper/SKILL.md`) and follow its stages and gates.
- When the user wants a first draft, a polish, or a language/consistency revision of an existing paper, use the
  `1st-draft-paper` skill (`.claude/skills/1st-draft-paper/SKILL.md`).
- When the user wants a second draft or a referee-level revision, use the `2nd-draft-paper` skill
  (`.claude/skills/2nd-draft-paper/SKILL.md`).
- Papers live in `papers/<slug>/`. When resuming, run `python3 scripts/rp.py status <slug>` first.
- `app.py` + `rp_agent/agent.py` are an alternative standalone web app that needs an Anthropic API key; the skill
  doesn't use them (it reuses only `rp_agent/literature.py` and `rp_agent/project.py`).
