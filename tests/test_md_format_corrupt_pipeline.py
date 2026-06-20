from pathlib import Path

import harrix_pylib as h
from harrix_pylib.md_format.formatter import read_markdown_text

SOURCE = """---
author: Anton Sergienko
lang: en
---

# Title

## Sub

```python
def cleanup() -> None
```

<details>
<summary>Code:</summary>

```python
def cleanup() -> None:
    for tag in REMOVE_TAGS:
        pass
```

</details>
"""


def test_format_yaml_and_markdown_on_r_double_crlf_file(tmp_path: Path) -> None:
    path = tmp_path / "note.md"
    path.write_bytes(SOURCE.replace("\n", "\r\r\n").encode("utf-8"))
    text = read_markdown_text(path)
    formatted = h.md.format_markdown_content(h.md.format_yaml_content(text))
    data = formatted.encode("utf-8")
    assert data.count(b"\r\r\n") == 0
    assert "# Title\r\n\r\n## Sub" in formatted
    assert "for tag in REMOVE_TAGS:\n" in formatted.replace("\r\n", "\n")
