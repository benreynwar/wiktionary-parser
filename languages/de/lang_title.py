# -*- coding: utf-8 -*-

from wiktionary_parser.formating_type import RegexFT
from wiktionary_parser.sections import FTSection
from wiktionary_parser.exceptions import InconsistentEntry
from wiktionary_parser.alerts import WordTitleMismatchAlert

def chop_prefix_get_data(section, groupdict):
    """
    Makes sure that the word in the regex matches that of the page.
    If it doesn't then chopping of the prefix was probably a mistake.
    """
    word = section.get_property('title')
    scraped_word = groupdict['word']
    if word != scraped_word:
        whole_word = groupdict['whole_word'].rstrip()
        #if word != whole_word:
        #    raise DodgyWord()
        groupdict['word'] = whole_word
    return groupdict

def no_word_get_data(section, groupdict):
    groupdict['word'] = section.get_property('title')
    return groupdict
    
    
class deLangTitleSection(FTSection):

    name = 'Language Title Section'

    def process_data(self, data):
        self.parent.set_property('language', data['language'])
        # Check that word is compatible with page title
        page_title = self.get_property('page').title
        word = data['word']
        if not self.word_matches_title(page_title, word, data['language']):
            message = '%s: %s does not match title %s' % (data['language'], word, page_title) 
            alert = WordTitleMismatchAlert(
                message=message, language=data['language'],
                title=page_title, word=word)
            self.alerts.append(alert)

    def word_matches_title(self, page_title, word, language):
        if language == 'Lateinisch':
            # FIXME: Could have a mapping from non-accented to accented letters.
            # Don't check Latin words because they put accents on word but not on title.
            return True
        if u'®' in word or u'[[' in word or u'!' in word or '?' in word or '&' in word:
            return True
        if '/' in page_title:
            return True
        if language == 'Indogermanisch':
            word = word.replace('*', '')
        #word = word.replace('&#39;', "'")
        return (word == page_title)

    fts = []

    # Incorrect Formatting Types that are Readable/Fixable
    standard_fix_func = lambda data: u'== %s ({{Sprache|%s}}) ==' % \
        (data['word'], data['language'])

    # Word needs fixing
    
    prefixes = set(['der', 'die', 'das', 'Der', 'Die', 'Das', 'de', 'the', 'to', 'dat'])
    prefix_strings = [u'(?:%s)' % prefix for prefix in prefixes]
    prefix_string = '|'.join(prefix_strings)


    fts.append(RegexFT(
            description=u"Unnötig Artikeln entfernt (auch 'to' vor englische Verben).",
            slug=u'Artikeln_enfernt',
            regex=u'==\s*(?P<whole_word>(?:(?:der)|(?:die)|(?:das)|(?:de)|(?:the)|(?:to))\s+(?P<word>.*?))\s*\({{Sprache\|(?P<language>[\w\s]+)}}\)\s*==',
            fix_func=standard_fix_func,
            get_data=chop_prefix_get_data, ))
    
    fts.append(RegexFT(
            description=u"'Wort' oder <nowiki>{{PAGENAME}} oder {{<includeonly>subst:</includeonly>PAGENAME}}</nowiki> benutzt in der Überschrift, statt das richtige Wort.",
            slug=u'Wort_ersetzt',
            regex=u'==\s*(?:(?:Wort)|(?:{{<includeonly>subst:</includeonly>PAGENAME}})|(?:{{PAGENAME}}))\s*\({{Sprache\|(?P<language>[\w\s]+)}}\)\s*==',
            fix_func=standard_fix_func,
            get_data=no_word_get_data, ))

    fts.append(RegexFT(
            description=u"Nur die Sprache steht in die Überschrift.  Wort eingefügt.",
            slug=u'Wort_eingefügt',
            regex=u'==\s*\({{Sprache\|(?P<language>[\w\s]+)}}\)\s*==',
            fix_func=standard_fix_func,
            get_data=no_word_get_data, ))

    fts.append(RegexFT(
            description=u"<nowiki>'''???''' {{Sprache|???}} ersetzt mit ??? {{Sprache|???}}</nowiki>",
            slug=u'Überschrift_Anführungsstriche_entfernt',
            regex=u"==\s*'''(?P<word>.*?)'''\s*\({{Sprache\|(?P<language>[\w\s]+)}}\)\s*==",
            fix_func=standard_fix_func, ))

    fts.append(RegexFT(
            description=u'<nowiki>Entfernt <span lang="???"> um Titel</nowiki>',
            slug=u'Entfernt_Span',
            regex=u'==\s*<span lang="[\w-]+">(?P<word>.*?)</span>\s*\({{Sprache\|(?P<language>[\w\s]+)}}\)\s*==',
            fix_func=standard_fix_func, ))

    # Correct Formatting Types

    def prefix_matching_func(section, groupdict):
        word = groupdict['word']
        word2 = groupdict['word2']
        if (word.capitalize() == word2 or word2.capitalize() == word):
            return True
        return False
            
    fts.append(RegexFT(
            description='Prefix z.B. "aero-, Aero-"',
            slug='Prefix',
            regex=u'==\s*(?P<word>\w*-?),\s*(?P<word2>\w*-?)\s*\({{Sprache\|(?P<language>[\w\s]+)}}\)\s*==',
            matching_func=prefix_matching_func,
            correct=True, ))

    # Not sure if this one is really correct.
    fts.append(RegexFT(
            description='Altgreichisch Wörter benutzen {{Polytonisch|???}} in der Überschrift.',
            slug='Polytonisch',
            regex=u'==\s*{{Polytonisch\|(?P<word>.*?)}}\s*\({{Sprache\|(?P<language>[\w\s]+)}}\)\s*==',
            correct=True, ))

    fts.append(RegexFT(
            description='Normal',
            slug='normal',
            regex=u'==\s*(?P<word>.*?)\s*\({{Sprache\|(?P<language>[\w\s]+)}}\)\s*==',
            correct=True, ))
    
    fts.append(RegexFT(
            description='Korean Words don\'t appear to match the pattern, but I\'m calling them correct for now.',
            slug='korean_hanja',
            regex=u'==\s*(?P<word>.*?)\s*\((?P<language>Koreanisch)\s*{{Schriftzeichen\|Hanja}}\)\s*==',
            correct=True, ))
    
    fts.append(RegexFT(
            description='Two languages are given for the word',
            slug='two_langs',
            regex=u'==\s*(?P<word>.*?)\s*\({{Sprache\|(?P<language>[\w\s]+)}}, {{Sprache\|(?P<language2>[\w\s]+)}}\)\s*==',
            correct=True, ))
    
    fts.append(RegexFT(
            description=u'<nowiki>[[Hilfe:Umschrift|Umschrift]] wird mit {{Sprache|Umschrift}} ersetzt.</nowiki>',
            slug=u'Umschrift_Überschrift_Formatierung',
            regex=u'==\s*(?P<word>.*?)\s*\(\[\[Hilfe:Umschrift\|(?P<language>Umschrift)\]\]\)\s*==',
            fix_func=standard_fix_func, ))
    
    fts.append(RegexFT(
            description=u'Verwandschaftgrade Überschrift soll Ebene 4 sein nicht Ebene 2.',
            slug=u'Verwandtschaftsgrade_Überschriftebene',
            regex=u'==\s*(?P<contents>(Verwandtschaftsgrade)|(Beziehungen duch eine Ehe)\s*\(.*?\))\s*==',
            ignore=True, readable=False,
            fix_func=lambda section, groupdict: u'==== %s ====' % groupdict['contents'],))
    
    fts.append(RegexFT(
            description=u'Klammern fehlend um die Sprache.',
            slug=u'Klammern_fehlend_um_Sprache',
            regex=u'==\s*(?P<word>.*?)\s*\(?{{Sprache\|(?P<language>[\w\s]+)}}\)?\s*==',
            fix_func=standard_fix_func, ))

#    fts.append(RegexFT(
#            description='No brackets around the language.',
#            slug='forgot_brackets',
#            regex=u'==\s*(?P<word>.*?)\s*{{Sprache\|(?P<language>[\w\s]+)}}\s*==',
#            fix_func=standard_fix_func, ))
    
    fts.append(RegexFT(
            description='Two languages are given for the word but incorrect formatted.',
            slug='two_langs_incorrect',
            regex=u'==\s*(?P<word>.*?)\s*\({{Sprache\|(?P<language>[\w\s]+)}}[\s,/]*{{Sprache\|(?P<language2>[\w\s]+)}}\)\s*==',
            fix_func=lambda section, groupdict: u'== %s ({{Sprache|%s}}, {{Sprache|%s}}) ==' % \
                (groupdict['word'], groupdict['language'], groupdict['language2']),))
    

