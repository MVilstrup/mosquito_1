class Page():
    def __init__(self, reponse):
        raise NotImplementedError('subclasses must override __init__()!')

    def get_body(self):
        raise NotImplementedError('subclasses must override get_body()!')

    def get_links(self):
        raise NotImplementedError('subclasses must override get_links()!')

    def get_text(self):
        raise NotImplementedError('subclasses must override get_text()!')
