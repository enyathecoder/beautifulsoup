import collections.abc
import itertools

import pytest

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString, Tag

PARSERS = ["html.parser", "lxml"]


def _soup(markup, parser="html.parser"):
    if parser == "lxml":
        pytest.importorskip("lxml")
    return BeautifulSoup(markup, parser)


def _describe(node):
    # Tags are shown by name, everything else by its text.
    return node.name if isinstance(node, Tag) else str(node)


class TestSoupIteration:
    def test_visits_every_node_in_document_order(self):
        # Not just the top level: every tag and string, parents before
        # their children, the way the markup is written.
        soup = _soup("<p>a<b>x<i>y</i></b>z</p><div>w</div>")

        assert [_describe(n) for n in soup] == [
            "p", "a", "b", "x", "i", "y", "z", "div", "w",
        ]
        assert list(soup) == list(soup.descendants)
        # The soup object itself is not one of its nodes.
        assert all(node is not soup for node in soup)

    def test_yields_every_kind_of_node(self):
        soup = _soup("<!DOCTYPE html><p>text<!-- note --><b>bold</b></p>")

        nodes = list(soup)
        kinds = {type(n) for n in nodes}
        assert {Doctype, Tag, NavigableString, Comment} <= kinds

        by_kind = {type(n): n for n in nodes}
        assert by_kind[Doctype] == "html"
        assert by_kind[Comment] == " note "
        assert [n.name for n in nodes if isinstance(n, Tag)] == ["p", "b"]
        # A Comment is a NavigableString too, so it is easy to tell apart
        # only by checking the more specific class first.
        assert isinstance(by_kind[Comment], NavigableString)

    def test_iteration_is_lazy(self):
        # The nodes come one at a time from an iterator. They are not
        # handed out from a list that was built up front.
        soup = _soup("<ul>" + "<li>item</li>" * 1000 + "</ul>")

        iterator = iter(soup)
        assert isinstance(iterator, collections.abc.Iterator)
        assert not isinstance(iterator, (list, tuple))
        assert iter(iterator) is iterator  # an iterator, not a container

        assert next(iterator).name == "ul"
        assert next(iterator).name == "li"
        assert next(iterator) == "item"
        assert next(iterator).name == "li"  # picks up where it stopped

        # The strongest sign that nothing was collected up front: a node
        # that changes after the iteration has started is seen as it is
        # *now*. A list built at the start would still hold the old node.
        soup = _soup("<p>a</p><p>b</p>")
        iterator = iter(soup)
        assert next(iterator).name == "p"
        soup.find_all("p")[1].string = "CHANGED"
        assert [str(n) for n in iterator if isinstance(n, NavigableString)] == [
            "a",
            "CHANGED",
        ]

        soup = _soup("<ul>" + "<li>item</li>" * 1000 + "</ul>")
        # Stopping early is allowed and gives the first nodes of the
        # full traversal.
        assert list(itertools.islice(soup, 5)) == list(soup.descendants)[:5]
        # Every loop starts a fresh traversal.
        assert list(soup) == list(soup)
        # 1 <ul> + 1000 <li> + 1000 strings.
        assert sum(1 for _ in soup) == 2001

    def test_empty_text_only_and_deeply_nested_documents(self):
        # Nothing to visit.
        assert list(_soup("")) == []

        # A document that is only text has one node, a string.
        only_text = list(_soup("just text"))
        assert only_text == ["just text"]
        assert type(only_text[0]) is NavigableString

        # Very deep nesting is walked without recursion errors.
        depth = 3000
        deep = _soup("<div>" * depth + "bottom" + "</div>" * depth)
        nodes = list(deep)
        assert len(nodes) == depth + 1
        assert nodes[-1] == "bottom"

    @pytest.mark.parametrize("parser", PARSERS)
    def test_parsers_and_tag_iteration_unchanged(self, parser):
        soup = _soup(
            "<html><body><p id='a'>one<b>two</b></p><p>three</p></body></html>",
            parser,
        )

        names = [_describe(n) for n in soup]
        assert names == [
            "html", "body", "p", "one", "b", "two", "p", "three",
        ]
        assert list(soup) == list(soup.descendants)

        # Only the soup object changed. Iterating over a Tag still gives
        # just its direct children, as before.
        first_p = soup.find("p")
        assert [_describe(n) for n in first_p] == ["one", "b"]
        assert list(first_p) == first_p.contents