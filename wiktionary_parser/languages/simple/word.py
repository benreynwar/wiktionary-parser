from wiktionary_parser.word import Word

class simpleWord(Word):
    
    def __init__(self, *args, **kwargs):
        super(simpleWord, self).__init__(*args, **kwargs)
        self.language = 'english'


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
        
