"""
This module deals with processing the noun plural forms.
"""

from wiktionary_parser.sections import FTSection
from wiktionary_parser.formating_type import RegexFT
from wiktionary_parser.alerts import FixableAlert

def get_data(section, groupdict):
    title = section.get_property('title')
    singular1 = groupdict.get('singular1', None)
    singular2 = groupdict.get('singular2', None)
    plural1 = groupdict.get('plural1', None)
    plural2 = groupdict.get('plural2', None)
    no_singular = ('no_singular' in groupdict)
    add_s = ('add_s' in groupdict)
    no_plural = ('no_plural' in groupdict) or (plural1 == 'none')
    if no_singular:
        plural1 = title
    elif singular1 is None:
        singular1 = title
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
    data = {}
    data['singulars'] = singulars
    data['plurals'] = plurals
    data['title'] = title
    return data

class irrnounAlert(FixableAlert):
    slug = "irrnoun_used"
    description = "Replace the irrnoun template with the noun template."
    
class np_RegexFT(RegexFT):
    """
    Sets the default data processing function.
    """
    def __init__(self, *args, **kwargs):
        if 'get_data' not in kwargs:
            kwargs['get_data'] = get_data
        super(np_RegexFT, self).__init__(*args, **kwargs)


class simpleNounPluralSection(FTSection):

    name = 'Noun Plural Section'

    def process_data(self, data):
        word = self.get_property('word')
        word.plurals = data['plurals']
        word.singulars = data['singulars']

    # The optimum formating
    def standard_fix_func(data):
        title = data['title']
        plurals = data['plurals']
        singulars = data['singulars']
        if len(plurals) == 1 and len(singulars) == 1:
            if plurals[0] == singulars[0] + 's':
                if title == singulars[0]:
                    return "{{noun}}\n"
                else:
                    return "{{noun|%s}}\n" % singulars[0]
            else:
                return "{{noun|%s|%s}}\n" % (singulars[0], plurals[0])
        if len(singulars) == 1 and len(plurals) == 2:
            return "{{noun|%s|%s|%s}}\n" % (singulars[0], plurals[0], plurals[1])
        if len(singulars) == 0 and len(plurals) == 1:
            if title == plurals[0]:
                return "{{noun2}}\n"
            else:
                raise StandardError("Title does not match plural but no singular is found.")
        if len(singulars == 2 and len(plurals) == 1):
            return "{{noun3|%s|%s|%s}}\n" % (singulars[0], singulars[1], plurals[0])
        raise StandardError("Do not know how to format this.")

    fts = []

    fts.append(np_RegexFT(
            description="Plural is formed with an s.",
            slug='add_s',
            regex='^{{noun(?P<add_s>)}}\s*$',
            correct=True, ))

    fts.append(np_RegexFT(
            description="Irregular plural.",
            slug="irregular",
            regex='^{{noun\|(?P<singular1>[\w\s-]+)\|(?P<plural1>[\w\s-]+)}}\s*$',
            correct=True, ))

    fts.append(np_RegexFT(
            description="two plurals",
            slug="two_plurals",
            regex="{{noun\|(?P<singular1>[\w\s-]+)\|(?P<plural1>[\w\s-]+)\|(?P<plural2>[\w\s-]+)}}\s*$",
            correct=True, ))

    fts.append(np_RegexFT(
            description="no singular",
            slug="no_singular",
            regex="^{{noun2(?P<no_singular>)}}\s*$",
            correct=True, ))

    fts.append(np_RegexFT(
            description="two singulars",
            slug="two_singulars",
            regex="^{{noun3\|(?P<singular1>[\w\s-]+)\|(?P<singular2>[\w\s-]+)\|(?P<plural1>[\w\s-]+)}}\s*$",
            correct=True, ))

    fts.append(np_RegexFT(
            description="give singular - add an s",
            slug="give_singular_add_s",
            regex="^{{noun(?P<add_s>)\|(?P<singular1>[\w\s-]+)}}\s*$",
            correct=True, ))

    fts.append(np_RegexFT(
            description="Proper Noun",
            slug="proper_noun",
            regex="^{{proper noun(?P<proper>)(?P<no_plural>)}}\s*$",
            correct=True, ))
        
    # Incorrect forms

    fts.append(np_RegexFT(
            description="Irregular plural (2nd form).",
            slug="irregular2",
            regex='^{{irrnoun\|(?P<plural1>[\w\s-]+)}}\s*$',
            alert_class = irrnounAlert,
            fix_func= standard_fix_func, ))

    # Should this really be no plural.
    fts.append(np_RegexFT(
            description="A letter.",
            slug="letter",
            regex='^{{letter(?P<no_plural>)\|(?P<singular1>[\w\s-]+)}}\s*$',
            correct=True, ))

    fts.append(np_RegexFT(
            description="no singular (2nd form)",
            slug="no_singular2",
            regex="^{{noun2(?P<no_singular>)\|(?P<plural1>[\w\s-]+)}}\s*$",
            correct=True, ))
    
