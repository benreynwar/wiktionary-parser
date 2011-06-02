# -*- coding: utf-8 -*-
"""
This example extracts a number of words from the simple.wiktionary xml file.
"""

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.languages.simple.page import simplePage

xml_file = open('../../wiktionary_data/simplewiktionary-20110514-pages-articles.xml')
xml_parser = XMLPageParser(xml_file, simplePage)

# The words we want to extract
wanted_words = set([u'fish'])

found_words = set([])

for title, page in xml_parser.from_titles(wanted_words):
    page.parse()
    # Print out a summary of the want
    for word in page.words:
        print word.summary()
    found_words.add(title)
    if wanted_words == found_words:
        break
    
