from .page import Page
import cgi
import asyncio
import lxml.html
import nltk


class HTMLPage(Page):
    def __init__(self, response):
        if response.status != 200:
            raise ValueError(
                "The response shold be 200 for the HTML page to be parsed")
        content_type = response.headers.get('content-type')

        if not content_type:
            raise ValueError("Content type could not be determined")

        content_type, pdict = cgi.parse_header(content_type)
        if not content_type == "text/html":
            raise ValueError("Only HTML documents are accepted")

        self._body = yield from response.text()

    @asyncio.coroutine
    def body(self):
        return self._body

    @asyncio.coroutine
    def links(self):
        dom = lxml.html.fromstring(self_body)
        for link in dom.xpath('//a/@href'):
            yield link

    @asyncio.coroutine
    def text(self):
        yield from nltk.clean_html(self._body)
