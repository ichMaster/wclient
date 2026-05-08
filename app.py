"""
wclient — Terminal HTTP API Client

A simple TUI for composing and sending HTTP requests,
inspired by Postman / Insomnia, built with Textual.
"""
from __future__ import annotations

import json
import time

import httpx
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Select,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

HTTP_METHODS = [
    ("GET", "GET"),
    ("POST", "POST"),
    ("PUT", "PUT"),
    ("PATCH", "PATCH"),
    ("DELETE", "DELETE"),
    ("HEAD", "HEAD"),
    ("OPTIONS", "OPTIONS"),
]


def parse_headers(text: str) -> dict[str, str]:
    headers = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            headers[key.strip()] = value.strip()
    return headers


def prettify_json(text: str) -> str:
    if not text.strip():
        return text
    try:
        return json.dumps(json.loads(text), indent=2)
    except (json.JSONDecodeError, ValueError):
        return text


def format_size(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


class APIClient(App):
    """Terminal HTTP API Client TUI."""

    CSS_PATH = "client.tcss"
    TITLE = "wclient"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "send", "Send"),
        Binding("escape", "focus_url", "URL"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Horizontal(id="bar"):
            yield Select(HTTP_METHODS, value="GET", id="method")
            yield Input(placeholder="https://api.example.com/endpoint", id="url")
            yield Button("Send", variant="primary", id="send")

        with TabbedContent(id="tabs"):
            with TabPane("Headers", id="tab-headers"):
                yield TextArea(
                    id="header-input",
                    text="# One header per line: Key: Value",
                    soft_wrap=False,
                )
            with TabPane("Body", id="tab-body"):
                yield TextArea(id="body-input", language="json", soft_wrap=False)

        yield Static(id="status")

        with TabbedContent(id="res-tabs"):
            with TabPane("Body", id="tab-res-body"):
                yield TextArea(
                    id="res-body", read_only=True, language="json", soft_wrap=False
                )
            with TabPane("Headers", id="tab-res-headers"):
                yield DataTable(id="res-headers")

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#url", Input).focus()
        self.query_one("#res-headers", DataTable).add_columns("Header", "Value")

    def action_focus_url(self) -> None:
        self.query_one("#url", Input).focus()

    def action_send(self) -> None:
        self._send()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send":
            self._send()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "url":
            self._send()

    @work(exclusive=True)
    async def _send(self) -> None:
        url = self.query_one("#url", Input).value.strip()
        if not url:
            self.notify("Enter a URL", severity="error", timeout=3)
            return

        method = self.query_one("#method", Select).value
        headers = parse_headers(self.query_one("#header-input", TextArea).text)
        body = self.query_one("#body-input", TextArea).text

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        status = self.query_one("#status", Static)
        status.update(f"[yellow]→ {method} {url}")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                t0 = time.monotonic()

                content = (
                    body.encode()
                    if body.strip() and method in ("POST", "PUT", "PATCH")
                    else None
                )

                resp = await client.request(
                    method=method, url=url, headers=headers, content=content
                )
                elapsed = time.monotonic() - t0

                body_text = resp.text
                if "json" in resp.headers.get("content-type", ""):
                    body_text = prettify_json(body_text)

                self.query_one("#res-body", TextArea).text = body_text

                ht = self.query_one("#res-headers", DataTable)
                ht.clear()
                for k, v in resp.headers.items():
                    ht.add_row(k, v)

                status.update(
                    f"[bold]{resp.status_code}[/]  "
                    f"[green]{elapsed * 1000:.0f} ms[/]  "
                    f"[cyan]{format_size(len(resp.content))}[/]"
                )
        except httpx.TimeoutException:
            status.update("[red]Timed out[/]")
            self.notify("Request timed out", severity="error", timeout=3)
        except httpx.RequestError as e:
            status.update(f"[red]{e}[/]")
            self.notify(str(e), severity="error", timeout=3)
        except Exception as e:
            status.update("[red]Error[/]")
            self.notify(str(e), severity="error", timeout=3)


if __name__ == "__main__":
    APIClient().run()
