"""The agent loop: streams Claude's replies, runs tools, and persists the conversation."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Iterator

import anthropic

from .config import (DEFAULT_EFFORT, MAX_AGENT_STEPS, MAX_TOKENS, MODEL, WEB_FETCH_MAX_USES,
                     WEB_SEARCH_MAX_USES)
from .project import Project
from .prompts import SYSTEM_PROMPT
from .tools import run_tool, tool_definitions

IMAGE_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}
TEXT_SUFFIXES = {".tex", ".txt", ".md", ".bib", ".csv", ".py", ".json"}
MAX_TEXT_ATTACHMENT = 200_000

SERVER_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search", "max_uses": WEB_SEARCH_MAX_USES},
    {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": WEB_FETCH_MAX_USES},
]


class PaperAgent:
    def __init__(self, project: Project, effort: str = DEFAULT_EFFORT, allow_python: bool = False,
                 client: anthropic.Anthropic | None = None):
        self.project = project
        self.effort = effort
        self.allow_python = allow_python
        self.client = client or anthropic.Anthropic()
        self.messages: list[dict] = project.load_messages()
        self.tools = tool_definitions() + SERVER_TOOLS  # fixed order keeps the prompt cache valid

    # ------------------------------------------------------------ input
    def _user_content(self, text: str, attachments: list[tuple[str, bytes]]) -> list[dict]:
        blocks: list[dict] = []
        for filename, data in attachments:
            safe = Path(filename).name
            (self.project.root / "inputs" / safe).write_bytes(data)
            mime = mimetypes.guess_type(safe)[0] or ""
            suffix = Path(safe).suffix.lower()
            if mime == "application/pdf":
                blocks.append({"type": "document", "title": safe,
                               "source": {"type": "base64", "media_type": "application/pdf",
                                          "data": base64.standard_b64encode(data).decode()}})
            elif mime in IMAGE_TYPES:
                blocks.append({"type": "image",
                               "source": {"type": "base64", "media_type": mime,
                                          "data": base64.standard_b64encode(data).decode()}})
            elif suffix in TEXT_SUFFIXES:
                body = data.decode("utf-8", errors="replace")
                if len(body) > MAX_TEXT_ATTACHMENT:
                    body = body[:MAX_TEXT_ATTACHMENT] + "\n... [truncated; full file at inputs/" + safe + "]"
                blocks.append({"type": "text", "text": f'<uploaded_file name="{safe}">\n{body}\n</uploaded_file>'})
            else:
                blocks.append({"type": "text", "text": f"(The user uploaded {safe}, a type I can't read directly; "
                                                        f"it is saved at inputs/{safe}.)"})
        if attachments:
            names = ", ".join(Path(f).name for f, _ in attachments)
            text = f"[Uploaded: {names} — saved under inputs/]\n\n{text}".strip()
        blocks.append({"type": "text", "text": text or "(see the attached files)"})
        return blocks

    # ------------------------------------------------------------ one model call
    def _stream_once(self) -> Iterator[dict]:
        params = dict(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[{"type": "text", "text": SYSTEM_PROMPT}],
            tools=self.tools,
            messages=self.messages,
            thinking={"type": "adaptive", "display": "summarized"},
            output_config={"effort": self.effort},
            cache_control={"type": "ephemeral"},  # caches the growing conversation prefix
            # If a safety classifier declines, the API re-runs the request on a fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        with self.client.beta.messages.stream(**params) as stream:
            for event in stream:
                if event.type == "content_block_start":
                    b = event.content_block
                    if b.type == "thinking":
                        yield {"type": "thinking_start"}
                    elif b.type == "tool_use":
                        yield {"type": "tool_writing", "name": b.name}
                elif event.type == "content_block_delta":
                    d = event.delta
                    if d.type == "text_delta":
                        yield {"type": "text", "text": d.text}
                    elif d.type == "thinking_delta":
                        yield {"type": "thinking", "text": d.thinking}
                elif event.type == "content_block_stop":
                    b = event.content_block
                    if b.type == "server_tool_use":
                        inp = b.input if isinstance(b.input, dict) else {}
                        detail = inp.get("query") or inp.get("url") or ""
                        yield {"type": "server_tool", "name": b.name, "detail": str(detail)}
                    elif b.type == "fallback":
                        yield {"type": "notice", "text": "The primary model declined part of this request; a "
                                                         "fallback model continued it."}
            return stream.get_final_message()

    # ------------------------------------------------------------ public
    def run(self, text: str, attachments: list[tuple[str, bytes]] | None = None) -> Iterator[dict]:
        """Run one user turn. Yields UI events; the conversation is saved after every step."""
        self.messages.append({"role": "user", "content": self._user_content(text, attachments or [])})
        self.project.save_messages(self.messages)
        ctx = {"allow_python": self.allow_python, "last_user_text": text}
        bad_json_retries = 0

        for _ in range(MAX_AGENT_STEPS):
            try:
                msg = yield from self._stream_once()
            except anthropic.APIError:
                raise
            except ValueError as e:
                # Eagerly streamed tool input that the SDK could not parse at all: re-issue the request.
                bad_json_retries += 1
                if bad_json_retries > 2:
                    yield {"type": "error", "text": f"Repeatedly received malformed tool input: {e}"}
                    return
                continue

            self.messages.append({"role": "assistant", "content": [b.to_dict(mode="json") for b in msg.content]})
            self.project.save_messages(self.messages)
            stop = msg.stop_reason
            tool_uses = [b for b in msg.content if b.type == "tool_use"]

            if stop == "refusal":
                yield {"type": "error", "text": "The model declined to continue this request."}
                return
            if stop == "pause_turn":  # long server-tool turn (web search); re-send to resume
                continue
            if stop == "max_tokens":
                if tool_uses:
                    # A truncated tool input may parse as a valid but incomplete object: never run it.
                    results = [{"type": "tool_result", "tool_use_id": tu.id, "is_error": True,
                                "content": "Your output hit the token limit, so this call's input was truncated and "
                                           "it was not run. Re-issue it with smaller pieces (one section per file)."}
                               for tu in tool_uses]
                    self.messages.append({"role": "user", "content": results})
                    self.project.save_messages(self.messages)
                    continue
                yield {"type": "notice", "text": "The reply hit the output limit. Say 'continue' to resume."}
                return
            if stop == "tool_use" and tool_uses:
                results = []
                for tu in tool_uses:
                    yield {"type": "tool_start", "name": tu.name, "input": tu.input}
                    content, is_error = run_tool(self.project, tu.name, tu.input, ctx)
                    yield {"type": "tool_end", "name": tu.name, "result": content, "is_error": is_error}
                    results.append({"type": "tool_result", "tool_use_id": tu.id, "content": content,
                                    **({"is_error": True} if is_error else {})})
                self.messages.append({"role": "user", "content": results})
                self.project.save_messages(self.messages)
                continue
            return  # end_turn

        yield {"type": "notice", "text": f"Stopped after {MAX_AGENT_STEPS} steps. Say 'continue' to keep going."}
