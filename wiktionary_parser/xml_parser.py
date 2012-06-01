"""
Parses the xml level of the wiktionary xml dump returning one
page object at a time.  The main wiktionary format itself
however still needs to be parsed elsewhere.

>>> xml_file = open('data/enwiktionary-20090824-pages-articles.xml')
>>> xml_parser = XMLPageParser(xml_file)
>>> counter = 0
>>> show_num = 347
>>> for page in xml_parser:
...     if page.title.find(':') != -1:
...         continue
...     if counter == show_num:
...         print page.text
...     counter += 1
...     if counter > show_num:
...         break
==English==
<BLANKLINE>
===Etymology===
{{suffix|abolition|ism}}
<BLANKLINE>
===Noun===
{{en-noun}}
<BLANKLINE>
#An opinion in favor of the [[abolition]] of something.
<BLANKLINE>
====Usage notes====
* In the US this almost always refers to the historical movement to abolish slavery.
<BLANKLINE>
====Related terms====
*[[abolitionist]]
<BLANKLINE>
[[Category:English nouns ending in "-ism"]]
<BLANKLINE>
[[et:abolitionism]]
[[fr:abolitionism]]
[[io:abolitionism]]
[[hu:abolitionism]]
[[sv:abolitionism]]
[[vi:abolitionism]]
"""

from xml.dom.minidom import parseString

from wiktionary_utils.text_splitter import Splitter, Block
from page import Page


class PageBlock(Block):
    start_pattern = '<page>'
    stop_pattern = '</page>'
    slug = 'PageBlock'
    

class XMLPageParser(object):

    class CannotParse(Exception):
        pass

    def __init__(self, xml, page_class, session=None):
        self.xml = xml
        self.pbc = PageBlock
        self.page_class = page_class
        self.xml_splitter = Splitter(self.xml, [self.pbc])
        self.session = session

    def __iter__(self):
        for page_contents in self.xml_splitter:
            page_xml = ''.join([self.pbc.start_pattern, page_contents.text, self.pbc.stop_pattern])
            page_dom = parseString(page_xml)
            page_node = page_dom.childNodes[0]
            title = self.get_node(page_node, 'title')
            text = self.get_node(page_node, 'text')
            revision_id = self.get_node_id(page_node, 'revision'),
            page = self.page_class.get_and_update(
                self.session, title, revision_id, text)
            yield page


    def from_titles(self, wanted_titles, session=None):
        for page_contents in self.xml_splitter:
            page_xml = ''.join([self.pbc.start_pattern, page_contents.text, self.pbc.stop_pattern])
            page_dom = parseString(page_xml)
            page_node = page_dom.childNodes[0]
            title = self.get_node(page_node, 'title')
            if title in wanted_titles:
                text = self.get_node(page_node, 'text')
                revision_id = self.get_node_id(page_node, 'revision')
                page = self.page_class.get_and_update(
                    self.session, title, revision_id, text)
                yield page

    def get_node(self, node, tag):
        node_obj = self.get_node_obj(node, tag)
        children = node_obj.childNodes
        num_children = len(children)
        if num_children == 1:
            return children[0].nodeValue
        elif num_children == 0:
            return None
        else:
            raise self.CannotParse('More than one child')

    def get_node_id(self, node, tag):
        node = self.get_node_obj(node, tag)
        import pdb
        for child in node.childNodes:
            if getattr(child, 'tagName', None) == 'id':
                return child.childNodes[0].nodeValue

    def get_node_obj(self, node, tag):
        matches = node.getElementsByTagName(tag)
        num_matches = len(matches)
        if num_matches == 0:
            return None
        elif num_matches == 1:
            match = matches[0]
            return match
        else:
            import pdb
            pdb.set_trace()
            raise self.CannotParse('More than one match')

if __name__ == "__main__":
    import doctest
    doctest.testmod()
