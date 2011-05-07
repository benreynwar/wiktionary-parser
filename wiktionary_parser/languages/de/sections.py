# -*- coding: utf-8 -*-

import re

from wiktionary_parser.formating_type import RegexFT
from wiktionary_parser.sections import Level2Block, Level3Block, ChildrenSection, Block, FillerSection, FTSection
from wiktionary_parser.exceptions import ParsingError, InconsistentEntry
from wiktionary_parser.wiktionary_utils.text_splitter import Chopper, FillerBlock

from .lang_title import deLangTitleSection
from .wortart_title import deWortartTitleSection
from .substantiv_tabelle import SubstantivTabelleSection
from .bedeutungen import BedeutungenSection, BeispieleSection, UebersetzungenSection
from .word import deSubstantiv

class deLanguageSection(ChildrenSection):

    def __init__(self, *args, **kwargs):
        super(deLanguageSection, self).__init__(*args, **kwargs)
        self.property_dict['language'] = None

    def parse(self, shallow=False):
        super(deLanguageSection, self).parse()
        # The only thing that a deLanguageSection should contain
        # is the title and deWortartSections.
        l2bs = list(Chopper(self.text, [Level2Block,]))
        if len(l2bs) != 1:
            raise ParsingError()
        title = l2bs[0].start_tag
        content = l2bs[0].text
        lang_title_sec = deLangTitleSection(text=title, parent=self).parse()
        if not lang_title_sec.readable():
            new_section = FillerSection(text=self.text, parent=self.parent,
                                        correct=False)
            return new_section.parse()
        self.children.append(lang_title_sec)
        for l3b in Chopper(content, [Level3Block,],
                           filler_blocks=True, include_tags=True):
            if isinstance(l3b, FillerBlock):
                section = FillerSection(text=l3b.text, parent=self, correct=True)
            else:
                section = deWortartSection(text=l3b.text, parent=self)
            if not shallow:
                section = section.parse()
            self.children.append(section)
        return self

    
type_mapping = {
    deSubstantiv: [u'Substantiv', u'Vorname', u'Nachname', u'Eigenname', u'Toponym', u'Singularetantum',]
    }
type_to_page_class = {}
# Create dictionary to convert types to page_class
for page_class, types in type_mapping.items():
    for typ in types:
        if typ in type_to_page_class:
            raise StandardError('Duplicate')
        type_to_page_class[typ] = page_class


class deWortartSection(ChildrenSection):

    def __init__(self, *args, **kwargs):
        super(deWortartSection, self).__init__(*args, **kwargs)
        self.property_dict['types'] = []
        self.property_dict['word'] = None

    def parse(self):
        super(deWortartSection, self).parse()
        l3bs = list(Chopper(self.text, [Level3Block,]))
        if len(l3bs) != 1:
            import pdb
            pdb.set_trace()
            raise ParsingError()
        title = l3bs[0].start_tag
        content = l3bs[0].text
        wortart_title_sec = deWortartTitleSection(text=title, parent=self).parse()
#        if not wortart_title_sec.readable():
#            new_section = FillerSection(text=self.text, parent=self.parent, correct=False)
#            return new_section
        wortart_content = deWortartContentSection(text=content, parent=self).parse()
        self.children.append(wortart_title_sec)
        self.children.append(wortart_content)
        return self

    def add_type(self, typ):
        types = self.get_property('types')
        word = self.get_property('word')
        types.append(typ)
        if self.get_property('language') == 'Deutsch' and not word:
            page_class = type_to_page_class.get(typ, None)
            if page_class:
                title = self.get_property('page').title
                new_word = page_class(title)
                new_word.language = self.get_property('language')
                self.set_property('word', new_word)
                self.get_property('page').words.append(new_word)
       

block_starts = {u'{{Substantiv-Tabelle': SubstantivTabelleSection,
                u'{{Silbentrennung}}': None,
                u'{{Aussprache}}': None,
                u'{{Bedeutungen}}': BedeutungenSection,
                u'{{Herkunft}}': None,
                u'{{Beispiele}}': BeispieleSection,
                u'{{Synonyme}}': None,
                u'{{Gegenwörter}}': None,
                u'{{Oberbegriffe}}': None,
                u'{{Unterbegriffe}}': None,
                u'{{Redewendungen}}': None,
                u'{{Sprichwörter}}': None,
                u'{{Charakteristische Wortkombinationen}}': None,
                u'{{Abgeleitete Begriffe}}': None,
                u'==== Übersetzungen ====': UebersetzungenSection,
                u'{{Dialektausdrücke': None,
                u'{{Referenzen}}': None,
                u'{{Ähnlichkeiten}}': None,
                u'{{Verkleinerungsformen}}': None,
                u'{{Abkürzungen}}': None, 
                u'{{Weibliche Wortformen}}': None,
                u'{{Männliche Wortformen}}': None,
                u'{{Alternative Schreibweisen}}': None, 
                u'{{Sprichwörter}}': None,
                u'{{Namensvarianten}}': None, 
                u'{{Symbole}}': None, 
                u'{{Bekannte Namensträger}}': None,
                u'{{Anmerkung}}': None,
                u'{{Anmerkungen}}': None,
                u'{{Kurzformen}}': None,
                u'{{Sinnverwandte Wörter}}': None,
                
                }

class BlockFactory(object):
    def __init__(self):
        self.counter = 0
    def new_block(self, block_start, section_class, default_section_class):
        if section_class is None:
            section_class = default_section_class
        class _Block(Block):
            start_pattern = block_start
            slug = str(self.counter)
            self.counter += 1
            def make_section(self, parent):
                return section_class(text=self.text, parent=parent)
        return _Block
block_factory = BlockFactory()

class NewFillerBlock(Block):
    def make_section(self, parent):
        return FillerSection(text=self.text, parent=parent)

block_classes = [block_factory.new_block(block_start, section_class, FillerSection)
                 for block_start, section_class in block_starts.items()]

class deWortartContentSection(ChildrenSection):
    
    def parse(self):
        super(deWortartContentSection, self).parse()
        if self.get_property('language') == 'Deutsch':
            blocks = list(Chopper(self.text, block_classes, filler_blocks=True,
                                   filler_block_class=NewFillerBlock))
            for block in blocks:
                section = block.make_section(parent=self)
                self.children.append(section.parse())
        else:
            section = FillerSection(text=self.text, parent=self)
            self.children.append(section.parse())
        return self

