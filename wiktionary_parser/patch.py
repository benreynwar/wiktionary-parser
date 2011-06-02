import re

class Patch(object):

    def __init__(self, regex, slug, process_data_func, rubbish=False,
                 section_type=None, description=''):
        self.regex = regex
        self.section_type = section_type
        self.description = description
        self.rubbish = rubbish
        self.process_data_func = process_data_func
        self.slug = slug
        try:
            self.pattern = re.compile(self.regex, re.UNICODE | re.DOTALL)
        except:
            print 'Failed regex is %s', self.regex
            raise
        self.data = None
        self.counter = 0

    def extract(self, section):
        match = self.pattern.match(section.patched_text)
        if match is not None:
            self.counter += 1
            data = match.groupdict()
            self.process_data_func(section, data)
            return data['before'] + data['after']
        return None


