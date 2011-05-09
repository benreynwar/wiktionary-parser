# -*- coding: utf-8 -*-
"""
Test whether removal of HTML tags is working
>>> text="Hello there <small> person </small> with an <unknown> tag</unknown>"
>>> print wikitext_to_plaintext(text)
Hello there  person  with an  tag

Test whether removal of wiki links is working
>>> text="I'm a [[wikilink]] who [[is fab|smells bad]]"
>>> print wikitext_to_plaintext(text)
I&#39;m a wikilink who smells bad

Test whether adding of emphasis is working
>>> text="This is ''a very exciting [[fish|book]]'' isn't it."
>>> print wikitext_to_plaintext(text)
This is <em>a very exciting book</em> isn&#39;t it.

Test whether it is escaping html.
>>> text = "Will this let me [[do some <script>nasty stuff</script>]] or not."
>>> print wikitext_to_plaintext(text)
Will this let me do some &lt;script&gt;nasty stuff&lt;/script&gt; or not.
"""
import StringIO

#from django.utils.html import escape

from wiktionary_parser.wiktionary_utils.text_splitter import Block, Splitter, FillerBlock as OldFillerBlock
from wiktionary_parser.alerts import NoTemplateMatchAlert

class SquareBracketBlock(Block):
    start_pattern = '\[\['
    stop_pattern = '\]\]'
    slug = 'square_bracket_block'
    
    def to_text(self):
        bits = self.text.split('|')
        if len(bits) == 1:
            return bits[0]
        elif len(bits) == 2:
            return bits[1]
        else:
            raise StandardError("to many |'s")


class HtmlBlock(Block):
    start_pattern = '<'
    stop_pattern = '>'
    slug = 'html_block'

    def to_text(self):
        return ''

templates = {'Literaturliste': lambda p: '',
             'ugs.': lambda p: "''umgangssprachlich%s''" % p[1],
             'kPl.': lambda p: "''kein Plural%s''" % p[1],
             'n': lambda p: 'n',
             'Audio': lambda p: '',
             }

class TemplateBlock(Block):
    """
    Processes named templates.
    Returns a tuple of (processed text, raised alerts).
    """
    start_pattern = '{{'
    stop_pattern = '}}'
    slug = 'template_block'

    def __init__(self, *args, **kwargs):
        super(TemplateBlock, self).__init__(*args, **kwargs)
        self.alerts = []

    def to_text(self):
        params = self.text.split('|')
        if len(params) < 2:
            params.append('')
        template_name = params[0]
        if template_name not in templates:
            message = 'The template name %s is not known.' % template_name
            alert = NoTemplateMatchAlert(
                message=message, title=None)
            self.alerts.append(alert)
            return '{{%s}}' % self.text
        else:
            return templates[template_name](params)

class QuoteBlock(Block):
    # Patterns are actually "''" but represented in escaped form.
    start_pattern = "&#39;&#39;"
    stop_pattern = "&#39;&#39;"
    slug = "quote_block"

    def to_text(self):
        return '<em>%s</em>' % self.text


class FillerBlock(OldFillerBlock):
    
    def to_text(self):
        return self.text

def str_to_file_obj(text):
    file_obj = StringIO.StringIO()
    file_obj.write(text)
    file_obj.seek(0)
    return file_obj

def apply_blocks(text, blocks):
    file_obj = str_to_file_obj(text)
    splitter = Splitter(file_obj, blocks, filler_blocks=True, filler_block_class=FillerBlock)
    new_text = []
    alerts = []
    for block in splitter:
        new_text.append(block.to_text())
        if hasattr(block, 'alerts'):
            alerts += block.alerts
    return (''.join(new_text), alerts)

def wikitext_to_plaintext(wikitext):
    text, alerts = apply_blocks(wikitext, [SquareBracketBlock, HtmlBlock, TemplateBlock])
    # Needs some HTML escaping
    #text = escape(text)
    text, more_alerts = apply_blocks(text, [QuoteBlock])
    alerts += more_alerts
    return (text, alerts)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

