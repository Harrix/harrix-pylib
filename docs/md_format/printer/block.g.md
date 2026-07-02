---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `block.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `_blockquote_line_content`](#-function-_blockquote_line_content)
- [🔧 Function `_blockquote_line_depth`](#-function-_blockquote_line_depth)
- [🔧 Function `_blockquote_needs_blank_line`](#-function-_blockquote_needs_blank_line)
- [🔧 Function `_join_blockquote_blocks`](#-function-_join_blockquote_blocks)
- [🔧 Function `_join_blocks`](#-function-_join_blocks)
- [🔧 Function `_render_alert`](#-function-_render_alert)
- [🔧 Function `_render_block`](#-function-_render_block)
- [🔧 Function `_render_blockquote`](#-function-_render_blockquote)
- [🔧 Function `_render_fence`](#-function-_render_fence)
- [🔧 Function `_render_heading`](#-function-_render_heading)
- [🔧 Function `_render_indented_code_block`](#-function-_render_indented_code_block)
- [🔧 Function `_render_math_block`](#-function-_render_math_block)
- [🔧 Function `_render_until_close`](#-function-_render_until_close)
- [🔧 Function `_should_join_without_blank_line`](#-function-_should_join_without_blank_line)
- [🔧 Function `_wrap_blockquote_block`](#-function-_wrap_blockquote_block)

</details>

## 🔧 Function `_blockquote_line_content`

```python
def _blockquote_line_content(line: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _blockquote_line_content(line: str) -> str:
    content = line.lstrip()
    while content.startswith(">"):
        content = content[1:]
        content = content.removeprefix(" ")
    return content.strip()
```

</details>

## 🔧 Function `_blockquote_line_depth`

```python
def _blockquote_line_depth(line: str) -> int
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _blockquote_line_depth(line: str) -> int:
    stripped = line.lstrip()
    depth = 0
    while stripped.startswith(">"):
        depth += 1
        stripped = stripped[1:]
        stripped = stripped.removeprefix(" ")
    return depth
```

</details>

## 🔧 Function `_blockquote_needs_blank_line`

```python
def _blockquote_needs_blank_line(previous: str, current: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

````python
def _blockquote_needs_blank_line(previous: str, current: str) -> bool:
    previous_lines = [line for line in previous.rstrip().splitlines() if line.strip()]
    current_lines = [line for line in current.lstrip().splitlines() if line.strip()]
    if not previous_lines or not current_lines:
        return False
    if _blockquote_line_depth(current_lines[0]) > _blockquote_line_depth(previous_lines[-1]):
        return True
    previous_last = _blockquote_line_content(previous_lines[-1])
    current_first = _blockquote_line_content(current_lines[0])
    if current_first.startswith("|"):
        return True
    if previous_last.startswith("|"):
        return True
    if previous_last.startswith("<!--") and current_first.startswith("<!--"):
        return False
    if current_first.startswith("-"):
        if previous_last.startswith(("-", "*", "+")):
            return False
        if previous_last and previous_last[0].isdigit() and ". " in previous_last[:4]:
            return False
        return True
    if current_first.startswith(("#", "|", "```")):
        return False
    return True
````

</details>

## 🔧 Function `_join_blockquote_blocks`

```python
def _join_blockquote_blocks(blocks: list[str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _join_blockquote_blocks(blocks: list[str]) -> str:
    if not blocks:
        return ""
    joined: list[str] = [blocks[0].rstrip("\n")]
    for block in blocks[1:]:
        if _blockquote_needs_blank_line(joined[-1], block):
            joined.append(">")
        joined.append(block.rstrip("\n"))
    return "\n".join(joined) + "\n"
```

</details>

## 🔧 Function `_join_blocks`

```python
def _join_blocks(parts: list[str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _join_blocks(
    parts: list[str],
    *,
    tokens: list[Token] | None = None,
    part_indices: list[int] | None = None,
    source_lines: list[str] | None = None,
) -> str:
    cleaned: list[str] = []
    cleaned_indices: list[int] = []
    for part_index, part in enumerate(parts):
        stripped = part.strip("\n")
        if not stripped:
            continue
        current_token_index = part_indices[part_index] if part_indices and part_index < len(part_indices) else None
        previous_token_index = cleaned_indices[-1] if cleaned_indices else None
        if cleaned and (
            _should_join_without_blank_line(cleaned[-1], stripped)
            or _source_blocks_are_adjacent(tokens, previous_token_index, current_token_index, source_lines)
        ):
            cleaned[-1] = cleaned[-1].rstrip("\n") + "\n" + stripped + "\n"
            if current_token_index is not None:
                cleaned_indices[-1] = current_token_index
        else:
            cleaned.append(stripped + "\n")
            if current_token_index is not None:
                cleaned_indices.append(current_token_index)
    if not cleaned:
        return ""
    return "\n\n".join(block.rstrip("\n") for block in cleaned) + "\n"
```

</details>

## 🔧 Function `_render_alert`

```python
def _render_alert(tokens: list[Token], index: int) -> tuple[str, int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_alert(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
    normalize_star_to_dash: bool = False,
) -> tuple[str, int]:
    markers = task_list_markers or []
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    close_index = _find_close(tokens, index, "alert_close")
    alert_token = tokens[index]
    kind = "NOTE"
    if alert_token.meta and isinstance(alert_token.meta, dict):
        kind = str(alert_token.meta.get("kind", kind))
    body_parts: list[str] = []
    inner_index = index + 1
    while inner_index < close_index:
        token = tokens[inner_index]
        if token.type in {"alert_title_open", "alert_title_close"}:
            inner_index += 1
            continue
        if token.type == "inline" and inner_index > index + 1 and tokens[inner_index - 1].type == "alert_title_open":
            inner_index += 1
            continue
        chunk, inner_index = _render_block(
            tokens,
            inner_index,
            options=options,
            task_list_markers=markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            normalize_star_to_dash=normalize_star_to_dash,
            preserve_source_line=False,
        )
        if chunk:
            body_parts.append(chunk.strip())
    body = normalize_inline_spaces(" ".join(body_parts))
    alert_line = f"[!{kind}] {body}".rstrip() if body else f"[!{kind}]"
    if options.prose_wrap == "always":
        quoted = _wrap_blockquote_block(alert_line, options=options) + "\n"
    else:
        quoted = f"> {alert_line}\n"
    return quoted, close_index + 1
```

</details>

## 🔧 Function `_render_block`

```python
def _render_block(tokens: list[Token], index: int) -> tuple[str, int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_block(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    wrap_paragraph: bool = True,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
    normalize_star_to_dash: bool = False,
    preserve_source_line: bool = True,
    in_list_item: bool = False,
    in_blockquote: bool = False,
) -> tuple[str, int]:
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    token = tokens[index]
    if token.type == "heading_open":
        return _render_heading(
            tokens,
            index,
            options=options,
            hard_break_styles=break_styles,
            source_lines=source_lines if preserve_source_line else None,
        )
    if token.type == "paragraph_open":
        return _render_paragraph(
            tokens,
            index,
            options=options,
            wrap=wrap_paragraph,
            hard_break_styles=break_styles,
            source_lines=source_lines,
            preserve_source_line=preserve_source_line,
        )
    if token.type == "blockquote_open":
        return _render_blockquote(
            tokens,
            index,
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            normalize_star_to_dash=normalize_star_to_dash,
        )
    if token.type == "alert_open":
        return _render_alert(
            tokens,
            index,
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            normalize_star_to_dash=normalize_star_to_dash,
        )
    if token.type == "bullet_list_open":
        return _render_list(
            tokens,
            index,
            ordered=False,
            options=options,
            task_list_markers=task_list_markers or [],
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            normalize_star_to_dash=normalize_star_to_dash,
            in_blockquote=in_blockquote,
        )
    if token.type == "ordered_list_open":
        return _render_list(
            tokens,
            index,
            ordered=True,
            options=options,
            task_list_markers=task_list_markers or [],
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            normalize_star_to_dash=normalize_star_to_dash,
            in_blockquote=in_blockquote,
        )
    if token.type == "fence":
        return _render_fence(token), index + 1
    if token.type == "code_block":
        return _render_indented_code_block(token.content), index + 1
    if token.type == "hr":
        return f"{_format_hr_markup(token.markup or '---', preserve=in_list_item)}\n", index + 1
    if token.type == "math_block":
        return _render_math_block(token), index + 1
    if token.type == "math_block_label":
        return _render_math_block(token, label=token.info), index + 1
    if token.type == "table_open":
        return _render_table(
            tokens,
            index,
            options=options,
            hard_break_styles=break_styles,
            source_lines=source_lines if preserve_source_line else None,
        )
    if token.type == "html_block":
        return f"{token.content.rstrip()}\n", index + 1
    if token.type in {"dl_open", "dt_open", "dd_open"}:
        return _render_until_close(
            tokens,
            index,
            token.type.replace("_open", "_close"),
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            normalize_star_to_dash=normalize_star_to_dash,
        ), index + 1
    return "", index + 1
```

</details>

## 🔧 Function `_render_blockquote`

```python
def _render_blockquote(tokens: list[Token], index: int) -> tuple[str, int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

````python
def _render_blockquote(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
    normalize_star_to_dash: bool = False,
) -> tuple[str, int]:
    markers = task_list_markers or []
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    close_index = _find_close(tokens, index, "blockquote_close")
    inner_parts: list[str] = []
    inner_index = index + 1
    while inner_index < close_index:
        chunk, inner_index = _render_block(
            tokens,
            inner_index,
            options=options,
            task_list_markers=markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            normalize_star_to_dash=normalize_star_to_dash,
            preserve_source_line=False,
            in_blockquote=True,
        )
        if chunk:
            inner_parts.append(chunk)
    if (
        options.prose_wrap == "always"
        and len(inner_parts) == 1
        and inner_parts
        and all(not part.lstrip().startswith(("-", "|", "#", "```")) for part in inner_parts)
        and not any("[[" in part and "\n" in part for part in inner_parts)
    ):
        merged = normalize_inline_spaces(
            " ".join(part.strip().replace("\n", " ") for part in inner_parts if part.strip())
        )
        quoted = _wrap_blockquote_block(merged, options=options) + "\n"
        return quoted, close_index + 1
    quoted_blocks: list[str] = []
    for block in inner_parts:
        if options.prose_wrap == "always":
            quoted_blocks.append(_wrap_blockquote_block(block, options=options))
        else:
            quoted_lines = [f"> {line}" if line else ">" for line in block.rstrip().splitlines()]
            quoted_blocks.append("\n".join(quoted_lines))
    quoted = _join_blockquote_blocks(quoted_blocks)
    return quoted, close_index + 1
````

</details>

## 🔧 Function `_render_fence`

```python
def _render_fence(token: Token) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

````python
def _render_fence(token: Token) -> str:
    info = (token.info or "").strip()
    fence = "```"
    content = token.content.strip("\n")
    return f"{fence}{info}\n{content}\n{fence}\n"
````

</details>

## 🔧 Function `_render_heading`

```python
def _render_heading(tokens: list[Token], index: int) -> tuple[str, int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_heading(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
    source_lines: list[str] | None = None,
) -> tuple[str, int]:
    source_line = _plain_heading_source_line(tokens, index, source_lines)
    if source_line is not None:
        return f"{source_line}\n", index + 3
    setext_source = _setext_heading_source_line(tokens, index, source_lines)
    if setext_source is not None:
        return f"{setext_source}\n", index + 3
    level = int(tokens[index].tag[1])
    inline = tokens[index + 1]
    text = _render_inline(inline.children or [], options=options, hard_break_styles=hard_break_styles)
    return f"{'#' * level} {text}\n", index + 3
```

</details>

## 🔧 Function `_render_indented_code_block`

```python
def _render_indented_code_block(content: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_indented_code_block(content: str) -> str:
    lines = content.rstrip("\n").splitlines()
    if not lines:
        return "    \n"
    return "\n".join(f"    {line}" if line.strip() else "" for line in lines) + "\n"
```

</details>

## 🔧 Function `_render_math_block`

```python
def _render_math_block(token: Token) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_math_block(token: Token, *, label: str | None = None) -> str:
    content = token.content.strip()
    if label:
        return f"$$\n{content}\n$$ ({label})\n"
    return f"$$\n{content}\n$$\n"
```

</details>

## 🔧 Function `_render_until_close`

```python
def _render_until_close(tokens: list[Token], index: int, close_type: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_until_close(
    tokens: list[Token],
    index: int,
    close_type: str,
    *,
    options: FormatOptions,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    canonicalize_bullets: bool = False,
    normalize_star_to_dash: bool = False,
) -> str:
    markers = task_list_markers or []
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list_layouts or []
    close_index = _find_close(tokens, index, close_type)
    parts: list[str] = []
    inner_index = index + 1
    while inner_index < close_index:
        chunk, inner_index = _render_block(
            tokens,
            inner_index,
            options=options,
            task_list_markers=markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            normalize_star_to_dash=normalize_star_to_dash,
            preserve_source_line=False,
        )
        if chunk:
            parts.append(chunk)
    return _join_blocks(parts)
```

</details>

## 🔧 Function `_should_join_without_blank_line`

```python
def _should_join_without_blank_line(previous: str, current: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _should_join_without_blank_line(previous: str, current: str) -> bool:
    prev_lines = previous.strip("\n").splitlines()
    if not prev_lines:
        return False
    last_line = prev_lines[-1].strip()
    if last_line.startswith("<!-- prettier-ignore"):
        return True
    if current.lstrip().startswith("<!-- prettier-ignore"):
        return True
    return False
```

</details>

## 🔧 Function `_wrap_blockquote_block`

```python
def _wrap_blockquote_block(block: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _wrap_blockquote_block(block: str, *, options: FormatOptions) -> str:
    lines = block.rstrip().splitlines()
    wrapped_lines: list[str] = []
    for line in lines:
        if not line.strip():
            wrapped_lines.append(">")
            continue
        prefix = "> "
        wrapped = wrap_prose(line, width=options.print_width, prefix=prefix, continuation=prefix)
        wrapped_lines.extend(wrapped.split("\n"))
    return "\n".join(wrapped_lines)
```

</details>
