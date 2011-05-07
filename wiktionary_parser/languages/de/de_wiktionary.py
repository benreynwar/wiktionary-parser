"""
Info for parsing german wiktionary pages.
"""

from wiktionary_parser.wiktionary_utils.text_splitter import Block

class ParsingError(Exception):
    pass
class InconsistentEntry(Exception):
    pass


class SpracheSection(Block):
    start_pattern = u'{{Sprache\|'
    stop_pattern = u'}}'
    pattern_string = u'{{Sprache\|(?P<language>[/w/s]+)}}'
    pattern = re.compile(pattern_string, re.UNICODE)
    def process(self):
        matches = self.pattern.search(self.text)
        if not matches:
            raise ParsingError()
        set_property(word, 'language', matches.language)

        
class WortartSection(BracedSection):
    slugs = set('Wortart')
    pattern_string = u'{{Wortart\|(?P<word_type>[/w/s]+)\|(?P<language>[/w/s]+)}}'
    pattern = re.compile(pattern_string, re.UNICODE)
    def process(self):
        matches = self.pattern.search(self.text)
        if not matches:
            raise ParsingError()
        set_property(word, 'language', matches.language)
        set_property(word, 'word_type', matches.word_type)


class Word(object):
    def __init__(self):
        self.word_type = None
        self.language = None
    def set_property(self, attr_name, value):
        attr = self.get_attr(attr_name)
        if not attr:
            attr = value
        elif attr != value:
            raise InconsitentEntry()

class GermanWord(object):
    
geg_ich_pattern = re.compile(u'Gegenwart_ich=([^\|\n]+)',re.UNICODE)
