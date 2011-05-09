# -*- coding: utf-8 -*-

from wiktionary_parser.sections import FTSection
from wiktionary_parser.formating_type import RegexFT

class simpleWordTypeTitleSection(FTSection):

    name = 'Word Type Title Section'

    def process_data(self, data):
        self.parent.set_property('wordtype', data['wordtype'])

    fts = []

    # Incorrect Formatting Types that are Readable/Fixable
    standard_fix_func = lambda data: u'==%s==' % \
        (data['wordtype'])

    # Correct Formatting

    fts.append(RegexFT(
            description='Standard wordtype title.',
            slug='standard',
            regex=u'==\s*(?P<wordtype>[\w]+)\s*==',
            correct=True, ))

