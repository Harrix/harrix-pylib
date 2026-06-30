<!-- case: yaml_complex -->

---
- hello: world
- 123
---

# something

<!-- case: yaml_empty-2 -->

---
---

Content

<!-- case: yaml_empty -->

---
---

<!-- case: yaml_simple-2 -->

---
hello: world
---

Content

<!-- case: yaml_simple -->

---
hello: world
---

<!-- case: yaml_trailing-spaces -->

---
v spaces
---

This paragraph should be considered part of the _markdown_ instead of _yaml_.

---
