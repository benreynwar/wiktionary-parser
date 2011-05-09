# -*- coding: utf-8 -*-
"""
This example scans through the simple-english wiktionary file and displays
an alerts that the parser raises.
"""

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.languages.simple.page import simplePage

xml_file = open('../../wiktionary_data/simplewiktionary-20110505-pages-articles.xml')
xml_parser = XMLPageParser(xml_file, simplePage)

page_count = 0
errors = 0

for page in xml_parser:
    page_count += 1
    page.parse()
    all_alerts = page.get_alerts()
    if all_alerts:
        errors += 1
        print('--------')
        print(page.title)
        print('--------')        
        for alert in all_alerts:
            print(alert.description)
            if hasattr(alert, 'message'):
                print(alert.message)

    if page_count % 1000 == 0:
        print('*************************')
        print('%s pages parsed - %s pages with alerts' % (page_count, errors))
        print('*************************')
