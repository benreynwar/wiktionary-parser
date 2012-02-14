.. wiktionary-parser documentation master file, created by
   sphinx-quickstart on Sun May  8 22:15:08 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to wiktionary-parser's documentation!
=============================================

Wiktionary-Parser is a python package for parsing and autocorrecting wiktionary pages.

Currently supported wiktionarys:

- simple english - simple.wiktionary.org - parses definitions, examples, plurals, and conjugations.
- german - de.wiktionary.org - parses definitions, examples, gender, conjugations

Requirements:

- the wiktionary_parser package
- the wikitools package (available on pypi, or from http://code.google.com/p/python-wikitools/)

Useful things to have:

- a wiktionary xml dump (http://dumps.wikimedia.org/backup-index.html)

Below are two examples giving an idea of what one can do with the parser.


XML file parsing example
------------------------

The first example is parsing words from the simple.wiktionary.org xml file.

The file simplewiktionary-20110514-pages-articles.xml has been downloaded and placed in a wiktionary_data folder.

    >>> # The XMLPageParser is a utility to break the xml file down into pages.
    >>> from wiktionary_parser.xml_parser import XMLPageParser
    >>> # simpePage respresents a page from the simple.wiktionary.org site
    >>> from wiktionary_parser.languages.simple.page import simplePage
    >>> xml_file = open('../../wiktionary_data/simplewiktionary-20110514-pages-articles.xml')
    >>> xml_parser = XMLPageParser(xml_file, simplePage)
    >>> from itertools import islice
    >>> # Iterating through the xml_parser returns instances of simplePage
    >>> # Create a list of the first 500 pages.
    >>> pages = list(islice(xml_parser, 500))
    >>> # What's the title of the first page
    >>> pg0 = pages[0]
    >>> pg0.title
    u'MediaWiki:Aboutwikipedia'
    >>> pg0 = pg0.parse()
    >>> # We can check how many words are defined on a given page by:
    >>> len(pg0.words)
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
    [3] Susan acts nice so people like her, but she tells lies when they cannot hear her.
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

Parsing a page taken from the wikimedia API
-------------------------------------------

    >>> import wikitools
    >>> from wiktionary_parser.languages.de.page import dePage
    >>> page_title = 'Fisch'
    >>> site = wikitools.wiki.Wiki('http://de.wiktionary.org/w/api.php')
    >>> wikipage = wikitools.Page(site, page_title)
    >>> text = wikipage.getWikiText()
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

Contents:

.. toctree::
   :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

