from difflib import Differ

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.languages.de.page import dePage

xml_file = open('../../data/dewiktionary-20090913-pages-articles.xml')

xml_parser = XMLPageParser(xml_file, dePage)

counter = 0
show_num = 10
for page in xml_parser:
    page.parse()
    if page.fixable():
        print '%s FIXABLE'  % page.title
        page.fix()
    new_text = page.render()
    if new_text != page.text:
        result = list(Differ().compare(page.text.split('\n'), new_text.split('\n')))
        for line in result:
            if line[0] != ' ':
                print line
        print '----------------------------------'
        #break
