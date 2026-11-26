# RP Agent

This repository helps an academic author turn a research idea into a structured LaTeX paper.

- When the user wants to start, continue or revise a paper (or shares an idea, a PDF or an image of one), use the
  `research-paper` skill (`.claude/skills/research-paper/SKILL.md`) and follow its stages and gates.
- Papers live in `papers/<slug>/`. When resuming, run `python3 scripts/rp.py status <slug>` first.
- `app.py` + `rp_agent/agent.py` are an alternative standalone web app that needs an Anthropic API key; the skill
  doesn't use them (it reuses only `rp_agent/literature.py` and `rp_agent/project.py`).
