"""
For parsing a user page.
"""

import re

from sqlalchemy import Column, Integer, String, Text, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from wiktionary_parser.db import Base, Session
from wiktionary_parser.page import Page

class User(Base):

    __tablename__ = 'user'

    username = Column(String, primary_key=True)
    language = Column(String, primary_key=True)
    page_title = Column(String)

    language_proficiencies = relationship('LanguageProficiency', backref='user')

    all_users = {}
    def __init__(self, username, language):
        self.username = username
        self.language = language
        self.page_title = u'User:{0}'.format(username)

    @property
    def page(self):
        session = Session.object_session(self)
        page = session.query(Page).get((self.page_title, self.language))
        return page
    
    @classmethod
    def get_user(cls, username, language, session):
        user = session.query(User).get((username, language))
        if user:
            return user
        else:
            return None

    @classmethod
    def make_user_from_page(cls, page, session):
        if not page.title.startswith('User:') or '/' in page.title:
            raise ValueError(u'`page` is not a user page.  Title is {0}'.format(page.title))
        username = page.title[len('User:'):]
        return make_user(username, page.language, session)

    @classmethod
    def make_user(cls, username, language, session):
        user = cls.get_user(username, language, session)
        if user is None:
            user = User(username, language)
            session.add(user)
        return user

    def set_proficiencies(self):
        session = Session.object_session(self)
        pattern = re.compile('\{\{Babel(\-13)?\|(?P<content>[a-zA-Z\-0-9\\|]+)}\}')
        if not self.page.text:
            matches = []
        else:
            matches = re.findall(pattern, self.page.text)
        bits = []
        for match in matches:
            content = match[1]
            bits += content.split('|')
        old_lps = self.language_proficiencies
        continuing_lps = []
        new_lps = []
        for bit in bits:
            if not bit:
                continue
            # Work out the language and proficiency.
            if bit[-1] in '0123456789':
                proficiency = int(bit[-1])
                language = bit[:-2]
            else:
                proficiency = LanguageProficiency.NATIVE
                language = bit
            old_match = None
            # Check whether there already exists a record for this.
            for lp in old_lps:
                if lp.language == language and lp.proficiency == proficiency:
                    old_match = lp
                    break
            # Make a not if it exists.
            if old_match:
                continuing_lps.append(old_match)
            # And add it if it doesn't
            else:
                new_lps.append(LanguageProficiency(self, language, proficiency))
        deleted_lps = list(set(old_lps) - set(continuing_lps))
        for lp in deleted_lps:
            import pdb
            pdb.set_trace()
            session.delete(lp)
        for lp in new_lps:
            session.add(lp)
        

class LanguageProficiency(Base):

    __tablename__ = 'language_proficiency'

    # Use this integer to represent native ability.
    NATIVE = 9
    
    id = Column(Integer, primary_key=True)
    user_username = Column(String)
    user_language = Column(String)
    language = Column(String)
    proficiency = Column(Integer)
    __table_args__ = (
        ForeignKeyConstraint(['user_username', 'user_language'],
                             ['user.username', 'user.language']),
        )

    def __init__(self, user, language, proficiency):
        self.user_username = user.username
        self.user_language = user.language
        self.language = language
        self.proficiency = proficiency
        
    def __repr__(self):
        return '<LanguageProficiency({0.user_username}, {0.user_language}, {0.language}, {0.proficiency})>'.format(self)
