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
        self.alert_sections = {}
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
                section = AlertSection(text=level3block.text, parent=self, heading=level3block.start_tag)
                section = section.parse()
                if section.get_property('alert_slug') in self.alert_sections:
                    raise ParsingError('Two EinsatzSections with same title.')
                self.alert_sections[section.get_property('alert_slug')] = section
            self.children.append(section)
        return self

    def finish(self):
        regex = 'STATUS: Running'
        self.top_section.text = re.sub(regex, 'STATUS: Finished', self.top_section.text)
        
    def add_change(self, change):
        alert = change.alert
        if alert.slug not in self.alert_sections:
            alert_section = AlertSection.create(alert)
            self.alert_sections[alert.slug] = alert_section
            self.children.append(alert_section)
        self.alert_sections[alert.slug].add_change(change)

    @classmethod
    def create(cls, einsatz):
        heading = '== %s ==' % einsatz.title
        string = '\n' + heading + '\n' + wikidatetime + '<br/>\n'
        string += einsatz.description + '<br/>\n'
        string += 'STATUS: Running<br/>\n'
        einsatz_section = cls(heading=heading, text=string)
        einsatz_section.parse()
        return einsatz_section

class AlertSection(Section):
    """
    The log of each bot run, groups the changes made into different sets of
    corrected formating types.
    """
    def __init__(self, heading=None, *args, **kwargs):
        super(AlertSection, self).__init__(*args, **kwargs)
        self.property_dict['alert_slug'] = None
        self.heading = heading

    def parse(self):
        regex = u'=== (?P<title>[\w\s]+) ==='
        pattern = re.compile(regex, re.UNICODE)
        match = pattern.match(self.heading)
        if match:
            self.set_property('alert_slug', match.groupdict()['title'])
        else:
            print self.heading
            raise ParsingError('Cannot parse log page.')
        return self

    @classmethod
    def create(cls, alert):
        heading = u'=== %s ===' % alert.slug
        string = u'\n' + heading + u'\n'
        string += alert.description + u'<br/>\n\n'
        alert_section = cls(heading=heading, text=string)
        alert_section.parse()
        return alert_section

    def add_change(self, change):
        if self.text[-1] == u'\n':
            self.text = self.text[:-1]
        self.text += u'[[%s]], \n' % change.word

