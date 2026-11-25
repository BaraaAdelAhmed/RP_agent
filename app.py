"""Streamlit web UI for the research-paper agent.  Run:  streamlit run app.py"""

from __future__ import annotations


import anthropic
import streamlit as st

from rp_agent.agent import PaperAgent
from rp_agent.config import DEFAULT_EFFORT, MODEL
from rp_agent.project import STAGE_LABELS, STAGES, Project

st.set_page_config(page_title="Research Paper Agent", page_icon="📝", layout="wide")

UPLOAD_TYPES = ["pdf", "png", "jpg", "jpeg", "gif", "webp", "tex", "txt", "md", "bib", "csv"]


def tool_label(name: str, data: dict | None) -> str:
    data = data or {}
    labels = {
        "search_literature": lambda d: f"🔎 Searching literature: *{d.get('query', '')}*",
        "add_reference": lambda d: f"📚 Adding reference `{d.get('identifier', '')}`",
        "remove_reference": lambda d: f"🗑️ Removing reference `{d.get('key', '')}`",
        "write_file": lambda d: f"✍️ Writing `{d.get('path', '')}`",
        "read_file": lambda d: f"📖 Reading `{d.get('path', '')}`",
        "list_files": lambda d: "📂 Listing files",
        "set_stage": lambda d: f"🧭 Stage → **{d.get('stage', '')}**",
        "record_user_approval": lambda d: f"✅ Recording your approval: {d.get('gate', '')}",
        "run_python": lambda d: f"🐍 Running `{d.get('script_path', '')}`",
        "compile_latex": lambda d: "🛠️ Compiling LaTeX",
        "web_search": lambda d: f"🌐 Web search: *{d.get('detail', '')}*",
        "web_fetch": lambda d: f"🌐 Fetching {d.get('detail', '')}",
    }
    return labels.get(name, lambda d: f"🔧 {name}")(data)


# ------------------------------------------------------------------ sidebar: project
with st.sidebar:
    st.title("📝 Research Paper Agent")
    projects = Project.list_all()
    with st.form("new_project", clear_on_submit=True):
        new_name = st.text_input("New project name", placeholder="e.g. RIS-aided ISAC")
        if st.form_submit_button("Create project") and new_name.strip():
            st.session_state.project = Project.open(new_name).name
            st.rerun()
    if projects:
        current = st.session_state.get("project") or projects[-1]
        st.session_state.project = st.selectbox(
            "Project", projects, index=projects.index(current) if current in projects else 0)

if not st.session_state.get("project"):
    st.header("Start a new paper")
    st.write("Create a project in the sidebar. Then describe your idea in the chat, or upload a PDF or an image of it.")
    st.stop()

project = Project.open(st.session_state.project)
state = project.state

# ------------------------------------------------------------------ sidebar: progress & settings
with st.sidebar:
    st.subheader("Progress")
    cur = STAGES.index(state.stage)
    for i, s in enumerate(STAGES):
        icon = "✅" if i < cur else ("▶️" if i == cur else "⬜")
        st.markdown(f"{icon} {STAGE_LABELS[s]}")
    if state.working_title:
        st.caption(f"**Working title:** {state.working_title}")
    if state.novelty_verdict:
        st.caption(f"**Novelty:** {state.novelty_verdict}")

    with st.expander("Approval gates"):
        st.caption("The agent records these from your messages. You can also set them here.")
        nov = st.checkbox("Novelty assessment approved", value=state.novelty_approved)
        stc = st.checkbox("Titles & structure approved", value=state.structure_approved, disabled=not nov)
        if nov != state.novelty_approved or (stc and nov) != state.structure_approved:
            state.novelty_approved, state.structure_approved = nov, (stc and nov)
            state.approvals.append({"gate": "manual (sidebar)", "quote": f"novelty={nov}, structure={stc and nov}"})
            project.save_state()
            st.rerun()

    st.subheader("Settings")
    effort = st.selectbox("Reasoning effort", ["medium", "high", "xhigh", "max"],
                          index=["medium", "high", "xhigh", "max"].index(DEFAULT_EFFORT)
                          if DEFAULT_EFFORT in ("medium", "high", "xhigh", "max") else 1,
                          help="Higher means deeper analysis, but it is slower and uses more tokens.")
    allow_python = st.toggle("Allow local Python for figures/simulations", value=False,
                             help="Lets the agent run the Python scripts it writes on THIS machine, inside the "
                                  "project folder, to produce figures and numerical results. Without it, the "
                                  "Results section gets clearly marked placeholders instead of numbers.")
    st.caption(f"Model: `{MODEL}`")
    st.download_button("⬇️ Download project (.zip)", project.zip_bytes(), file_name=f"{project.name}.zip",
                       use_container_width=True)

# ------------------------------------------------------------------ main
st.header(state.working_title or project.name)
chat_tab, files_tab = st.tabs(["💬 Chat", "📄 Files"])

with files_tab:
    files = project.list_files()
    if not files:
        st.info("No files yet. They appear here as the agent writes them.")
    else:
        default = files.index("main.tex") if "main.tex" in files else 0
        sel = st.selectbox("File", files, index=default)
        path = project.root / sel
        data = path.read_bytes()
        st.download_button(f"Download {path.name}", data, file_name=path.name)
        suffix = path.suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            st.image(data)
        elif suffix == ".md":
            st.markdown(data.decode(errors="replace"))
        elif suffix in {".tex", ".bib", ".sty", ".cls"}:
            st.code(data.decode(errors="replace"), language="latex", line_numbers=True)
        elif suffix in {".py", ".csv", ".txt", ".dat", ".log", ".json"}:
            st.code(data.decode(errors="replace"), language="python" if suffix == ".py" else None)
        else:
            st.caption("Binary file. Use the download button.")

with chat_tab:
    chat = project.load_chat()
    if not chat:
        st.info("**How it works:** 1) describe your idea, or upload a PDF or image of it → 2) the agent searches the "
                "literature and reports how novel the idea is → 3) it proposes titles and a tailored structure → "
                "4) it writes the LaTeX project (Problem Formulation, Analysis and Results in full; Introduction as "
                "guide points) with a verified `references.bib`.")
    for entry in chat:
        with st.chat_message(entry["role"]):
            if entry.get("files"):
                st.caption("📎 " + ", ".join(entry["files"]))
            if entry.get("activity"):
                with st.expander(f"Activity ({len(entry['activity'])} steps)"):
                    st.markdown("\n\n".join(entry["activity"]))
            st.markdown(entry.get("text", ""))

    prompt = st.chat_input("Describe your idea, answer the agent, or attach a PDF or image…",
                           accept_file="multiple", file_type=UPLOAD_TYPES)

    if prompt:
        text = prompt.text or ""
        attachments = [(f.name, f.getvalue()) for f in (prompt.files or [])]
        user_entry = {"role": "user", "text": text, "files": [a[0] for a in attachments]}
        chat.append(user_entry)
        project.save_chat(chat)
        with st.chat_message("user"):
            if attachments:
                st.caption("📎 " + ", ".join(a[0] for a in attachments))
            st.markdown(text)

        with st.chat_message("assistant"):
            status = st.status("Working…", expanded=False)
            thinking_box = status.empty()
            out = st.empty()
            reply, activity, thinking = "", [], ""
            agent = PaperAgent(project, effort=effort, allow_python=allow_python)
            try:
                for ev in agent.run(text, attachments):
                    t = ev["type"]
                    if t == "text":
                        reply += ev["text"]
                        out.markdown(reply + "▌")
                    elif t == "thinking_start":
                        if reply and not reply.endswith("\n\n"):
                            reply += "\n\n"
                        thinking = ""
                        status.update(label="Thinking…")
                    elif t == "thinking":
                        thinking += ev["text"]
                        thinking_box.caption(thinking[-600:])
                    elif t == "tool_writing":
                        status.update(label=tool_label(ev["name"], {}).split(":")[0] + "…")
                    elif t == "tool_start":
                        label = tool_label(ev["name"], ev["input"] if isinstance(ev["input"], dict) else {})
                        activity.append(label)
                        status.write(label)
                        status.update(label=label)
                    elif t == "tool_end" and ev["is_error"]:
                        note = f"⚠️ `{ev['name']}`: {ev['result'][:300]}"
                        activity.append(note)
                        status.write(note)
                    elif t == "server_tool":
                        label = tool_label(ev["name"], ev)
                        activity.append(label)
                        status.write(label)
                    elif t in ("notice", "error"):
                        reply += f"\n\n> **{'Note' if t == 'notice' else 'Error'}:** {ev['text']}"
                status.update(label=f"Done — {len(activity)} steps", state="complete")
            except anthropic.AuthenticationError:
                status.update(label="Authentication failed", state="error")
                reply += "\n\n> **Error:** No valid Anthropic credentials. Set `ANTHROPIC_API_KEY` and restart."
            except anthropic.RateLimitError:
                status.update(label="Rate limited", state="error")
                reply += "\n\n> **Error:** Rate limited by the API. Wait a minute, then say 'continue'."
            except anthropic.APIStatusError as e:
                status.update(label="API error", state="error")
                reply += f"\n\n> **API error {e.status_code}:** {e.message}"
            except anthropic.APIConnectionError:
                status.update(label="Network error", state="error")
                reply += "\n\n> **Error:** Could not reach the Anthropic API. Check your connection."
            out.markdown(reply)
            chat.append({"role": "assistant", "text": reply, "activity": activity})
            project.save_chat(chat)
        st.rerun()
