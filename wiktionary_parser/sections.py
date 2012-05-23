# -*- coding: utf-8 -*-
"""
Info for parsing german wiktionary pages.

Testing Level2Block chopping first:

>>> import StringIO
>>> from wiktionary_parser.wiktionary_utils.text_splitter import Chopper

>>> file_obj = StringIO.StringIO()
>>> file_obj.write(\"""== Test ==.  Here is a quick test == to make sure == that
... the splitting into sections is working as == one might
... expect ==.  The '==' are ignored unless the first one occurs at the beginning
... == of a new line. == Although they are still
... == not allowed to wrap around onto the next
... one ==.  Importantly
... === minor headings ===
... should not trigger splitting while
... == major ones ==
... should.\""")
>>> file_obj.seek(0)
>>> file_splitter = Chopper(file_obj, [Level2Block, ], include_tags=True)
>>> for block in file_splitter:
...     print '----------'
...     print block
----------
== Test ==.  Here is a quick test == to make sure == that
the splitting into sections is working as == one might
expect ==.  The '==' are ignored unless the first one occurs at the beginning
<BLANKLINE>
----------
== of a new line. == Although they are still
== not allowed to wrap around onto the next
one ==.  Importantly
=== minor headings ===
should not trigger splitting while
<BLANKLINE>
----------
== major ones ==
should.
"""

import re
from StringIO import StringIO
import copy

from wiktionary_parser.wiktionary_utils.text_splitter import Block, Splitter, Chopper
from wiktionary_parser.exceptions import InconsistentEntry
from wiktionary_parser.alerts import PatchRemainderAlert, NoFTMatchAlert, FixableAlert
from .exceptions import FixingError, NotParsedYet

class Level2Block(Block):
    start_pattern = '^(?P<true_tag>==.*?[^=]==)(?P<post_tag>[^=])'
    slug = 'level2'

class Level3Block(Block):
    start_pattern = '^(?P<true_tag>===.*[^=]===)(?P<post_tag>[^=])'
    slug = 'level3'

class Section(object):

    def __init__(self, text, parent=None):
        self.property_dict = {}
        self.parent = None
        self.parsed = False
        self.old_text = None
        self.text = text
        self.parent = parent
        self.children = []
        self.alerts = []
        self.all_alerts = None

    def get_all_alerts(self):
        if self.all_alerts is not None:
            return self.all_alerts
        if not self.parsed:
            raise StandardError('Has not been parsed yet.')
        alerts = {}
        for alert in self.alerts:
            klass = alert.__class__
            if klass not in alerts:
                alerts[klass] = []
            alerts[klass].append(alert)
        for child in self.children:
            for klass, child_alerts in child.get_all_alerts().items():
                if klass not in alerts:
                    alerts[klass] = []
                for alert in child_alerts:
                    alerts[klass].append(alert)
        self.all_alerts = alerts
        return alerts
    
    def get_fixable_alerts(self):
        all_alerts = self.get_all_alerts()
        fixable_alerts = []
        for alert_type, alerts in all_alerts.items():
            if alert_type.fixable:
                fixable_alerts = fixable_alerts + alerts
        return fixable_alerts

    def get_alerts(self, klass=None):
        if self.all_alerts is None:
            self.get_all_alerts()
        if klass is not None:
            if klass not in self.all_alerts:
                return []
            else:
                return self.all_alerts[klass]
        else:
            all_alerts = []
            for alerts in self.all_alerts.values():
                for alert in alerts:
                    all_alerts.append(alert)
            return all_alerts

    def render(self, old=False, show_sections=False):
        """
        If ``old`` is True then the wikitext before any fixes is returned.
        """
        if not self.children:
            if old:
                rendering = self.old_text
            else:
                rendering = self.text
        else:
            rendering = ''
            for child in self.children:
                rendering += child.render(old=old, show_sections=show_sections)
        if show_sections:
            prefix = '**<%s>**' % unicode(self)
            suffix = '**</%s>**' % unicode(self)
            return prefix + rendering + suffix
        else:
            return rendering
            
    def get_property(self, property_name):
        if property_name in self.property_dict:
            return self.property_dict[property_name]
        if self.parent is None:
            raise AttributeError
        return self.parent.get_property(property_name)

    def set_property(self, property_name, value):
        if property_name in self.property_dict:
            old_value = self.property_dict[property_name]
            if old_value is not None and old_value != value:
                raise InconsistentEntry(old_value, value)
            self.property_dict[property_name] = value
        else:
            raise AttributeError

    def check_property(self, property_name, value):
        old_value = self.get_property(property_name)
        if old_value != value:
            raise InconsistentEntry(old_value, value)

    def force_property(self, property_name, value):
        try:
            self.check_property(property_name, value)
        except InconsistentEntry:
            self.property_dict[property_name] = value

    def fixable(self):
        if self.children:
            for child in self.children:
                if child.fixable():
                    return True
            return False
        else:
            if get_fixable_alerts():
                return True
            else:
                return False

    def fix(self):
        raise NotImplemented()
        
    def parse(self):
        self.parsed = True
        return self

class ChildrenSection(Section):
    
    def fix(self):
        """
        Shouldn't be used very often.  Normally fixing will
        be done directly on the sections to be fixed.  They
        are brought to attention through alerts.
        """
        fixes = set([])
        for child in self.children:
            child_fixes = child.fix()
            fixes = fixes|child_fixes
        return fixes


class LeafSection(Section):
    
    def fix(self):
        fixables = self.get_fixable_alerts()
        fixes = set([])
        if fixables:
            if self.old_text:
                raise FixingError(
                    'A fix has already been performed on this section')
            new_text = fixables[0].fixed_text
            fixes.add(type(fixables[0]))
            self.old_text = self.text
            self.text = new_text
        return fixes        


class FTSection(LeafSection):

    def __init__(self, *args, **kwargs):
        super(FTSection, self).__init__(*args, **kwargs)
        self.formating_type = None

    def parse(self):
        super(FTSection,self).parse()
        for ft in self.fts:
            ftdict = ft.read(self)
            if ftdict is not None:
                self.formating_type = ft
                self.ftdict = ftdict
                data = self.ftdict['data']
                if data is not None:
                    self.process_data(data)
                if 'fixed_text' in self.ftdict:
                    page_title = self.get_property('page').title
                    message = '%s: FIXABLE: %s' % (page_title, ft.description)
                    if ft.alert_class is not None:
                        alert = ft.alert_class(
                            message=message, title=page_title, section=self,
                            fixed_text=self.ftdict['fixed_text'])
                        self.alerts.append(alert)
                return self
        # No match to a formating type.
        page_title = self.get_property('page').title
        message = '%s: Section="%s": No formating types matched.' % \
            (page_title, self.__class__.__name__)
        alert = NoFTMatchAlert(
            message=message, text=self.text,
            title=page_title, section_class=self.__class__)
        self.alerts.append(alert)
        return self

    def readable(self):
        if not self.parsed:
            raise NotParsedYet()
        return (hasattr(self, 'ftdict') and 'data' in self.ftdict)
    

class FillerSection(LeafSection):
    """
    A section for a region of text that cannot be parsed.
    Used simply to store the text.
    """
    
    def __init__(self, correct=False, **kwargs):
        super(FillerSection, self).__init__(**kwargs)
        self.parsed = True
        self.correct = correct


class PatchedSection(LeafSection):

    patches = []
    end_regex = u"""^[\s,'"\[\]\-/();]*$"""
    end_pattern = re.compile(end_regex, re.UNICODE)
    
    def parse(self):
        super(PatchedSection, self).parse()
        self.patched_text = self.text
        for patch in self.patches:
            no_matches = False
            while not no_matches:
                new_text = patch.extract(self)
                if new_text is not None:
                    self.patched_text = new_text
                else:
                    no_matches = True
        if not self.end_pattern.match(self.patched_text):
            page_title = self.get_property('page').title
            message = '%s: Text without patches = %s, Full text = %s' % (page_title, self.patched_text, self.text) 
            alert = PatchRemainderAlert(
                message=message, patched_text=self.patched_text,
                text=self.text, title=page_title)
            self.alerts.append(alert)
        return self

    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
