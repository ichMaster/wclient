# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

wclient — a terminal HTTP API client TUI (like Postman/Insomnia for the terminal), built with Textual and httpx.

## Setup & Run

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Architecture

Single-file app (`app.py`) with a Textual CSS stylesheet (`client.tcss`).

- **`APIClient`** (subclass of `textual.app.App`) is the sole application class. It owns the entire UI: method selector, URL input, request headers/body editors, and response display panels.
- **`_send()`** is the core async worker (decorated with `@work(exclusive=True)`) that builds and fires HTTP requests via `httpx.AsyncClient`. It runs off the main thread so the TUI stays responsive.
- **`client.tcss`** controls layout — top bar (method/URL/send button), request tabs (headers + body), status line, and response tabs (body + headers table). Modify heights and margins here, not in Python.

## Key behaviors to preserve

- URLs without a scheme get `https://` prepended automatically.
- Request body is only sent for POST, PUT, PATCH — ignored for other methods.
- JSON responses are auto-prettified when `content-type` contains "json".
- 30-second request timeout via httpx.
