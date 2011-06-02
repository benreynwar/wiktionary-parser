from wiktionary_parser.word import Word
from wiktionary_parser.languages.simple.templates import simpleTemplateBlock

class simpleWord(Word):

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
    
    typeslug = 'verb'

    def __init__(self, *args, **kwargs):
        super(simpleVerb, self).__init__(*args, **kwargs)
        self.conjugations = None

    def summary(self):
        out = [super(simpleVerb, self).summary()]
        if self.conjugations:
            for i, conj in enumerate(self.conjugations):
                out.append('Conjugation %s:' % (i+1))
                out.append(conj.summary())
        return '\n'.join(out)

class simpleAdjective(simpleWord):

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

class simpleDeterminer(simpleWord):
    typeslug = 'determiner'

class simplePreposition(simpleWord):
    typeslug = "preposition"

class simpleInterjection(simpleWord):
    typeslug = "interjection"

class simpleSubordinator(simpleWord):
    typeslug = "subordinator"

class simpleConjunction(simpleWord):
    typeslug = "conjunction"

class simpleAdverb(simpleAdjective):
    typeslug = "adverb"

class simplePronoun(simpleWord):
    typeslug = "pronoun"

class simpleCoordinator(simpleWord):
    typeslug = "coordinator"

