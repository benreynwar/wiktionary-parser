"""
Tools for dealing with german articles.

``ARTICLES`` is a dictionary which returns the appropriate
definite article for a tuple key of the form (case, plural, gender).

``POSSIBLE_ARTICLES`` is a set of all the possible articles.
"""

from .base import MASC, FEM, NEUT
from .base import NOM, AKK, DAT, GEN

# The definite articles are listed here in a more compact form
# to make them more readable.  They are then expanded into the
# ARTICLES dictionary.
_gender_indices = [(0, MASC), (1, FEM), (2, NEUT)]
_singular_def_articles = {NOM: (u'der', u'die', u'das'),
                          AKK: (u'den', u'die', u'das'),
                          DAT: (u'dem', u'der', u'dem'),
                          GEN: (u'des', u'der', u'des'),
                          }
_plural_def_articles = { NOM: (u'die', u'die', u'die'),
                         AKK: (u'die', u'die', u'die'), 
                         DAT: (u'den', u'den', u'den'),
                         GEN: (u'der', u'der', u'der'),
                         }

# Create the ARTICLES dictionary
# The key is a tuple of the form (case, plural, gender).
ARTICLES = {}
for def_articles, plural in ((_singular_def_articles, False),
                             (_plural_def_articles, True)):
    for case, articles in def_articles.items():
        for index, gender in _gender_indices:
            ARTICLES[(case, plural, gender)] = articles[index]

POSSIBLE_ARTICLES = set([article for article in ARTICLES.values()])
