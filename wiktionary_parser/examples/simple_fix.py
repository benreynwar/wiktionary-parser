# -*- coding: utf-8 -*-

import wikitools

from wiktionary_parser.languages.simple.page import simplePage
from wiktionary_parser.languages.simple.alerts import UnknownType
from wiktionary_parser.bots.einsatz import Einsatz
from wiktionary_parser.bots.utils import delta

xml_file = open('../../wiktionary_data/simplewiktionary-20110514-pages-articles.xml')

site = wikitools.wiki.Wiki('http://simple.wiktionary.org/w/api.php')

username = 'Gyroidbot'

run = Einsatz(u'Trial Run', u'A trial run doing two types of formating fixes.', xml_file, simplePage,
              site, username, live=True, online=True, memory_file_name = 'simple_memory.txt')

#run.scan_xml(max_no=10)
#run.approval()
run.run()

if False:
    page = run.get_page('do')
    old_page = page.text
    page.parse()
    page.fix()
    import pdb
    pdb.set_trace()
    new_page = page.render()
    print(delta(old_page, new_page, surrounding_lines=2))

#print run.memory
#run.scan_xml()
#run.approval()
#run.run()

            
            

        

    
