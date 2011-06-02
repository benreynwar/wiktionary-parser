from wiktionary_parser.utils import TemplateBlock

nofunc = lambda p: ''

simple_templates = {
    # Verbs
    'intransitive verb': nofunc,
    'intransitive': nofunc,
    'transitive verb': nofunc,
    'transitive': nofunc,
    'ti verb': nofunc, # transitive and intransitive
    'linking verb': nofunc,
    'past tense and participle of': nofunc,
    'past tense of': nofunc,
    'past participle of': nofunc,
    'present participle of': nofunc,
    'gerund-participle of': nofunc,
    'third person singular of': nofunc,
    'third-person singular of': nofunc,
    'usually plural': nofunc,
    # Nouns
    'ordinal number': nofunc,
    'plural': nofunc,
    'singular': nofunc,
    'pluralonly': nofunc,
    'countable': nofunc,
    'uncountable': nofunc,
    'cu noun': nofunc, # countable and uncountable
    'plural of': lambda p: 'plural of %s' % p[1],
    # Adjective
    'sentence adverb': nofunc,
    'comparative': nofunc,
    'comparative of': nofunc,
    'superlative of': nofunc,
    # random
    'other spelling of': nofunc,
    'geometry': nofunc,
    'geography': nofunc,
    'military': nofunc,
    'geology': nofunc,
    'grammar': nofunc,
    'grammar context': nofunc,
    'music': nofunc,
    'technical': nofunc,
    'medicine': nofunc,
    'zoology': nofunc,
    'computing': nofunc,
    'sport': nofunc,
    'sports': nofunc,
    'math': nofunc,
    'mathematics': nofunc,
    'chemistry': nofunc,
    'physics': nofunc,
    'biology': nofunc,
    'botany': nofunc,
    'weather': nofunc,
    'colorbox': nofunc, # Make a colored box to display color.
    'law': nofunc,
    # general purpose
    'a': lambda p: '(%s)' % p[1],
    'UK': nofunc,
    'US': nofunc,
    'rare': nofunc,
    'idiom': nofunc,
    'dialectal': nofunc,
    'colloquial': nofunc,
    'attrib': nofunc,
    'formal': nofunc,
    'vulgar': nofunc,
    'slang': nofunc,
    'context': nofunc,
    'old': nofunc,
    'see': nofunc,
    'wikiquote': nofunc,
    'antonyms': nofunc,
    'synonyms': nofunc,
    'informal': nofunc,
    
    }

class simpleTemplateBlock(TemplateBlock):
    templates = simple_templates


