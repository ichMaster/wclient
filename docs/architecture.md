# Architecture Overview

wclient is a terminal-based HTTP API client built on two libraries:

- **Textual** — a Python TUI (Text User Interface) framework that provides reactive widgets, CSS-based styling, async workers, and key bindings.
- **httpx** — an async-capable HTTP client that replaces `requests` for non-blocking network calls.

The entire application lives in a single file (`app.py`) with styling in a separate Textual CSS file (`client.tcss`).

## Application Class: `APIClient`

`APIClient` subclasses `textual.app.App`, the root class of every Textual application. It is responsible for:

1. **Declaring the widget tree** via `compose()`.
2. **Registering key bindings** via the `BINDINGS` class variable.
3. **Handling events** (button presses, input submissions, mount lifecycle).
4. **Executing HTTP requests** in an async background worker.

### Class-level Configuration

```python
CSS_PATH = "client.tcss"   # Textual loads and applies this stylesheet automatically
TITLE = "wclient"           # Shown in the terminal title bar / Header widget
```

`BINDINGS` maps keyboard shortcuts to actions:

| Shortcut | Action method        | Description          |
|----------|----------------------|----------------------|
| Ctrl+Q   | `action_quit()`      | Exit the application |
| Ctrl+S   | `action_send()`      | Send the HTTP request|
| Escape   | `action_focus_url()` | Move focus to the URL input |

`action_quit()` is inherited from `App` — the other two are defined explicitly in `APIClient`.

## Widget Tree

The `compose()` method builds the following UI structure (top to bottom):

```
Header (clock enabled)
├── Horizontal #bar
│   ├── Select #method          — HTTP method dropdown (GET, POST, etc.)
│   ├── Input #url              — URL text input
│   └── Button #send            — "Send" button
├── TabbedContent #tabs         — Request configuration
│   ├── TabPane "Headers"
│   │   └── TextArea #header-input   — raw header text, one per line
│   └── TabPane "Body"
│       └── TextArea #body-input     — request body (JSON syntax highlighting)
├── Static #status              — status line (status code, timing, size)
├── TabbedContent #res-tabs     — Response display
│   ├── TabPane "Body"
│   │   └── TextArea #res-body       — response body (read-only, JSON highlighting)
│   └── TabPane "Headers"
│       └── DataTable #res-headers   — response headers as a two-column table
└── Footer                      — shows available key bindings
```

Every widget has a unique `id` attribute, which serves two purposes:
- **CSS targeting** — the stylesheet references widgets by `#id`.
- **Python querying** — `self.query_one("#id", WidgetType)` retrieves the widget instance at runtime.

## Request Lifecycle

The full lifecycle of sending a request is:

1. **Trigger** — user clicks Send, presses Ctrl+S, or hits Enter in the URL input. All three paths converge on calling `self._send()`.
2. **Validation** — `_send()` reads the URL input. If empty, it shows a toast notification and returns early.
3. **Preparation** — the method, headers, body, and URL are collected from the widgets. If the URL lacks a scheme (`http://` or `https://`), `https://` is prepended.
4. **Status update** — the status line shows a yellow arrow with the method and URL to indicate an in-flight request.
5. **HTTP call** — an `httpx.AsyncClient` is created with a 30-second timeout. The request body is only attached for POST, PUT, and PATCH methods. The request is `await`ed.
6. **Response rendering** — the response body is placed in the read-only TextArea. If the `content-type` header contains "json", the body is auto-prettified with 2-space indentation. Response headers are loaded into the DataTable row by row.
7. **Status update** — the status line displays the HTTP status code, elapsed time in milliseconds, and response size in human-readable units.
8. **Error handling** — timeout, request errors, and unexpected exceptions are each caught separately and displayed both on the status line and as toast notifications.

## Async Worker Pattern

`_send()` is decorated with `@work(exclusive=True)` from Textual. This means:

- The method runs as a Textual **worker** — it executes asynchronously without blocking the UI event loop.
- `exclusive=True` ensures that only one instance of `_send()` runs at a time. If a new request is triggered while a previous one is still in flight, the previous worker is cancelled and the new one starts.
- Inside the worker, code can safely access and update widgets because Textual workers run within the app's async context (unlike raw threads).

## Event Handlers

Textual uses a naming convention for event handlers: `on_<widget>_<event>`.

| Method | Trigger | Behavior |
|--------|---------|----------|
| `on_mount()` | App has been mounted to the DOM | Focuses the URL input and adds columns ("Header", "Value") to the response headers DataTable |
| `on_button_pressed()` | Any Button is clicked | Checks if the pressed button's `id` is `"send"`, then calls `_send()` |
| `on_input_submitted()` | Enter is pressed inside an Input | Checks if the input's `id` is `"url"`, then calls `_send()` |

## Data Flow Diagram

```
User Input                          Network
──────────                          ───────
URL bar ─────────┐
Method dropdown ─┤
Headers editor ──┤──▶ _send() ──▶ httpx.AsyncClient.request()
Body editor ─────┘                      │
                                        ▼
                                   HTTP Response
                                        │
                      ┌─────────────────┼─────────────────┐
                      ▼                 ▼                  ▼
               Response body    Response headers    Status/timing
               (TextArea)       (DataTable)         (Static)
```
