"""
Define German Word objects.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from wiktionary_parser.word import Word
from wiktionary_parser.languages.simple.templates import simpleTemplateBlock

from wiktionary_parser.db import Base, Session

class simpleWord(Word):

    __mapper_args__ = {'polymorphic_identity': 'simpleWord'}
    typeslug = 'word'

    def __init__(self, *args, **kwargs):
        if 'tags' in kwargs:
            tags = kwargs.pop('tags')
        super(simpleWord, self).__init__(*args, **kwargs)
        self.language = 'english'
        self.tags = tags

    def str_definitions_and_examples(self):
        return super(simpleWord, self).str_definitions_and_examples(
            template_block=simpleTemplateBlock)

    def summary(self):
        out = [super(simpleWord, self).summary()]
        if self.tags:
            out.append('Tags: %s' % ", ".join(self.tags))
        return '\n'.join(out)
            

class simpleNoun(simpleWord):
    
    __mapper_args__ = {'polymorphic_identity': 'simpleNoun'}
    typeslug = 'noun'

    def __init__(self, *args, **kwargs):
        super(simpleNoun, self).__init__(*args, **kwargs)
        self.singulars = None
        self.plurals = None

    def summary(self):
        out = [super(simpleNoun, self).summary()]
        if self.singulars:
            out.append('Singular: %s' % ', '.join(self.singulars))
        else:
            out.append('No singular.')
        if self.plurals:
            out.append('Plural: %s' % ', '.join(self.plurals))
        else:
            out.append('No plural.')
        return '\n'.join(out)

class simpleVerb(simpleWord):
    
    __mapper_args__ = {'polymorphic_identity': 'simpleVerb'}
    typeslug = 'verb'

    def __init__(self, *args, **kwargs):
        super(simpleVerb, self).__init__(*args, **kwargs)
        self.setup()

    def setup(self):
        self.conjugations = None

    def summary(self):
        out = [super(simpleVerb, self).summary()]
        if self.conjugations:
            for i, conj in enumerate(self.conjugations):
                out.append('Conjugation %s:' % (i+1))
                out.append(conj.summary())
        return '\n'.join(out)

class simpleAdjective(simpleWord):

    __mapper_args__ = {'polymorphic_identity': 'simpleAdjective'}
    typeslug = 'adjective'

    def __init__(self, *args, **kwargs):
        super(simpleAdjective, self).__init__(*args, **kwargs)
        self.comparative = None
        self.superlative = None
        
    def summary(self):
        out = [super(simpleAdjective, self).summary()]
        out.append('Comparative: %s' % self.comparative)
        out.append('Superlative: %s' % self.superlative)
        return '\n'.join(out)

class simpleOther(simpleWord):
    __mapper_args__ = {'polymorphic_identity': 'simpleOther'}
    typeslug = 'other'

class simpleDeterminer(simpleWord):
    __mapper_args__ = {'polymorphic_identity': 'simpleDeterminer'}
    typeslug = 'determiner'

class simplePreposition(simpleWord):
    __mapper_args__ = {'polymorphic_identity': 'simplePreposition'}
    typeslug = "preposition"

class simpleInterjection(simpleWord):
    __mapper_args__ = {'polymorphic_identity': 'simpleInterjection'}
    typeslug = "interjection"

class simpleSubordinator(simpleWord):
    __mapper_args__ = {'polymorphic_identity': 'simpleSubordinator'}
    typeslug = "subordinator"

class simpleConjunction(simpleWord):
    typeslug = "conjunction"

class simpleAdverb(simpleAdjective):
    typeslug = "adverb"

class simplePronoun(simpleWord):
    typeslug = "pronoun"

class simpleCoordinator(simpleWord):
    typeslug = "coordinator"

