# -*- coding: utf-8 -*-

import re

from wiktionary_parser.formating_type import RegexFT
from wiktionary_parser.sections import Level2Block, Level3Block, ChildrenSection, Block, FillerSection, FTSection
from wiktionary_parser.exceptions import ParsingError, InconsistentEntry
from wiktionary_parser.wiktionary_utils.text_splitter import Chopper, FillerBlock

from wiktionary_parser.languages.simple.wordtype_title import simpleWordTypeTitleSection
from wiktionary_parser.languages.simple.word import simpleNoun, simpleVerb

type_mapping = {
    'Noun': simpleNoun,
    'Verb': simpleVerb,
}

class simpleWordTypeSection(ChildrenSection):

    def __init__(self, *args, **kwargs):
        super(simpleWordTypeSection, self).__init__(*args, **kwargs)
        # The simple wiktionary only deals with english words.
        self.property_dict['language'] = 'english'
        self.property_dict['wordtype'] = None
        self.property_dict['word'] = None

    def parse(self, shallow=False):
        super(simpleWordTypeSection, self).parse()
        l2bs = list(Chopper(self.text, [Level2Block,]))
        if len(l2bs) != 1:
            raise ParsingError()
        title = l2bs[0].start_tag
        content = l2bs[0].text
        wordtype_title_sec = simpleWordTypeTitleSection(text=title, parent=self).parse()
        word_class = type_mapping[self.get_property('wordtype')]
        new_word = word_class(self.parent.title)
        self.set_property('word',  new_word)
        self.parent.words.append(new_word)
        if not wordtype_title_sec.readable():
            new_section = FillerSection(text=self.text, parent=self.parent,
                                        correct=False)
            return new_section.parse()
        self.children.append(wordtype_title_sec)
        for l3b in Chopper(content, [Level3Block,],
                           filler_blocks=True, include_tags=True):
            if isinstance(l3b, FillerBlock):
                section = simpleWordTypeHeaderSection(text=l3b.text, parent=self)
            else:
                section = FillerSection(text=l3b.text, parent=self, correct=True)
            if not shallow:
                section = section.parse()
            self.children.append(section)
        return self


class simpleWordTypeHeaderSection(ChildrenSection):
    
    def parse(self):
        super(simpleWordTypeHeaderSection, self).parse()

        word = self.get_property('word')
        
        lines = self.text.splitlines()
        definitions = []
        examples = []
        for line in lines:
            # Extract the definitions and examples
            if line.startswith('#:'):
                example_list.append(line[2:])
            elif line.startswith('#'):
                if definitions:
                    examples.append(example_list)
                definitions.append(line[2:])
                example_list = []
            # Extract the {{noun}} template
            elif line.startswith('{{noun'):
                pattern = re.compile('{{noun\|(?P<singular>[\w\s]+)\|(?P<plural>[\w\s]+)}}', re.UNICODE|re.DOTALL)
                match = pattern.match(line)
                if match:
                    plural = match.groupdict()['plural']
                    singular = match.groupdict()['singular']
                    if word.title != singular:
                        import pdb
                        pdb.set_trace()
                        raise StandardError('%s and %s should be the same' % (word.title, singular))
                    assert(word.title == singular)
                    word.plural = plural

        word.definitions = definitions
        word.examples = examples 

        section = FillerSection(text=self.text, parent=self)
        self.children.append(section.parse())

        return self

