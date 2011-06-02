"""
This module contains the Einsatz class which is used for scanning wiktionary
for defects and then correcting them with command-line user approval.
"""

import wikitools

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.languages.utils import get_page_class

from wiktionary_parser.bots.utils import wikidatetime, delta, user_choice, YES, NO, QUIT, SKIP
from wiktionary_parser.bots.memory import FixMemory
from wiktionary_parser.bots.log import LogPage
from wiktionary_parser.alerts import FixableAlert


class EndEinsatz(Exception):
    pass

class Change(object):
    def __init__(self, word, alert):
        self.word = word
        self.alert = alert

class Einsatz(object):
    """
    A bot run.

    Parses the wiktional xml dump and find fixable defects.
    Displays the fixable defects to a user for approval.
    Corrects defects.
    Produces a log.

    """

    def __init__(self, title, description, xml_file, page_class, site, username, live=True, online=True, memory_file_name=None):
        self.title = title
        self.live = live
        self.log_frequency = 20
        self.online = online
        if online:
            self.site = site
        self.description = description
        self.words = []
        self.xml_file = xml_file
        self.page_class = page_class
        self.memory = FixMemory(memory_file_name)
        self.username = username
        if self.online:
            self.wikilogpage = wikitools.Page(site, u'User:%s/Log' % self.username)
            self.log_page = LogPage(title=self.wikilogpage.title, text=self.wikilogpage.getWikiText()).parse()
            self.site.login(self.username)
        else:
            self.log_page = LogPage(title=u'Bot Log Page', text='').parse()
        self.log_section = None

    def requires_approval(self, page):
        fixable_alerts = page.get_fixable_alerts()
        if not fixable_alerts:
            return False
        # See what changes are suggested
        for alert in fixable_alerts:
            alert.section.fix()
        new_text = page.render()
        text_delta = delta(page.text, new_text, surrounding_lines=2)
        if not text_delta:
            return False
        # See if they've already been fixed/approved/disapproved
        if self.memory.in_memory(page.title, text_delta):
            return False
        print 'Provisional Fixable alert for page %s. Check online.' % page.title
        # Get current page from online if possible
        if self.online:
            old_text_delta = text_delta
            page = self.get_page(page.title)
            if page is None:
                return False
            page.parse()
            for alert in page.get_fixable_alerts():
                alert.section.fix()
            new_text = page.render()
            text_delta = delta(page.text, new_text, surrounding_lines=2)
            if not text_delta:
                self.memory.mark_fixed(page.title, old_text_delta)
                return False
            # See if they've already been fixed/approved/disapproved
            if self.memory.in_memory(page.title, text_delta):
                return False
        self.memory.mark_needs_approval(page.title, text_delta)
        return True

    def get_user_approval(self, title, text_delta):
        print 'Page %s' % title
        response = user_choice(text_delta)
        if response == QUIT:
            return False
        elif response == YES:
            self.memory.approve(title, text_delta)
            print title, 'will be fixed.'
        elif response == NO:
            self.memory.reject(title, text_delta)
            print title, 'wont be fixed.'
        elif response == SKIP:
            print title, 'wont be fixed this time.'
        else:
            raise StandardError('Unknown Response')
        return True

    def get_page(self, title):
        if self.online:
            wikipage = wikitools.Page(self.site, title)
            if wikipage.isRedir():
                return None
            try:
                text = wikipage.getWikiText()
                text = unicode(text, 'utf-8')
                return self.page_class(title=title, text=text)
            except (wikitools.NoPage):
                return None
        else:
            raise StandardError('Not online')

    def write_page(self, title, text, comment):
        if self.online and self.live:
            wikipage = wikitools.Page(self.site, title)
            text = text.encode('utf8')
            wikipage.edit(text=text, summary=comment)
            print(u'Changed Page %s.' % title)
        else:
            print(u'Would have changed page %s if live (%s)' % (title, comment))
                        
    def repair_page(self, page_title, allowed_delta):
        if not self.online:
            raise StandardError('Must be online to repair page.')
        page = self.get_page(page_title)
        if page is None:
            print u'Page no longer exists.'
            return set([])
        page.parse()
        comments = []
        changes = set([])
        for alert in page.get_fixable_alerts():
            alert.section.fix()
            comments.append(alert.slug)
            changes.add(Change(page.title, alert))
        new_text = page.render()
        text_delta = delta(page.text, new_text, surrounding_lines=2)
        if text_delta:
            if text_delta == allowed_delta:
                comment = u'[[User:%s/Log#%s|%s]], ' % (self.username, self.title, u', '.join(comments))
                self.write_page(page_title, new_text, comment)
                if self.live:
                    self.memory.mark_fixed(page.title, text_delta)
                return changes
            else:
                self.memory.remove(page.title, text_delta)
                print u'Page has changed since modification approved. Removing from memory.'
        return set([])

    def refresh_log(self):
        if self.online and self.live:
            self.log_page = LogPage(title=self.wikilogpage.title, text=self.wikilogpage.getWikiText()).parse()
        else:
            self.log_page = LogPage(title=self.log_page.title, text=self.log_page.render())
        self.log_page.parse()
        self.log_section = self.log_page.einsatz_sections[self.title]

    def log(self, changes, commit=False):
        if not self.log_section:
            self.log_section = self.log_page.add_einsatz_section(self)
        for change in changes:
            self.log_section.add_change(change)
        if commit:
            self.write_page(self.log_page.title, self.log_page.render(), 'updating log')
                
    def scan_xml(self, max_no=None):
        # Check title hasn't been used before
        if self.title in self.log_page.einsatz_sections:
            raise StandardError(u'title has been used before')
        # Parse xml dump
        xml_parser = XMLPageParser(self.xml_file, self.page_class)
        counter = 0
        all_counter = 0
        for page in xml_parser:
            all_counter += 1
            page.parse()
            if self.requires_approval(page):
                counter += 1
                print '%d: %d: Fixable alert for page %s' % (counter, all_counter, page.title)
                if max_no is not None and counter >= max_no:
                    break
            if all_counter % 1000 == 0:
                print all_counter
                self.memory.save()
        self.memory.save()
    
    def approval(self):
        # Get user approval for the various suggested changes
        for title, text_delta in self.memory.all_needing_approval():
            didnt_quit = self.get_user_approval(title, text_delta)
            if not didnt_quit:
                break
        self.memory.save()

    def run(self, max_no=None):
        # Make the approved changes.
        counter = 0
        for title, info in self.memory.items():
            delta = info[0]
            code = info[1]
            if code == self.memory.FIX:
                changes = self.repair_page(title, delta)
                if counter % self.log_frequency == 0:
                    commit = True
                else:
                    commit = False
                self.log(changes, commit=commit)
                counter += 1
                if max_no is not None and counter >= max_no:
                    break
        # Finalise log
        if self.log_section:
            self.log_section.finish()
            self.log(set([]), commit=True)
            print self.log_page.render()
        self.memory.save()
