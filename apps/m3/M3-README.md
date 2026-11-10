# Milestone-3

## Technical brief: SoupReplacer in Milestone 2 vs. Milestone 3

**Milestone 2:** `SoupReplacer(og_tag, alt_tag)` renames every tag of one name to
another during parsing. It is easy to explain, easy to test and hard to misuse,
but it can only do one fixed rename.

**Milestone 3:** `name_xformer` returns a new name, `attrs_xformer` returns new attributes, and `xformer` edits the tag directly.
The price is more complexity. The hardest part to implement was end
tags: in Milestone 2, `</b>` could be renamed with the same simple lookup, but
in Milestone 3 the new name can come from any function, so the parser has to
remember each tag's original name to close the right tag. `xformer` is also the
riskiest option, because it can change anything about the tag.

**Recommendation:** Extend BeautifulSoup with the Milestone 3 interface and keep the Milestone 2 form in the same class. Reasons:

1. Milestone 3 handles real needs: tasks 7 of Milestone 1 work through
   one API.
2. Keeping the shortcut costs nothing, and simple cases stay one line.
3. The risk can be managed with documentation and tests: state the order in which
   the functions run, and state that `xformer` should only change the name and
   attributes of the tag it is given.