from wiktionary_parser.alerts import Alert, FixableAlert

class MissingTypeTemplate(Alert):
    description = 'The type template is missing.'

class EarlyExample(Alert):
    description = 'An example preceded any definition.'

class AdjectiveConjugationAlert(Alert):
    description = "A problem with the adjective conjugation."
