# -*- coding: utf-8 -*-

import re

from wiktionary_parser.wiktionary_utils.text_splitter import Block, Chopper, FillerBlock
from wiktionary_parser.formating_type import RegexFT
from wiktionary_parser.patch import Patch
from wiktionary_parser.sections import ChildrenSection, FTSection, FillerSection, PatchedSection
from wiktionary_parser.exceptions import InconsistentEntry
from wiktionary_parser.alerts import LanguageMismatchAlert
from wiktionary_parser.languages.de.word import deSubstantiv

allowed_types = [
    u'Substantiv', u'Vorname', u'Nachname', u'Eigenname', u'Toponym', u'Singularetantum',
    u'Pluraletantum',
    u'Verb', u'Konjugierte Form', u'Hilfsverb', u'Deklinierte Form',
    u'Partizip II', u'Partizip I',
    u'Pronomen', u'Indefinitpronomen', u'Personalpronomen', u'Possessivpronomen',
    u'Demonstrativpronomen', u'Reflexivpronomen', u'Relativpronomen',
    u'Interrogativpronomen', u'Interrogativpronomen',
    u'Präfix', u'Ortsnamen-Grundwort', u'Suffix', u'Gebundenes Lexem', u'Lexem',
    u'Adjektiv',
    u'Adverb', u'Pronominaladverb', u'Interrogativadverb',
    u'Abkürzung',
    u'Wortverbindung', u'Redewendung', u'Sprichwort', u'Merkspruch',
    u'Interjektion', u'Onomatopoetikum', u'Grußformel',
    u'Numerale', u'Buchstabe',
    u'Präposition',
    u'Artikel', 
    u'Konjunktion', u'Subjunktion', 
    u'Partikel', u'Vergleichespartikel', u'Gradpartikel',
    u'Modalpartikel', u'Fokuspartikel', u'Antwortpartikel',
    u'Vergleichspartikel', u'Negationspartikel',
    u'Postposition',
    u'Satzzeichen',]


class deWortartTitleSection(ChildrenSection):

    name = 'Wortart Title Section'

    class WortartTitlePieceBlock(Block):
        start_pattern = '{{Wortart'
        slug = 'Wortart_Title_Piece_Block'
        
    class WortartTitleTagBlock(Block):
        start_pattern = '==='
        slug = 'Wortart_Title_Tag_Block'
    
    def parse(self):
        super(deWortartTitleSection, self).parse()
        for piece in Chopper(self.text, [self.WortartTitlePieceBlock, self.WortartTitleTagBlock],
                             filler_blocks=True, include_tags=True):
            if isinstance(piece, FillerBlock) or isinstance(piece, self.WortartTitleTagBlock):
                section = FillerSection(text=piece.text, parent=self, correct=True)
            else:
                section = deWortartTitlePieceSection(text=piece.text, parent=self)
            self.children.append(section.parse())
        # Check to see if it is a kind of name
        # This is a low tech check.  Improve later.
        hints = set(['Vorname', 'Nachname', 'Eigenname'])
        word = self.get_property('word')
        if word:
            for hint in hints:
                if hint in self.text:
                    word.is_name = True
        return self


# A whole bunch of patches for processing the level 3 wortart headings follows

class deWortartTitlePieceSection(PatchedSection):
    
    patches = []

    def wortart_pd(section, data):
        data['before'] = ''
        try:
            section.check_property('language', data['language'])
        except InconsistentEntry:
            page_title = section.get_property('page').title
            language1 = section.get_property('language')
            language2 = data['language']
            message = '%s: Languages inconsistent (%s and %s)' % (page_title, language1, language2) 
            alert = LanguageMismatchAlert(
                message=message, title=page_title, language1=language1,
                language2=language2, )
            section.alerts.append(alert)
        section.parent.parent.add_type(data['type'])

    patches.append(Patch( 
            regex=u'^{{Wortart\|(?P<type>[\w\s\-]+)\|(?P<language>[\w\s]+)}}(?P<after>.*)$',
            slug='Wortart',
            process_data_func=wortart_pd,))

    def wortart_no_lang_pd(section, data):
        data['before'] = ''
        section.get_property('types').append(data['type'])
        
    patches.append(Patch( 
            regex=u'^{{Wortart\|(?P<type>[\w\s\-]+)}}(?P<after>.*)$',
            slug='Wortart_no_lang',
            process_data_func=wortart_no_lang_pd,))
            
    def gender_pd(section, data):
        word = section.get_property('word')
        if word:
            gender = data['gender']
            if gender == 'w':
                gender = 'f'
            word.gender = gender

    patches.append(Patch(
            regex=u'^(?P<before>.*){{(?P<gender>[mfnw])}}(?P<after>.*)$',
            slug='gender',
            process_data_func=gender_pd,))
    
    def plural_pd(section, data):
        pass
        #section.get_property('plurals').append(data['plural'])

    patches.append(Patch(
            regex=u'^(?P<before>.*)Plural:?\s*„?(?P<plural>[\w[\]\\\/]+)“?(?P<after>.*)$',
            slug='plural',
            process_data_func=plural_pd,))
    
    terms = [
        (u'(?:<!--.*-->?)', (), ),
        # NOUNS
        # Gender
        (u'kein Geschlecht', (),),
        (u'\s[mfnw][\s\.]', (),),
        (u"'[mfnw]'", (),),
        (u'{{u}}', (),),
        (u'{{Utrum}}', (),),
        # Plural
        (u'{{kSg\.}}', (),),
        (u'{{kPl\.}}', (),),
        (u'nur Plural', (),),
        (u'ohne Plural', (),),
        (u'kein Plural', (),),
        (u'kein Pl\.', (),),
        (u'meist Pl\.', (),),
        (u'pl\.', (),),
        (u'nur im Plural', (),),
        (u'nur Singular', (),),
        (u'Pl\. ungebräuchlich', (),),
        (u'vorwiegend im Pl\.', (),),
        (u'meist im Plural', (),),
        (u"''Plural''", (),),
        # Types
        (u'Toponym', (),),
        (u'Vorname', (),),
        (u'Nachname', (),),
        (u'Eigenname ohne Artikel', (),),
        (u'Eigenname mit Artikel', (),),
        (u'Eigenname', (),),
        (u'Eigename', (),),
        (u'Name', (),),
        (u'Dialektausdruck', (),),        
        (u'Redewendung', (),),        
        (u'Akronym', (),),        
        (u'Wortverbindung', (),),        
        (u'Tierlaut', (),),
        (u'Fremdwort', (),),
        (u'Singularetantum', (),),
        # Property
        (u'mit adjektivischer Deklination', (),),
        (u'adjektivische Deklination', (),),
        (u'ohne Artikel', (),),
        (u'mit Artikel', (),),
        # VERBS
        (u'unregelmäßig', ('regular', False),),
        (u'regelmäßig', ('regular', True),),
        (u'regelmässig', ('regular', True),),
        (u'intransitiv', (),),
        (u'transitiv', (),),
        (u'reflexiv', (),),
        (u'infinitiv', (),),
        (u'schwach', (),),
        (u'starke Beugung', (),),
        (u'stark', (),),
        (u'nicht trennbar', (),),
        (u'untrennbar', (),),
        (u'trennbar', (),),
        (u'unpersönlich', (),),
        (u'Vollverb', (),),
        (u'haben', (),),
        (u'sein', (),),
        # ADJECTIVE
        (u'{{kSt\.}}', (),),
        (u'unflektierbar', (),),
        (u'indekl\.', (),),
        (u'indeklinabel', (),),
        (u'undeklinierbar', (),),
        (u'keine Steigerung', (),),
        (u'ohne Steigerung', (),),
        (u'nicht steigerbar', (),),
        (u'steigerbar', (),),
        (u'unflektiert', (),),
        (u'attributiv', (),),
        # PREPOSITION
        (u'mit Genitiv', (),),
        ]

    bad_terms = [
        u'{{Geschlecht}}',
        u'und',
        u'auch',
        u'oder',
        u'</?small>',
        ]

    for term_info in terms:
        term = term_info[0]
        patches.append(Patch(
                regex=u'^(?P<before>.*?)(?P<term>%s)(?P<after>.*)$' % term,
                slug=term,
                process_data_func=lambda section, data: None,))

    for term in bad_terms:
        patches.append(Patch(
                regex=u'^(?P<before>.*?)(?P<term>%s)(?P<after>.*)$' % term,
                slug=term,
                process_data_func=lambda section, data: None,))
                

class Whatever(object):

    '^{{Wortart\|(?P<type>[\w\s]+))}}'
    '{{[mfn]}}'
    
    fts = []

    fts.append(RegexFT(
            description="Normal",
            slug='normal',
            regex='^{{Wortart\|(?P<type>[\w\s]+)\|(?P<language>[\w\s]+)}}\s*,?\s*$',
            correct = True, ))
    
    fts.append(RegexFT(
            description="Wortart mit Geschlecht",
            slug='geschlecht',
            regex='^{{Wortart\|(?P<type>[\w\s]+)\|(?P<language>[\w\s]+)}}\s*,\s*{{(?P<gender>[mfn])}}\s*$',
            correct = True, ))

    fts.append(RegexFT(
            description="Keine Sprache mit der Wortart.",
            slug='keine_Sprache_mit_der_Wortart',
            regex='^{{Wortart\|(?P<type>[\w\s]+)}}\s*,?\s*(?:{{(?P<gender>[mfn])}}\s*)?$',
            readable = False, 
            ))

