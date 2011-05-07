"""
Tools for dealing with german nouns.

``fks`` is a list of all the FlexionsKlassen.

``fks_for_gender`` is a dictionary with gender as the key, and a lists of
flektionsklassen as the values.

``fks_from_genders`` is a function taking an iterable of genders and returning
a list of flektionsklassen.
"""

from wiktionary_parser.wiktionary_utils.levenshtein import levenshtein
from .base import CASES, GENDERS, MASC, FEM, NEUT, NOM, AKK, DAT, GEN

class Flexionsklasse(object):
    """
    How noun-endings are formed.  Each instance is a Flexionsklasse which
    describes how a group of nouns decline.
    
    The nominativ singular and plural forms are taken to be the stems.  All
    endings are relative to these.
    """

    def __init__(self, slug, genders, endings_dict):
        """
        ``slug`` is just a string to associate with this for debugging purposes.
        ``genders`` is a set of genders for which this class is possible.
        ``endings_dict`` has keys of the form (case, plural) and the values are
        lists of tuples where the first element of each tuple is an acceptable
        ending, and the second element (is it exists) specifies how the stem
        must end for this to be an acceptable ending.
        e.g. [('e',), ('se', ['s'])] indicates that 'e' is an acceptable ending
        but 'se' is also acceptable so long as the stem ends in an 's'.
        """
        self.slug = slug
        self.genders = genders
        self.endings = {}
        for case in CASES:
            for plural in (False, True):
                # The default ending is no ending.
                self.endings[(case, plural)] = endings_dict.get((case, plural), [('',),])

    def __unicode__(self):
        return self.slug
    def __repr__(self):
        return unicode(self).encode('utf-8')

    class PossibleMatch(Exception):
        """
        This exception is raised if the deklination does not match this Flexionsklasse,
        but that a typo is the suspected cause.
        """
        def __init__(self, lev, corrected_dekl):
            self.lev = lev
            self.corrected_dekl = corrected_dekl

    def matches(self, nom_form, case, plural, dekl):
        """
        Checks whether a given deklination ``dekl`` of case, ``case`` and plurality
        ``plural`` is consistent with the nominativ form ``nom_form``.
        """
        ending_infos = self.endings[(case, plural)]
        min_lev_info = {}
        for ending_info in ending_infos:
            ending = ending_info[0]
            try:
                stem_endings = ending_info[1]
            except IndexError:
                stem_endings = None
            if stem_endings is not None:
                stem_ending_OK = False
                for stem_ending in stem_endings:
                    if nom_form.endswith(stem_ending):
                        stem_ending_OK = True
                        break
                if not stem_ending_OK:
                    continue
            if not dekl.endswith(ending):
                continue
            if nom_form + ending == dekl:
                return True
            if not ending:
                stem = dekl
            else:
                stem = dekl[:-len(ending)]
            lev = levenshtein(stem, nom_form)
            if not min_lev_info or lev < min_lev_info['lev']:
                min_lev_info['lev'] = lev
                min_lev_info['corrected_dekl'] = nom_form + ending
        if min_lev_info:
            raise self.PossibleMatch(
                lev=min_lev_info['lev'],
                corrected_dekl=min_lev_info['corrected_dekl'])
        return False


fks = []
fks.append(Flexionsklasse('es/s', set([MASC, NEUT]), {
            (DAT, False): [('',), ('e',), ('(e)',)],
            (GEN, False): [('s',), ('es',), ('(e)s',)],
            # Must add an 'n' unless then last letter is already an 'n'
            # or if the plural is formed with an 's' or 'a'.
            (DAT, True): [('n',), ('', ['n','s', 'a', 'i'])],
            }))
fks.append(Flexionsklasse('en', set([MASC]), {
            (AKK, False): [('en',)],
            (DAT, False): [('en',)],
            (GEN, False): [('en',)],
            }))
fks.append(Flexionsklasse('blank', set([FEM, MASC, NEUT]), {
            (DAT, True): [('n',), ('', ['n','s', 'a', 'i'])],
            }))
fks.append(Flexionsklasse('ses', set([MASC, NEUT]), {
            (DAT, False): [('', ['s']), ('se', ['s']), ('(se)', ['s'])],
            (GEN, False): [('ses', ['s'])],
            (DAT, True): [('n',), ('', ['n','s', 'a', 'i'])],
            }))
fks.append(Flexionsklasse('ens', set([MASC]), {
            (AKK, False): [('en',)],
            (DAT, False): [('en',)],
            (GEN, False): [('ens',)],
            }))
fks.append(Flexionsklasse('m_adj', set([MASC]), {
            (AKK, False): [('n',)],
            (DAT, False): [('n',)],
            (GEN, False): [('n',)],
            }))
fks.append(Flexionsklasse('fn_adj', set([FEM, NEUT]), {
            (DAT, False): [('n',)],
            (GEN, False): [('n',)],
            }))

fks_for_gender = {}
for gender in GENDERS:
    fks_for_gender[gender] = []
for fk in fks:
    for gender in fk.genders:
        fks_for_gender[gender].append(fk)

def fks_from_genders(genders):
    fks = []
    for gender in genders:
        new_fks = fks_for_gender[gender]
        for fk in new_fks:
            if fk not in fks:
                fks.append(fk)
    return fks
