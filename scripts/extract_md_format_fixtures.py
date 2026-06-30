"""One-off helper: extract md-format fixtures from upstream snapshot tests."""

from __future__ import annotations

import re
import sys
from pathlib import Path

UPSTREAM_ROOT = Path(r"D:\Downloads\prettier-main\tests\format\markdown")
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "tests" / "data" / "md_format"

EXCLUDE_CASES = {
    "code.md",
    "ignore-code.md",
    "issue-17746-code-before-list.md",
    "issue-17746-code-sibling-nested-list.md",
    "issue-17746-fenced-code-then-nested-list.md",
    "issue-17746-indented-code-then-nested-list.md",
}
EXCLUDE_TOPICS = {
    "code",
    "fenced-code-block",
    "multiparser-css",
    "multiparser-js",
    "multiparser-json",
    "broken-plugins",
    "mdx",
    "commonmark-test-suite",
    "commonmark-test-suite-legacy",
    "gfm-test-suite",
    "spec-legacy",
    "jsx-semi",
    "liquid",
}

PREFERRED_PROSE_WRAP = "always"
ALLOWED_CODE_LANGS = {"", "md", "markdown"}

SNAPSHOT_ENTRY_RE = re.compile(
    r'exports\[`(?P<filename>[^`]+) - \{"proseWrap":"(?P<wrap>[^"]+)"\} format 1`\] = `\n'
    r"====================================options=====================================\n"
    r"(?P<options>.*?)"
    r"=====================================input======================================\n"
    r"(?P<input>.*?)"
    r"=====================================output=====================================\n"
    r"(?P<output>.*?)"
    r"\n================================================================================\n`;",
    re.DOTALL,
)

FENCE_RE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})[ \t]*(?P<lang>[^\n`~]*)[ \t]*\n"
    r"(?P<body>.*?)"
    r"(?P=indent)(?P=fence)[ \t]*$",
    re.DOTALL,
)


def extract(*, dry_run: bool = False) -> list[str]:
    stems: list[str] = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for topic_dir in sorted(UPSTREAM_ROOT.iterdir()):
        if not topic_dir.is_dir():
            continue
        topic = topic_dir.name
        if topic in EXCLUDE_TOPICS:
            continue

        snapshots: dict[str, tuple[str, str]] = {}
        snap_path = topic_dir / "__snapshots__" / "format.test.js.snap"
        snapshots.update(_parse_snapshots(snap_path))
        for sub in sorted(topic_dir.rglob("__snapshots__/format.test.js.snap")):
            if sub == snap_path:
                continue
            sub_topic = topic_dir.name
            rel = sub.parent.parent.relative_to(topic_dir)
            if str(rel) != ".":
                sub_topic = f"{topic}/{rel.as_posix().replace('/', '_')}"
            for name, (inp, out) in _parse_snapshots(sub).items():
                snapshots[f"{sub_topic}::{name}"] = (inp, out)

        selected: list[tuple[str, str, str]] = []
        for case_name, (inp, out) in sorted(snapshots.items()):
            short_name = case_name.split("::")[-1]
            if short_name in EXCLUDE_CASES:
                continue
            if _code_blocks_reformatted(inp, out):
                continue
            stem = _fixture_stem(topic, short_name)
            selected.append((stem, inp, out))

        if not selected:
            continue

        trivial = all(inp == out for _, inp, out in selected)
        if trivial and len(selected) > 5:
            bundled = _bundle_small_cases(topic, selected)
        elif len(selected) >= 6 and all(len(inp) < 200 and len(out) < 200 for _, inp, out in selected):
            bundled = _bundle_small_cases(topic, selected)
        else:
            bundled = selected

        for stem, before, after in bundled:
            stems.append(stem)
            if not dry_run:
                _write_fixture_pair(stem, before, after)

    return stems


def _bundle_small_cases(
    topic: str,
    cases: list[tuple[str, str, str]],
    *,
    max_bundle: int = 8,
    max_chars: int = 4000,
) -> list[tuple[str, str, str]]:
    if len(cases) <= 3:
        return cases
    bundled: list[tuple[str, str, str]] = []
    chunk: list[tuple[str, str, str]] = []
    chunk_chars = 0

    def flush() -> None:
        nonlocal chunk, chunk_chars
        if not chunk:
            return
        if len(chunk) == 1:
            bundled.append(chunk[0])
        else:
            names = "_".join(stem for stem, _, _ in chunk[:3])
            if len(chunk) > 3:
                names += f"_and_{len(chunk) - 3}_more"
            bundle_stem = names if names.startswith(topic.replace("/", "_")) else f"{topic.replace('/', '_')}_{names}"
            before_parts: list[str] = []
            after_parts: list[str] = []
            for stem, before_text, after_text in chunk:
                before_parts.append(f"<!-- case: {stem} -->\n\n{before_text.rstrip()}\n")
                after_parts.append(f"<!-- case: {stem} -->\n\n{after_text.rstrip()}\n")
            before = "\n".join(before_parts)
            after = "\n".join(after_parts)
            bundled.append((bundle_stem, before, after))
        chunk = []
        chunk_chars = 0

    for name, before, after in cases:
        size = len(before) + len(after)
        if chunk and (len(chunk) >= max_bundle or chunk_chars + size > max_chars):
            flush()
        chunk.append((name, before, after))
        chunk_chars += size
    flush()
    return bundled


def _code_blocks_reformatted(input_text: str, output_text: str) -> bool:
    for raw_in, raw_out in (
        (input_text, output_text),
        (_strip_blockquote_prefix(input_text), _strip_blockquote_prefix(output_text)),
    ):
        in_blocks = _extract_fenced_blocks(raw_in)
        out_blocks = _extract_fenced_blocks(raw_out)
        if len(in_blocks) != len(out_blocks):
            return True
        for (in_lang, in_body), (out_lang, out_body) in zip(in_blocks, out_blocks, strict=True):
            if in_lang != out_lang:
                return True
            if in_lang in ALLOWED_CODE_LANGS:
                continue
            if in_body != out_body:
                return True
    return False


def _extract_fenced_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for match in FENCE_RE.finditer(text):
        lang = match.group("lang").strip().lower()
        body = match.group("body")
        blocks.append((lang, body))
    return blocks


def _fixture_stem(topic: str, case_name: str) -> str:
    stem = Path(case_name).stem
    safe_topic = topic.replace("/", "_")
    raw = f"{safe_topic}_{stem}"
    return re.sub(r'[<>:"/\\|?*]', "-", raw).replace(" ", "_")


def _parse_snapshots(snap_path: Path) -> dict[str, tuple[str, str]]:
    if not snap_path.is_file():
        return {}
    content = snap_path.read_text(encoding="utf-8")
    cases: dict[str, tuple[str, str]] = {}
    for match in SNAPSHOT_ENTRY_RE.finditer(content):
        if match.group("wrap") != PREFERRED_PROSE_WRAP:
            continue
        filename = match.group("filename")
        input_text = _unescape_snapshot(match.group("input"))
        output_text = _unescape_snapshot(match.group("output"))
        cases[filename] = (input_text, output_text)
    return cases


def _strip_blockquote_prefix(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("> "):
            lines.append(line[2:])
        elif line in {">", ">\n"}:
            lines.append("\n" if line.endswith("\n") else "")
        else:
            lines.append(line)
    return "".join(lines)


def _unescape_snapshot(text: str) -> str:
    return text.replace("\\`", "`")


def _write_fixture_pair(stem: str, before: str, after: str) -> None:
    before_path = OUTPUT_DIR / f"{stem}__before.md"
    after_path = OUTPUT_DIR / f"{stem}__after.md"
    before_path.write_text(before.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
    after_path.write_text(after.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    stems = extract(dry_run=dry_run)
    print(f"{'Would write' if dry_run else 'Wrote'} {len(stems)} fixture pairs")
    for stem in stems:
        print(f"  {stem}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
