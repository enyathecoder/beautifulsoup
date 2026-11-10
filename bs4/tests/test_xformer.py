import pytest
from bs4 import BeautifulSoup, SoupReplacer, SoupStrainer

PARSERS = ["html.parser", "lxml"]

HTML_DOC = (
    '<html><body><p class="intro big" id="x">Hello <b class="k">bold '
    "<b>nested</b></b> world</p><p>Plain <i>italic</i> and "
    "<b>more bold</b><br></p></body></html>"
)

def _soup(markup, parser, **kwargs):
    if parser == "lxml":
        pytest.importorskip("lxml")
    return BeautifulSoup(markup, parser, **kwargs)


class TestSoupReplacerXformers:
    @pytest.mark.parametrize("parser", PARSERS)
    def test_name_xformer(self, parser):
        # The function sees each tag and returns its new name. End tags
        # follow, and the result equals renaming after parsing.
        def b_to_blockquote(tag):
            return "blockquote" if tag.name == "b" else tag.name

        replacer = SoupReplacer(name_xformer=b_to_blockquote)
        during = _soup(HTML_DOC, parser, replacer=replacer)

        assert during.find_all("b") == []
        assert len(during.find_all("blockquote")) == 3
        assert "</b>" not in during.decode()
        assert during.find("blockquote")["class"] == ["k"]

        after = _soup(HTML_DOC, parser)
        for tag in after.find_all("b"):
            tag.name = "blockquote"
        assert during.decode() == after.decode()

    @pytest.mark.parametrize("parser", PARSERS)
    def test_attrs_xformer(self, parser):
        # The function returns a tag's new attributes. Returning None
        # leaves a tag alone. This is Milestone-1 task 7 done during
        # parsing: every <p> gets class="test".
        def add_test_class(tag):
            if tag.name == "p":
                return {**tag.attrs, "class": "test"}
            return None

        replacer = SoupReplacer(attrs_xformer=add_test_class)
        during = _soup(HTML_DOC, parser, replacer=replacer)

        paragraphs = during.find_all("p")
        assert len(paragraphs) == 2
        # "class" is multi-valued in HTML, so it is stored as a list,
        # exactly as for a class found in the document.
        assert all(p["class"] == ["test"] for p in paragraphs)
        assert paragraphs[0]["id"] == "x"  # other attributes are kept
        assert during.find("b")["class"] == ["k"]  # other tags untouched

        after = _soup(HTML_DOC, parser)
        for p_tag in after.find_all("p"):
            p_tag["class"] = "test"
        assert during.prettify() == after.prettify()

    @pytest.mark.parametrize("parser", PARSERS)
    def test_xformer_modifies_tag_in_place(self, parser):
        # xformer returns nothing; it changes the tag it is given.
        def remove_class_attr(tag):
            if "class" in tag.attrs:
                del tag.attrs["class"]

        replacer = SoupReplacer(xformer=remove_class_attr)
        soup = _soup(HTML_DOC, parser, replacer=replacer)

        assert soup.find_all(class_=True) == []
        assert soup.find("p")["id"] == "x"  # only class was removed
        assert soup.find("p").decode().startswith('<p id="x">')
        assert "class=" not in soup.decode()

    @pytest.mark.parametrize("parser", PARSERS)
    def test_xformer_can_rename_tag(self, parser):
        # An xformer that changes tag.name leaves the parser believing
        # the tag is still called "b". The end tags must still close it.
        def rename(tag):
            if tag.name == "b":
                tag.name = "blockquote"

        soup = _soup(HTML_DOC, parser, replacer=SoupReplacer(xformer=rename))

        assert soup.find_all("b") == []
        outer = soup.find("blockquote")
        assert outer.find("blockquote").string == "nested"
        # Text after the closing </b> is back outside the blockquote.
        assert outer.next_sibling == " world"
        assert soup.decode().count("<blockquote") == 3
        assert soup.decode().count("</blockquote>") == 3

    @pytest.mark.parametrize("parser", PARSERS)
    def test_functions_run_in_order_and_combine(self, parser):
        # name_xformer and attrs_xformer both see the tag as it was in the document;
        # xformer runs last and sees the new name and attributes.
        seen = {}

        def name_xformer(tag):
            seen["name"] = (tag.name, dict(tag.attrs))
            return "strong" if tag.name == "b" else None

        def attrs_xformer(tag):
            seen["attrs"] = (tag.name, dict(tag.attrs))
            if tag.name == "b":
                return {**tag.attrs, "data-was": tag.name}
            return None

        def xformer(tag):
            if tag.name == "strong":
                seen["xformer"] = (tag.name, dict(tag.attrs))

        replacer = SoupReplacer(name_xformer=name_xformer, attrs_xformer=attrs_xformer, xformer=xformer)
        soup = _soup('<p><b id="1">x</b></p>', parser, replacer=replacer)

        assert seen["name"] == ("b", {"id": "1"})
        assert seen["attrs"] == ("b", {"id": "1"})
        assert seen["xformer"] == ("strong", {"id": "1", "data-was": "b"})
        assert soup.find("strong").attrs == {"id": "1", "data-was": "b"}

        # The Milestone-2 pair still works, alone and with the new
        # functions, and so does parse_only.
        pair = SoupReplacer("b", "blockquote")
        assert _soup(HTML_DOC, parser, replacer=pair).find("b") is None
        both = SoupReplacer(
            "b", "blockquote", attrs_xformer=lambda t: {"data-x": "1"}
        )
        found = _soup(HTML_DOC, parser, replacer=both).find("blockquote")
        assert found.attrs == {"data-x": "1"}
        strained = _soup(
            HTML_DOC,
            parser,
            replacer=SoupReplacer(xformer=lambda t: t.attrs.update(seen="1")),
            parse_only=SoupStrainer("i"),
        )
        assert strained.decode() == '<i seen="1">italic</i>'

    def test_invalid_arguments(self):
        # Nothing to do, or an incomplete or contradictory request.
        with pytest.raises(ValueError):
            SoupReplacer()
        with pytest.raises(ValueError):
            SoupReplacer("b")
        with pytest.raises(ValueError):
            SoupReplacer("b", "blockquote", name_xformer=lambda tag: "x")
        # The transformers must be functions.
        with pytest.raises(TypeError):
            SoupReplacer(xformer="not a function")
        with pytest.raises(TypeError):
            SoupReplacer(attrs_xformer={"class": "test"})

        # A function that returns the wrong thing is reported clearly.
        bad_name = SoupReplacer(name_xformer=lambda tag: 42)
        with pytest.raises(TypeError):
            BeautifulSoup("<b>x</b>", "html.parser", replacer=bad_name)
        bad_attrs = SoupReplacer(attrs_xformer=lambda tag: "class=test")
        with pytest.raises(TypeError):
            BeautifulSoup("<b>x</b>", "html.parser", replacer=bad_attrs)