from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import orm

from wiktionary_parser.sections import Level2Block, ChildrenSection
from wiktionary_parser.db import Base

class Page(ChildrenSection, Base):
    """
    The information contained in a wiktionary page.
    Takes care of the first level of processing.
    """

    __tablename__ = 'pages'
    title = Column(String, primary_key=True)
    language = Column(String, primary_key=True)
    discriminator = Column('type', String)
    text = Column(Text)
    revision_id = Column(Integer)
    __mapper_args__ = {'polymorphic_on': discriminator}

    def __init__(self, title, text, revision_id=0):
        ChildrenSection.__init__(self, text=text)
        self.title = title
        self.revision_id = revision_id
        self.words = []
        # wordtypes keeps track of how many words of each type are on the page.
        # If we have two words of the same type we use their order as an identifier.
        self.wordtypes = {}
        self.property_dict['title'] = title
        self.property_dict['page'] = self
        self.property_dict['alerts'] = set([])
        self.needssaving = False

    @orm.reconstructor
    def init_on_load(self):
        self.__init__(self.title, self.text, self.revision_id)
        
    @classmethod
    def get(cls, session, title):
        if session is None:
            return None
        language = cls.class_language
        page = session.query(cls).get((title, language))
        return page

    @classmethod
    def get_and_update(cls, session, title, revision_id, text):
        page = cls.get(session, title)
        if page is None:
            page = cls(title, text, revision_id)
        else:
            page.update(revision_id, text)
        return page

    def update(self, revision_id, text):
        if revision_id > self.revision_id:
            self.revision_id = revision_id
            self.text = text
            self.needssaving = True

    def page(self):
        return self
    
