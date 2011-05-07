from sections import Level2Block, ChildrenSection


class Word(object):
    def __init__(self, title):
        self.title = title
        self.examples = []
        self.meanings = []


class Page(ChildrenSection):
    """
    The information contained in a wiktionary page.
    Takes care of the first level of processing.
    """

    def __init__(self, title, text):
        super(Page, self).__init__(text=text)
        self.title = title
        self.words = []
        self.property_dict['title'] = title
        self.property_dict['page'] = self
        self.property_dict['alerts'] = set([])
        
    def page(self):
        return self
    
