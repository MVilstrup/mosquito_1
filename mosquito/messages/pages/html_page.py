from .page import Page
import cgi
import asyncio
import nltk
from mosquito.messages import URL
from lxml.html import document_fromstring


class HTMLPage(Page):

    def __init__(self, response=None, instance=None):
        if response is None and instance is None:
            raise ValueError(
                "Either a response or an instance has to be provided")

        if instance is not None:
            self.decode(instance)
        else:
            if response.status != 200:
                raise ValueError(
                    "The response shold be 200 for the HTML page to be parsed")

            content_type = response.headers.get('content-type')
            if not content_type:
                raise ValueError("Content type could not be determined")

            content_type, pdict = cgi.parse_header(content_type)
            if not content_type == "text/html":
                raise ValueError("Only HTML documents are accepted")

            self._body = response.text
            self._encoding = pdict.get("charset")
            self.url = URL(url=response.url)

    def body(self):
        return self._body

    def links(self):
        dom = document_fromstring(self._body)
        dom.make_links_absolute(self.url.to_string())
        for link in dom.xpath('//a/@href'):
            try:
                yield URL(url=link)
            except:
                continue

    def text(self):
        yield from nltk.clean_html(self._body)
