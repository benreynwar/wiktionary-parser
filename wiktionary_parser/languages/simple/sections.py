# -*- coding: utf-8 -*-

import re

from wiktionary_parser.formating_type import RegexFT
from wiktionary_parser.sections import Level2Block, Level3Block, ChildrenSection, Block, FillerSection, FTSection, LeafSection
from wiktionary_parser.exceptions import ParsingError, InconsistentEntry
from wiktionary_parser.fix import Fix
from wiktionary_parser.wiktionary_utils.text_splitter import Chopper, FillerBlock

from wiktionary_parser.languages.simple.wordtype_title import simpleWordTypeTitleSection
from wiktionary_parser.languages.simple.word import simpleNoun, simpleVerb, simpleAdjective

from wiktionary_parser.languages.simple.noun_plural import simpleNounPluralSection
from wiktionary_parser.languages.simple.verb_conjugation import simpleVerbConjugationSection
from wiktionary_parser.languages.simple.adjective_conjugation import simpleAdjectiveConjugationSection
from wiktionary_parser.languages.simple.alerts import MissingTypeTemplate, EarlyExample, UnknownType, Level2_not_Level3


level2_mapping = {
    # Valid Word Types
    'Noun': simpleNoun,
    'Verb': simpleVerb,
    'Adjective': simpleAdjective,
    'Determiner': None,
    'Preposition': None,
    'Interjection': None,
    'Subordinator': None,
    'Conjunction': None,
    'Expression': None,
    'Abbreviation': None, 
    'Contraction': None,
    'Adverb': None,
    'Pronoun': None,
    'Prefix': None,
    'Collocation': None,
    'Coordinator': None,
    'Symbol': None,
    'Abbreviation': None,
    'Number': None, 
    'Numeral': None,
    'Suffix': None,
    'Acronym': None,
    'Initialism': None,
    # Gallery is a bunch of pictures.  Don't know if it should be a level done.
    'Gallery': None,
    None: None,
}

level3_mapping = {
    # Should be a level down
    'Use': None,
    'Phrases': None,
    'Synonyms': None,
    'Antonyms': None,
    'Anagrams': None,
    'Notes': None,
    'Pronunciation': None,
    'Abbreviations': None,
    'Phrase': None,
    'Acronyms': None,
    'Etymology': None,
    'Usage': None,
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
        wordtype = self.get_property('wordtype')
        # If we don't get a recognisable word type then we can't parse this section.
        if wordtype not in level2_mapping:
            page_title = self.get_property('page').title
            section = FillerSection(text=self.text, parent=self.parent)
            if wordtype in level3_mapping:
                # This should be a level 3 heading.
                message = "%s: The heading %s should be level 3 not level 2." % (page_title, wordtype)
                fixed_text = u"===%s===%s" % (wordtype, content)
                alert = Level2_not_Level3(section, fixed_text, message, page_title)
            else:
                message = '%s: The word type "%s" is not known.' % (page_title, wordtype) 
                alert = UnknownType(
                    message=message, title=page_title)
            section.alerts.append(alert)
            return section
        word_class = level2_mapping[wordtype]
        if word_class is None:
            return FillerSection(text=self.text, parent=self.parent)
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
    
    noun_template_names = ('letter', 'irrnoun', 'noun', 'proper noun')
    noun_regexes = ["(?P<content>{{%s[\w\s\|'=-]*}})(?P<after>.*)" % name for name in noun_template_names]

    adjective_template_names = ('adjective', 'adj')
    adjective_regexes = ["(?P<content>{{%s[\w\s\|'=-]*}})(?P<after>.*)" % name for name in adjective_template_names]

    wordtype_info = {
        'Noun': (noun_regexes, simpleNounPluralSection),
        'Verb': (["(?P<content>{{verb[\w\s\|'=-]*}})(?P<after>.*)"], simpleVerbConjugationSection),
        'Adjective': (adjective_regexes, simpleAdjectiveConjugationSection),
        }

    def __init__(self, *args, **kwargs):
        super(simpleWordTypeHeaderSection, self).__init__(*args, **kwargs)
        self.wordtype = self.get_property('wordtype')
        regexs, klass = self.wordtype_info[self.wordtype]
        self.wordtype_patterns = [re.compile(regex, re.UNICODE|re.DOTALL) for regex in regexs]
        self.match_class = klass

    def add_section(self, current_section, current_text, last_line=False):
        if current_section is not None:
            text = '\n'.join(current_text)
            if not last_line:
                text = text + '\n'
            self.children.append(current_section(text=text, parent=self).parse())        

    def parse(self):
        super(simpleWordTypeHeaderSection, self).parse()

        current_section = None
        current_text = []

        found_match = False
        
        # Reverse the lines so we can pop from the end.
        lines = self.text.splitlines()
        lines.reverse()

        while lines:
            line = lines.pop()
            for pattern in self.wordtype_patterns:
                match = pattern.match(line)
                if match:
                    break
            if match:
                gd = match.groupdict()
                self.add_section(current_section, current_text)
                self.add_section(self.match_class, [gd['content']])
                if gd['after']:
                    lines.append(gd['after'])
                current_section = None
                current_text = []
                found_match = True
            elif line.startswith('#'):
                if current_section is not simpleDefsExamplesSection:
                    self.add_section(current_section, current_text)
                    current_section = simpleDefsExamplesSection
                    current_text = []
                current_text.append(line)
            else:
                if current_section is not FillerSection:
                    self.add_section(current_section, current_text)
                    current_section = FillerSection
                    current_text = []
                current_text.append(line)
        
        last_line = not self.text.endswith('\n')
        self.add_section(current_section, current_text, last_line=last_line)

        if not found_match:
            page_title = self.get_property('page').title
            wordtype = self.get_property('wordtype')
            message = '%s: A template for wordtype %s was not found.' % (page_title, wordtype) 
            alert = MissingTypeTemplate(
                message=message, title=page_title)
            self.alerts.append(alert)

        return self


class simpleDefsExamplesSection(LeafSection):
    
    def parse(self):
        super(simpleDefsExamplesSection, self).parse()
        word = self.get_property('word')
        lines = self.text.splitlines()
        definitions = []
        examples = []
        example_list = None
        early_examples = False
        # We expect example sentences to come after the appropriate definitions.
        # If they come before any definitions they are lumped in with the first
        # and an alert is raised.
        for line in lines:
            # Extract the definitions and examples
            if line.startswith('#:'):
                if example_list is None:
                    early_examples = True
                    example_list = []
                example_list.append(line[2:].strip())
            elif line.startswith('#'):
                if definitions:
                    examples.append(example_list)
                definitions.append(line[1:].strip())
                if not (early_examples and not examples):
                    example_list = []
            else:
                # FIX ME: better error
                raise StandardError('Each line should begin with # or #:')
        if early_examples:
            page_title = self.get_property('page').title
            message = '%s: A example preceded the first definition.' % (page_title) 
            alert = EarlyExample(
                message=message, title=page_title)
            self.alerts.append(alert)
            
        word.definitions = definitions
        word.examples = examples 
        return self
        

