class SilbentrennungSection(FTSection):

    def process_data(self, data):
        pass
    extra = u"(?:(?:''[^']*'')|(?:\([^()]\)))?"

    wp = u"%s\s*(?:(?:'*[\w·\s,-]+'*!?,?)|(?:{{fehlend}}))\s*%s\s*" % (extra, extra)

    #wp = u'(?:(?:[\w·\s,-]+)|(?:{{fehlend}}))/s*'
    
    fts = []
    base = u'^\n{{Silbentrennung}}\s*:?(?P<singular>%s)(?:&nbsp)?;?\s*' % wp
    end = u'\s*(?P<comment><!--.*-->)?\s*$'
    # kein Singular
    kein_singular_forms = [u'{{kSg\.}}', ]
    kein_singular_regex = u'(?P<kein_singular_form>%s)' % u'|'.join(
        [u'(?:%s)' % form for form in kein_singular_forms])
    kein_singular_base = base.replace(u'(?P<singular>%s)' % wp, u'%s,?' %
                                      kein_singular_regex)
    # Plural
    plural_forms = [u'{{Pl\.}}:?', u"''pl\.:?''", u"''Plural:?'':?",
                    u"''Pl\.:?''", u'Pl\.:?'] 
    plural_regex = u'(?P<plural_form>%s:?)' % u'|'.join(
        [u'(?:%s)' % form for form in plural_forms])
    # kein Plural
    kein_plural_forms = [u'{{kPl\.}}', u"''kein Plural''",
                         u"{{Pl.}} ''kein Plural''",
                         u"{{Pl\.}} kein [[Plural]]",]
    kein_plural_regex = u'(?P<kein_plural_form>%s)' % u'|'.join(
        [u'(?:%s)' % form for form in kein_plural_forms])
    # keine Steigerung
    keine_steigerung_forms = [u'{{kSt\.}}', u"''keine Steigerung''"]
    keine_steigerung_regex = u'(?P<keine_steigerung_form>%s)' % u'|'.join(
        [u'(?:%s)' % form for form in keine_steigerung_forms])
    # blank
    blank_forms = [u'/s*', u'/s*-/s*', u'/s*,/s*{{Pl\.}}\s*']
    blank_regex = u'(?P<blank_form>%s)' % u'|'.join(
        [u'(?:%s)' % form for form in blank_forms])
    
    fts.append(RegexFT(
            description=u"Normal.",
            slug=u'normal',
            regex=base + u'%s\s*%s' % (plural_regex, wp) + end,
            correct=True,))

    fts.append(RegexFT(
            description=u"Zwei Pluralformen.",
            slug=u'zwei_Pluralen',
            regex=base+u'{{Pl\.1}}\s*%s\s*{{Pl\.2}}\s*%s' % (wp, wp) + end,
            correct=True,))

    fts.append(RegexFT(
            description=u"Plural fehlend und kein {{kPl.}} da.",
            slug=u'plural_fehlend',
            regex=base+end,
            correct=True,))

    fts.append(RegexFT(
            description=u"Kein Plural.",
            slug=u'kein_Plural',
            regex=base+u'%s' % (kein_plural_regex,) + end,
            correct=True,))

    fts.append(RegexFT(
            description=u"Kein Singular.",
            slug=u'kein_Singular',
            regex=kein_singular_base + u'%s\s*%s' % (plural_regex, wp) + end,
            correct=True,))

    fts.append(RegexFT(
            description="Verb",
            slug=u'Verb',
            regex=base+u'{{Prät\.}}\s*%s\s*{{Part\.}}\s*%s' % (wp, wp) + end,
            correct=True,))

    fts.append(RegexFT(
            description="Adjectiv",
            slug=u'Adjectiv',
            regex=base+u'{{Komp\.}}\s*%s\s*{{Sup\.}}\s*%s' % (wp, wp) + end,
            correct=True,))

    fts.append(RegexFT(
            description=u"Keine Steigerung.",
            slug=u'keine_Steigerung',
            regex=base + u'%s\s*%s' % (keine_steigerung_regex, wp) + end,
            correct=True,))    
    
    fts.append(RegexFT(
            description="Keine_Superlative",
            slug=u'keine_Superlative',
            regex=base+u'{{Komp\.}}\s*%s\s*' % (wp, ) + end,
            correct=True,))

    fts.append(RegexFT(
            description="Blank",
            slug=u'blank',
            regex=base + blank_regex + end,
            correct=True,))

    fts.append(RegexFT(
            description="Genetiv",
            slug=u'genetiv',
            regex=base + '{{Gen\.}}\s*%s\s*' % (wp, ) + end,
            correct=True,))

    fts.append(RegexFT(
            description="Rechtschreibung",
            slug = u'Rechtschreibung',
            regex = u"^\n{{Silbentrennung}}\n:''[Nn]eue Rechtschreibung:''.*\n:''[Aa]lte Rechtschreibung:''.*$",
            correct=True,))

    

