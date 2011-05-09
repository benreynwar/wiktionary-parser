"""
This module deals with processing the adjective conjugation forms.
"""

from wiktionary_parser.sections import FTSection
from wiktionary_parser.formating_type import RegexFT

from wiktionary_parser.languages.simple.alerts import AdjectiveConjugationAlert

ADJ_CONJ_DOESNT_EXIST = ('Adjective conjugation does not exist.',)

class simpleAdjectiveConjugationSection(FTSection):

    name = 'Adjective Conjugation Section'

    def process_data(self, data):
        word = self.get_property('word')
        if 'noncomparable' in data:
            # The positive adjective form should match the word title.
            if 'positive' in data and data['positive'] != word.title:
                page_title = self.get_property('page').title
                message = ('%s: Positive adjective conjugation (%s) does not match title (%s).' %
                           (page_title, data['positive'], word.title))
                alert = AdjectiveConjugationAlert(
                    message=message, title=page_title)
                self.alerts.append(alert)
            word.comparative = ADJ_CONJ_DOESNT_EXIST
            word.superlative = ADJ_CONJ_DOESNT_EXIST
        elif 'moreandmost' in data:
            word.comparative = 'more %s' % word.title
            word.superlative = 'most %s' % word.title
        else:
            word.comparative = data['comparative']
            word.superlative = data['superlative']
            

    fts = []

    fts.append(RegexFT(
            description="non-comparable",
            slug="noncomparable",
            regex="^{{adjective(?P<noncomparable>)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="non-comparable (2)",
            slug="noncomparable2",
            regex="^{{adjective(?P<noncomparable>)\|(?P<positive>[\w\s-]+)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="uses more and most",
            slug="moreandmost",
            regex="^{{adjective(?P<moreandmost>)\|more=true}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="uses more and most (2)",
            slug="moreandmost2",
            regex="^{{adjective(?P<moreandmost>)\|(?P<positive>[\w\s-]+)\|more=true}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="uses forms",
            slug="forms",
            regex="^{{adjective\|(?P<positive>[\w\s-]+)\|(?P<comparative>[\w\s-]+)\|(?P<superlative>[\w\s-]+)}}$",
            correct=True, ))

    # Incorrect (I think) (but I'm not marking them as incorrect because I don't want
    # to set up correcting functions.

    fts.append(RegexFT(
            description="non-comparable (3)",
            slug="noncomparable3",
            regex="^{{adjective(?P<noncomparable>)\|more=false}}$",
            correct=True, ))

    # Everything again but using 'adj' template
    # I'm putting this separate in case one wants to fix it later.

    fts.append(RegexFT(
            description="non-comparable (4)",
            slug="noncomparable4",
            regex="^{{adj(?P<noncomparable>)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="non-comparable (5)",
            slug="noncomparable5",
            regex="^{{adj(?P<noncomparable>)\|(?P<positive>[\w\s-]+)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="uses more and most (3)",
            slug="moreandmost3",
            regex="^{{adj(?P<moreandmost>)\|more=true}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="uses more and most (4)",
            slug="moreandmost4",
            regex="^{{adj(?P<moreandmost>)\|(?P<positive>[\w\s-]+)\|more=true}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="uses forms (2)",
            slug="forms2",
            regex="^{{adj\|(?P<positive>[\w\s-]+)\|(?P<comparative>[\w\s-]+)\|(?P<superlative>[\w\s-]+)}}$",
            correct=True, ))

    fts.append(RegexFT(
            description="non-comparable (6)",
            slug="noncomparable6",
            regex="^{{adj(?P<noncomparable>)\|more=false}}$",
            correct=True, ))
