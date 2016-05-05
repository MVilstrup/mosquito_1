class Extractor(object):
    """docstring for Extractor"""

    def __init__(self, tag, attribute, type="html", unique=False):
        super(Extractor, self).__init__()
        self.scan_tag = tag
        self.scan_attr = attr
        self.unique = unique
        self.select = cssselect.CSSSelector(tag)

    async def get_all(self):
        raise NotImplementedError("get_all should be implemented")

    async def get_first(self):
        raise NotImplementedError("get_first should be implemented")
