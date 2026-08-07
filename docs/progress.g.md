---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `progress.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ProgressBar`](#%EF%B8%8F-class-progressbar)
  - [⚙️ Method `ProgressBar.__init__`](#%EF%B8%8F-method-progressbar__init__)
  - [⚙️ Method `ProgressBar.finish`](#%EF%B8%8F-method-progressbarfinish)
  - [⚙️ Method `ProgressBar.update`](#%EF%B8%8F-method-progressbarupdate)
- [🔧 Function `iter_with_progress`](#-function-iter_with_progress)
- [🔧 Function `render_progress`](#-function-render_progress)
- [🔧 Function `render_progress_ascii`](#-function-render_progress_ascii)

</details>

## 🏛️ Class `ProgressBar`

```python
class ProgressBar
```

In-place progress bar written to a stream (default: stderr when it is a TTY).

When enabled, draws `0/total` immediately so the bar is visible before the first item finishes.

<details>
<summary>Code:</summary>

```python
class ProgressBar:
    def __init__(
        self,
        total: int,
        *,
        stream: TextIO | None = None,
        enabled: bool | None = None,
        width: int = _DEFAULT_WIDTH,
    ) -> None:
        """Create a progress bar and draw the initial `0/total` line when enabled.

        Args:

        - `total` (`int`): Total items.
        - `stream` (`TextIO | None`): Output stream. Defaults to `sys.stderr`.
        - `enabled` (`bool | None`): Force on/off. Defaults to `stream.isatty()` and `total > 0`.
        - `width` (`int`): Bar width. Defaults to `40`.

        """
        self.total = max(0, total)
        self.width = width
        self.stream: TextIO = stream if stream is not None else sys.stderr
        if enabled is None:
            enabled = bool(getattr(self.stream, "isatty", lambda: False)()) and self.total > 0
        self.enabled = bool(enabled) and self.total > 0
        self.done = 0
        self._last_len = 0
        self._use_ascii = False
        if self.enabled:
            self._write_line(0)

    def finish(self) -> None:
        """Draw a final 100% line and leave it visible on its own row."""
        if not self.enabled:
            return
        self.done = self.total
        try:
            # Clear leftovers from a longer previous in-place draw, then print 100% permanently.
            clear_width = max(self._last_len, len(render_progress(self.total, self.total, width=self.width)))
            self.stream.write("\r" + (" " * clear_width) + "\r")
            self.stream.flush()
        except OSError:
            return
        self._write_line(self.total)
        try:
            self.stream.write("\n")
            self.stream.flush()
        except OSError:
            return
        self._last_len = 0

    def update(self, done: int | None = None) -> None:
        """Set or increment progress and redraw when appropriate.

        Args:

        - `done` (`int | None`): Number of completed items. `None` increments by one.
          Defaults to `None`.

        Returns:

        - `None`.

        """
        if not self.enabled:
            return
        if done is None:
            self.done += 1
        else:
            self.done = max(0, done)
        if not self._should_redraw(self.done):
            return
        self._write_line(self.done)

    def _should_redraw(self, done: int) -> bool:
        if done <= 1 or done >= self.total:
            return True
        if self.total < _FULL_REDRAW_TOTAL:
            return True
        step = max(1, self.total // 100)
        return done % step == 0

    def _write_line(self, done: int) -> None:
        renderer = render_progress_ascii if self._use_ascii else render_progress
        line = renderer(done, self.total, width=self.width)
        try:
            padded = line if len(line) >= self._last_len else line + (" " * (self._last_len - len(line)))
            self.stream.write("\r" + padded)
            self.stream.flush()
            self._last_len = len(line)
        except UnicodeEncodeError:
            self._use_ascii = True
            line = render_progress_ascii(done, self.total, width=self.width)
            try:
                padded = line if len(line) >= self._last_len else line + (" " * (self._last_len - len(line)))
                self.stream.write("\r" + padded)
                self.stream.flush()
                self._last_len = len(line)
            except OSError:
                self.enabled = False
        except OSError:
            self.enabled = False
```

</details>

### ⚙️ Method `ProgressBar.__init__`

```python
def __init__(self, total: int) -> None
```

Create a progress bar and draw the initial `0/total` line when enabled.

Args:

- `total` (`int`): Total items.
- `stream` (`TextIO | None`): Output stream. Defaults to `sys.stderr`.
- `enabled` (`bool | None`): Force on/off. Defaults to `stream.isatty()` and `total > 0`.
- `width` (`int`): Bar width. Defaults to `40`.

<details>
<summary>Code:</summary>

```python
def __init__(
    self,
    total: int,
    *,
    stream: TextIO | None = None,
    enabled: bool | None = None,
    width: int = _DEFAULT_WIDTH,
) -> None:
    self.total = max(0, total)
    self.width = width
    self.stream: TextIO = stream if stream is not None else sys.stderr
    if enabled is None:
        enabled = bool(getattr(self.stream, "isatty", lambda: False)()) and self.total > 0
    self.enabled = bool(enabled) and self.total > 0
    self.done = 0
    self._last_len = 0
    self._use_ascii = False
    if self.enabled:
        self._write_line(0)
```

</details>

### ⚙️ Method `ProgressBar.finish`

```python
def finish(self) -> None
```

Draw a final 100% line and leave it visible on its own row.

<details>
<summary>Code:</summary>

```python
def finish(self) -> None:
    if not self.enabled:
        return
    self.done = self.total
    try:
        # Clear leftovers from a longer previous in-place draw, then print 100% permanently.
        clear_width = max(self._last_len, len(render_progress(self.total, self.total, width=self.width)))
        self.stream.write("\r" + (" " * clear_width) + "\r")
        self.stream.flush()
    except OSError:
        return
    self._write_line(self.total)
    try:
        self.stream.write("\n")
        self.stream.flush()
    except OSError:
        return
    self._last_len = 0
```

</details>

### ⚙️ Method `ProgressBar.update`

```python
def update(self, done: int | None = None) -> None
```

Set or increment progress and redraw when appropriate.

Args:

- `done` (`int | None`): Number of completed items. `None` increments by one.
  Defaults to `None`.

Returns:

- `None`.

<details>
<summary>Code:</summary>

```python
def update(self, done: int | None = None) -> None:
    if not self.enabled:
        return
    if done is None:
        self.done += 1
    else:
        self.done = max(0, done)
    if not self._should_redraw(self.done):
        return
    self._write_line(self.done)
```

</details>

## 🔧 Function `iter_with_progress`

```python
def iter_with_progress(items: Sequence[T]) -> Iterator[T]
```

Yield items while updating a progress bar.

When `show_progress` is `True`, the bar is shown only if the stream is a TTY.
When `show_progress` is `False`, iteration is silent.

Args:

- `items` (`Sequence[T]`): Items to iterate over.
- `show_progress` (`bool`): Draw the progress bar. Defaults to `True`.
- `stream` (`TextIO | None`): Target stream. Defaults to `None` (stderr).
- `width` (`int`): Bar width in characters. Defaults to `40`.

Yields:

- `T`: Each item from `items`, in order.

<details>
<summary>Code:</summary>

```python
def iter_with_progress(
    items: Sequence[T],
    *,
    show_progress: bool = True,
    stream: TextIO | None = None,
    width: int = _DEFAULT_WIDTH,
) -> Iterator[T]:
    total = len(items)
    enabled = False if not show_progress else None
    bar = ProgressBar(total, stream=stream, enabled=enabled, width=width)
    try:
        for index, item in enumerate(items, start=1):
            yield item
            bar.update(index)
    finally:
        bar.finish()
```

</details>

## 🔧 Function `render_progress`

```python
def render_progress(done: int, total: int) -> str
```

Return a single-line progress string.

Args:

- `done` (`int`): Number of completed items.
- `total` (`int`): Total number of items.
- `width` (`int`): Bar width in characters. Defaults to `40`.

Returns:

- `str`: e.g. `Progress: |████░░░░| 2/8 (25%)`.

<details>
<summary>Code:</summary>

```python
def render_progress(done: int, total: int, *, width: int = _DEFAULT_WIDTH) -> str:
    safe_done = max(0, done)
    safe_total = max(0, total)
    if safe_total <= 0:
        pct = 100
        filled = width
        display_done = 0
        display_total = 0
    else:
        display_done = min(safe_done, safe_total)
        display_total = safe_total
        pct = min(100, int(100 * display_done / safe_total))
        filled = min(width, round(width * display_done / safe_total))
    empty = width - filled
    bar = ("█" * filled) + ("░" * empty)
    return f"Progress: |{bar}| {display_done}/{display_total} ({pct}%)"
```

</details>

## 🔧 Function `render_progress_ascii`

```python
def render_progress_ascii(done: int, total: int) -> str
```

ASCII fallback when the stream cannot encode block characters.

Args:

- `done` (`int`): Number of completed items.
- `total` (`int`): Total number of items.
- `width` (`int`): Bar width in characters. Defaults to `40`.

Returns:

- `str`: e.g. `Progress: |####----| 2/8 (25%)`.

<details>
<summary>Code:</summary>

```python
def render_progress_ascii(done: int, total: int, *, width: int = _DEFAULT_WIDTH) -> str:
    safe_done = max(0, done)
    safe_total = max(0, total)
    if safe_total <= 0:
        pct = 100
        filled = width
        display_done = 0
        display_total = 0
    else:
        display_done = min(safe_done, safe_total)
        display_total = safe_total
        pct = min(100, int(100 * display_done / safe_total))
        filled = min(width, round(width * display_done / safe_total))
    empty = width - filled
    bar = ("=" * filled) + ("-" * empty)
    return f"Progress: |{bar}| {display_done}/{display_total} ({pct}%)"
```

</details>
