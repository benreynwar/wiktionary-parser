# -*- coding: utf-8 -*-

import re
from string import Template

from wiktionary_parser.wiktionary_utils.matching import MatchMatrix, CannotPair
from wiktionary_parser.wiktionary_utils.regex_splitter import chop
from wiktionary_parser.wiktionary_utils.formating import remove_enclosing_formating

from wiktionary_parser.sections import Section, FillerSection, LeafSection
from wiktionary_parser.formating_type import RegexFT
from wiktionary_parser.exceptions import NotParsedYet, FixingError

from .word import deSubstantiv
from .alerts import SubstantivTabelleAlert, FixableSubstantivTabelleAlert, UnreadableAlert

from .grammar.base import CASES, GENDERS, NOM
from .grammar.articles import ARTICLES, POSSIBLE_ARTICLES
from .grammar.nouns import fks, fks_from_genders, fks_for_gender

# Possible exceptions
# Months - e.g. Maertz
# Languages - e.g. Niederlaendisch
# Foreign - e.g. Wiktionary
# Name - e.g. Hornungs
# Multiple words

# Get slug refering to case and plurality.
def cps(case, plural):
    if not plural:
        return case + u'_S'
    else:
        return case + u'_P'

# If the levenshtein required to correct an entry is greater than
# this then no correction is suggested.
LEV_CUTOFF = 2


class SubstantivTabelleException(Exception):
    pass
class CannotAssignDeclinations(SubstantivTabelleException):
    pass
class CannotParse(SubstantivTabelleException):
    pass


nom_article_to_gender = dict([(ARTICLES[(NOM, False, gender)], gender) for gender in GENDERS])


class SubstantivFormating(object):
    
    def __init__(self, start_tag, stop_tag):
        self.start_tag = start_tag
        self.stop_tag = stop_tag
        
    def clean(self, text):
        new_text = remove_enclosing_formating(text, re.escape(self.start_tag),
                                              re.escape(self.stop_tag), remove_half=True)
        if new_text == text:
            return None
        else:
            return new_text
    
    def apply(self, text):
        return self.start_tag + text + self.stop_tag


small_format = SubstantivFormating('<small>', '</small>')
bracket_format = SubstantivFormating('(', ')')


class SubstantivSingleForm(object):
    """
    Contains an entry from Substantiv-Tabelle.  The splitting
    by <br/> is already done, so several of these may correspond
    to one entry.
    """

    # The order of the formats matters here.
    # We assume <small> tag will enclose the brackets.
    formats = [small_format, bracket_format]
    sa_regex = (lambda name: u'(?P<%s>%s)' % (
            name, u'|'.join([u'(?:%s)' % pa for pa in POSSIBLE_ARTICLES])))
    single_article_pattern = re.compile(u'^%s$' % sa_regex('article'), re.UNICODE)
    article_regex = u'%s(?:\s*/?\s*\(?%s\)?)?' % (sa_regex('article'), sa_regex('article2'))
    article_pattern = re.compile(u'^%s$' % article_regex, re.UNICODE)
    split_regex = u'^\s*(?P<articles>(?:<small>)?\(?%s\)?(?:</small>)?)\s*(?P<dekl>.*?)\s*$' % article_regex
    split_pattern = re.compile(split_regex, re.UNICODE)

    def __init__(self, case, plural, raw=None, article=None, dekl=None):
        self.raw = raw
        self.case = case
        self.plural = plural
        self.cleaned = None
        self.article = article
        self.dekl = dekl
        self.applied_formats = []
        self.applied_article_formats = []

    def __repr__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        if self.dekl:
            return self.dekl + u'(%s, %s)' % (self.case, self.plural)
        else:
            return self.raw + u'(%s, %s)' % (self.case, self.plural)
        
    def sibling(self, first=False, **kwargs):
        ssf = SubstantivSingleForm(self.case, self.plural, **kwargs)
        # make copies
        ssf.applied_formats = self.applied_formats[:]
        if first:
            ssf.applied_article_formats = self.applied_article_formats[:]
        return ssf

    def clean(self):
        self.cleaned = self.raw
        for format in self.formats:
            cleaned = format.clean(self.cleaned)
            if cleaned is not None:
                self.cleaned = cleaned
                self.applied_formats.append(format)
        self.cleaned = self.cleaned.strip()
        self.cleaned = self.cleaned.strip(',')
        # Get rid of Wiki links
        self.cleaned = self.cleaned.replace('[', '')
        self.cleaned = self.cleaned.replace(']', '')
                
    def clean_article(self):
        if self.article:
            for format in self.formats:
                cleaned = format.clean(self.article)
                if cleaned is not None:
                    self.article = cleaned
                    self.applied_article_formats.append(format)

    def unformated_render(self):
        if self.article:
            return self.article + ' ' + self.dekl
        else:
            return self.dekl

    def render(self):
        f_article = None
        # apply formats in reverse order that they were removed
        if self.article:
            f_article = self.article
            for format in reversed(self.applied_article_formats):
                f_article = format.apply(f_article)
        if f_article:
            combined = f_article + ' ' + self.dekl
        else:
            combined = self.dekl
        for format in reversed(self.applied_formats):
            combined = format.apply(combined)
        return combined

    def process(self):
        # Replace a funny slash
        self.raw = self.raw.replace(u'\u2013', u'-')
        self.raw = self.raw.replace(u'\u2014', u'-')
        blank_regexes = ['.*{{fehlend.*', '<center>\s*-\s*</?center>', '-+', '{{center\|-}}']
        bracketed = ['(%s)?' % regex for regex in blank_regexes]
        blank_regex = '^\s*%s\s*$' % ''.join(bracketed)
        blank_pattern = re.compile(blank_regex, re.UNICODE)
        # Check that it is valid
        if blank_pattern.match(self.raw):
            return []
        # Remove any formating surrounds all contents
        self.clean()
        # Extract the articles
        match = self.split_pattern.match(self.cleaned)
        if match:
            gd = match.groupdict()
            self.article = gd['articles']
            self.dekl = gd['dekl']
        else:
            self.dekl = self.cleaned
        # Remove formating from article
        self.clean_article()
        # See if a slash '/' separates out two forms
        # If it does we just return a list of these forms
        chop_position = 0
        chop_pattern = re.compile(u'([/,;])')
        while True:
            chopped = chop(self.unformated_render(),
                           chop_pattern, instance=chop_position)
            if not chopped:
                break
            chop_position += 1
            all_match = True
            all_ssfs = []
            first = True
            for part in chopped:
                ssf = self.sibling(first=first, raw=part)
                first = False
                try:
                    ssfs = ssf.process()
                except CannotParse:
                    all_match = False
                    break
                for ssf in ssfs:
                    if not ssf.dekl:
                        all_match = False
                        break
                if not all_match:
                    break
                all_ssfs = all_ssfs + ssfs
            if all_match and all_ssfs:
                # If only the first one has an article, then that article
                # was probably meant to be for all of them.
                if all_ssfs[0].article:
                    no_others_have_article = True
                    for ssf in all_ssfs[1:]:
                        if ssf.article:
                            no_others_have_article = False
                    if no_others_have_article:
                        for ssf in all_ssfs[1:]:
                            ssf.article = all_ssfs[0].article
                            ssf.applied_article_formats = all_ssfs[0].applied_article_formats
                return all_ssfs
        # Check if there are two articles
        if self.article:
            single_or_double_match = self.article_pattern.match(self.article)
            if not single_or_double_match:
                raise CannotParse('Article doesnt match pattern')
            single_match = self.single_article_pattern.match(self.article)
            if not single_match:
                # We appear to have two articles there
                gd = single_or_double_match.groupdict()
                article1 = gd['article']
                article2 = gd['article2']
                dekl1 = self.sibling(article=article1, dekl=self.dekl)
                dekl2 = self.sibling(article=article2, dekl=self.dekl)
                return [dekl1, dekl2]
        return [self]


class SubstantivMultipleForm(object):
    
    version_splitter_regex = u'</?\s*br\s*/?>'

    def __init__(self, raw, case, plural):
        self.raw = raw
        self.case = case
        self.plural = plural
        self.forms = None

    def process(self):
        # First split the form into its multiple versions if any
        self.raws = re.split(self.version_splitter_regex, self.raw)
        self.forms = []
        for raw in self.raws:
            form = SubstantivSingleForm(raw=raw, case=self.case, plural=self.plural)
            # Process the form.  This returns a list since potentially
            # the form may have been split into several
            forms = form.process()
            for form in forms:
                self.forms.append(form)
        # Little fix to change [Kind, Kinde] into [Kind(e)] and
        # [Kinds, Kindes] into [Kind(e)s]
        if len(self.forms) == 2:
            if len(self.forms[0].dekl) > len(self.forms[1].dekl):
                lf = self.forms[0]
                sf = self.forms[1]
            else:
                lf = self.forms[1]
                sf = self.forms[0]
            if lf.article == sf.article:
                if len(lf.dekl) == len(sf.dekl) + 1:
                    if lf.dekl[:-1] == sf.dekl and lf.dekl[-1] == 'e':
                        sf.dekl = sf.dekl + u'(e)'
                        self.forms = [sf]
                if len(lf.dekl) == len(sf.dekl) + 1:
                    if lf.dekl[:-2] == sf.dekl[:-1] and lf.dekl[-2:] == 'es' and sf.dekl[-1] == 's':
                        sf.dekl = sf.dekl[:-1] + u'(e)s'
                        self.forms = [sf]
        return self.forms
        

class SubstantivSingleFormColl(object):

    def __init__(self, forms, plural, poss_genders=GENDERS,
                 poss_fks=fks, name=None):
        self.poss_genders = poss_genders
        self.poss_fks = fks
        self.forms = {}
        self.plural = plural
        for form in forms.values():
            self.add_form(form, possible_genders=self.poss_genders,
                          possible_fks=self.poss_fks)
        if NOM not in self.forms:
            raise StandardError(u'Nominativ form must be given')
        if name is None:
            self.name = unicode(self.forms[NOM])
        else:
            self.name = name
        self.set_poss_fks(poss_fks)
        # Work out whether the nominative article is consistent with the 
        # given possible genders.
        if self.forms[NOM].article and not self.plural:
            try:
                gender = nom_article_to_gender[self.forms[NOM].article]
            except KeyError:
                raise CannotAssignDeclinations()
            if gender in poss_genders:
                self.set_poss_genders(set([gender]))
            else:
                raise StandardError(u'Nominative article does not match gender')
        else:
            self.set_poss_genders(poss_genders)

    def __str__(self):
        return unicode(self).encode('utf-8')
    def __repr__(self):
        return unicode(self).encode('utf-8')
    def __unicode__(self):
        return self.name

    def copy(self):
        the_copy = SubstantivSingleFormColl(
            forms=self.forms, plural=self.plural, poss_genders=self.poss_genders.copy(),
            poss_fks=self.poss_fks.copy(), name=self.name+'_copy')
        return the_copy                     

    def add_form(self, form, possible_genders, possible_fks):
        if not possible_genders or not possible_fks:
            raise StandardError('There must be some possible genders and fks.')
        if form.case in self.forms:
            raise StandardError(u'Multiple forms of same case')
        if form.plural != self.plural:
            raise StandardError(u'Plurality is not consistent')
        self.forms[form.case] = form
        # Then we set genders and flexionsklassen.
        self.set_poss_genders(possible_genders)
        self.set_poss_fks(possible_fks)
        
    def narrow_flexionsklassen(self, old_flexionsklassen, poss_genders):
        new_fks = set([])
        for fk in fks_from_genders(poss_genders):
            if fk in old_flexionsklassen:
                new_fks.add(fk)
        return new_fks

    def set_poss_genders(self, poss_genders):
        self.poss_genders = poss_genders
        new_fks = self.narrow_flexionsklassen(self.poss_fks, poss_genders)
        if not new_fks:
            raise StandardError('No Possible noun cases now')
        self.poss_fks = new_fks

    def narrow_genders(self, old_genders, poss_fks):
        new_genders = set([])
        for gender in old_genders:
            for fk in poss_fks:
                if fk in fks_for_gender[gender]:
                    new_genders.add(gender)
                    break
        return new_genders

    def set_poss_fks(self, poss_fks):
        self.poss_fks = poss_fks
        new_genders = self.narrow_genders(self.poss_genders, poss_fks)
        if not new_genders:
            raise StandardError('No Possible gender')
        self.poss_genders = new_genders

    def form_matches(self, this_form):
        article_matches = None
        dekl_matches = None
        article_fixable = False
        dekl_fixable = False
        correct_article = None
        correct_dekl = None
        matched_genders = self.poss_genders.copy()
        matched_fks = self.poss_fks.copy()
        key = (this_form.case, this_form.plural)
        # If the nominative form doesnt have an article then neither should this form
        if self.forms[NOM].article is None:
            if this_form.article is None:
                article_matches = True
            else:
                article_matches = False
                article_fixable = True
                correct_article = None
        # See if the article here matches any of the possible genders
        if article_matches is None:
            for gender in matched_genders.copy():
                if this_form.article == ARTICLES[(this_form.case, this_form.plural, gender)]:
                    article_matches = True
                else:
                    matched_genders.remove(gender)
            # If there's only one possible gender then we can correct the article easily.
            if not article_matches:
                if len(self.poss_genders) == 1:
                    article_fixable = True
                    correct_article = ARTICLES[(this_form.case, this_form.plural, list(self.poss_genders)[0])]
                    matched_genders = self.poss_genders
                else:
                    article_fixable = False
        if article_matches is None:
            article_matches = False
        # What are the allowed noun cases
        # We could only run this is matched_genders has changed, but we don't.
        matched_fks = self.narrow_flexionsklassen(matched_fks, matched_genders)
        # The Noun form should start with the nominative form
        if not this_form.dekl.startswith(self.forms[NOM].dekl):
            dekl_matches = False
            # It is almost certainly a typo.
            # Try to fix it.
            levenshteins = []
            # Loop through all possible endings
            # For all that match see which stem is closest to the nominativ form.
            # Use Levenshtein to quantify this.
            for fk in matched_fks.copy():
                try:
                    m = fk.matches(self.forms[NOM].dekl, this_form.case, this_form.plural, this_form.dekl)
                except fk.PossibleMatch, pm:
                    levenshteins.append((pm.corrected_dekl, pm.lev, fk))
            # We only repair typos with levenshteins LEV_CUTOFF or better.
            # If two options have same levenshtein we do not make fix.
            min_lev = LEV_CUTOFF + 1
            best_dekl = None
            best_fk = None
            for dekl, lev, fk in levenshteins:
                if lev == min_lev:
                    if dekl != best_dekl:
                        best_dekl = None
                        best_fk = None
                elif lev < min_lev:
                    min_lev = lev
                    best_dekl = dekl
                    best_fk = fk
            if best_dekl:
                dekl_fixable = True
                correct_dekl = best_dekl
                matched_fks = set([best_fk])
            else:
                dekl_fixable = False
        else:
            for fk in matched_fks.copy():
                # Does the form end in one the allowed endings
                matching_ending = False
                try:
                    matches = fk.matches(self.forms[NOM].dekl, this_form.case, this_form.plural, this_form.dekl)
                except fk.PossibleMatch:
                    matches = None
                if matches:
                    dekl_matches = True
                else:
                    matched_fks.remove(fk)
            if dekl_matches is None:
                dekl_matches = False
        # We could only run this is matched_fks has changed, but we don't.
        matched_genders = self.narrow_genders(matched_genders, matched_fks)
        # Check we've got some genders and fks
        if ((article_matches or article_fixable) and
            (dekl_matches or dekl_fixable)):
            if not matched_genders or not matched_fks:
                raise StandardError('The are not possible genders or fks given')
        return FormMatch(article_matches=article_matches,
                         article_fixable=article_fixable,
                         correct_article=correct_article,
                         dekl_matches=dekl_matches,
                         dekl_fixable=dekl_fixable,
                         correct_dekl=correct_dekl,
                         matched_genders=matched_genders,
                         matched_fks=matched_fks)
            

class FormMatch(object):
    def __init__(self, article_matches=True, dekl_matches=True,
                 article_fixable=False, dekl_fixable = False,
                 correct_article=None, correct_dekl=None,
                 matched_genders=None, matched_fks=None,):
        self.article_matches = article_matches
        self.dekl_matches = dekl_matches
        self.article_fixable = article_fixable
        self.dekl_fixable = dekl_fixable
        self.correct_article = correct_article
        self.correct_dekl = correct_dekl
        self.matched_genders = matched_genders
        self.matched_fks = matched_fks
        


class SubstantivMultipleFormColl(object):
    """
    Corresponds to one row in the Substantiv-Tabelle, which could potentially
    hold several possible ways of declining the noun.
    """

    def __init__(self, raws, plural=None, poss_fks=fks, poss_genders=GENDERS):
        self.raws = raws
        self.plural = plural
        # Have fixes been made
        self.fixed = False
        self.poss_fks = poss_fks
        self.poss_genders = poss_genders

    def process(self):
        """
        Returns a list of SubstativSingleFormColl objects.  Each one representing
        a possible way of declining the noun.
        """
        # Process each case in the table (e.g. Nominativ, Akkustiv)
        # ``forms`` is a dictionary with an entry for each case.
        # Each entry contains a list of possible declinations.
        forms = {}
        for case in CASES:
            forms[case] = SubstantivMultipleForm(
                self.raws[case], case=case, plural=self.plural).process()
        self.form_colls = []
        # Check to see if all cases are blank
        all_blank = True
        for case in CASES:
            if forms[case]:
                all_blank = False
        if all_blank:
            return []
        # ``form_colls`` is a list of SubstantivSingleFormColl objects.
        # Each one of these objects represents a possible way of the declining
        # the noun.  Here they are generated, containing at first only the 
        # Nominativ form.
        for nom_form in forms[NOM]:
            self.form_colls.append(
                SubstantivSingleFormColl(
                    forms = {NOM:nom_form,}, plural=self.plural,
                    poss_fks=self.poss_fks, poss_genders=self.poss_genders))
        # We now loop through the other cases.  Each case can contain
        # several forms and we attempt to assign the forms to the
        # correct SubstativSingleFormColl object.
        other_cases = CASES - set([NOM])
        for case in other_cases:
            if not forms[case]:
                raise CannotAssignDeclinations
        for case in other_cases:
            # Can match information for all form_coll, form pairs
            fms= {}
            for form_coll in self.form_colls:
                fms[form_coll] = {}
                for form in forms[case]:
                    fm = form_coll.form_matches(form)
                    fms[form_coll][form] = fm
            # Make match matrix
            matches = {}
            for form_coll in self.form_colls:
                matches[form_coll] = {}
                for form in forms[case]:
                    fm = fms[form_coll][form]
                    matches[form_coll][form] = fm.article_matches and fm.dekl_matches
            # Now try to pair form_colls with forms
            try:
                matching_pairs = MatchMatrix(matches).get_pairs()
            except CannotPair, e:
                # If there was only one pair that didn't match then it may well be a typo.
                if len(e.A) == 1 and len(e.B) == 1:
                    form_coll = e.A.pop()
                    form = e.B.pop()
                    fm = fms[form_coll][form]
                    if ((fm.article_matches or fm.article_fixable) and
                        (fm.dekl_matches or fm.dekl_fixable)):
                        if fm.article_fixable:
                            form.article = fm.correct_article
                            self.fixed = True
                        if fm.dekl_fixable:
                            form.dekl = fm.correct_dekl
                            self.fixed = True
                        matching_pairs = e.pairs
                        matching_pairs.add((form_coll, form))
                    else:
                        raise CannotAssignDeclinations
                else:
                    raise CannotAssignDeclinations
            matched_form_colls = set([])
            new_pairs = []
            # If there are any repeats of the collection that means we need to create
            # a new collection.
            for form_coll, form in matching_pairs:
                fm = fms[form_coll][form]
                if not ((fm.article_matches or fm.article_fixable) and
                    (fm.dekl_matches or fm.dekl_fixable)):
                    print fm.article_matches
                    print fm.article_fixable
                    print fm.dekl_matches
                    print fm.dekl_fixable
                    print matches[form_coll][form]
                    raise StandardError
                old_form_coll = form_coll
                if form_coll in matched_form_colls:
                    form_coll = form_coll.copy()
                    self.form_colls.append(form_coll)
                matched_form_colls.add(form_coll)
                new_pairs.append((form_coll, form, old_form_coll))
            # Assign forms to collections
            for form_coll, form, old_form_coll in new_pairs:
                genders = fms[old_form_coll][form].matched_genders
                fks = fms[old_form_coll][form].matched_fks
                form_coll.add_form(form, genders, fks)
        return self.form_colls

            
class SubstantivTabelleSection(LeafSection):
                 
    regex = u"\s*\|(?P<before>.*)"
    regex += u"Wer oder was\? \(Einzahl\)=(?P<Nom_S>.*)"
    regex += u"\|Wer oder was\? \(Mehrzahl\)=(?P<Nom_P>.*)"
    regex += u"\|Wessen\? \(Einzahl\)=(?P<Gen_S>.*)"
    regex += u"\|Wessen\? \(Mehrzahl\)=(?P<Gen_P>.*)"
    regex += u"\|Wem\? \(Einzahl\)=(?P<Dat_S>.*)"
    regex += u"\|Wem\? \(Mehrzahl\)=(?P<Dat_P>.*)"
    regex += u"\|Wen\? \(Einzahl\)=(?P<Akk_S>.*)"
    regex += u"\|Wen\? \(Mehrzahl\)=(?P<Akk_P>.*?)"
    regex += u"}}(?P<after>.*)"
    pattern = re.compile(regex, re.UNICODE|re.DOTALL)

    base_fixed_text = u"\n{{{{Substantiv-Tabelle|{before}"
    base_fixed_text += u"Wer oder was? (Einzahl)={Nom_S}\n"
    base_fixed_text += u"|Wer oder was? (Mehrzahl)={Nom_P}\n"
    base_fixed_text += u"|Wessen? (Einzahl)={Gen_S}\n"
    base_fixed_text += u"|Wessen? (Mehrzahl)={Gen_P}\n"
    base_fixed_text += u"|Wem? (Einzahl)={Dat_S}\n"
    base_fixed_text += u"|Wem? (Mehrzahl)={Dat_P}\n"
    base_fixed_text += u"|Wen? (Einzahl)={Akk_S}\n"
    base_fixed_text += u"|Wen? (Mehrzahl)={Akk_P}\n"
    base_fixed_text += u"}}}}{after}"

    def render_dict(self, form_colls):
        """
        Creates a dictionary with an entry for each cell in the Substantiv-Tabelle.
        """
        if not self.parsed:
            raise NotParsedYet()
        rd = {}
        for form_coll in form_colls:
            for form in form_coll.forms.values():
                key = cps(form.case, form.plural)
                if key not in rd:
                    rd[key] = []
                rd[key].append(form.render())
        for key, li in rd.items():
            uniques = []
            for element in li:
                if element not in uniques:
                    uniques.append(element)
            txt = '<br/>'.join(uniques)
            rd[key] = txt
        # Make sure no cells are missing
        for case in CASES:
            for plural in (False, True):
                key = cps(case, plural)
                if not key in rd:
                    rd[key] = '-'
        return rd
    
    def fix_text(self):
        colls = []
        if self.smfc:
            colls += self.smfc.form_colls
        if self.pmfc:
            colls += self.pmfc.form_colls
        rd = self.render_dict(colls)
        rd['before'] = self.data['before']
        rd['after'] = self.data['after']
        try:
            fixed_text = self.base_fixed_text.format(**rd)
        except KeyError:
            import pdb
            pdb.set_trace()
        return fixed_text

    def parse(self):
        super(SubstantivTabelleSection, self).parse()
        word = self.get_property('word')
        if not word or not word.genders:
            return self
        page_title = self.get_property('page').title
        page_title = 'blah'
        self.fixed_text = None
        match = self.pattern.match(self.text)
        if not match:
            message = u'%s: Substantiv-Tabelle in unreadable format.' % page_title
            alert = UnreadableAlert(message=message, title=page_title)
            self.alerts.append(alert)
            return FillerSection(text=self.text, parent=self.parent)
        data = match.groupdict()
        self.s_data = {}
        self.p_data = {}
        for case in CASES:
            self.s_data[case] = data[cps(case, False)]
            self.p_data[case] = data[cps(case, True)]
        all_assigned = True
        poss_fks = fks
        poss_genders = GENDERS
        smfc = SubstantivMultipleFormColl(self.s_data, plural=False)
        try:
            smfc.process()
            # This is to make plural match singular
            # But we don't check that every gender and flexionklasse present in
            # singular is present in plural.  They just can't be something
            # completely different.
            # I should really lump singular and plural together into one MultipleFormColl
            if smfc.form_colls:
                poss_fks = set([])
                poss_genders = set([])
                for form_coll in smfc.form_colls:
                    poss_fks = poss_fks | form_coll.poss_fks
                    poss_genders = poss_genders | form_coll.poss_genders
        except SubstantivTabelleException, e:
            smfc = None
        try:
            pmfc = SubstantivMultipleFormColl(
                self.p_data, plural=True,
                poss_fks=poss_fks, poss_genders=poss_genders)
            pmfc.process()
        except SubstantivTabelleException, e:
            pmfc = None
        self.data = data
        self.smfc = smfc
        self.pmfc = pmfc
        if (self.smfc and self.smfc.form_colls) or (self.pmfc and self.pmfc.form_colls):
            self.fixed_text = self.fix_text()
        word.s_colls = getattr(smfc, 'form_colls', None)
        word.p_colls = getattr(pmfc, 'form_colls', None)
        if ((getattr(self.smfc, 'fixed', False) or getattr(self.pmfc, 'fixed', False)) and
            not word.is_name):
            message = u'%s: Substantiv Tabelle has been fixed.\n' % (page_title, )
            message += self.text
            message += '-----------------\n'
            message += self.fixed_text
            alert = FixableSubstantivTabelleAlert(section=self, fixed_text=self.fixed_text,
                                                  message=message, title=page_title)
            self.alerts.append(alert)
        # Doesn't always need to be an alert here.
        # It should just make a note if it is a singular only or plural only noun.
        if smfc is None or pmfc is None:
            if isinstance(e, CannotAssignDeclinations):
                message = u'Substantiv-Tabelle is ambiguous.'
                message += self.text
                alert = SubstantivTabelleAlert(message=message, title=page_title)
                self.alerts.append(alert)
            else:
                raise e
        return self

