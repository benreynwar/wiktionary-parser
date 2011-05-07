# -*- coding: utf-8 -*-

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.languages.de.page import dePage
from wiktionary_parser.languages.de.sections import deLanguageSection, SubstantivTabelleSection #, SilbentrennungSection
from wiktionary_parser.languages.de.lang_title import deLangTitleSection
from wiktionary_parser.languages.de.wortart_title import deWortartTitlePieceSection
from wiktionary_parser.alerts import NoFTMatchAlert, PatchRemainderAlert, LanguageMismatchAlert, WordTitleMismatchAlert, FixableAlert

import codecs

xml_file = open('../../wiktionary_data/dewiktionary-20110504-pages-articles.xml')

class Scan(object):
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.word_mismatch_alerts = []
        self.language_mismatch_alerts = []
        self.has_run = False
        
    def parse_if_german(self, page):
        page.parse(shallow=True)
        # Only parse german pages
        for child in page.children:
            if isinstance(child, deLanguageSection):
                child.parse(shallow=True)
                for grandchild in child.children:
                    if (isinstance(grandchild, deLangTitleSection) or
                        grandchild.get_property('language') == 'Deutsch'):
                        grandchild.parse()

    def run(self):
        if self.has_run:
            raise StandardError('Already Run')
        self.has_run = True
        xml_parser = XMLPageParser(self.xml_file, dePage)
        counter = 0
        alert_counter = 0
        for page in xml_parser:
            try:
                counter += 1
                if counter % 1000 == 0:
                    print counter
                page.parse()
                all_alerts = page.get_all_alerts()
                if not all_alerts:
                    continue
                for alert_type, alerts in all_alerts.items():
                    for alert in alerts:
                        alert_counter += 1
                        print counter, alert_counter
                        print alert.message
                        #if alert_type is NoFTMatchAlert and alert.section_class == SubstantivTabelleSection:
#                            silben_counter += 1
#                            print silben_counter, counter
                        #    print alert.text
#                for alert in all_alerts.get(NoFTMatchAlert, []):
#                    print alert.title, alert.text
#                for alert in all_alerts.get(PatchRemainderAlert, []):
#                    print alert.title, alert.patched_text, '--------------', alert.text
            except:
                print 'Failed on page %s' % page.title
                print page.text
                raise

    def check_alerts_out(self, page):
        alerts = page.get_property('alerts')
        if alerts:
            #print page.title
            for alert in alerts:
                #print alert.message
                if isinstance(alert, NoFTMatchAlert):
                    print alert.title, alert.text
                if isinstance(alert, PatchRemainderAlert):
                    counter += 1
                    print counter, counter3, counter2, alert.title, alert.patched_text, '-------------------', alert.text
                if isinstance(alert, WordTitleMismatchAlert):
                    self.word_mismatch_alerts.append(alert)
                if isinstance(alert, LanguageMismatchAlert):
                    self.language_mismatch_alerts.append(alert)

    def patch_summary(self):
        string = ''
        for patch in deWortartTitlePieceSection.patches:
            string += '%s %s\n' % (patch.regex, unicode(patch.counter))
        return string
            

    def word_mismatch_wikitable(self):
        language_mismatch_alerts.sort(
            key=lambda alert: (alert.language.lower(), alert.title.lower()))
        wikitable_str = u'''{| class="wikitable" border="1"
|-
!  Sprache
!  Titel
!  Überschrift Wort
'''
        for alert in mismatch_alerts:
            wikitable_str += u'|-\n| %s || [[%s]] || %s\n' % (alert.language, alert.title, alert.word)
        wikitable_str += u'|}\n'
        return wikitable_str
        
scan = Scan(xml_file)

if __name__ == "__main__":
    scan.run()
    print scan.patch_summary()
