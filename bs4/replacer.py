from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional

if TYPE_CHECKING:
    from .element import Tag

#: A function that takes a tag and returns the tag's new name.
_NameXformer = Callable[["Tag"], Optional[str]]
#: A function that takes a tag and returns the tag's new attributes.
_AttrsXformer = Callable[["Tag"], Optional[Mapping[str, Any]]]
#: A function that takes a tag and modifies it in place. Returns nothing.
_Xformer = Callable[["Tag"], None]


class SoupReplacer(object):
    """Transforms tags *while the document is parsed*.

    Like `SoupStrainer`, a `SoupReplacer` is passed to the
    `BeautifulSoup` constructor, here as the ``replacer`` argument. Each
    tag is transformed as soon as the parser creates it, so the tree
    never has to be traversed a second time.

    There are two ways to build one.

    **Replacement pair (Milestone 2).** Every tag named ``og_tag`` is
    renamed ``alt_tag``::

        b_to_blockquote = SoupReplacer("b", "blockquote")

    **Transformer functions (Milestone 3).** Each function is given the
    tag that was just created::

        # name_xformer returns the tag's new name.
        SoupReplacer(name_xformer=lambda tag: "blockquote" if tag.name == "b" else tag.name)

        # attrs_xformer returns the tag's new attributes (a dict).
        SoupReplacer(attrs_xformer=lambda tag: {**tag.attrs, "class": "test"})

        # xformer changes the tag in place and returns nothing.
        def remove_class_attr(tag):
            if "class" in tag.attrs:
                del tag.attrs["class"]
        SoupReplacer(xformer=remove_class_attr)

    For every tag the functions run in this order:

    1. ``name_xformer`` and ``attrs_xformer`` are both called with the
       tag exactly as it appeared in the document. Their results are
       then applied. A function that returns ``None`` leaves that part
       of the tag unchanged.
    2. ``xformer`` is called last, with the tag that now carries the new
       name and attributes. It may change the tag in any way.

    The ``og_tag``/``alt_tag`` pair can be combined with
    ``attrs_xformer`` and ``xformer``, but not with ``name_xformer``,
    since both would decide the tag's name.

    :param og_tag: The name of the tags to be replaced.
    :param alt_tag: The name those tags will have in the parse tree.
    :param name_xformer: A function ``f(tag) -> str`` giving a tag's
        new name.
    :param attrs_xformer: A function ``f(tag) -> dict`` giving a tag's
        new attributes.
    :param xformer: A function ``f(tag) -> None`` that modifies a tag
        in place.
    """

    og_tag: Optional[str]
    alt_tag: Optional[str]
    name_xformer: Optional[_NameXformer]
    attrs_xformer: Optional[_AttrsXformer]
    xformer: Optional[_Xformer]

    def __init__(
            self,
            og_tag: Optional[str] = None,
            alt_tag: Optional[str] = None,
            *,
            name_xformer: Optional[_NameXformer] = None,
            attrs_xformer: Optional[_AttrsXformer] = None,
            xformer: Optional[_Xformer] = None,
    ):
        # --- the Milestone 2 replacement pair ---
        if (og_tag is None) != (alt_tag is None):
            raise ValueError("og_tag and alt_tag must be given together.")
        if og_tag is not None and alt_tag is not None:
            if not isinstance(og_tag, str) or not isinstance(alt_tag, str):
                raise TypeError("og_tag and alt_tag must both be strings.")
            if not og_tag or not alt_tag:
                raise ValueError("og_tag and alt_tag must not be empty.")
            if name_xformer is not None:
                raise ValueError(
                    "Give either og_tag/alt_tag or name_xformer, not both."
                )

        # --- the Milestone 3 transformer functions ---
        for label, func in (
                ("name_xformer", name_xformer),
                ("attrs_xformer", attrs_xformer),
                ("xformer", xformer),
        ):
            if func is not None and not callable(func):
                raise TypeError(f"{label} must be a function.")

        if og_tag is None and not (name_xformer or attrs_xformer or xformer):
            raise ValueError(
                "SoupReplacer needs og_tag and alt_tag, or at least one of "
                "name_xformer, attrs_xformer and xformer."
            )

        self.og_tag = og_tag
        self.alt_tag = alt_tag
        self.name_xformer = name_xformer
        self.attrs_xformer = attrs_xformer
        self.xformer = xformer

    def replace_name(self, name: str) -> str:
        """Return the name a tag called ``name`` gets from the
        ``og_tag``/``alt_tag`` pair.

        :param name: The tag name found in the document.
        :return: ``alt_tag`` if ``name`` is ``og_tag``; otherwise ``name``
            unchanged.
        """
        if self.og_tag is not None and name == self.og_tag:
            return self.alt_tag  # type: ignore[return-value]
        return name

    def get_new_name(self, tag: Tag) -> Optional[str]:
        """Work out the new name of a freshly created tag.

        :param tag: The tag, as it appeared in the document.
        :return: The new name, or None if the name should not change.

        :meta private:
        """
        if self.og_tag is not None:
            new_name = self.replace_name(tag.name)
        elif self.name_xformer is not None:
            new_name = self.name_xformer(tag)
        else:
            return None
        if new_name is None:
            return None
        if not isinstance(new_name, str) or not new_name:
            raise TypeError(
                "name_xformer must return a non-empty string or None, "
                f"not {new_name!r}."
            )
        return new_name

    def get_new_attrs(self, tag: Tag) -> Optional[Mapping[str, Any]]:
        """Work out the new attributes of a freshly created tag.

        :param tag: The tag, as it appeared in the document.
        :return: The new attributes, or None if they should not change.

        :meta private:
        """
        if self.attrs_xformer is None:
            return None
        new_attrs = self.attrs_xformer(tag)
        if new_attrs is not None and not isinstance(new_attrs, Mapping):
            raise TypeError(
                "attrs_xformer must return a dict of attributes or None, "
                f"not {new_attrs!r}."
            )
        return new_attrs

    def run_xformer(self, tag: Tag) -> None:
        """Let ``xformer`` modify a tag in place, if there is one.

        :param tag: The tag, after the new name and attributes were applied.

        :meta private:
        """
        if self.xformer is not None:
            self.xformer(tag)

    def __repr__(self) -> str:
        if self.og_tag is not None:
            return f"SoupReplacer({self.og_tag!r}, {self.alt_tag!r})"
        given = [
            label
            for label, func in (
                ("name_xformer", self.name_xformer),
                ("attrs_xformer", self.attrs_xformer),
                ("xformer", self.xformer),
            )
            if func is not None
        ]
        return f"SoupReplacer({', '.join(given)})"