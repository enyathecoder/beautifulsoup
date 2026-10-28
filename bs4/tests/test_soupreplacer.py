"""Tests for SoupReplacer, which renames tags while a document is parsed."""

import pytest

from bs4 import BeautifulSoup, SoupReplacer

PARSERS = ["html.parser", "lxml"]

HTML_DOC = (
    '<html><body><p class="intro">Hello <b id="x">bold <b>nested</b></b> '
    "world</p><p>Plain <i>italic</i> and <b>more bold</b></p></body></html>"
)


def _soup(markup, parser, **kwargs):
    if parser == "lxml":
        pytest.importorskip("lxml")
    return BeautifulSoup(markup, parser, **kwargs)


class TestSoupReplacer:
    @pytest.mark.parametrize("parser", PARSERS)
    def test_replaces_start_and_end_tags(self, parser):
        # Every <b> becomes <blockquote>; attributes, nesting, text and
        # all the other tags are left alone.
        replacer = SoupReplacer("b", "blockquote")
        soup = _soup(HTML_DOC, parser, replacer=replacer)

        assert soup.find_all("b") == []
        assert len(soup.find_all("blockquote")) == 3
        assert soup.find("blockquote")["id"] == "x"
        assert soup.find("blockquote").find("blockquote").string == "nested"
        assert soup.find("i").string == "italic"
        assert soup.p["class"] == ["intro"]
        # The end tags were renamed too, so the markup is well formed.
        assert "</b>" not in soup.decode()
        assert soup.decode().count("</blockquote>") == 3

    @pytest.mark.parametrize("parser", PARSERS)
    def test_same_result_as_renaming_after_parsing(self, parser):
        # Renaming during parsing must give exactly the tree that the
        # Milestone-1 approach (parse, then rename every tag) gives.
        after = _soup(HTML_DOC, parser)
        for tag in after.find_all("b"):
            tag.name = "blockquote"

        during = _soup(HTML_DOC, parser, replacer=SoupReplacer("b", "blockquote"))

        assert during.decode() == after.decode()
        assert during.prettify() == after.prettify()

        # Without a replacer nothing changes.
        assert len(_soup(HTML_DOC, parser).find_all("b")) == 3