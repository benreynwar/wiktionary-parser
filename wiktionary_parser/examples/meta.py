"""
Testing creation of pages.
"""

import logging
from itertools import islice

from wiktionary_parser.xml_parser import XMLPageParser
from wiktionary_parser.db import Session, Base, engine
from wiktionary_parser.languages.en.page import enPage
from wiktionary_parser.page import Page
from wiktionary_parser.meta.user import User
from wiktionary_parser.meta.comment import Comment
from wiktionary_parser.config import setup_logging

def load_xml():
    session = Session()
    Base.metadata.create_all(engine)
    xml_file = open('../../wiktionary_data/enwiktionary-20120220-pages-meta-current.xml')
    xml_parser = XMLPageParser(xml_file, enPage)
    total_lines = 0
    counter = 0
    for page in xml_parser:
        ev = session.query(Page).filter(Page.language==page.language, Page.title==page.title)
        if ev.count() == 0:
            session.add(page)
        if counter % 1000 == 0:
            print(counter)
            session.commit()
            print('committed')
        counter += 1
    session.commit()

def setup():
    Base.metadata.create_all(engine)    

def create_users():
    session = Session()
    pgs = session.query(Page).filter(Page.title.like('User:%'))
    counter = 0
    for page in pgs:
        if '/' in page.title:
            continue
        user = User.make_user_from_page(page, session)
        session.add(user)
        counter += 1
        if counter % 1000 == 0:
            print(counter)
            session.commit()
    session.commit()

def create_language_proficiencies():
    session = Session()
    users = session.query(User).all()
    counter = 0
    for user in users:
        user.set_proficiencies()
        if counter % 200 == 0:
            print(counter)
            session.commit()
        counter += 1
    session.commit()

def create_comments():
    session = Session()
    pages = session.query(Page).filter(Page.title.like('Talk:%'))
    counter = 0
    for page in pages:
        Comment.from_page(page, session)
        if counter % 200 == 0:
            print(counter)
            session.commit()
        counter += 1
    session.commit()

if __name__ == '__main__':
    setup_logging(logging.INFO)
    setup()
    #create_language_proficiencies()
    #create_users()
    create_comments()
    #load_xml()
