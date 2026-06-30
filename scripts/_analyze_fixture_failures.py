"""Analyze fixture test failures by category."""

from __future__ import annotations

from pathlib import Path

from harrix_pylib.md_format.formatter import format_markdown_content

ROOT = Path(__file__).resolve().parents[1] / "tests" / "data" / "md_format"


def _looks_like_wrap_only(before: str, after: str, result: str) -> bool:
    if before.replace("\n", " ") == after.replace("\n", " "):
        return False
    collapsed_before = "".join(before.split())
    collapsed_after = "".join(after.split())
    collapsed_result = "".join(result.split())
    return collapsed_result == collapsed_before and collapsed_after != collapsed_before


def main() -> None:
    identity_fail = []
    wrap_only = []
    other_fail = []
    passed = []

    for before_path in sorted(ROOT.glob("*__before.md")):
        stem = before_path.name[: -len("__before.md")]
        after_path = ROOT / f"{stem}__after.md"
        if not after_path.is_file():
            continue
        before = before_path.read_text(encoding="utf-8")
        after = after_path.read_text(encoding="utf-8")
        result = format_markdown_content(before, end_of_line="lf", prose_wrap="always", print_width=80)
        if result == after:
            passed.append(stem)
            continue
        if before == after:
            identity_fail.append(stem)
        elif _looks_like_wrap_only(before, after, result):
            wrap_only.append(stem)
        else:
            other_fail.append(stem)

    print(f"passed: {len(passed)}")
    print(f"identity_fail (before==after but formatter changes): {len(identity_fail)}")
    for s in identity_fail:
        print(f"  {s}")
    print(f"wrap_only: {len(wrap_only)}")
    for s in wrap_only:
        print(f"  {s}")
    print(f"other_fail: {len(other_fail)}")
    for s in other_fail:
        print(f"  {s}")


if __name__ == "__main__":
    main()
