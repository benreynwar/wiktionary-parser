from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy import orm

from wiktionary_parser.utils import wikitext_to_plaintext as w2p
from wiktionary_parser.db import Base, Session

class Definition(Base):
    __tablename__ = "definitions"
    id = Column(Integer, primary_key=True)
    word_id = Column(Integer, ForeignKey('words.id'))
    order = Column(Integer)
    text = Column(String)
    word = relationship("Word", backref=backref("_definitions", order_by=order))

class Example(Base):
    __tablename__ = "examples"
    id = Column(Integer, primary_key=True)
    definition_id = Column(Integer, ForeignKey('definitions.id'))
    order = Column(Integer)
    text = Column(String)
    definition = relationship("Definition", backref=backref('examples', order_by=order))

class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True)
    discriminator = Column('type', String)
    title = Column(String)
    order = Column(Integer)
    language = Column(String)
    __mapper_args__ = {'polymorphic_on': discriminator}
    __table_args__ = (
        UniqueConstraint(title, discriminator, order),
        )

    def __init__(self, title, order=0):
        """
        definitions is a list of definitions.
        examples is a list of lists of examples. ie. examples[0] is a list of
          examples corresponding to definitions[0].
        """
        self.title = title
        self.language = None
        self.definitions = []
        self.examples = []
        self.order = order

    def setup(self):
        pass

    @orm.reconstructor
    def init_on_load(self):
        self.setup()

    def set_definitions(self, defs):
        def_objs = [Definition(order=i, word=self, text=d)
                    for i, d in enumerate(defs)]
        self._definitions = def_objs;
        
    def get_definitions(self):
        return [def_obj.text for def_obj in self._definitions]

    definitions = property(get_definitions, set_definitions)

    def set_examples(self, examp_lists):
        def_objs = self._definitions
        examp_objs = []
        for i, examps in enumerate(examp_lists):
            def_obj = def_objs[i]
            def_obj.examples = [Example(order=j, definition=def_obj, text=examp)
                                for j, examp in enumerate(examps)]
            
    def get_examples(self):
        data = []
        for d in self._definitions:
            data.append([examp.text for examp in d.examples])
        return data
            
    examples = property(get_examples, set_examples)

    def str_definitions_and_examples(self, template_block={}):
        # Should return alerts
        out = []
        example_lists = self.examples
        len_diff = len(self.definitions) - len(example_lists)
        if len_diff > 0:
            example_lists += [[]] * len_diff
        for definition, examples in zip(self.definitions, example_lists):
            definition = w2p(definition, template_block=template_block)
            out.append(definition.strip())
            for example in examples:
                example = w2p(example, template_block=template_block)
                out.append(' - %s' % example.strip())
        out = '\n'.join(out)
        out = w2p(out)
        return out

    def summary(self):
        out = []
        heading = '%s (%s)' % (self.title, self.typeslug)
        out.append('*' * len(heading))
        out.append(heading)
        out.append('*' * len(heading))
        if self.definitions:
            out.append('Definitions:')
            for i, defi in enumerate(self.definitions):
                out.append('[%s] ' % (i+1) + w2p(defi))
        if self.examples:
            out.append('Examples:')
            for i, exams in enumerate(self.examples):
                for ex in exams:
                    out.append('[%s] ' % (i+1) + w2p(ex))
        return '\n'.join(out)
    
    @classmethod
    def get_and_update(cls, title, order=0, session=None, **kwargs):
        """
        Recover a word from the database.
        """
        if session is None:
            return cls(title, order, **kwargs)
        words = session.query(cls).filter_by(title=title, order=order)
        n_words = words.count()
        if n_words == 0:
            return cls(title, order, **kwargs)
        elif n_words == 1:
            return words[0]
        else:
            import pdb
            pdb.set_trace()
            raise StandardError("Found multiple words with what should be a unique identifier.")

    
