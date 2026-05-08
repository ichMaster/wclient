# wclient

A terminal HTTP API client with a Textual TUI — compose requests, set headers and body, send any HTTP method, and view formatted responses.

## Install

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
python app.py
```

| Key | Action |
|---|---|
| `Ctrl+S` | Send request |
| `Escape` | Focus URL input |
| `Ctrl+Q` | Quit |

## Features

- Method selector: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- Custom headers — one `Key: Value` per line
- Request body editor with JSON syntax highlighting
- Response body with auto-prettified JSON and syntax highlighting
- Response headers table
- Status code, request timing, and response size display
- 30 s request timeout
- URLs without a scheme get `https://` prepended automatically
- Body is only sent for POST/PUT/PATCH

## Dependencies

- [textual](https://textual.textualize.io) — TUI framework
- [httpx](https://www.python-httpx.org) — async HTTP client
