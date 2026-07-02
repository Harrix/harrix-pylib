---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paragraph.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `_broken_wiki_link_source_paragraph`](#-function-_broken_wiki_link_source_paragraph)
- [🔧 Function `_join_prose_run_parts`](#-function-_join_prose_run_parts)
- [🔧 Function `_join_without_space`](#-function-_join_without_space)
- [🔧 Function `_merged_run_is_link_only_paragraphs`](#-function-_merged_run_is_link_only_paragraphs)
- [🔧 Function `_merged_run_is_whitespace_inline_code`](#-function-_merged_run_is_whitespace_inline_code)
- [🔧 Function `_merged_run_should_join_as_prose`](#-function-_merged_run_should_join_as_prose)
- [🔧 Function `_paragraph_contains_hangul`](#-function-_paragraph_contains_hangul)
- [🔧 Function `_paragraph_is_cjk_dominant`](#-function-_paragraph_is_cjk_dominant)
- [🔧 Function `_paragraph_run_end`](#-function-_paragraph_run_end)
- [🔧 Function `_paragraph_single_text_source_line`](#-function-_paragraph_single_text_source_line)
- [🔧 Function `_paragraph_source_line`](#-function-_paragraph_source_line)
- [🔧 Function `_plain_heading_source_line`](#-function-_plain_heading_source_line)
- [🔧 Function `_plain_inline_code_source_line`](#-function-_plain_inline_code_source_line)
- [🔧 Function `_plain_paragraph_source_line`](#-function-_plain_paragraph_source_line)
- [🔧 Function `_render_joined_prose_run`](#-function-_render_joined_prose_run)
- [🔧 Function `_render_merged_whitespace_inline_code`](#-function-_render_merged_whitespace_inline_code)
- [🔧 Function `_render_paragraph`](#-function-_render_paragraph)
- [🔧 Function `_setext_heading_source_line`](#-function-_setext_heading_source_line)
- [🔧 Function `_should_wrap_prose`](#-function-_should_wrap_prose)
- [🔧 Function `_source_blocks_are_adjacent`](#-function-_source_blocks_are_adjacent)
- [🔧 Function `_source_bullet_marker`](#-function-_source_bullet_marker)
- [🔧 Function `_source_line_is_more_literal`](#-function-_source_line_is_more_literal)
- [🔧 Function `_strip_list_item_content`](#-function-_strip_list_item_content)
- [🔧 Function `_try_render_merged_link_paragraphs`](#-function-_try_render_merged_link_paragraphs)
- [🔧 Function `_try_render_merged_paragraphs`](#-function-_try_render_merged_paragraphs)
- [🔧 Function `_unparsed_image_reference_source_line`](#-function-_unparsed_image_reference_source_line)

</details>

## 🔧 Function `_broken_wiki_link_source_paragraph`

```python
def _broken_wiki_link_source_paragraph(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _broken_wiki_link_source_paragraph(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None:
    if not source_lines:
        return None
    paragraph_map = tokens[index].map
    if not paragraph_map:
        return None
    span = paragraph_map[1] - paragraph_map[0]
    source = "\n".join(source_lines[paragraph_map[0] : paragraph_map[1]])
    if "[[" not in source:
        return None
    if "]]" not in source:
        # Paragraph with an unclosed [[  ΓÇö no matching ]].
        # Collapse multi-line to one line (joining with space), preserving literal content.
        stripped_first = source.split("\n")[0].strip() if "\n" in source else source.strip()
        if stripped_first.startswith("[["):
            return " ".join(line.strip() for line in source.split("\n") if line.strip())
        return None
    # Check that the inline token has a softbreak (meaning the [[...]] is split across lines)
    # rather than being a proper wiki_link token (already handled by wiki_link rendering).
    inline = tokens[index + 1]
    children = inline.children or []
    has_softbreak = any(c.type == "softbreak" for c in children)
    has_wiki_link = any(c.type == "wiki_link" for c in children)
    if not has_softbreak and not has_wiki_link:
        return None
    if has_wiki_link and not has_softbreak:
        # Proper wiki_link token ΓÇö will be rendered correctly without source override
        return None
    # For paragraphs with softbreaks where [[...]] spans lines, preserve source.
    lines = source.split("\n")

    # Find a line that has an unclosed [[  (i.e. has [[ but no ]] after it)
    def _has_unclosed_wiki_open(line: str) -> bool:
        pos = line.find("[[")
        if pos < 0:
            return False
        rest = line[pos + 2 :]
        return "]]" not in rest

    opening_idx = next((i for i, line in enumerate(lines) if _has_unclosed_wiki_open(line)), None)
    if opening_idx is None:
        return None
    closing_idx = next((i for i in range(len(lines) - 1, opening_idx, -1) if "]]" in lines[i]), None)
    if closing_idx is None:
        return None
    return source
```

</details>

## 🔧 Function `_join_prose_run_parts`

```python
def _join_prose_run_parts(parts: list[str]) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _join_prose_run_parts(parts: list[str]) -> str:
    if not parts:
        return ""
    merged = parts[0]
    for part in parts[1:]:
        if not part:
            continue
        if not merged:
            merged = part
            continue
        if should_omit_space_between(merged, part):
            merged += part
        else:
            merged += f" {part}"
    return normalize_inline_spaces(escape_ordered_list_like_line_starts(merged))
```

</details>

## 🔧 Function `_join_without_space`

```python
def _join_without_space(left: str, right: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _join_without_space(left: str, right: str) -> bool:
    return should_omit_space_between(left, right)
```

</details>

## 🔧 Function `_merged_run_is_link_only_paragraphs`

```python
def _merged_run_is_link_only_paragraphs(tokens: list[Token], start: int, run_end: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _merged_run_is_link_only_paragraphs(tokens: list[Token], start: int, run_end: int) -> bool:
    paragraph_index = start
    while paragraph_index < run_end:
        children = tokens[paragraph_index + 1].children or []
        if not any(child.type == "link_open" for child in children):
            return False
        if any(child.type not in {"link_open", "link_close", "text", "softbreak", "code_inline"} for child in children):
            return False
        paragraph_index += 3
    return paragraph_index > start
```

</details>

## 🔧 Function `_merged_run_is_whitespace_inline_code`

```python
def _merged_run_is_whitespace_inline_code(tokens: list[Token], start: int, run_end: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _merged_run_is_whitespace_inline_code(tokens: list[Token], start: int, run_end: int) -> bool:
    paragraph_index = start
    while paragraph_index < run_end:
        inline = tokens[paragraph_index + 1]
        children = inline.children or []
        if len(children) != 1 or children[0].type != "code_inline":
            return False
        if children[0].content.strip():
            return False
        paragraph_index += 3
    return paragraph_index > start
```

</details>

## 🔧 Function `_merged_run_should_join_as_prose`

```python
def _merged_run_should_join_as_prose(tokens: list[Token], start: int, run_end: int) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _merged_run_should_join_as_prose(tokens: list[Token], start: int, run_end: int) -> bool:
    paragraph_index = start
    while paragraph_index < run_end:
        inline = tokens[paragraph_index + 1]
        children = inline.children or []
        if any(child.type not in {"text", "softbreak"} for child in children):
            return False
        paragraph_index += 3
    return paragraph_index > start
```

</details>

## 🔧 Function `_paragraph_contains_hangul`

```python
def _paragraph_contains_hangul(text: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _paragraph_contains_hangul(text: str) -> bool:
    non_space = [char for char in text if not char.isspace()]
    if not non_space:
        return False
    hangul_count = sum(1 for char in non_space if _is_hangul(char))
    return hangul_count > 0
```

</details>

## 🔧 Function `_paragraph_is_cjk_dominant`

```python
def _paragraph_is_cjk_dominant(text: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _paragraph_is_cjk_dominant(text: str) -> bool:
    non_space = [char for char in text if not char.isspace()]
    if not non_space:
        return False
    cjk_count = sum(1 for char in non_space if _is_cjk(char))
    return cjk_count / len(non_space) >= 0.15
```

</details>

## 🔧 Function `_paragraph_run_end`

```python
def _paragraph_run_end(tokens: list[Token], start: int) -> int | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _paragraph_run_end(tokens: list[Token], start: int) -> int | None:
    if tokens[start].type != "paragraph_open" or not tokens[start].map:
        return None
    run_end = start
    last_line_end = tokens[start].map[1]
    while run_end + 3 < len(tokens) and tokens[run_end + 3].type == "paragraph_open":
        next_map = tokens[run_end + 3].map
        if not next_map or next_map[0] != last_line_end:
            break
        last_line_end = next_map[1]
        run_end += 3
    if run_end == start:
        return None
    return run_end + 3
```

</details>

## 🔧 Function `_paragraph_single_text_source_line`

```python
def _paragraph_single_text_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _paragraph_single_text_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None:
    if not source_lines:
        return None
    paragraph_map = tokens[index].map
    if not paragraph_map or paragraph_map[1] - paragraph_map[0] != 1:
        return None
    inline = tokens[index + 1]
    children = inline.children or []
    if len(children) != 1 or children[0].type != "text":
        return None
    line_index = paragraph_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return None
    return source_lines[line_index]
```

</details>

## 🔧 Function `_paragraph_source_line`

```python
def _paragraph_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _paragraph_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None:
    if not source_lines:
        return None
    paragraph_map = tokens[index].map
    if not paragraph_map or paragraph_map[1] - paragraph_map[0] != 1:
        return None
    line_index = paragraph_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return None
    return source_lines[line_index]
```

</details>

## 🔧 Function `_plain_heading_source_line`

```python
def _plain_heading_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _plain_heading_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None:
    if not source_lines:
        return None
    heading_map = tokens[index].map
    if not heading_map or heading_map[1] - heading_map[0] != 1:
        return None
    line_index = heading_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return None
    source_line = source_lines[line_index]
    if not source_line.lstrip().startswith("#"):
        return None
    stripped = source_line.strip()
    if re.fullmatch(r"#+ .+ #+\s*", stripped):
        return None
    return source_line
```

</details>

## 🔧 Function `_plain_inline_code_source_line`

```python
def _plain_inline_code_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _plain_inline_code_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None:
    if not source_lines:
        return None
    paragraph_map = tokens[index].map
    if not paragraph_map or paragraph_map[1] - paragraph_map[0] != 1:
        return None
    inline = tokens[index + 1]
    children = inline.children or []
    if len(children) != 1 or children[0].type != "code_inline":
        return None
    line_index = paragraph_map[0]
    if line_index < 0 or line_index >= len(source_lines):
        return None
    source_line = source_lines[line_index].strip()
    if not SINGLE_TICK_INLINE_CODE_RE.fullmatch(source_line):
        return None
    return source_line
```

</details>

## 🔧 Function `_plain_paragraph_source_line`

```python
def _plain_paragraph_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _plain_paragraph_source_line(
    tokens: list[Token],
    index: int,
    source_lines: list[str] | None,
    *,
    options: FormatOptions,
    rendered_line: str,
) -> str | None:
    source_line = _paragraph_single_text_source_line(tokens, index, source_lines)
    if source_line is None:
        return None
    if "\u00a0" in source_line:
        return source_line.rstrip("\n")
    if "\u3000" in source_line:
        return source_line.rstrip("\n")
    if (
        _paragraph_is_cjk_dominant(source_line.rstrip("\n"))
        and text_display_width(source_line.rstrip("\n")) > options.print_width
        and not (options.prose_wrap == "always" and _paragraph_contains_hangul(source_line.rstrip("\n")))
    ):
        return source_line.rstrip("\n")
    if options.prose_wrap == "always" and _should_wrap_prose(
        source_line.rstrip("\n"), prefix="", width=options.print_width
    ):
        return None
    if rendered_line.rstrip("\n") == source_line.rstrip("\n"):
        return None
    if _source_line_is_more_literal(source_line, rendered_line):
        return source_line
    return None
```

</details>

## 🔧 Function `_render_joined_prose_run`

```python
def _render_joined_prose_run(tokens: list[Token], start: int, run_end: int) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_joined_prose_run(
    tokens: list[Token],
    start: int,
    run_end: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
) -> str:
    break_styles = hard_break_styles or HardBreakStyles()
    parts: list[str] = []
    paragraph_index = start
    while paragraph_index < run_end:
        inline = tokens[paragraph_index + 1]
        parts.append(
            _render_inline(
                inline.children or [],
                options=options,
                hard_break_styles=break_styles,
                softbreak_as_space=True,
            ).strip()
        )
        paragraph_index += 3
    merged = _join_prose_run_parts(parts)
    if "\\_" not in merged and _should_wrap_prose(merged, prefix="", width=options.print_width):
        merged = wrap_prose(merged, width=options.print_width)
    return merged
```

</details>

## 🔧 Function `_render_merged_whitespace_inline_code`

```python
def _render_merged_whitespace_inline_code(tokens: list[Token], start: int, run_end: int) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_merged_whitespace_inline_code(tokens: list[Token], start: int, run_end: int) -> str:
    contents: list[str] = []
    paragraph_index = start
    while paragraph_index < run_end:
        children = tokens[paragraph_index + 1].children or []
        contents.append(children[0].content)
        paragraph_index += 3
    return _format_code_inline(" ".join(contents))
```

</details>

## 🔧 Function `_render_paragraph`

```python
def _render_paragraph(tokens: list[Token], index: int) -> tuple[str, int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _render_paragraph(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    wrap: bool = True,
    hard_break_styles: HardBreakStyles | None = None,
    source_lines: list[str] | None = None,
    preserve_source_line: bool = True,
) -> tuple[str, int]:
    if preserve_source_line:
        inline_code_line = _plain_inline_code_source_line(tokens, index, source_lines)
        if inline_code_line is not None:
            return f"{inline_code_line}\n", index + 3
    broken_wiki_line = _broken_wiki_link_source_paragraph(tokens, index, source_lines)
    if broken_wiki_line is not None:
        return f"{broken_wiki_line.rstrip()}\n", index + 3
    image_reference_line = _unparsed_image_reference_source_line(tokens, index, source_lines)
    if image_reference_line is not None:
        return f"{image_reference_line.rstrip()}\n", index + 3
    inline = tokens[index + 1]
    children = inline.children or []
    if _inline_children_are_link_run(children):
        text = _render_packed_link_run(
            children,
            options=options,
            hard_break_styles=hard_break_styles,
        )
        return f"{text}\n", index + 3
    use_space_breaks = options.prose_wrap == "always"
    text = escape_ordered_list_like_line_starts(
        _render_inline(
            inline.children or [],
            options=options,
            hard_break_styles=hard_break_styles,
            softbreak_as_space=use_space_breaks,
        )
    )
    if (
        wrap
        and options.prose_wrap == "always"
        and "\u00a0" not in text
        and _should_wrap_prose(text.rstrip("\n"), prefix="", width=options.print_width)
    ):
        body = text.rstrip("\n")
        if "\n" in body and "  \n" not in body:
            body = "\n".join(wrap_prose(part, width=options.print_width) if part else part for part in body.split("\n"))
        else:
            body = wrap_paragraph_prose(body, width=options.print_width)
        text = body
    source_line = (
        _plain_paragraph_source_line(tokens, index, source_lines, options=options, rendered_line=text.rstrip("\n"))
        if preserve_source_line
        else None
    )
    if source_line is not None:
        return f"{source_line.rstrip()}\n", index + 3
    return f"{text.rstrip()}\n", index + 3
```

</details>

## 🔧 Function `_setext_heading_source_line`

```python
def _setext_heading_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _setext_heading_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None:
    if not source_lines:
        return None
    heading_map = tokens[index].map
    if not heading_map or heading_map[1] - heading_map[0] != 2:
        return None
    markup = tokens[index].markup or ""
    if markup not in {"=", "-"}:
        return None
    lines = source_lines[heading_map[0] : heading_map[1]]
    if len(lines) != 2:
        return None
    return "\n".join(lines)
```

</details>

## 🔧 Function `_should_wrap_prose`

```python
def _should_wrap_prose(text: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _should_wrap_prose(text: str, *, prefix: str, width: int) -> bool:
    return _prose_display_width(prefix + text) > width
```

</details>

## 🔧 Function `_source_blocks_are_adjacent`

```python
def _source_blocks_are_adjacent(tokens: list[Token] | None, previous_index: int | None, current_index: int | None, source_lines: list[str] | None) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _source_blocks_are_adjacent(
    tokens: list[Token] | None,
    previous_index: int | None,
    current_index: int | None,
    source_lines: list[str] | None,
) -> bool:
    if tokens is None or source_lines is None or previous_index is None or current_index is None:
        return False
    previous_map = tokens[previous_index].map
    current_map = tokens[current_index].map
    if not previous_map or not current_map:
        return False
    if previous_map[1] != current_map[0]:
        return False
    # Check there's no blank line at the end of the previous block.
    last_line_index = previous_map[1] - 1
    if last_line_index >= 0 and last_line_index < len(source_lines) and not source_lines[last_line_index].strip():
        return False
    previous_type = tokens[previous_index].type
    current_type = tokens[current_index].type
    if previous_type in {"bullet_list_open", "ordered_list_open"} and current_type in {
        "bullet_list_open",
        "ordered_list_open",
    }:
        if previous_type == current_type == "bullet_list_open":
            previous_source_line = source_lines[previous_map[0]] if previous_map[0] < len(source_lines) else ""
            current_source_line = source_lines[current_map[0]] if current_map[0] < len(source_lines) else ""
            if _source_bullet_marker(previous_source_line) != _source_bullet_marker(current_source_line):
                return False
        return True
    if "html_block" not in {previous_type, current_type}:
        return False
    if previous_type in {"bullet_list_open", "ordered_list_open"} or current_type in {
        "bullet_list_open",
        "ordered_list_open",
    }:
        return False
    previous_source_line = source_lines[previous_map[0]] if previous_map[0] < len(source_lines) else ""
    return not LIST_MARKER_LINE_RE.match(previous_source_line.lstrip())
```

</details>

## 🔧 Function `_source_bullet_marker`

```python
def _source_bullet_marker(line: str) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _source_bullet_marker(line: str) -> str | None:
    match = re.match(r"\s*([-*+])\s+", line)
    if match is None:
        return None
    return match.group(1)
```

</details>

## 🔧 Function `_source_line_is_more_literal`

```python
def _source_line_is_more_literal(source_line: str, rendered_line: str) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _source_line_is_more_literal(source_line: str, rendered_line: str) -> bool:
    if source_line.count("\\") > rendered_line.count("\\"):
        return True
    if "&" in source_line and source_line != rendered_line:
        if "&amp;" in source_line or "&#" in source_line:
            return True
    return False
```

</details>

## 🔧 Function `_strip_list_item_content`

```python
def _strip_list_item_content(line: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _strip_list_item_content(line: str) -> str:
    match = LIST_ITEM_CONTENT_RE.match(line)
    if match is None:
        return line
    return match.group(2)
```

</details>

## 🔧 Function `_try_render_merged_link_paragraphs`

```python
def _try_render_merged_link_paragraphs(tokens: list[Token], index: int) -> tuple[str | None, int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _try_render_merged_link_paragraphs(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
) -> tuple[str | None, int]:
    run_end = _paragraph_run_end(tokens, index)
    if run_end is None:
        return None, index
    if not _merged_run_is_link_only_paragraphs(tokens, index, run_end):
        return None, index
    break_styles = hard_break_styles or HardBreakStyles()
    parts: list[str] = []
    paragraph_index = index
    while paragraph_index < run_end:
        inline = tokens[paragraph_index + 1]
        parts.append(
            _render_inline(
                inline.children or [],
                options=options,
                hard_break_styles=break_styles,
            ).strip()
        )
        paragraph_index += 3
    return " ".join(part for part in parts if part) + "\n", run_end
```

</details>

## 🔧 Function `_try_render_merged_paragraphs`

```python
def _try_render_merged_paragraphs(tokens: list[Token], index: int) -> tuple[str | None, int]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _try_render_merged_paragraphs(
    tokens: list[Token],
    index: int,
    *,
    options: FormatOptions,
    hard_break_styles: HardBreakStyles | None = None,
) -> tuple[str | None, int]:
    if options.prose_wrap != "always":
        return None, index
    run_end = _paragraph_run_end(tokens, index)
    if run_end is None:
        return None, index
    if _merged_run_is_whitespace_inline_code(tokens, index, run_end):
        return f"{_render_merged_whitespace_inline_code(tokens, index, run_end)}\n", run_end
    if _merged_run_should_join_as_prose(tokens, index, run_end):
        return (
            f"{_render_joined_prose_run(tokens, index, run_end, options=options, hard_break_styles=hard_break_styles)}\n",
            run_end,
        )
    return None, index
```

</details>

## 🔧 Function `_unparsed_image_reference_source_line`

```python
def _unparsed_image_reference_source_line(tokens: list[Token], index: int, source_lines: list[str] | None) -> str | None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _unparsed_image_reference_source_line(
    tokens: list[Token], index: int, source_lines: list[str] | None
) -> str | None:
    source_line = _paragraph_source_line(tokens, index, source_lines)
    if source_line is None:
        return None
    inline = tokens[index + 1]
    children = inline.children or []
    if any(child.type == "image" for child in children):
        return None
    if not children or not all(child.type in {"text", "code_inline"} for child in children):
        return None
    stripped = source_line.lstrip()
    stripped = source_line.lstrip()
    if stripped.endswith("][]") and stripped.startswith("[") and "![" not in stripped:
        return _strip_list_item_content(source_line)
    if "![" not in stripped or "][" not in stripped:
        return None
    if stripped.endswith("][]"):
        match = EMPTY_IMAGE_REFERENCE_RE.match(stripped)
        if match is None:
            return _strip_list_item_content(source_line)
        raw_alt = match.group("alt")
        alt = " ".join(raw_alt.split())
        if raw_alt == alt:
            return f"![{alt}][]"
        return f"![ {alt} ][]"
    return _strip_list_item_content(source_line)
```

</details>
