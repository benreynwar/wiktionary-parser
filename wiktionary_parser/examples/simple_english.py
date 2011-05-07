# -*- coding: utf-8 -*-
"""
This example extracts a number of words from the wiktionary xml file.
"""

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.languages.simple.page import simplePage

xml_file = open('../../wiktionary_data/simplewiktionary-20110505-pages-articles.xml')
xml_parser = XMLPageParser(xml_file, simplePage)

wanted_words = set([u'fish', u'sheep'])

found_words = set([])

for title, page in xml_parser.from_titles(wanted_words):
    page.parse()
    for word in page.words:
        print word.summary()
        print('')
