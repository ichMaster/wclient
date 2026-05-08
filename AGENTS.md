# AGENTS.md

## Quick start

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## What it is

A terminal HTTP API client TUI (Textual). Compose requests, set headers/body, send HTTP methods, view formatted responses.

## Project structure

| Path | Purpose |
|---|---|
| `app.py` | Textual application — entrypoint |
| `client.tcss` | Textual stylesheet |
| `requirements.txt` | Dependencies: textual, httpx |

## Commands

| Command | Action |
|---|---|
| `python app.py` | Launch the TUI |
| `pip install -r requirements.txt` | Install deps |

## TUI keybindings (built-in)

| Key | Action |
|---|---|
| `Ctrl+S` | Send request |
| `Escape` | Focus URL input |
| `Ctrl+Q` | Quit |

## Notes

- URLs without a scheme get `https://` prepended automatically.
- Request body is only sent for POST/PUT/PATCH.
- JSON responses are auto-prettified.
- Only two dependencies: `textual` (TUI framework) and `httpx` (async HTTP).
