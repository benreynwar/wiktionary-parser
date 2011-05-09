"""
This module deals with processing the noun plural forms.
"""

from wiktionary_parser.sections import FTSection
from wiktionary_parser.formating_type import RegexFT

class simpleNounPluralSection(FTSection):

    name = 'Noun Plural Section'

    def process_data(self, data):
        word = self.get_property('word')
        singular1 = data.get('singular1', None)
        singular2 = data.get('singular2', None)
        plural1 = data.get('plural1', None)
        plural2 = data.get('plural2', None)
        no_singular = ('no_singular' in data)
        add_s = ('add_s' in data)
        no_plural = ('no_plural' in data) or (plural1 == 'none')
        if no_singular:
            plural1 = word.title
        elif singular1 is None:
            singular1 = word.title
        if add_s:
            plural1 = singular1 + 's'
        singulars = []
        if not no_singular:
            assert(singular1 is not None)
            singulars.append(singular1)
            if singular2 is not None:
                singulars.append(singular2)
        plurals = []
        if not no_plural:
            assert(plural1 is not None)
            plurals.append(plural1)
            if plural2 is not None:
                plurals.append(plural2)
        word.plurals = plurals
        word.singulars = singulars

    fts = []

    fts.append(RegexFT(
            description="Plural is formed with an s.",
            slug='add_s',
            regex='^{{noun(?P<add_s>)}}\s*$',
            correct=True, ))

    fts.append(RegexFT(
            description="Irregular plural.",
            slug="irregular",
            regex='^{{noun\|(?P<singular1>[\w\s-]+)\|(?P<plural1>[\w\s-]+)}}\s*$',
            correct=True, ))

    fts.append(RegexFT(
            description="two plurals",
            slug="two_plurals",
            regex="{{noun\|(?P<singular1>[\w\s-]+)\|(?P<plural1>[\w\s-]+)\|(?P<plural2>[\w\s-]+)}}\s*$",
            correct=True, ))

    fts.append(RegexFT(
            description="no singular",
            slug="no_singular",
            regex="^{{noun2(?P<no_singular>)}}\s*$",
            correct=True, ))

    fts.append(RegexFT(
            description="two singulars",
            slug="two_singulars",
            regex="^{{noun3\|(?P<singular1>[\w\s-]+)\|(?P<singular2>[\w\s-]+)\|(?P<plural1>[\w\s-]+)}}\s*$",
            correct=True, ))

    fts.append(RegexFT(
            description="give singular - add an s",
            slug="give_singular_add_s",
            regex="^{{noun(?P<add_s>)\|(?P<singular1>[\w\s-]+)}}\s*$",
            correct=True, ))

    fts.append(RegexFT(
            description="Proper Noun",
            slug="proper_noun",
            regex="^{{proper noun(?P<proper>)(?P<no_plural>)}}\s*$",
            correct=True, ))
        
    # Incorrect forms

    fts.append(RegexFT(
            description="Irregular plural (2nd form).",
            slug="irregular2",
            regex='^{{irrnoun\|(?P<plural1>[\w\s-]+)}}\s*$',
            correct=True, ))

    # Should this really be no plural.
    fts.append(RegexFT(
            description="A letter.",
            slug="letter",
            regex='^{{letter(?P<no_plural>)\|(?P<singular1>[\w\s-]+)}}\s*$',
            correct=True, ))

    fts.append(RegexFT(
            description="no singular (2nd form)",
            slug="no_singular2",
            regex="^{{noun2(?P<no_singular>)\|(?P<plural1>[\w\s-]+)}}\s*$",
            correct=True, ))

    
