"""
This module deals with processing the verb conjugation forms.
"""

from wiktionary_parser.sections import FTSection
from wiktionary_parser.formating_type import RegexFT

class NormalVerbConjugation(object):
    
    def __init__(self, plain, third, third_past, past_part, pres_part):
        self.plain = plain
        self.third = third
        self.third_past = third_past
        self.past_part = past_part
        self.pres_part = pres_part

    def summary(self):
        out = []
        out.append('I %s (present)' % self.plain)
        out.append('He %s (present)' % self.third)
        out.append('He %s (past)' % self.third_past)
        out.append('He is %s (present participle)' % self.pres_part)
        out.append('He has %s (past participle)' % self.past_part)
        return '\n'.join(out)

class ToBeVerbConjugation(object):
    """
    I think this is only used for "to be".
    """
    def __init__(self, plain, first, second, third, first_past, second_past, past_part, pres_part):
        self.plain = plain
        self.first = first
        self.second = second
        self.third = third
        self.first_past = first_past
        self.second_past = second_past
        self.past_part = past_part
        self.pres_part = pres_part

    def summary(self):
        out = []
        out.append('to %s' % self.plain)
        out.append('I %s (present)' % self.first)
        out.append('You %s (present)' % self.second)
        out.append('He %s (present)' % self.third)
        out.append('I %s (past)' % self.first_past)
        out.append('You %s (past)' % self.second_past)
        out.append('He is %s (present participle)' % self.pres_part)
        out.append('He has %s (past participle)' % self.past_part)
        return '\n'.join(out)

class ModalVerbConjugation(object):

    def __init__(self, plain, past, negative):
        self.plain = plain
        self.past = past
        self.negative = negative

    def summary(self):
        out = []
        out.append('He %s eat (present)' % self.plain)
        out.append('He %s eat (past)' % self.past)
        out.append('He %s eat (negative present)' % self.negative)
        return '\n'.join(out)


class AuxiliaryVerbConjugation(object):

    def __init__(self, plain, third, past):
        self.plain = plain
        self.third = third
        self.past = past

    def summary(self):
        out = []
        out.append('I %s (present)' % self.plain)
        out.append('He %s (present)' % self.third)
        out.append('He %s (past)' % self.past)
        return '\n'.join(out)

class simpleVerbConjugationSection(FTSection):

    name = 'Verb Conjugation Section'

    def process_data(self, data):
        word = self.get_property('word')

        plain = data.get('plain', None)
        third = data.get('third', None)
        past = data.get('past', None)
        past_part = data.get('past_part', None)
        pres_part = data.get('pres_part', None)
        stem = data.get('stem', None)
        ending = data.get('ending', None)

        modal = ('modal' in data)
        to_be = ('to_be' in data)
        auxiliary = ('auxiliary' in data)

        if to_be:
            data.pop('to_be')
            conj = ToBeVerbConjugation(**data)

        elif modal:
            data.pop('modal')
            conj = ModalVerbConjugation(**data)

        elif auxiliary:
            data.pop('auxiliary')
            conj = AuxiliaryVerbConjugation(**data)
        
        else:
            if stem is not None:
                if ending == 'e':
                    plain = stem + 'e'
                    past = stem + 'ed'
                    pres_part = stem + 'ing'
                elif ending == 'y':
                    plain = stem + 'y'
                    third = stem + 'ies'
                    past = stem + 'ied'
                elif ending == 'es':
                    plain = stem
                    third = stem + 'es'
                elif len(ending) == 1:
                    # Make sure that the ending is the same as the last letter of the stem.
                    if ending != stem[-1] and not (ending == 'k' and stem[-1] == 'c'):
                        raise StandardError("stem is %s and ending is %s" % (stem, ending))
                    plain = stem
                    past = stem + ending + 'ed'
                    pres_part = stem + ending + 'ing'
                else:
                    raise StandardError('Verb template does not match.')
            if plain is None:
                plain = word.title
            if third is None:
                third = plain + 's'
            if past is None:
                past = plain + 'ed'
            if past_part is None:
                past_part = past
            if pres_part is None:
                pres_part = plain + 'ing'            
            conj = NormalVerbConjugation(plain, third, past, past_part, pres_part)

            if word.conjugations is None:
                word.conjugations = []
            word.conjugations.append(conj)

    fts = []

    fts.append(RegexFT(
            description="Regular",
            slug="regular",
            regex="^{{verb(?P<regular>)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="Regular (2)",
            slug="regular2",
            regex="^{{verb(?P<regular>)\|regular=true}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="The pagename is not the base verb.",
            slug="pagename_not_base",
            regex="^{{verb\|(?P<plain>[\w\s-]+)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="Ending adjustment",
            slug="end adjust",
            regex="^{{verb\|(?P<stem>[\w\s-]+)\|(?P<ending>[\w]+)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="Past tense is the same as past participle",
            slug="past_is_past_part",
            regex="^{{verb\|(?P<plain>[\w\s-]+)\|(?P<third>[\w\s-]+)\|(?P<past>[\w\s-]+)\|(?P<pres_part>[\w\s-]+)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="Irregular",
            slug="irregular",
            regex="^{{verb2?\|(?P<plain>[\w\s-]+)\|(?P<third>[\w\s-]+)\|(?P<past>[\w\s-]+)\|(?P<past_part>[\w\s-]+)\|(?P<pres_part>[\w\s-]+)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="Irregular",
            slug="irregular",
            regex="^{{verb3(?P<to_be>)\|(?P<plain>[\w\s-]+)\|(?P<first>[\w\s-]+)\|(?P<second>[\w\s-]+)\|(?P<third>[\w\s-]+)\|(?P<first_past>[\w\s-]+)\|(?P<second_past>[\w\s-]+)\|(?P<past_part>[\w\s-]+)\|(?P<pres_part>[\w\s-]+)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="Modal",
            slug="modal",
            regex="^{{verb4(?P<modal>)\|(?P<plain>[\w\s-]+)\|(?P<past>[\w\s-]+)\|(?P<negative>[\w\s'-]+)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="Modal",
            slug="modal",
            regex="^{{verb5(?P<auxiliary>)\|(?P<plain>[\w\s-]+)\|(?P<third>[\w\s-]+)\|(?P<past>[\w\s'-]+)}}$",
            correct=True, ))
