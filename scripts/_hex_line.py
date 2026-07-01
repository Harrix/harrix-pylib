from pathlib import Path

lines = Path("tests/data/md_format/link_title__before.md").read_text(encoding="utf-8").splitlines()
for idx in [4, 8, 12, 16, 20, 26]:
    line = lines[idx]
    q = line.index('"')
    part = line[q:]
    Path("_tmp_hex.txt").open("a", encoding="utf-8").write(
        f"line {idx+1}: {line}\n  {part}\n  {[hex(ord(c)) for c in part]}\n\n"
    )
