# -*- coding: utf-8 -*-
"""
This example extracts a number of words from the wiktionary xml file.
"""

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.languages.de.page import dePage

xml_file = open('../../wiktionary_data/dewiktionary-20110504-pages-articles.xml')
xml_parser = XMLPageParser(xml_file, dePage)

german_words = set([u'Bank', u'Kiefer'])

found_words = set([])

for title, page in xml_parser.from_titles(german_words):
    found_words.add(title)
    page.parse()
    for word in page.words:
        print('')
        print(word.title)
        print('******************')
        if word.bedeutungen:
            print('--Bedeutungen---------------')
            print(word.bedeutungen)
        if word.beispiele:
            print('--Beispiele-----------------')
            print(word.beispiele)
        if word.gender:
            print('--Gender--------------------')
            print(word.gender)
        if 'en' in word.translation:
            print('--English Translation-------')
            print(word.translation['en'])
        print('******************')
    alerts = page.get_all_alerts()
    if alerts:
        print('There are alerts for this page (%s):' % page.title)
        for alert in alerts:
            print('   %s' % alert.description)
    if found_words == german_words:
        break

unfound_words = set(german_words) - found_words
if unfound_words:
    print("The following words were not found:")
    print(unfound_words)
else:
    print("All words were found.")
