from lxml.html import parse


class Extractor(object):

    def __init__(self):
        pass

    def _extractLinks(self, page):
        """ Extract hrefs """
        dom = parse(page).getroot()
        dom.make_links_absolute()
        links = dom.cssselect('a')
        return [link.get('href') for link in links if link.get('href')]
