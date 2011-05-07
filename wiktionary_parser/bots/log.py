import re

from wiktionary_parser.sections import Level2Block, Level3Block, Section, FillerSection
from wiktionary_parser.exceptions import ParsingError
from wiktionary_parser.wiktionary_utils.text_splitter import Chopper, FillerBlock
from wiktionary_parser.page import Page
from wiktionary_parser.bots.utils import wikidatetime

class LogPage(Page):
    """
    The page where the bots logs are kept.
    """
    def parse(self):
        self.einsatz_sections = {}
        for level2block in Chopper(self.text, [Level2Block,],
                                   filler_blocks=True, include_tags=True):
            # It's allowed to have some unknown text before the first
            # level2 block.
            if isinstance(level2block, FillerBlock):
                section = FillerSection(text=level2block.text, parent=self)
                section = section.parse()
            else:
                section = EinsatzSection(text=level2block.text, parent=self, heading=level2block.start_tag)
                section = section.parse()
                if section.get_property('einsatz_slug') in self.einsatz_sections:
                    raise ParsingError('EinsatzSection title is not unique.')
                self.einsatz_sections[section.get_property('einsatz_slug')] = section
            self.children.append(section)
        return self

    def add_einsatz_section(self, einsatz):
        if einsatz.title in self.einsatz_sections:
            raise StandardError('title is not unique')
        section = EinsatzSection.create(einsatz)
        self.einsatz_sections[einsatz.title] = section
        self.children.append(section)
        return section
                        
class EinsatzSection(Section):
    """
    The section of a log page corresponding to one bot run.
    """
    def __init__(self, heading=None, *args, **kwargs):
        super(EinsatzSection, self).__init__(*args, **kwargs)
        self.property_dict['einsatz_slug'] = None
        self.heading = heading
        self.ft_sections = {}
    def parse(self):
        regex = '== (?P<title>.+) =='
        pattern = re.compile(regex, re.UNICODE)
        match = pattern.match(self.heading)
        if match:
            self.set_property('einsatz_slug', match.groupdict()['title'])
        else:
            raise ParsingError('Cannot parse log page.')
        for level3block in Chopper(self.text, [Level3Block,],
                                   filler_blocks=True, include_tags=True):
            # It's allowed to have some unknown text before the first
            # level3 block.
            if isinstance(level3block, FillerBlock):
                section = FillerSection(text=level3block.text, parent=self)
                section = section.parse()
                self.top_section = section
            else:
                section = FTSection(text=level3block.text, parent=self, heading=level3block.start_tag)
                section = section.parse()
                if section.get_property('ft_slug') in self.ft_sections:
                    raise ParsingError('Two EinsatzSections with same title.')
                self.ft_sections[section.get_property('ft_slug')] = section
            self.children.append(section)
        return self

    def finish(self):
        regex = 'STATUS: Running'
        self.top_section.text = re.sub(regex, 'STATUS: Finished', self.top_section.text)
        
    def add_change(self, change):
        ft = change.fix
        if ft.slug not in self.ft_sections:
            ft_section = FTSection.create(ft)
            self.ft_sections[ft.slug] = ft_section
            self.children.append(ft_section)
        self.ft_sections[ft.slug].add_change(change)

    @classmethod
    def create(cls, einsatz):
        heading = '== %s ==' % einsatz.title
        string = '\n' + heading + '\n' + wikidatetime + '<br/>\n'
        string += einsatz.description + '<br/>\n'
        string += 'STATUS: Running<br/>\n'
        einsatz_section = cls(heading=heading, text=string)
        einsatz_section.parse()
        return einsatz_section

class FTSection(Section):
    """
    The log of each bot run, groups the changes made into different sets of
    corrected formating types.
    """
    def __init__(self, heading=None, *args, **kwargs):
        super(FTSection, self).__init__(*args, **kwargs)
        self.property_dict['ft_slug'] = None
        self.heading = heading

    def parse(self):
        regex = u'=== (?P<title>[\w\s]+) ==='
        pattern = re.compile(regex, re.UNICODE)
        match = pattern.match(self.heading)
        if match:
            self.set_property('ft_slug', match.groupdict()['title'])
        else:
            print self.heading
            raise ParsingError('Cannot parse log page.')
        return self

    @classmethod
    def create(cls, ft):
        heading = u'=== %s ===' % ft.slug
        string = u'\n' + heading + u'\n'
        string += ft.description + u'<br/>\n\n'
        ft_section = cls(heading=heading, text=string)
        ft_section.parse()
        return ft_section

    def add_change(self, change):
        if self.text[-1] == u'\n':
            self.text = self.text[:-1]
        self.text += u'[[%s]], \n' % change.word

