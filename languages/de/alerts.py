from wiktionary_parser.alerts import Alert, FixableAlert

class SubstantivTabelleAlert(Alert):
    description = 'Substantiv Tabelle seems incorrect'

class FixableSubstantivTabelleAlert(FixableAlert):
    description = 'Substantiv Tabelle seems incorrect'

class UnreadableAlert(Alert):
    description = 'Substantiv Tabelle was not readable.'
