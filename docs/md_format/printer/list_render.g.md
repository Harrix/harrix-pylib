---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `list_render.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `_align_ordered_list_prefix`](#-function-_align_ordered_list_prefix)
- [🔧 Function `_bullet_item_leading_spaces`](#-function-_bullet_item_leading_spaces)
- [🔧 Function `_direct_list_item_count`](#-function-_direct_list_item_count)
- [🔧 Function `_is_indented_source_codeblock`](#-function-_is_indented_source_codeblock)
- [🔧 Function `_is_list_block`](#-function-_is_list_block)
- [🔧 Function `_line_has_task_checkbox`](#-function-_line_has_task_checkbox)
- [🔧 Function `_list_followed_by_indented_codeblock`](#-function-_list_followed_by_indented_codeblock)
- [🔧 Function `_list_has_nested_bullets`](#-function-_list_has_nested_bullets)
- [🔧 Function `_list_is_loose`](#-function-_list_is_loose)
- [🔧 Function `_list_item_checkbox`](#-function-_list_item_checkbox)
- [🔧 Function `_list_item_followed_by_indented_codeblock`](#-function-_list_item_followed_by_indented_codeblock)
- [🔧 Function `_list_item_has_extra_blocks`](#-function-_list_item_has_extra_blocks)
- [🔧 Function `_list_item_is_loose`](#-function-_list_item_is_loose)
- [🔧 Function `_list_item_nested_list_index`](#-function-_list_item_nested_list_index)
- [🔧 Function `_list_item_source_line`](#-function-_list_item_source_line)
- [🔧 Function `_list_marker_prefix`](#-function-_list_marker_prefix)
- [🔧 Function `_list_source_indent`](#-function-_list_source_indent)
- [🔧 Function `_ordered_item_leading_spaces`](#-function-_ordered_item_leading_spaces)
- [🔧 Function `_ordered_list_leading_spaces`](#-function-_ordered_list_leading_spaces)
- [🔧 Function `_ordered_list_marker_target_width`](#-function-_ordered_list_marker_target_width)
- [🔧 Function `_ordered_marker_delimiter`](#-function-_ordered_marker_delimiter)
- [🔧 Function `_ordered_marker_specs_from_source`](#-function-_ordered_marker_specs_from_source)
- [🔧 Function `_ordered_sibling_gap_before_item`](#-function-_ordered_sibling_gap_before_item)
- [🔧 Function `_render_list`](#-function-_render_list)
- [🔧 Function `_render_list_item_lines`](#-function-_render_list_item_lines)
- [🔧 Function `_should_preserve_list_marker_spacing`](#-function-_should_preserve_list_marker_spacing)
- [🔧 Function `_star_marker_becomes_dash`](#-function-_star_marker_becomes_dash)
- [🔧 Function `_top_level_list_base_indent`](#-function-_top_level_list_base_indent)
- [🔧 Function `_top_level_list_single_item_is_simple`](#-function-_top_level_list_single_item_is_simple)
- [🔧 Function `_wrap_list_item_prose`](#-function-_wrap_list_item_prose)

</details>

## 🔧 Function `_align_ordered_list_prefix`

```python
def _align_ordered_list_prefix(raw_prefix: str, tab_width: int = 2) -> str
```

Apply Prettier's alignListPrefix to a raw ordered-list prefix.

<details>
<summary>Code:</summary>

```python
def _align_ordered_list_prefix(raw_prefix: str, tab_width: int = 2) -> str:
    rest_spaces = len(raw_prefix) % tab_width
    additional = 0 if rest_spaces == 0 else tab_width - rest_spaces
    if additional >= 4:
        additional = 0
    return raw_prefix + " " * additional
```

</details>

## 🔧 Function `_bullet_item_leading_spaces`

```python
def _bullet_item_leading_spaces(tokens: list[Token], item_index: int, source_lines: list[str] | None) -> int
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _bullet_item_leading_spaces(tokens: list[Token], item_index: int, source_lines: list[str] | None) -> int:
    line = _list_item_source_line(tokens, item_index, source_lines)
    if not line:
        return 1
    checkbox_bullet_match = _CHECKBOX_BULLET_SPACES_RE.match(line)
    if checkbox_bullet_match:
        return len(checkbox_bullet_match.group(2))
    checkbox_match = _CHECKBOX_LEADING_SPACES_RE.match(line)
    if checkbox_match:
        return len(checkbox_match.group(2))
    bullet_match = _BULLET_LEADING_SPACES_RE.match(line)
    if bullet_match:
        return len(bullet_match.group(2))
    return 1
```

</details>

## 🔧 Function `_direct_list_item_count`

```python
def _direct_list_item_count(tokens: list[Token], list_index: int, close_index: int) -> int
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _direct_list_item_count(tokens: list[Token], list_index: int, close_index: int) -> int:
    count = 0
    child_index = list_index + 1
    while child_index < close_index:
        if tokens[child_index].type == "list_item_open":
            count += 1
            child_index = _find_close(tokens, child_index, "list_item_close") + 1
            continue
        child_index += 1
    return count
```

</details>

## 🔧 Function `_is_indented_source_codeblock`

```python
def _is_indented_source_codeblock(token: Token, source_lines: list[str] | None) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_indented_source_codeblock(token: Token, source_lines: list[str] | None) -> bool:
    if token.type != "code_block":
        return False
    if not source_lines:
        return True
    code_map = token.map
    if not code_map:
        return True
    line = source_lines[code_map[0]]
    return bool(line.startswith("    ") or line.startswith("\t") or line[:1] == " ")
```

</details>

## 🔧 Function `_is_list_block`

```python
def _is_list_block(block: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _is_list_block(block: str) -> bool:
    for line in block.splitlines():
        if not line.strip():
            continue
        return is_list_line(line)
    return False
```

</details>

## 🔧 Function `_line_has_task_checkbox`

```python
def _line_has_task_checkbox(line: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _line_has_task_checkbox(line: str) -> bool:
    return bool(re.search(r"\[[ xX]\]", line)) or "HSKMDFMTTASK" in line
```

</details>

## 🔧 Function `_list_followed_by_indented_codeblock`

```python
def _list_followed_by_indented_codeblock(tokens: list[Token], list_close_index: int, source_lines: list[str] | None) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_followed_by_indented_codeblock(
    tokens: list[Token], list_close_index: int, source_lines: list[str] | None
) -> bool:
    next_index = list_close_index + 1
    if next_index >= len(tokens):
        return False
    return _is_indented_source_codeblock(tokens[next_index], source_lines)
```

</details>

## 🔧 Function `_list_has_nested_bullets`

```python
def _list_has_nested_bullets(tokens: list[Token], start: int, end: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_has_nested_bullets(tokens: list[Token], start: int, end: int) -> bool:
    depth = 0
    for index in range(start, end):
        token = tokens[index]
        if token.type == "bullet_list_open":
            if depth > 0:
                return True
            depth += 1
        elif token.type == "bullet_list_close":
            depth -= 1
    return False
```

</details>

## 🔧 Function `_list_is_loose`

```python
def _list_is_loose(tokens: list[Token], index: int, close_index: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_is_loose(tokens: list[Token], index: int, close_index: int) -> bool:
    item_ranges: list[tuple[int, int]] = []
    item_index = index + 1
    while item_index < close_index:
        if tokens[item_index].type != "list_item_open":
            item_index += 1
            continue
        item_close = _find_close(tokens, item_index, "list_item_close")
        item_map = tokens[item_index].map
        close_map = tokens[item_close].map
        if item_map and close_map:
            item_ranges.append((item_map[0], close_map[1]))
        if _list_item_is_loose(tokens, item_index, item_close):
            return True
        item_index = item_close + 1
    for sibling_index in range(1, len(item_ranges)):
        if item_ranges[sibling_index][0] > item_ranges[sibling_index - 1][1]:
            return True
    return False
```

</details>

## 🔧 Function `_list_item_checkbox`

```python
def _list_item_checkbox(tokens: list[Token], item_open_index: int) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_item_checkbox(tokens: list[Token], item_open_index: int) -> str | None:
    checked = tokens[item_open_index].attrGet("checked")
    if checked is None:
        return None
    return "[x] " if checked else "[ ] "
```

</details>

## 🔧 Function `_list_item_followed_by_indented_codeblock`

```python
def _list_item_followed_by_indented_codeblock(tokens: list[Token], item_close: int, source_lines: list[str] | None) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_item_followed_by_indented_codeblock(
    tokens: list[Token], item_close: int, source_lines: list[str] | None
) -> bool:
    next_index = item_close + 1
    if next_index >= len(tokens):
        return False
    next_token = tokens[next_index]
    if next_token.type == "code_block":
        return _is_indented_source_codeblock(next_token, source_lines)
    if next_token.type in {"bullet_list_close", "ordered_list_close"}:
        return _list_followed_by_indented_codeblock(tokens, next_index, source_lines)
    return False
```

</details>

## 🔧 Function `_list_item_has_extra_blocks`

```python
def _list_item_has_extra_blocks(tokens: list[Token], item_index: int, item_close: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_item_has_extra_blocks(tokens: list[Token], item_index: int, item_close: int) -> bool:
    paragraph_count = 0
    child_index = item_index + 1
    while child_index < item_close:
        child = tokens[child_index]
        if child.type == "paragraph_open":
            paragraph_count += 1
            child_index += 3
            continue
        if child.type in {"bullet_list_open", "ordered_list_open"}:
            close_type = "ordered_list_close" if child.type == "ordered_list_open" else "bullet_list_close"
            child_index = _find_close(tokens, child_index, close_type) + 1
            continue
        if child.type in {"code_block", "fence"}:
            return True
        if child.type == "blockquote_open":
            child_index = _find_close(tokens, child_index, "blockquote_close") + 1
            continue
        child_index += 1
    return paragraph_count > 1
```

</details>

## 🔧 Function `_list_item_is_loose`

```python
def _list_item_is_loose(tokens: list[Token], item_open_index: int, item_close_index: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_item_is_loose(tokens: list[Token], item_open_index: int, item_close_index: int) -> bool:
    paragraph_count = 0
    nested_list_count = 0
    previous_block_end: int | None = None
    child_index = item_open_index + 1
    while child_index < item_close_index:
        token = tokens[child_index]
        if token.map and previous_block_end is not None and token.map[0] > previous_block_end:
            return True
        if token.type == "paragraph_open":
            paragraph_count += 1
            paragraph_close = child_index + 2
            if tokens[paragraph_close].map:
                previous_block_end = tokens[paragraph_close].map[1]
            child_index += 3
            continue
        if token.type in {"bullet_list_open", "ordered_list_open"}:
            nested_list_count += 1
            nested_close = _find_close(
                tokens,
                child_index,
                "ordered_list_close" if token.type == "ordered_list_open" else "bullet_list_close",
            )
            if tokens[nested_close].map:
                previous_block_end = tokens[nested_close].map[1]
            child_index = nested_close + 1
            continue
        if token.type == "html_block":
            if token.map:
                previous_block_end = token.map[1]
            child_index += 1
            continue
        if token.type in {
            "fence",
            "code_block",
            "blockquote_open",
            "table_open",
            "heading_open",
            "hr",
            "math_block",
            "math_block_label",
        }:
            return True
        _, child_index = _render_block(tokens, child_index)
        return True
    if paragraph_count > 1:
        return True
    block_count = paragraph_count + nested_list_count
    if block_count <= 1:
        return False
    return block_count != paragraph_count + nested_list_count
```

</details>

## 🔧 Function `_list_item_nested_list_index`

```python
def _list_item_nested_list_index(tokens: list[Token], item_index: int, item_close: int) -> int | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_item_nested_list_index(tokens: list[Token], item_index: int, item_close: int) -> int | None:
    child_index = item_index + 1
    while child_index < item_close:
        if tokens[child_index].type in {"bullet_list_open", "ordered_list_open"}:
            return child_index
        if tokens[child_index].type.endswith("_open"):
            child_index = _find_close(tokens, child_index, tokens[child_index].type.replace("_open", "_close")) + 1
            continue
        child_index += 1
    return None
```

</details>

## 🔧 Function `_list_item_source_line`

```python
def _list_item_source_line(tokens: list[Token], item_index: int, source_lines: list[str] | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_item_source_line(tokens: list[Token], item_index: int, source_lines: list[str] | None) -> str | None:
    if not source_lines:
        return None
    tok_map = tokens[item_index].map
    if not tok_map:
        return None
    line_index = tok_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return None
    return source_lines[line_index]
```

</details>

## 🔧 Function `_list_marker_prefix`

```python
def _list_marker_prefix(marker: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _list_marker_prefix(marker: str, *, align: bool = False, content_spaces: int | None = None) -> str:
    if content_spaces is not None:
        return f"{marker}{' ' * content_spaces}"
    if align and marker.endswith((".", ")")):
        return f"{marker}{' ' * max(1, 4 - len(marker))}"
    return f"{marker} "
```

</details>

## 🔧 Function `_list_source_indent`

```python
def _list_source_indent(tokens: list[Token], index: int, source_lines: list[str] | None) -> int
```

Return the leading-space indent of the list as it appears in source.

<details>
<summary>Code:</summary>

```python
def _list_source_indent(tokens: list[Token], index: int, source_lines: list[str] | None) -> int:
    if not source_lines:
        return 0
    tok_map = tokens[index].map
    if not tok_map:
        return 0
    line_index = tok_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return 0
    line = source_lines[line_index]
    return len(line) - len(line.lstrip())
```

</details>

## 🔧 Function `_ordered_item_leading_spaces`

```python
def _ordered_item_leading_spaces(tokens: list[Token], item_index: int, source_lines: list[str] | None) -> int
```

Return spaces between ordered marker and content for a single list item.

<details>
<summary>Code:</summary>

```python
def _ordered_item_leading_spaces(tokens: list[Token], item_index: int, source_lines: list[str] | None) -> int:
    if not source_lines:
        return 1
    tok_map = tokens[item_index].map
    if not tok_map:
        return 1
    line_index = tok_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return 1
    m = _ORDERED_LEADING_SPACES_RE.match(source_lines[line_index])
    return len(m.group(1)) if m else 1
```

</details>

## 🔧 Function `_ordered_list_leading_spaces`

```python
def _ordered_list_leading_spaces(tokens: list[Token], index: int, source_lines: list[str] | None) -> int
```

Return the number of spaces between the ordered marker and its content in source.

<details>
<summary>Code:</summary>

```python
def _ordered_list_leading_spaces(tokens: list[Token], index: int, source_lines: list[str] | None) -> int:
    if not source_lines:
        return 1
    tok_map = tokens[index].map
    if not tok_map:
        return 1
    line_index = tok_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return 1
    m = _ORDERED_LEADING_SPACES_RE.match(source_lines[line_index])
    return len(m.group(1)) if m else 1
```

</details>

## 🔧 Function `_ordered_list_marker_target_width`

```python
def _ordered_list_marker_target_width(tokens: list[Token], index: int, close_index: int) -> int | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _ordered_list_marker_target_width(
    tokens: list[Token],
    index: int,
    close_index: int,
    *,
    list_base_indent: int,
    source_lines: list[str] | None,
) -> int | None:
    target_width: int | None = None
    item_index = index + 1
    while item_index < close_index:
        if tokens[item_index].type != "list_item_open":
            item_index += 1
            continue
        item_close = _find_close(tokens, item_index, "list_item_close")
        nested_index = _list_item_nested_list_index(tokens, item_index, item_close)
        if nested_index is not None and source_lines:
            nested_indent = _list_source_indent(tokens, nested_index, source_lines)
            nested_target = nested_indent + 1
            target_width = nested_target if target_width is None else max(target_width, nested_target)
        item_index = item_close + 1
    if target_width is None:
        return None
    return max(target_width, list_base_indent + 2)
```

</details>

## 🔧 Function `_ordered_marker_delimiter`

```python
def _ordered_marker_delimiter(line: str) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _ordered_marker_delimiter(line: str) -> str | None:
    match = re.match(r"^\s*\d+([.)])\s+", line)
    return match.group(1) if match else None
```

</details>

## 🔧 Function `_ordered_marker_specs_from_source`

```python
def _ordered_marker_specs_from_source(tokens: list[Token], index: int, close_index: int, source_lines: list[str] | None) -> list[tuple[int, str]]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _ordered_marker_specs_from_source(
    tokens: list[Token], index: int, close_index: int, source_lines: list[str] | None
) -> list[tuple[int, str]]:
    if not source_lines:
        return []
    markers: list[tuple[int, str]] = []
    item_index = index + 1
    while item_index < close_index:
        if tokens[item_index].type != "list_item_open":
            item_index += 1
            continue
        tok_map = tokens[item_index].map
        if tok_map and 0 <= tok_map[0] < len(source_lines):
            m = re.match(r"^\s*(\d+)([.)])\s+", source_lines[tok_map[0]])
            if m:
                markers.append((int(m.group(1)), m.group(2)))
        item_index = _find_close(tokens, item_index, "list_item_close") + 1
    return markers
```

</details>

## 🔧 Function `_ordered_sibling_gap_before_item`

```python
def _ordered_sibling_gap_before_item(tokens: list[Token], item_index: int, prev_item_index: int, source_lines: list[str] | None) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _ordered_sibling_gap_before_item(
    tokens: list[Token],
    item_index: int,
    prev_item_index: int,
    source_lines: list[str] | None,
) -> bool:
    if not source_lines:
        return False
    prev_line = _list_item_source_line(tokens, prev_item_index, source_lines)
    curr_line = _list_item_source_line(tokens, item_index, source_lines)
    if not prev_line or not curr_line:
        return False
    if _ordered_marker_delimiter(curr_line) != ".":
        return False
    if _ordered_marker_delimiter(prev_line) != ".":
        return False
    return not _line_has_task_checkbox(prev_line) and _line_has_task_checkbox(curr_line)
```

</details>

## 🔧 Function `_render_list`

```python
def _render_list(tokens: list[Token], index: int) -> tuple[str, int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_list(
    tokens: list[Token],
    index: int,
    *,
    ordered: bool,
    options: FormatOptions,
    task_list_markers: list[TaskListMarker],
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
    normalize_star_to_dash: bool = False,
    list_depth: int = 0,
    in_blockquote: bool = False,
    parent_is_ordered: bool = False,
    parent_is_aligned: bool = False,
    forced_base_indent: int | None = None,
) -> tuple[str, int]:
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    close_type = "ordered_list_close" if ordered else "bullet_list_close"
    close_index = _find_close(tokens, index, close_type)
    layout = layouts.pop(0) if layouts else None
    loose = _list_is_loose(tokens, index, close_index)
    if layout is not None and not any(layout.gaps_before_item) and not any(layout.loose_items):
        # The token stream can appear loose only because of blank lines auto-inserted
        # around code-block placeholders; trust the layout when it says the list is tight.
        loose = False
    if forced_base_indent is not None:
        list_base_indent = forced_base_indent
    elif list_depth == 0 and source_lines:
        list_base_indent = _top_level_list_base_indent(tokens, index, close_index, source_lines)
    elif list_depth > 0 and source_lines:
        src_indent = _list_source_indent(tokens, index, source_lines)
        if ordered and src_indent > 0:
            list_base_indent = src_indent
        elif not ordered and src_indent == 0 and not in_blockquote:
            # Inline nested bullet immediately after parent marker (e.g. "1. - item").
            list_base_indent = 0
        elif not ordered and parent_is_ordered and src_indent > 0:
            list_base_indent = src_indent
        else:
            list_base_indent = list_depth * 2
    else:
        list_base_indent = list_depth * 2
    lines: list[str] = []
    source_markers: list[int] = []
    source_marker_delimiters: list[str] = []
    bullet_markers: list[str] = []
    if ordered:
        if source_lines:
            marker_specs = _ordered_marker_specs_from_source(tokens, index, close_index, source_lines)
            source_markers = [number for number, _ in marker_specs]
            source_marker_delimiters = [delimiter for _, delimiter in marker_specs]
        if not source_markers and ordered_list_marker_groups:
            source_markers = list(ordered_list_marker_groups.pop(0))
            source_marker_delimiters = ["."] * len(source_markers)
    elif not ordered and bullet_list_marker_groups:
        bullet_markers = bullet_list_marker_groups.pop(0)
    has_nested_bullets = _list_has_nested_bullets(tokens, index + 1, close_index)
    has_following_nested_dashes = _star_marker_becomes_dash(
        bullet_markers,
        bullet_list_marker_groups,
        has_nested_bullets=has_nested_bullets,
    )
    ordered_marker_target_width = None
    if ordered and source_lines and _list_followed_by_indented_codeblock(tokens, close_index, source_lines):
        ordered_marker_target_width = _ordered_list_marker_target_width(
            tokens, index, close_index, list_base_indent=list_base_indent, source_lines=source_lines
        )
    item_index = index + 1
    rendered_item_count = 0
    prev_item_index: int | None = None
    while item_index < close_index:
        if tokens[item_index].type != "list_item_open":
            item_index += 1
            continue
        item_close = _find_close(tokens, item_index, "list_item_close")
        checkbox = _list_item_checkbox(tokens, item_index)
        if ordered:
            delimiter = (
                source_marker_delimiters[rendered_item_count]
                if rendered_item_count < len(source_marker_delimiters)
                else "."
            )
            marker = f"{ordered_list_item_number(source_markers, rendered_item_count)}{delimiter}"
        elif list_depth > 0:
            marker = "-"
        elif rendered_item_count < len(bullet_markers):
            source_marker = bullet_markers[rendered_item_count]
            if (canonicalize_bullets and source_marker == "-") or (
                has_following_nested_dashes and source_marker == "*"
            ):
                marker = "-"
            else:
                marker = _normalize_bullet_marker(source_marker, normalize_star_to_dash=normalize_star_to_dash)
        else:
            marker = "-"
        item_leading_spaces = (
            _ordered_item_leading_spaces(tokens, item_index, source_lines)
            if ordered
            else _bullet_item_leading_spaces(tokens, item_index, source_lines)
        )
        preserve_marker_spacing = _should_preserve_list_marker_spacing(
            tokens,
            item_index,
            item_close,
            marker_spaces=item_leading_spaces,
            source_lines=source_lines,
            list_close_index=close_index,
        )
        if checkbox:
            marker = f"- {checkbox}".rstrip()
        if ordered and item_leading_spaces > 1 and not preserve_marker_spacing:
            if list_depth == 0 or not parent_is_ordered:
                item_is_aligned = True
            else:
                item_is_aligned = parent_is_aligned
        else:
            item_is_aligned = False
        marker_content_spaces = item_leading_spaces if preserve_marker_spacing else None
        if checkbox and preserve_marker_spacing and item_leading_spaces > 1:
            marker_content_spaces = None
            box = checkbox.strip()
            marker = f"-{' ' * item_leading_spaces}{box}"
        if ordered and not preserve_marker_spacing and ordered_marker_target_width is not None and not checkbox:
            marker_content_spaces = max(1, ordered_marker_target_width - list_base_indent - len(marker))
            item_is_aligned = False
        marker_prefix_only = _list_marker_prefix(
            marker,
            align=item_is_aligned,
            content_spaces=marker_content_spaces,
        )
        nested_base_indent = list_base_indent + len(marker_prefix_only)
        item_lines: list[str] = []
        child_index = item_index + 1
        while child_index < item_close:
            if tokens[child_index].type in {"bullet_list_open", "ordered_list_open"}:
                nested_inline = False
                if source_lines:
                    nested_map = tokens[child_index].map
                    parent_map = tokens[item_index].map
                    if nested_map and parent_map and nested_map[0] == parent_map[0]:
                        nested_inline = True
                nested_forced_indent = list_base_indent if nested_inline else nested_base_indent
                nested, child_index = _render_list(
                    tokens,
                    child_index,
                    ordered=tokens[child_index].type == "ordered_list_open",
                    options=options,
                    task_list_markers=task_list_markers,
                    ordered_list_marker_groups=ordered_list_marker_groups,
                    bullet_list_marker_groups=bullet_list_marker_groups,
                    hard_break_styles=break_styles,
                    list_layouts=layouts,
                    source_lines=source_lines,
                    canonicalize_bullets=canonicalize_bullets,
                    normalize_star_to_dash=normalize_star_to_dash,
                    list_depth=list_depth + 1,
                    in_blockquote=in_blockquote,
                    parent_is_ordered=ordered or parent_is_ordered,
                    parent_is_aligned=item_is_aligned if ordered else parent_is_aligned,
                    forced_base_indent=nested_forced_indent,
                )
                item_lines.append(nested.rstrip("\n"))
            else:
                from harrix_pylib.md_format.printer.block import _render_block

                chunk, child_index = _render_block(
                    tokens,
                    child_index,
                    options=options,
                    wrap_paragraph=False,
                    task_list_markers=task_list_markers,
                    ordered_list_marker_groups=ordered_list_marker_groups,
                    bullet_list_marker_groups=bullet_list_marker_groups,
                    hard_break_styles=break_styles,
                    list_layouts=layouts,
                    source_lines=source_lines,
                    canonicalize_bullets=canonicalize_bullets,
                    normalize_star_to_dash=normalize_star_to_dash,
                    preserve_source_line=False,
                    in_list_item=True,
                    in_blockquote=in_blockquote,
                )
                if chunk:
                    item_lines.append(chunk.rstrip("\n"))
        task_entry = task_list_entry_for_text(item_lines[0], task_list_markers) if item_lines else None
        if task_entry:
            task_marker, task_meta = task_entry
            if task_meta.marker_spaces > item_leading_spaces:
                item_leading_spaces = task_meta.marker_spaces
                preserve_marker_spacing = _should_preserve_list_marker_spacing(
                    tokens,
                    item_index,
                    item_close,
                    marker_spaces=item_leading_spaces,
                    source_lines=source_lines,
                    list_close_index=close_index,
                )
                marker_content_spaces = item_leading_spaces if preserve_marker_spacing else None
            item_lines[0] = f"{task_marker}{strip_task_placeholder(item_lines[0])}".rstrip()
        if rendered_item_count > 0:
            gap = False
            if ordered and source_lines and prev_item_index is not None:
                gap = _ordered_sibling_gap_before_item(tokens, item_index, prev_item_index, source_lines)
                if (
                    not gap
                    and layout
                    and rendered_item_count < len(layout.gaps_before_item)
                    and layout.gaps_before_item[rendered_item_count]
                ):
                    prev_line = _list_item_source_line(tokens, prev_item_index, source_lines)
                    curr_line = _list_item_source_line(tokens, item_index, source_lines)
                    if (
                        prev_line
                        and curr_line
                        and _ordered_marker_delimiter(prev_line) == "."
                        and _ordered_marker_delimiter(curr_line) == "."
                    ):
                        gap = True
            elif (
                not ordered
                and (
                    (
                        layout
                        and rendered_item_count < len(layout.gaps_before_item)
                        and layout.gaps_before_item[rendered_item_count]
                    )
                    or (loose and not in_blockquote)
                )
            ) or (
                ordered
                and (
                    (
                        layout
                        and rendered_item_count < len(layout.gaps_before_item)
                        and layout.gaps_before_item[rendered_item_count]
                    )
                    or (loose and not in_blockquote)
                )
            ):
                gap = True
            if gap:
                lines.append("")
        if layout and rendered_item_count < len(layout.loose_items):
            item_loose = layout.loose_items[rendered_item_count]
        else:
            item_loose = _list_item_is_loose(tokens, item_index, item_close)
        lines.extend(
            _render_list_item_lines(
                item_lines,
                marker=marker,
                loose=item_loose,
                options=options,
                base_indent=list_base_indent,
                in_blockquote=in_blockquote,
                align_prefix=item_is_aligned,
                marker_content_spaces=marker_content_spaces,
            )
        )
        rendered_item_count += 1
        prev_item_index = item_index
        item_index = item_close + 1
    return "\n".join(lines) + "\n", close_index + 1
```

</details>

## 🔧 Function `_render_list_item_lines`

```python
def _render_list_item_lines(item_lines: list[str]) -> list[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_list_item_lines(
    item_lines: list[str],
    *,
    marker: str,
    loose: bool,
    options: FormatOptions,
    base_indent: int = 0,
    in_blockquote: bool = False,
    align_prefix: bool = False,
    marker_content_spaces: int | None = None,
) -> list[str]:
    if not item_lines:
        return [(" " * base_indent) + marker]

    align_ordered_marker = align_prefix or (
        marker.endswith((".", ")")) and any(block.lstrip().startswith("<") for block in item_lines)
    )
    prefix = (" " * base_indent) + _list_marker_prefix(
        marker,
        align=align_ordered_marker,
        content_spaces=marker_content_spaces,
    )
    task_item = bool(item_lines and item_lines[0].startswith(("[ ] ", "[x] ")))
    indent = " " * len(prefix)
    first_continuation = " " * (len(prefix) + 4) if task_item else indent
    if marker.startswith("- ["):
        continuation_indent = " " * (base_indent + 2)
    elif base_indent == 0 or marker.endswith(".") or marker.endswith(")"):
        continuation_indent = " " * len(prefix)
    else:
        continuation_indent = " " * (base_indent + 2)
    rendered: list[str] = []
    for block_index, block in enumerate(item_lines):
        if (
            block_index == 0
            and options.prose_wrap == "always"
            and "\n" not in block
            and "# ignore:" not in block
            and ("](" not in block or ") - " in block)
            and "\\_" not in block
            and not _is_block_marker_line(block)
            and _should_wrap_prose(block, prefix=prefix, width=options.print_width)
        ):
            rendered.extend(
                _wrap_list_item_prose(
                    block,
                    prefix=prefix,
                    continuation=first_continuation,
                    width=options.print_width,
                )
            )
            continue
        block_lines = block.splitlines()
        if block_index == 0:
            rendered.append(prefix + block_lines[0])
            for continuation_line in block_lines[1:]:
                stripped = continuation_line.lstrip()
                line_indent = len(continuation_line) - len(stripped)
                if not in_blockquote and LIST_MARKER_LINE_RE.match(stripped) and line_indent >= len(prefix):
                    rendered.append(continuation_line)
                else:
                    rendered.append(f"{first_continuation}{continuation_line}")
            continue
        if block_index > 0 and not in_blockquote:
            previous_block = item_lines[block_index - 1]
            needs_gap = False
            if loose:
                if _is_list_block(block) and _is_list_block(previous_block):
                    needs_gap = False
                else:
                    needs_gap = not (_is_list_block(block) and previous_block.lstrip().startswith(">"))
            elif _is_list_block(previous_block) and not _is_list_block(block):
                needs_gap = not previous_block.lstrip().startswith(">")
            if needs_gap:
                rendered.append("")
        if _is_list_block(block):
            rendered.extend(block.splitlines())
        elif (
            options.prose_wrap == "always"
            and "\n" not in block
            and not _is_block_marker_line(block)
            and _should_wrap_prose(block, prefix=continuation_indent, width=options.print_width)
        ):
            rendered.extend(
                wrap_prose(
                    block,
                    width=options.print_width,
                    prefix=continuation_indent,
                    continuation=continuation_indent,
                ).split("\n")
            )
        else:
            rendered.extend(f"{continuation_indent}{continuation_line}" for continuation_line in block_lines)
    return rendered
```

</details>

## 🔧 Function `_should_preserve_list_marker_spacing`

```python
def _should_preserve_list_marker_spacing(tokens: list[Token], item_index: int, item_close: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _should_preserve_list_marker_spacing(
    tokens: list[Token],
    item_index: int,
    item_close: int,
    *,
    marker_spaces: int,
    source_lines: list[str] | None,
    list_close_index: int | None = None,
) -> bool:
    if marker_spaces <= 1:
        return False
    list_followed = list_close_index is not None and _list_followed_by_indented_codeblock(
        tokens, list_close_index, source_lines
    )
    if _list_item_has_extra_blocks(tokens, item_index, item_close) and not list_followed:
        return False
    if _list_item_followed_by_indented_codeblock(tokens, item_close, source_lines):
        return True
    return list_followed
```

</details>

## 🔧 Function `_star_marker_becomes_dash`

```python
def _star_marker_becomes_dash(bullet_markers: list[str], remaining_groups: list[list[str]]) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _star_marker_becomes_dash(
    bullet_markers: list[str],
    remaining_groups: list[list[str]],
    *,
    has_nested_bullets: bool,
) -> bool:
    if has_nested_bullets:
        return True
    nested_dash_groups = sum(
        1
        for offset in range(min(len(bullet_markers), len(remaining_groups)))
        if len(remaining_groups[offset]) == 1 and remaining_groups[offset][0] == "-"
    )
    if nested_dash_groups > 0:
        return True
    return len(bullet_markers) == 1
```

</details>

## 🔧 Function `_top_level_list_base_indent`

```python
def _top_level_list_base_indent(tokens: list[Token], index: int, close_index: int, source_lines: list[str] | None) -> int
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _top_level_list_base_indent(
    tokens: list[Token], index: int, close_index: int, source_lines: list[str] | None
) -> int:
    if not source_lines:
        return 0
    src_indent = _list_source_indent(tokens, index, source_lines)
    item_count = _direct_list_item_count(tokens, index, close_index)
    list_followed = _list_followed_by_indented_codeblock(tokens, close_index, source_lines)
    if src_indent > 0 and item_count > 1:
        return src_indent
    if src_indent >= 3 and item_count == 1 and _top_level_list_single_item_is_simple(tokens, index, close_index):
        return src_indent
    if src_indent > 0 and item_count == 1 and list_followed and src_indent < 3:
        return src_indent
    return 0
```

</details>

## 🔧 Function `_top_level_list_single_item_is_simple`

```python
def _top_level_list_single_item_is_simple(tokens: list[Token], list_index: int, close_index: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _top_level_list_single_item_is_simple(tokens: list[Token], list_index: int, close_index: int) -> bool:
    for item_index in range(list_index + 1, close_index):
        if tokens[item_index].type != "list_item_open":
            continue
        item_close = _find_close(tokens, item_index, "list_item_close")
        child_index = item_index + 1
        while child_index < item_close:
            child = tokens[child_index]
            if child.type == "paragraph_open":
                child_index += 3
                continue
            return False
        return True
    return False
```

</details>

## 🔧 Function `_wrap_list_item_prose`

```python
def _wrap_list_item_prose(block: str) -> list[str]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _wrap_list_item_prose(block: str, *, prefix: str, continuation: str, width: int) -> list[str]:
    split_at = block.find(") - ")
    if split_at < 0:
        return wrap_prose(block, width=width, prefix=prefix, continuation=continuation).split("\n")
    head = block[: split_at + 1]
    tail = block[split_at + 4 :]
    lines = [prefix + f"{head} -"]
    lines.extend(wrap_prose(tail, width=width, prefix=continuation, continuation=continuation).split("\n"))
    return lines
```

</details>
