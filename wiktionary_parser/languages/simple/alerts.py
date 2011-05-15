from wiktionary_parser.alerts import Alert, FixableAlert

class MissingTypeTemplate(Alert):
    description = 'The type template is missing.'

class EarlyExample(Alert):
    description = 'An example preceded any definition.'

class AdjectiveConjugationAlert(Alert):
    description = "A problem with the adjective conjugation."

class UnknownType(Alert):
    description = "The word type is unknown."

class WrongHeadingLevel(FixableAlert):
    description = "A heading is at the wrong level."

class Level2_not_Level3(WrongHeadingLevel):
    slug = "l2tol3"
    description = "A level 2 heading should be level 3."
