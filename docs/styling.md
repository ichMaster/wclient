# Styling with Textual CSS

wclient uses Textual's CSS dialect (TCSS) for layout and visual styling. The stylesheet is in `client.tcss` and is loaded automatically because `APIClient` declares `CSS_PATH = "client.tcss"`.

Textual CSS is similar to web CSS but operates on terminal widgets instead of DOM elements. It supports a subset of CSS properties relevant to TUI layout: `width`, `height`, `margin`, `padding`, `background`, `border`, and Textual-specific properties like `text-style`.

## Theme Variables

The stylesheet uses Textual theme variables (prefixed with `$`) rather than hard-coded colors:

| Variable     | Meaning                              |
|-------------|--------------------------------------|
| `$surface`  | Default background color             |
| `$primary`  | Primary accent color (used for request tabs border) |
| `$secondary`| Secondary accent color (used for response tabs border) |
| `$panel`    | Panel/toolbar background (used for the status bar) |

These variables automatically adapt when the user switches Textual themes (dark/light), so no manual color overrides are needed.

## Layout Structure

The UI is organized as a vertical stack of sections, each with specific height rules:

```
┌─────────────────────────────────────────────┐
│ Header (auto height from Textual)           │
├─────────────────────────────────────────────┤
│ #bar — height: 3 lines                      │
│ ┌──────────┬─────────────────────┬────────┐ │
│ │ Select   │ Input (1fr)         │ Button │ │
│ │ width:12 │ flexible            │ width:10│ │
│ └──────────┴─────────────────────┴────────┘ │
├─────────────────────────────────────────────┤
│ #tabs — height: 10 lines                    │
│ Request headers / body editors              │
├─────────────────────────────────────────────┤
│ #status — height: 1 line                    │
│ Status code, timing, response size          │
├─────────────────────────────────────────────┤
│ #res-tabs — height: 1fr (fills remaining)   │
│ Response body / headers display             │
├─────────────────────────────────────────────┤
│ Footer (auto height from Textual)           │
└─────────────────────────────────────────────┘
```

### Key Layout Details

**The top bar (`#bar`)**
- Fixed at 3 lines tall with horizontal padding of 1 character.
- Uses `align: center middle` to vertically center its children.
- The method `Select` has a fixed width of 12 characters and a right margin of 1.
- The URL `Input` has `width: 1fr` — the `fr` unit (fractional) means it takes all remaining horizontal space after the fixed-width Select and Button.
- The `Button` has a fixed width of 10 characters and a left margin of 1.

**Request tabs (`#tabs`)**
- Fixed height of 10 lines — enough for a few headers or a short JSON body.
- Bordered with a solid line in the `$primary` color.
- Horizontal margin of 1 character on each side.
- Both `#header-input` and `#body-input` TextAreas are set to `height: 100%` so they fill their respective tab panes entirely.

**Status line (`#status`)**
- Exactly 1 line tall.
- Horizontal padding of 2 characters.
- Background color uses `$panel` to visually separate it as a toolbar/info bar.
- Text is bold (`text-style: bold`).

**Response tabs (`#res-tabs`)**
- Height is `1fr`, meaning it expands to fill all vertical space not consumed by the fixed-height sections above. This ensures the response area grows with the terminal window.
- Bordered with a solid line in `$secondary` (visually distinguishes it from the request tabs).
- Margin of 1 character on all sides except the top (`margin: 0 1 1 1`).
- Both `#res-body` and `#res-headers` fill their tab panes at `height: 100%`.

## Modifying the Layout

Common adjustments:

- **Make the request editor taller:** Change `#tabs { height: 10; }` to a larger value (e.g., `15` or `20`).
- **Give the response area a fixed height instead of flexible:** Replace `#res-tabs { height: 1fr; }` with a fixed number like `height: 20;`.
- **Change the method selector width:** Adjust `#bar > Select { width: 12; }` — increase if you add longer method names.
- **Remove borders:** Delete the `border` lines from `#tabs` or `#res-tabs`.
