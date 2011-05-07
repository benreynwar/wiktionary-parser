from xml_parser import XMLPageParser

xml_file = open('data/enwiktionary-20090824-pages-articles.xml')
#xml_file = open('data/shorter.xml')

xml_parser = XMLPageParser(xml_file)

title_exclusions = ['MediaWiki:', 'Vorlage:']
counter = 0
show_num = 347
for page in xml_parser:
    if page.title.find(':') != -1:
#        print 'exclude -------', page.title
        continue
    if counter == show_num:
        print page.text
    counter += 1
    if counter > show_num:
        break
    #print page.text
