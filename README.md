# RP Agent — research paper structuring agent

A local web app that helps you turn a research idea into a structured LaTeX paper. You can start from a chat message, a PDF or an image. The agent is built on the Claude API (`claude-opus-5-5`) and runs on your own machine.

## Quick start with Claude Code (no API key needed)

If you have a Claude plan with Claude Code (for example a university Team seat), you don't need an API key:

1. Open **claude.ai/code** and start a session on this repository.
2. Type `/research-paper` followed by your idea, or attach a PDF or image of it. For example:
   `/research-paper I want to study ... ; I can run Python simulations; target: IEEE journal`
3. Follow the stages. Approve each gate in your own words, for example *"I approve the novelty assessment"* or
   *"use title 2 and this structure"*.
4. Claude commits the paper to `papers/<project>/` on the session branch. Download it from GitHub, or upload the
   folder to Overleaf.

To continue later, start a new session on that branch and say *"continue my paper <project>"*.

The skill lives in `.claude/skills/research-paper/SKILL.md`, its helper commands in `scripts/rp.py`. The hooks in
`.claude/settings.json` (`scripts/rp_hook.py`) block `.tex` writing until both gates are approved, and block
hand-editing `references.bib`.

### Turning the structured paper into a first draft

When the structured paper exists, type `/1st-draft-paper <project>` in a Claude Code session. It:
1. saves a snapshot of the sources and **audits** every line: a notation table, definitions of physical terms,
   dimensional checks, re-derivation of key steps and limiting cases, a claim–evidence map, equation and figure
   referencing, and language. It also proposes a plan to restructure the paper into **6–7 sections**. You approve the
   plan before anything is edited;
2. rewrites the Problem Formulation, Analysis and Results so every symbol and term is defined where it is first used
   and the narrative flows;
3. revises the language towards scientific-paper register (not a textbook), with equation and figure references used
   where they matter;
4. discusses the results by **main point** (a bold lead-in sentence, then evidence → mechanism → implication).
   **New physical insights are printed in blue** (`\finding{...}`) with a verified, well-established supporting
   reference. Set `\showfindingsfalse` in `main.tex` to print them in black for submission;
5. checks everything, writes a word diff against the snapshot, a change report and a simulated referee report.

The Introduction stays as guide points for you to write.

## Standalone web app (needs an Anthropic API key)

### What it does

| Stage | What happens | Output |
|---|---|---|
| 1. Discuss the idea | You chat, upload a PDF (for example a paper to extend) or upload an image (a whiteboard or a figure). The agent sharpens the idea with you until it fits in one precise sentence. | — |
| 2. Verify novelty (**gate**) | The agent searches OpenAlex, arXiv and Semantic Scholar with 8+ differently worded queries, and the web for very recent preprints. It compares the closest prior work, gives a verdict with a confidence level and states the paper's **strong point**. If the idea isn't novel, it proposes pivots. | `notes/novelty_report.md` |
| 3. Titles & structure (**gate**) | It proposes 5 candidate titles and a section structure with headings that suit this paper rather than generic ones. It also plans the figures and tables. | `notes/title_options.md`, `notes/outline.md` |
| 4. Write LaTeX + .bib | **Problem Formulation**, **Analysis** and **Results & Discussion** are written in full. The **Introduction** gets only headings and guide points. The Abstract and Conclusion get guide bullets. | `main.tex`, `sections/*.tex`, `references.bib`, `figures/` |
| 5. Check & hand over | The agent compiles the paper if LaTeX is installed, then fixes undefined citations and references. It ends with a list of what you still have to write. | `main.pdf` |

The two **gates** are enforced in code: the agent cannot write any `.tex` file until you approve the novelty assessment and then the titles and structure. It records an approval only when the quote comes word for word from your latest message. You can also tick the gates in the sidebar.

### Trustworthy references and results
- `references.bib` can only be changed through `add_reference`. That tool downloads the official BibTeX from doi.org, arXiv or OpenAlex, so the agent can't make up a reference. When a claim needs a citation it couldn't find, it writes `\TODO{citation needed}`.
- Numbers in the Results section come only from Python scripts the agent actually ran (if you turn that on) or from data you uploaded. Otherwise the Results section gets clearly marked `\figplaceholder{}` / `\TODO{}` items and the expected trends. Every script that made a figure is saved under `figures/` so you can rerun it.

### Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # or: ant auth login
streamlit run app.py
```

Open http://localhost:8501. Create a project in the sidebar, then describe your idea or attach files using the 📎 button in the chat box.

Optional:
- **LaTeX** (`latexmk` or `pdflatex` + `bibtex`): lets the agent compile and check the paper.
- **numpy / matplotlib**: needed for figures if you turn on *Allow local Python*. That switch lets the agent run the scripts it writes on your machine, inside the project folder. It is off by default.
- `S2_API_KEY`: a Semantic Scholar key for more reliable searches there. Without it, the source is skipped when rate-limited.
- `RP_AGENT_EFFORT` (`medium`/`high`/`xhigh`/`max`), `RP_AGENT_MODEL` and `RP_AGENT_PAPERS_DIR`: environment overrides.

### Project layout

```
app.py                 Streamlit UI (chat, file uploads, progress, file viewer, zip download)
rp_agent/agent.py      Agent loop: streaming Messages API, tool execution, pause/refusal/max-token handling
rp_agent/prompts.py    The workflow and per-section writing rules (edit this to change how papers are built)
rp_agent/tools.py      Tools: literature search, add/remove reference, read/write files, stage and approval gates,
                       run_python, compile_latex
rp_agent/literature.py OpenAlex / arXiv / Semantic Scholar search, DOI/arXiv BibTeX retrieval
papers/<project>/      One folder per paper; .session/ holds the saved conversation so you can resume it
```

### Notes
- No literature search can prove novelty with 100% certainty. The novelty report lists every query and source used, so you can judge how thorough the search was and extend it.
- The agent also uses Anthropic's server-side `web_search`/`web_fetch` tools. Web searches are billed per use on top of tokens.
- If a safety classifier declines a request, it is retried on a fallback model (`fallbacks: "default"`).
