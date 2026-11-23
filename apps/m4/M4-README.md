# Milestone-4

## Technical brief: an iterable BeautifulSoup

**What it does:** A `BeautifulSoup` object can be used directly in a `for` loop
and visits the whole tree. The implementation is one line, because the library
already had a `Tag.descendants`.

**Why a generator:** A loop over a large document should not need memory for a
list of every node, and it should be possible to stop after the first few nodes.
Following `next_element` gives both for free.

**Trade-off:** The change alters what `for x in soup` means: before it gave the
top-level nodes, now it gives all nodes. Code that relied on the old behavior
will see more nodes. I limited the change to the soup object and left `Tag`
alone, so loops over ordinary tags still give direct children. The price is an
inconsistency: `for x in soup` visits everything, but `for x in soup.p` visits
only the children of `<p>`.
