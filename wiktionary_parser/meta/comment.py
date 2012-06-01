"""
For parsing a discussion page and breaking it down into comments.
"""

import re, datetime, logging

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from wiktionary_parser.db import Base, Session
from wiktionary_parser.page import Page
from wiktionary_parser.meta.user import User

logger = logging.getLogger(__name__)

class Comment(Base):

    __tablename__ = 'comment'
    
    id = Column(Integer, primary_key=True)
    user_username = Column(String)
    page_title = Column(String)
    language = Column(String)
    date = Column(DateTime)
    text = Column(Text)
    n_words = Column(Integer)
    __table_args__ = (
        ForeignKeyConstraint(['user_username', 'language'],
                             ['user.username', 'user.language']),
        ForeignKeyConstraint(['page_title', 'language'],
                             ['page.title', 'page.language']),
        )
    
    def __init__(self, user, page, date, text):
        self.user_username = user.username
        self.page_title = page.title
        self.language = user.language
        if page.language != user.language:
            raise ValueError('Page language and User language must be the same')
        self.date = date
        self.text = text
        self.n_words = len(text.split())

    @property
    def page(self):
        session = Session.object_session(self)
        page = session.query(Page).get((self.page_title, self.language))
        return page

    @property
    def user(self):
        session = Session.object_session(self)
        user = session.query(User).get((self.user_username, self.language))
        return user

    @classmethod
    def from_page(cls, page, session):
        if not page.title.startswith('Talk:'):
            raise ValueError(u"Page {0} is not a talk page.".format(page.title))
        if not page.text:
            return []
        for bit in page.text.split('(UTC)')[:-1]:
            if not bit:
                continue
            #get username
            pattern = re.compile('(?P<before>.*)\[\[User:(?P<username>.+?)\|.+\]\](?P<after>.*)')
            special_pattern = re.compile('\[\[Special:Contributions.+|.+\]\]')
            match = re.search(pattern, bit)
            if not match:
                # If it's a non-registered user don't give a warning.
                special_match = re.search(special_pattern, bit)
                if not special_match:
                    logger.debug(u"Page {0}: Could not find user in '{1}'.".format(page.title, bit))
                continue
            gd = match.groupdict()
            username = gd['username']
            before = gd['before']
            after = gd['after']
            user = User.make_user(username, page.language, session)
            # Make sure the user get saved so it can be found.
            session.commit()
            datestr = ' '.join(after.split()[-4:])
            possible_date_formats = ('%H:%M, %d %b %Y',
                                     '%H:%M, %d %B %Y',
                                     '%d %b %Y %H:%M',
                                     '%d %B %Y %H:%M',
                                     '%H:%M %b %d, %Y',
                                     ') %Y-%m-%d %H:%M:%s.</small>'
                                     )
            date = None
            for df in possible_date_formats:
                try:
                    date = datetime.datetime.strptime(datestr, df)
                    break
                except ValueError:
                    pass
            if date is None:
                logger.debug(u"Could not parse date string '{0}'.".format(datestr))
            if date is not None:
                session.add(Comment(user, page, date, before))

    def __repr__(self):
        return '<Comment({0.user_username}, {0.page_title}, {0.language})>'.format(self)
