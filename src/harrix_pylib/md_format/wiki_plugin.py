"""Wiki-link `[[...]]` inline rule for markdown-it-py."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from markdown_it import MarkdownIt
    from markdown_it.rules_inline import StateInline

_WIKI_PATTERN = re.compile(r"^\[\[(.+?)\]\]", re.DOTALL)


def wiki_link_plugin(md: MarkdownIt) -> None:
    """Register wiki-link parsing before standard links."""

    def wiki_rule(state: StateInline, silent: bool) -> bool:  # noqa: FBT001
        if state.pos + 4 > len(state.src):
            return False
        if state.src[state.pos : state.pos + 2] != "[[":
            return False
        match = _WIKI_PATTERN.match(state.src, state.pos)
        if not match:
            return False
        if silent:
            return True
        token = state.push("wiki_link", "", 0)
        token.content = match.group(1)
        state.pos = match.end()
        return True

    md.inline.ruler.before("link", "wiki_link", wiki_rule)
