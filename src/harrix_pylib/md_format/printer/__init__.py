"""Render markdown-it tokens back to Markdown."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harrix_pylib.md_format.hard_break_format import HardBreakStyles
from harrix_pylib.md_format.link_destination_format import LinkDestination
from harrix_pylib.md_format.list_loose_format import ListLayout
from harrix_pylib.md_format.options import FormatOptions
from harrix_pylib.md_format.printer import context as printer_context
from harrix_pylib.md_format.printer.block import _join_blocks, _render_block
from harrix_pylib.md_format.printer.paragraph import (
    _try_render_merged_link_paragraphs,
    _try_render_merged_paragraphs,
)
from harrix_pylib.md_format.task_list_format import TaskListMarker

if TYPE_CHECKING:
    from markdown_it.token import Token


def render_tokens(
    tokens: list[Token],
    *,
    options: FormatOptions | None = None,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
    link_destinations: list[LinkDestination] | None = None,
) -> str:
    """Render top-level block tokens to Markdown."""
    previous_destinations = printer_context.ACTIVE_LINK_DESTINATIONS
    printer_context.ACTIVE_LINK_DESTINATIONS = (
        {entry.index: entry for entry in link_destinations} if link_destinations else None
    )
    try:
        return _render_tokens_impl(
            tokens,
            options=options,
            task_list_markers=task_list_markers,
            ordered_list_marker_groups=ordered_list_marker_groups,
            bullet_list_marker_groups=bullet_list_marker_groups,
            hard_break_styles=hard_break_styles,
            list_layouts=list_layouts,
            source_lines=source_lines,
        )
    finally:
        printer_context.ACTIVE_LINK_DESTINATIONS = previous_destinations


def _render_tokens_impl(
    tokens: list[Token],
    *,
    options: FormatOptions | None = None,
    task_list_markers: list[TaskListMarker] | None = None,
    ordered_list_marker_groups: list[list[int]] | None = None,
    bullet_list_marker_groups: list[list[str]] | None = None,
    hard_break_styles: HardBreakStyles | None = None,
    list_layouts: list[ListLayout] | None = None,
    source_lines: list[str] | None = None,
) -> str:
    fmt_options = options or printer_context.DEFAULT_OPTIONS
    markers = task_list_markers or []
    ordered_groups = list(ordered_list_marker_groups or [])
    bullet_groups = list(bullet_list_marker_groups or [])
    distinct_bullet_markers = {marker for group in bullet_groups for marker in group}
    canonicalize_bullets = len(distinct_bullet_markers) <= 1
    normalize_star_to_dash = "+" in distinct_bullet_markers
    break_styles = hard_break_styles or HardBreakStyles()
    layouts = list(list_layouts or [])
    parts: list[str] = []
    part_indices: list[int] = []
    index = 0
    while index < len(tokens):
        merged, next_index = _try_render_merged_paragraphs(
            tokens,
            index,
            options=fmt_options,
            hard_break_styles=break_styles,
        )
        if merged is not None:
            parts.append(merged)
            part_indices.append(index)
            index = next_index
            continue
        merged, next_index = _try_render_merged_link_paragraphs(
            tokens,
            index,
            options=fmt_options,
            hard_break_styles=break_styles,
        )
        if merged is not None:
            parts.append(merged)
            part_indices.append(index)
            index = next_index
            continue
        block_index = index
        chunk, index = _render_block(
            tokens,
            index,
            options=fmt_options,
            task_list_markers=markers,
            ordered_list_marker_groups=ordered_groups,
            bullet_list_marker_groups=bullet_groups,
            hard_break_styles=break_styles,
            list_layouts=layouts,
            source_lines=source_lines,
            canonicalize_bullets=canonicalize_bullets,
            normalize_star_to_dash=normalize_star_to_dash,
        )
        if chunk:
            parts.append(chunk)
            part_indices.append(block_index)
    return _join_blocks(parts, tokens=tokens, part_indices=part_indices, source_lines=source_lines)
