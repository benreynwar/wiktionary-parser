# -*- coding: utf-8 -*-
"""
>>> # The XMLPageParser is a utility to break the xml file down into pages.
>>> from wiktionary_parser.xml_parser import XMLPageParser
>>> # simpePage respresents a page from the simple.wiktionary.org site
>>> from wiktionary_parser.languages.simple.page import simplePage
>>> xml_file = open('../../wiktionary_data/simplewiktionary-20110505-pages-articles.xml')
>>> xml_parser = XMLPageParser(xml_file, simplePage)
>>> from itertools import islice
>>> # Iterating through the xml_parser returns instances of simplePage
>>> # Create a list of the first 500 pages.
>>> pages = list(islice(xml_parser, 500))
>>> # What's the title of the first page
>>> pages[0].title
u'MediaWiki:Aboutwikipedia'
>>> # We can check how many words are defined on a given page by:
>>> len(pages[0].words)
0
>>> # We'll try a different word.
>>> pg = pages[280]
>>> pg.title
u'act'
>>> pg = pg.parse()
>>> len(pg.words)
2
>>> word1 = pg.words[0]
>>> word2 = pg.words[1]
>>> print(word1.summary())
**********
act (verb)
**********
Definitions:
[0] {{intransitive}} & {{linking verb}} If you '''act''' in some way, you do something that makes people think you are that way.
Conjugation 1:
I act (present)
He acts (present)
He acted (past)
He is acting (present participle)
He has acted (past participle)
>>> print(word2.summary())
**********
act (noun)
**********
Definitions:
[0] {{countable}} Something done, a [[deed]].
Singular: act
Plural: acts
>>> len(word1.definitions)
1
>>> word1.definitions[0]
u"{{intransitive}} & {{linking verb}} If you '''act''' in some way, you do something that makes people think you are that way."
>>> len(word2.plurals)
1
>>> word2.plurals[0]
u'acts'
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
