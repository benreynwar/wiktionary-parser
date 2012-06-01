# -*- coding: utf-8 -*-
"""
>>> # The XMLPageParser is a utility to break the xml file down into pages.
>>> from wiktionary_parser.xml_parser import XMLPageParser
>>> # simpePage respresents a page from the simple.wiktionary.org site
>>> from wiktionary_parser.languages.simple.page import simplePage
>>> xml_file = open('../../wiktionary_data/simplewiktionary-20120210-pages-articles.xml')
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
[1] If you act in some way, you do something that makes people think you are that way.
[2] If you act, you perform in a film or a play.
Examples:
[1] When he must do something, he acts quickly.
[1] Don't do anything strange. Just act normal.
[1] She acted the fool when she saw him.
[2] Daniel Radcliffe acts in the Harry Potter films.
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
[1] Something done, a deed.
[2] An act is a law made by the government.
[3] An act is when you do something to make people believe something other than the truth.
[4] An act is a part of a play or film.
Examples:
[1] Going into the house on fire to help a child was a brave act.
[2] The UK's Freedom of Information Act was passed in 2004. It lets people ask questions of the government.
[3] Susan seems nice, but it's all an act.
[4] The curtain comes down at the end of each act.
Singular: act
Plural: acts
>>> len(word1.definitions)
2
>>> word1.definitions[0]
u'If you act in some way, you do something that makes people think you are that way.'
>>> len(word2.plurals)
1
>>> word2.plurals[0]
u'acts'
"""

if __name__ == "__main__":
    import doctest
    doctest.testmod()
