from wiktionary_parser.word import Word

class deWord(Word):
    
    def __init__(self, *args, **kwargs):
        super(deWord, self).__init__(*args, **kwargs)

class deSubstantiv(deWord):

    typeslug = 'Substantiv'

    def __init__(self, *args, **kwargs):
        super(deSubstantiv, self).__init__(*args, **kwargs)
        self._forms = {}
        self._gender = None
        self.multi_genders = False
        self.is_name = False

    form_keys = set([u'Nom_S', u'Nom_P', u'Akk_S', u'Akk_P', u'Dat_S', u'Dat_P',
                 u'Gen_S', u'Gen_P'])
    def _set_forms(self, forms):
        keys = set([])
        for k, v in forms.items():
            keys.add(k)
        if keys != self.form_keys:
            raise StandardError('forms not formed correctly')
        # Should put a check in to make sure values are OK.
        self._forms = forms
    def _get_forms(self):
        return self._forms
    forms = property(_get_forms, _set_forms)

    genders = set(['m', 'f', 'n'])
    def _set_gender(self, gender):
        if gender in self.genders:
            if self._gender is not None:
                self.multi_genders = True
            self._gender = gender
        else:
            raise StandardError('Gender not formed correctly.')
    def _get_gender(self):
        return self._gender
    gender = property(_get_gender, _set_gender)
    

