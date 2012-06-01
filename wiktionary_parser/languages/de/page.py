from wiktionary_parser.page import Page
from wiktionary_parser.sections import Level2Block, Section, FillerSection
from wiktionary_parser.wiktionary_utils.text_splitter import Chopper, FillerBlock
from .sections import deLanguageSection

class dePage(Page):

    def __init__(self, *args, **kwargs):
        self.language = 'de'
        super(dePage, self).__init__(*args, **kwargs)

    def title_OK(self):
        # Is it an info page
        if ':' in self.title:
            return False
        # Is it a conjugation page
        if '(Konjugation' in self.title:
            return False
        if '(Deklination' in self.title or '(deklination' in self.title or 'Deklination)' in self.title:
            return False
        # for some Czech words.  Probably should be one of the above.
        if '(Possessivadjektiv' in self.title:
            return False
        # Apparently it's a normal word.
        return True
    
    def parse(self, shallow=False):
        super(dePage, self).parse()
        if not self.title_OK():
            # No words on this page
            self.ignore = True
            return self
        for level2block in Chopper(self.text, [Level2Block,],
                                   filler_blocks=True, include_tags=True):
            # It's allowed to have some unknown text before the first
            # level2 block.
            if isinstance(level2block, FillerBlock):
                section = FillerSection(text=level2block.text, parent=self)
            else:
                section = deLanguageSection(text=level2block.text, parent=self)
            if not shallow:
                section = section.parse()
            self.children.append(section)
        return self
