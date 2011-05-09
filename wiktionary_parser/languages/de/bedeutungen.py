# -*- coding: utf-8 -*-

import re

from wiktionary_parser.sections import Section
from wiktionary_parser.utils import wikitext_to_plaintext as w2p

class BedeutungenSection(Section):
    def parse(self):
        super(BedeutungenSection, self).parse()
        word = self.get_property('word')
        content = self.text.lstrip(' \n\r\t').rstrip(' \n\r\t')
        if word is not None:
            text, alerts = w2p(content)
            self.alerts += alerts
            word.definitions.append(text)
        return self

class BeispieleSection(Section):
    def parse(self):
        super(BeispieleSection, self).parse()
        word = self.get_property('word')
        content = self.text.lstrip(' \n\r\t').rstrip(' \n\r\t')
        if word is not None:
            # FIXME (try to associate examples with definitions).
            text, alerts = w2p(content)
            self.alerts += alerts
            word.examples.append([text])
        return self

class UebersetzungenSection(Section):
    def replacement(self, match):
        return match.group('english')
    def parse(self):
        super(UebersetzungenSection, self).parse()
        regex = u'^\*{{en}}:(?P<content>.*)$'
        pattern = re.compile(regex, re.UNICODE)
        lines = self.text.split('\n')
        text = None
        for line in lines:
            match = pattern.match(line)
            if match:
                text = match.group('content')
                search_pattern = re.compile(u"{{Ü\|en\|(?P<english>[\w\s']*)}}", re.UNICODE)
                text = re.sub(search_pattern, self.replacement, text)
                search_pattern = re.compile(u"{{Ü\|en\|[\w\s']*|(?P<english>[\w\s']*)}}", re.UNICODE)
                text = re.sub(search_pattern, self.replacement, text)
        word = self.get_property('word')
        if word is not None:
            word.translation = {}
            if text is not None:
                word.translation['en'] = text
        return self
        
