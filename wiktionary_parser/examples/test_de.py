# -*- coding: utf-8 -*-
u"""
>>> import wikitools
>>> from wiktionary_parser.languages.de.page import dePage
>>> page_title = 'Fisch'
>>> site = wikitools.wiki.Wiki('http://de.wiktionary.org/w/api.php')
>>> wikipage = wikitools.Page(site, page_title)
>>> text = unicode(wikipage.getWikiText(), 'utf-8')
>>> pg = dePage(title=page_title, text=text)
>>> pg = pg.parse()
>>> for word in pg.words:
...    print(word.summary())
******************
Fisch (Substantiv)
******************
Definitions:
[1] Zoologie: Tier, das unter Wasser lebt und durch Kiemen atmet
[2] kein Plural: Fleisch von [1] als Lebensmittel
[3] zwölftes Sternbild auf der Ekliptik (Tierkreiszeichen) – üblich ist hier der Gebrauch des Plurals die Fische – oder ein in diesem Sternbild Geborener (hier auch Singular)
Examples:
[1] Der Wal ist kein Fisch.
[2] Fisch auf jeden Tisch. (Werbespruch aus der DDR)
[3] Fische sind meist rätselhafte Menschen.
[3] Er ist Wassermann und ich bin Fisch / darum bleibt bei uns die Liebe immer frisch – (Schlager)
>>> word.gender
u'm'
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
