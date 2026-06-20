---
author: Anton Sergienko

author-email: anton.b.sergienko@gmail.com

lang: en
---

# 📄 File `cleanup.py`

## 🔧 Function `cleanup`

```python

def cleanup(root: etree._Element) -> None

```

Remove metadata elements and deprecated attributes from the SVG tree.

<details>

<summary>Code:</summary>

```python

def cleanup(root: etree._Element) -> None:



    for tag in REMOVE_TAGS:



        for elem in root.iter(tag):



            parent = elem.getparent()



            if parent is not None:



                parent.remove(elem)

```

</details>
