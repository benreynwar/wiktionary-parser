from wiktionary_parser.utils import wikitext_to_plaintext as w2p


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
