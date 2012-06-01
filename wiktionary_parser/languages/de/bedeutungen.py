# -*- coding: utf-8 -*-

import re

from wiktionary_parser.alerts import Alert
from wiktionary_parser.sections import Section
from wiktionary_parser.utils import wikitext_to_plaintext_with_alerts as w2p

class BedeutungenNumberAlert(Alert):
    description = 'The number of the meaning seems incorrect or the meaning does not have a number.'
    def __init__(self, message, title):
        super(BedeutungenNumberAlert, self).__init__(message, title)

class BedeutungenSection(Section):
    def parse(self):
        super(BedeutungenSection, self).parse()
        word = self.get_property('word')
        content = self.text.lstrip(' \n\r\t').rstrip(' \n\r\t')
        definitions = []
        for line in content.split('\n'):
            if word is not None:
                text, alerts = w2p(line)
                self.alerts += alerts
                # Check that the definition starts with the appropriate number.
                defnum = len(definitions)+1
                expected_start = ":[{0}]".format(defnum)
                if text.startswith(expected_start):
                    text = text[len(expected_start):]
                    definitions.append(text)
                else:
                    message = u'The meaning is "{0}" and did not start with "{1}" as expected.'
                    message = message.format(text, expected_start)
                    alert = BedeutungenNumberAlert(message, word.title)
                    self.alerts.append(alert)
                    definitions.append(text)
        if word is not None:
            word.definitions = definitions
        return self

class BeispieleSection(Section):
    def parse(self):
        super(BeispieleSection, self).parse()
        word = self.get_property('word')
        if word is None:
            return self
        content = self.text.lstrip(' \n\r\t').rstrip(' \n\r\t')
        examples = []
        for line in content.split('\n'):
            if word is not None:
                # FIXME (try to associate examples with definitions).
                text, alerts = w2p(content)
                self.alerts += alerts
                examples.append(line)
        # Work out which meaning the examples go with.
        pattern = '^:\[(?P<defnum>\d+)\](?P<remainder>.*)'
        w_examples = [[] for d in word.definitions]
        for example in examples:
            match = re.match(pattern, example)
            if match:
                gd = match.groupdict()
                defnum = int(gd['defnum']) - 1
                if defnum >= len(word.definitions):
                    message = u'The example "{0}" started with a number with no matching definition.'
                    message.format(example)
                    alert = BedeutungenNumberAlert(message, word.title)
                    self.alerts.append(alert)
                else:
                    w_examples[defnum].append(gd['remainder'])
            else:
                message = u'The example "{0}" did not start with ":[number]".'
                message.format(example)
                alert = BedeutungenNumberAlert(message, word.title)
                self.alerts.append(alert)
        word.examples = w_examples
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
        
