---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `table.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `_escape_table_cell`](#-function-_escape_table_cell)
- [🔧 Function `_format_table_row`](#-function-_format_table_row)
- [🔧 Function `_format_table_separator`](#-function-_format_table_separator)
- [🔧 Function `_is_spurious_table_row`](#-function-_is_spurious_table_row)
- [🔧 Function `_parse_table_row_cells`](#-function-_parse_table_row_cells)
- [🔧 Function `_parse_table_rows`](#-function-_parse_table_rows)
- [🔧 Function `_prefer_source_table_block`](#-function-_prefer_source_table_block)
- [🔧 Function `_render_table`](#-function-_render_table)
- [🔧 Function `_table_cell_display_width`](#-function-_table_cell_display_width)
- [🔧 Function `_table_column_widths`](#-function-_table_column_widths)

</details>

## 🔧 Function `_escape_table_cell`

```python
def _escape_table_cell(cell: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _escape_table_cell(cell: str) -> str:
    if "|" not in cell:
        return cell
    if "`" in cell:
        return cell
    if "<" in cell and ">" in cell:
        return cell.replace("|", "&#124;")
    return cell.replace("|", r"\\|")
```

</details>

## 🔧 Function `_format_table_row`

```python
def _format_table_row(cells: list[str], column_widths: list[int], alignments: list[str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_table_row(
    cells: list[str],
    column_widths: list[int],
    alignments: list[str],
    *,
    strip_trailing_empty: bool = False,
) -> str:
    padded = cells + [""] * (len(column_widths) - len(cells))
    align_row = alignments + ["---"] * (len(column_widths) - len(alignments))
    effective_width = len(column_widths)
    if strip_trailing_empty:
        while effective_width > 1 and not padded[effective_width - 1].strip():
            effective_width -= 1
    padded = padded[:effective_width]
    column_widths = column_widths[:effective_width]
    align_row = align_row[:effective_width]
    formatted_cells: list[str] = []
    padded = [_escape_table_cell(cell) for cell in padded]
    for index, cell in enumerate(padded):
        width = column_widths[index]
        cell_width = _table_cell_display_width(cell)
        padding = max(width - cell_width, 0)
        align = align_row[index] if index < len(align_row) else "---"
        if align in {":--", "---"}:
            formatted_cells.append(f"{cell}{' ' * padding}")
        elif align == ":-:":
            left_pad = padding // 2
            formatted_cells.append(f"{' ' * left_pad}{cell}{' ' * (padding - left_pad)}")
        else:
            formatted_cells.append(f"{' ' * padding}{cell}")
    return "| " + " | ".join(formatted_cells) + " |"
```

</details>

## 🔧 Function `_format_table_separator`

```python
def _format_table_separator(column_widths: list[int], alignments: list[str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _format_table_separator(column_widths: list[int], alignments: list[str]) -> str:
    separators: list[str] = []
    for index, width in enumerate(column_widths):
        align = alignments[index] if index < len(alignments) else "---"
        core = align if align in {":--", ":-:", "--:"} else "---"
        if len(core) < width:
            if core == ":--":
                core = ":" + "-" * (width - 1)
            elif core == "--:":
                core = "-" * (width - 1) + ":"
            elif core == ":-:":
                core = ":" + "-" * max(width - 2, 1) + ":"
            else:
                core = "-" * width
        separators.append(core)
    return "| " + " | ".join(separators) + " |"
```

</details>

## 🔧 Function `_is_spurious_table_row`

```python
def _is_spurious_table_row(cells: list[str], width: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_spurious_table_row(cells: list[str], width: int) -> bool:
    min_spurious_width = 3
    if width < min_spurious_width or not cells[0].strip():
        return False
    if any(cells[index].strip() for index in range(1, width)):
        return False
    return looks_like_prose_table_row(cells[0].strip())
```

</details>

## 🔧 Function `_parse_table_row_cells`

```python
def _parse_table_row_cells(line: str) -> list[str] | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _parse_table_row_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]
```

</details>

## 🔧 Function `_parse_table_rows`

```python
def _parse_table_rows(text: str) -> list[list[str]]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _parse_table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        cells = _parse_table_row_cells(line)
        if cells is not None:
            rows.append(cells)
    return rows
```

</details>

## 🔧 Function `_prefer_source_table_block`

```python
def _prefer_source_table_block(source_text: str, formatted_text: str) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _prefer_source_table_block(source_text: str, formatted_text: str) -> str | None:
    source_rows = _parse_table_rows(source_text)
    formatted_rows = _parse_table_rows(formatted_text)
    if not source_rows or source_rows != formatted_rows:
        return None
    if len(source_text) >= len(formatted_text):
        return source_text if source_text.endswith("\n") else f"{source_text}\n"
    return None
```

</details>

## 🔧 Function `_render_table`

```python
def _render_table(tokens: list[Token], index: int) -> tuple[str, int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_table(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
    source_lines: list[str] | None = None,
) -> tuple[str, int]:
    close_index = _find_close(tokens, index, "table_close")
    rows: list[list[str]] = []
    is_header = False
    alignments: list[str] = []
    cell_alignments: list[str] = []
    row_index = index + 1
    while row_index < close_index:
        token = tokens[row_index]
        if token.type == "thead_open":
            is_header = True
            row_index += 1
            continue
        if token.type in {"thead_close", "tbody_open", "tbody_close"}:
            if token.type == "thead_close":
                is_header = False
            row_index += 1
            continue
        if token.type == "tr_open":
            row_close = _find_close(tokens, row_index, "tr_close")
            cells: list[str] = []
            cell_index = row_index + 1
            while cell_index < row_close:
                if tokens[cell_index].type in {"th_open", "td_open"}:
                    style = str(tokens[cell_index].attrGet("style") or "")
                    if "text-align:center" in style:
                        cell_alignments.append("center")
                    elif "text-align:right" in style:
                        cell_alignments.append("right")
                    elif "text-align:left" in style:
                        cell_alignments.append("left")
                    else:
                        cell_alignments.append("default")
                    inline = tokens[cell_index + 1]
                    cells.append(
                        _render_inline(
                            inline.children or [], in_table=True, options=options, hard_break_styles=hard_break_styles
                        )
                    )
                    cell_index += 3
                else:
                    cell_index += 1
            if is_header and not alignments:
                alignments = [_alignment_separator(align) for align in cell_alignments]
                rows.append(cells)
                rows.append(alignments)
            else:
                rows.append(cells)
            row_index = row_close + 1
            continue
        row_index += 1
    if not rows:
        return "", close_index + 1
    width = len(rows[0])
    header = rows[0]
    body_rows = rows[2:] if len(rows) > 1 else []
    trailing_paragraphs: list[str] = []
    filtered_body_rows: list[list[str]] = []
    for row in body_rows:
        padded_row = row + [""] * (width - len(row))
        if _is_spurious_table_row(padded_row[:width], width):
            trailing_paragraphs.append(padded_row[0].strip())
        else:
            filtered_body_rows.append(padded_row[:width])
    width_rows = [[_escape_table_cell(cell) for cell in row] for row in [header, *filtered_body_rows]]
    column_widths = _table_column_widths(width_rows, width)
    align_row = rows[1] if len(rows) > 1 else ["---"] * width
    lines = [
        _format_table_row(header, column_widths, align_row),
        _format_table_separator(column_widths, align_row),
        *(_format_table_row(row, column_widths, align_row, strip_trailing_empty=True) for row in filtered_body_rows),
    ]
    result = "\n".join(lines) + "\n"
    if trailing_paragraphs:
        result += "\n".join(f"{paragraph}\n" for paragraph in trailing_paragraphs)
    table_map = tokens[index].map
    if source_lines and table_map:
        source_text = "\n".join(source_lines[table_map[0] : table_map[1]])
        preferred = _prefer_source_table_block(source_text, result)
        if preferred is not None:
            return preferred, close_index + 1
    return result, close_index + 1
```

</details>

## 🔧 Function `_table_cell_display_width`

```python
def _table_cell_display_width(cell: str) -> int
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _table_cell_display_width(cell: str) -> int:
    escaped_pipe_width = sum(len(match.group(1)) // 2 for match in re.finditer(r"(\\+)\|", cell))
    return text_display_width(cell) - escaped_pipe_width
```

</details>

## 🔧 Function `_table_column_widths`

```python
def _table_column_widths(rows: list[list[str]], width: int) -> list[int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _table_column_widths(rows: list[list[str]], width: int) -> list[int]:
    column_widths = [3] * width
    for row in rows:
        for index, cell in enumerate(row[:width]):
            column_widths[index] = max(column_widths[index], _table_cell_display_width(cell), 3)
    return column_widths
```

</details>
