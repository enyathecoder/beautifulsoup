from __future__ import annotations

class SoupReplacer(object):
    """Replaces one tag name with another *while the document is parsed*.

    Like `SoupStrainer`, a `SoupReplacer` is passed to the
    `BeautifulSoup` constructor, here as the ``replacer`` argument. Every
    start tag and end tag named ``og_tag`` is turned into ``alt_tag`` as
    the parse tree is being built, so the tree never has to be traversed
    a second time to rename tags::

        b_to_blockquote = SoupReplacer("b", "blockquote")
        soup = BeautifulSoup(html_doc, replacer=b_to_blockquote)

    :param og_tag: The name of the tags to be replaced.
    :param alt_tag: The name those tags will have in the parse tree.
    """

    og_tag: str
    alt_tag: str

    def __init__(self, og_tag: str, alt_tag: str):
        if not isinstance(og_tag, str) or not isinstance(alt_tag, str):
            raise TypeError("og_tag and alt_tag must both be strings.")
        if not og_tag or not alt_tag:
            raise ValueError("og_tag and alt_tag must not be empty.")
        self.og_tag = og_tag
        self.alt_tag = alt_tag

    def replace_name(self, name: str) -> str:
        """Return the name a tag called ``name`` should have in the tree.

        :param name: The tag name found in the document.
        :return: ``alt_tag`` if ``name`` is ``og_tag``; otherwise ``name``
            unchanged.
        """
        if name == self.og_tag:
            return self.alt_tag
        return name

    def __repr__(self) -> str:
        return f"SoupReplacer({self.og_tag!r}, {self.alt_tag!r})"