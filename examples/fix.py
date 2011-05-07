# -*- coding: utf-8 -*-

from einsatz import Einsatz

xml_file = open('/Users/Ben/Web/wiktionary_data/dewiktionary-20091231-pages-articles.xml')
run = Einsatz(u'Substantiv Tabellen (7)', u'Substantiv Tabellen werden korrigiert.', xml_file, 'de', live=False, online=False, memory_file_name = 'deleteme_memory.txt')
#print run.memory
run.scan_xml()
#run.approval()
#run.run()

#page = run.get_page('Zug')
#page.parse()
#print run.requires_approval(page)
#import pdb
#pdb.set_trace()
            
            

        

    
