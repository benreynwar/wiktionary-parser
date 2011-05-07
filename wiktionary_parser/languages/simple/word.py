from wiktionary_parser.word import Word

class simpleWord(Word):
    
    def __init__(self, *args, **kwargs):
        super(simpleWord, self).__init__(*args, **kwargs)
        self.language = 'english'


class simpleNoun(simpleWord):
    
    typeslug = 'noun'

    def __init__(self, *args, **kwargs):
        super(simpleNoun, self).__init__(*args, **kwargs)
        self.plural = None

    def summary(self):
        out = [super(simpleNoun, self).summary()]
        if self.plural is not None:
            out.append('Plural:')
            out.append('   %s' % self.plural)
        return '\n'.join(out)

class simpleVerb(simpleWord):
    
    typeslug = 'verb'

    def __init__(self, *args, **kwargs):
        super(simpleVerb, self).__init__(*args, **kwargs)
        
