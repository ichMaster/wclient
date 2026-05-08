# Utility Functions

`app.py` defines three standalone utility functions outside the `APIClient` class. They are pure functions with no side effects and no dependency on application state.

---

## `parse_headers(text: str) -> dict[str, str]`

**Purpose:** Converts the raw text from the headers editor into a dictionary suitable for passing to httpx.

**Input:** A multi-line string where each line is expected to be in `Key: Value` format.

**Processing rules:**

1. The text is split by newlines (`splitlines()`).
2. Each line is stripped of leading/trailing whitespace.
3. Lines that are empty or start with `#` are skipped — this allows users to write comments in the headers editor (the default placeholder text uses this: `# One header per line: Key: Value`).
4. For lines containing a colon, `str.partition(":")` splits on the **first** colon only. This is important because header values may contain colons (e.g., `Authorization: Bearer abc:def:123`).
5. Both the key and value are stripped of whitespace.
6. If duplicate header names appear, later ones overwrite earlier ones (standard Python dict behavior).

**Return value:** A `dict[str, str]` mapping header names to their values.

**Example:**

```python
parse_headers("""
# Auth headers
Authorization: Bearer token123
Content-Type: application/json
""")
# Returns: {"Authorization": "Bearer token123", "Content-Type": "application/json"}
```

**Edge cases:**
- Lines without a colon are silently ignored (no error is raised).
- An empty or whitespace-only input returns an empty dict.

---

## `prettify_json(text: str) -> str`

**Purpose:** Attempts to parse a string as JSON and re-serialize it with 2-space indentation for human readability.

**Processing:**

1. If the input is empty or whitespace-only, it is returned as-is (avoids a parse attempt on blank responses).
2. `json.loads()` parses the string. If successful, `json.dumps(..., indent=2)` re-serializes it with pretty formatting.
3. If parsing fails (`JSONDecodeError` or `ValueError`), the original text is returned unmodified.

This function is used on HTTP response bodies when the `content-type` header contains the substring `"json"`. It is intentionally lenient — if the body claims to be JSON but isn't valid, it degrades to showing the raw text rather than crashing.

**Example:**

```python
prettify_json('{"a":1,"b":[2,3]}')
# Returns:
# {
#   "a": 1,
#   "b": [
#     2,
#     3
#   ]
# }

prettify_json("not json")
# Returns: "not json"
```

---

## `format_size(n: int) -> str`

**Purpose:** Converts a byte count into a human-readable string with an appropriate unit (B, KB, MB, or GB).

**Algorithm:**

1. Iterates through the units `("B", "KB", "MB")`.
2. At each step, if the value is less than 1024, it formats the number with one decimal place and the current unit.
3. If the value is still >= 1024 after dividing through all three units, it formats as GB.

**Note:** The function uses base-1024 divisions (binary-style), but labels with SI-style abbreviations (KB instead of KiB). This is common in developer tools and HTTP clients.

**Examples:**

```python
format_size(512)       # "512.0 B"
format_size(2048)      # "2.0 KB"
format_size(1572864)   # "1.5 MB"
```

**Parameter type:** The parameter `n` is typed as `int` (the length of `resp.content` in bytes), but because it is divided by 1024 in a loop, it becomes a float during processing. The `:.1f` format specifier handles this correctly.
