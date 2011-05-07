
class Word(object):

    def __init__(self, title):
        """
        definitions is a list of defintions.
        examples is a list of lists of examples. ie. examples[0] is a list of
          examples corresponding to definitions[0].
        """
        self.title = title
        self.language = None
        self.definitions = []
        self.examples = []

    def summary(self):
        out = []
        heading = '%s (%s)' % (self.title, self.typeslug)
        out.append('*' * len(heading))
        out.append(heading)
        out.append('*' * len(heading))
        if self.definitions:
            out.append('Definitions:')
            for i, defi in enumerate(self.definitions):
                out.append('[%s] ' % i + defi)
        if self.examples:
            out.append('Examples:')
            for i, exams in enumerate(self.examples):
                for ex in exams:
                    out.append('[%s] ' % i + ex)
        return '\n'.join(out)
