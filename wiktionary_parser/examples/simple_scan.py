# -*- coding: utf-8 -*-
"""
This example scans through the simple-english wiktionary file and displays
an alerts that the parser raises.
"""

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.languages.simple.page import simplePage

from wiktionary_parser.languages.simple.alerts import UnknownType

xml_file = open('../../wiktionary_data/simplewiktionary-20110514-pages-articles.xml')
xml_parser = XMLPageParser(xml_file, simplePage)

page_count = 0
errors = 0

for page in xml_parser:
    page_count += 1
    page.parse()
    if False:
        fixables = page.get_fixable_alerts()
        if fixables:
            print('--------')
            print(page.title)
            print('--------')        
            for alert in fixables:
                print(alert.description)
                print(alert.message)
            
    if False:
        all_alerts = page.get_alerts()
        if all_alerts:
            errors += 1
            for alert in all_alerts:
                if True:#isinstance(alert, UnknownType):
                    print('--------')
                    print(page.title)
                    print('--------')        
                    print(alert.description)
                    print(alert.message)
                    
    if True:
        counter = 0
        for word in page.words:
            counter += 1
            if 'BNC1000HW' in word.tags:
                print(word.summary())
            if counter > 100:
                break

    if page_count % 1000 == 0:
        print('*************************')
        print('%s pages parsed - %s pages with alerts' % (page_count, errors))
        print('*************************')
