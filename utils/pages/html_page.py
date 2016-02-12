from .page import Page
import cgi


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

    def get_body(self):
        return self._body

    def get_links(self):
        return self._links

    def get_text(self):
        return self._text
