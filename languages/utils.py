from .de.page import dePage

page_classes = {}
page_classes['de'] = dePage

def get_page_class(language_key):
    return page_classes[language_key]
    
