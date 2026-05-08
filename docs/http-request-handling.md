# HTTP Request Handling

This document covers the `_send()` method in detail — the core of wclient's functionality.

## Method Signature and Decorator

```python
@work(exclusive=True)
async def _send(self) -> None:
```

- **`async def`** — the method is a coroutine, allowing it to `await` the HTTP response without freezing the UI.
- **`@work(exclusive=True)`** — Textual's worker decorator. `exclusive=True` means that if `_send()` is called while a previous invocation is still running, the previous one is automatically cancelled. This prevents overlapping requests from clobbering each other's UI updates.

## Step-by-Step Walkthrough

### 1. Read and Validate the URL

```python
url = self.query_one("#url", Input).value.strip()
if not url:
    self.notify("Enter a URL", severity="error", timeout=3)
    return
```

`query_one("#url", Input)` retrieves the URL input widget by its CSS id. The second argument (`Input`) is a type hint that gives autocompletion and type safety. If the URL is empty after stripping whitespace, a toast notification is shown for 3 seconds and the method returns early.

### 2. Collect Request Parameters

```python
method = self.query_one("#method", Select).value
headers = parse_headers(self.query_one("#header-input", TextArea).text)
body = self.query_one("#body-input", TextArea).text
```

- `method` is the currently selected value from the dropdown (e.g., `"GET"`, `"POST"`).
- `headers` are parsed from the raw text using the `parse_headers()` utility.
- `body` is the raw text from the body editor — it is not parsed or validated at this stage.

### 3. Normalize the URL

```python
if not url.startswith(("http://", "https://")):
    url = "https://" + url
```

A convenience feature: users can type `api.example.com/users` instead of `https://api.example.com/users`. The check uses a tuple with `startswith()` to match either scheme. HTTPS is the default — there is no option to default to HTTP.

### 4. Show In-Flight Status

```python
status = self.query_one("#status", Static)
status.update(f"[yellow]→ {method} {url}")
```

The `Static` widget's `update()` method replaces its content. The `[yellow]` syntax is Textual's Rich markup — it colors the text yellow to indicate a pending request.

### 5. Execute the HTTP Request

```python
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
```

Key details:

- **`httpx.AsyncClient`** is used as an async context manager. A new client is created per request, which means connections are not reused across requests. This is acceptable for a manual API testing tool.
- **`timeout=30`** sets a 30-second timeout for the entire request (connection + read).
- **`time.monotonic()`** is used instead of `time.time()` to measure elapsed time. Monotonic clocks are immune to system clock adjustments and are the correct choice for measuring intervals.
- **Body is conditional:** the body is only sent (`content=body.encode()`) if it's non-empty AND the method is POST, PUT, or PATCH. For GET, DELETE, HEAD, and OPTIONS, `content=None` means no body is sent. The `encode()` call converts the string to bytes using UTF-8 (Python's default encoding).
- **`client.request()`** is the generic method that accepts any HTTP method as a string parameter, avoiding the need for separate `client.get()`, `client.post()`, etc. calls.

### 6. Render the Response Body

```python
body_text = resp.text
if "json" in resp.headers.get("content-type", ""):
    body_text = prettify_json(body_text)

self.query_one("#res-body", TextArea).text = body_text
```

- `resp.text` decodes the response bytes to a string (httpx handles encoding detection).
- The content-type check is a substring match — it catches `application/json`, `application/vnd.api+json`, `text/json`, etc. The fallback `""` avoids a `TypeError` if the header is missing.
- The response TextArea has `language="json"` set during composition, so it always applies JSON syntax highlighting (even for non-JSON responses — this is a minor imperfection that causes no harm since non-JSON text simply gets no highlighting).

### 7. Render the Response Headers

```python
ht = self.query_one("#res-headers", DataTable)
ht.clear()
for k, v in resp.headers.items():
    ht.add_row(k, v)
```

The DataTable is cleared first to remove headers from any previous response, then each header is added as a row. The columns ("Header", "Value") were already set up in `on_mount()`.

### 8. Update the Status Line

```python
status.update(
    f"[bold]{resp.status_code}[/]  "
    f"[green]{elapsed * 1000:.0f} ms[/]  "
    f"[cyan]{format_size(len(resp.content))}[/]"
)
```

Three pieces of information are shown with Rich markup:
- **Status code** in bold (e.g., `200`, `404`).
- **Elapsed time** in green, converted from seconds to milliseconds with no decimal places.
- **Response size** in cyan, formatted by `format_size()` (e.g., `1.5 KB`).

`resp.content` is the raw bytes, so `len()` gives the exact byte count.

## Error Handling

Three exception types are caught separately:

| Exception | Cause | Status Display | Notification |
|-----------|-------|---------------|--------------|
| `httpx.TimeoutException` | Request exceeded 30s | Red "Timed out" | "Request timed out" |
| `httpx.RequestError` | DNS failure, connection refused, invalid URL, etc. | Red error message | Error details |
| `Exception` | Any other unexpected error | Red "Error" | Error details |

All error handlers update both the status line (persistent) and show a toast notification (auto-dismisses after 3 seconds). The broad `Exception` catch is a safety net — in a TUI application, an unhandled exception would crash the entire terminal UI.

## Entry Points to `_send()`

There are three ways to trigger a request, all converging on `_send()`:

```
Ctrl+S  ──▶  action_send()  ──▶  _send()
                                    ▲
Send button click  ──▶  on_button_pressed()  ──┘
                                    ▲
Enter in URL input ──▶  on_input_submitted() ──┘
```

The `action_send()` method is a one-liner that calls `_send()`. `on_button_pressed()` and `on_input_submitted()` both check the widget `id` before delegating, ensuring they don't fire for other buttons or inputs (even though there currently is only one of each).
