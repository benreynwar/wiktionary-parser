# -*- coding: utf-8 -*-

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.languages.de.page import dePage
from wiktionary_parser.languages.de.sections import deLanguageSection, deWortartSection, deWortartContentSection
from wiktionary_parser.languages.de.substantiv_tabelle import SubstantivTabelleSection
from wiktionary_parser.languages.de.alerts import SubstantivTabelleAlert, FixableSubstantivTabelleAlert

import codecs

xml_file = open('/Users/Ben/Web/wiktionary_data/dewiktionary-20090927-pages-articles.xml')
alert_file = codecs.open('/Users/Ben/Web/wiktionary_parser/bots/st_alerts.txt', 'w', 'utf-8')

class Scan(object):
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.has_run = False
        
    def run(self):
        if self.has_run:
            raise StandardError('Already Run')
        self.has_run = True
        xml_parser = XMLPageParser(self.xml_file, dePage)
        counter = 0
        alert_counter = 0
        f_alert_counter = 0
        st_counter = 0
        for page in xml_parser:
            try:
                counter += 1
                if counter % 1000 == 0:
                    print counter
                page.parse()
                # get wortart sections
                wortart_sections = []
                for section in page.children:
                    if isinstance(section, deLanguageSection):
                        for section2 in section.children:
                            if isinstance(section2, deWortartSection):
                                wortart_sections.append(section2)
                alerts = []
                f_alerts = []
                for section in wortart_sections:
                    word = section.get_property('word')
                    if word and not word.is_name:
                        alerts = alerts + section.get_alerts(SubstantivTabelleAlert)
                        f_alerts = f_alerts + section.get_alerts(FixableSubstantivTabelleAlert)
                    # Check if it has a substativ-tabelle
                        for child in section.children:
                            if isinstance(child, deWortartContentSection):
                                for grandchild in child.children:
                                    if isinstance(grandchild, SubstantivTabelleSection):
                                        st_counter += 1
                for alert in alerts:
                    alert_counter += 1
                    print counter, alert_counter, f_alert_counter, st_counter
                    print alert.message
                for alert in f_alerts:
                    f_alert_counter += 1
                    print counter, alert_counter, f_alert_counter, st_counter
                    print alert.message
            except:
                print 'Failed on page %s' % page.title
                print page.text
                raise

scan = Scan(xml_file)

if __name__ == "__main__":
    scan.run()
