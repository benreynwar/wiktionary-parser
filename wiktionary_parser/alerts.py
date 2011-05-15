class Alert(object):
    """
    If the parser notices something that doesn't count as
    an error, but it thinks should be brought to attention
    then it creates and alert and adds it to the pages
    alerts.
    """
    description = 'Generic Alert'
    fixable = False

    def __init__(self, message, title):
        self.message = message
        self.title = title


class PatchRemainderAlert(Alert):
    description = 'All patches have been removed from the text, but there is still meaningful text remaining.'
    def __init__(self, patched_text, text, *args, **kwargs):
        super(PatchRemainderAlert, self).__init__(*args, **kwargs)
        self.patched_text = patched_text
        self.text = text


class NoFTMatchAlert(Alert):
    description = 'No formating types matched to this section.'
    def __init__(self, section_class, text, *args, **kwargs):
        super(NoFTMatchAlert, self).__init__(*args, **kwargs)
        self.section_class = section_class
        self.text = text


class FixableAlert(Alert):
    slug = None
    description = 'The section can be repaired by the parser.'
    fixable = True
    def __init__(self, section, fixed_text, *args, **kwargs):
        super(FixableAlert, self).__init__(*args, **kwargs)
        self.section = section
        self.fixed_text = fixed_text


class AutoFixableAlert(FixableAlert):
    description = "This section can be repaired by the parser.  We're are very confident that it is correct so that the parser can change it without approval."


class WordTitleMismatchAlert(Alert):
    description = 'The word in the Heading Level 2 does not match the page title.'
    def __init__(self, language, word, *args, **kwargs):
        super(WordTitleMismatchAlert, self).__init__(*args, **kwargs)
        self.language = language
        self.word = word


class LanguageMismatchAlert(Alert):
    description = 'The language in heading 1 does not match the language in heading 2.'
    def __init__(self, language1, language2, *args, **kwargs):
        super(LanguageMismatchAlert, self).__init__(*args, **kwargs)
        self.language1 = language1
        self.language2 = language2


class MismatchAlert(Alert):
    description = 'Generic mismatch between two entries which should be identical.'
    def __init__(self, entry1, entry2, *args, **kwargs):
        super(LanguageMismatchAlert, self).__init__(*args, **kwargs)
        self.entry1 = entry1
        self.entry2 = entry2

    
class MissingContentAlert(Alert):
    description = 'Required content is missing from the entry.'

class NoTemplateMatchAlert(Alert):
    description = "A template was found but the name of the template is not known."
