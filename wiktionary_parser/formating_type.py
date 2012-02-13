import re
from .exceptions import NotImplemented


class FormatingType(object):
    """
    Represents a particular manner in which a section is formatted.
    """
    
    def __init__(self, slug, description):
        self.slug = slug
        self.description = description

    def read(self, section):
        """
        If the section doesn't match it returns ``None``.  If it does match
        it processes the section and returns a dictionary as follows:

        ``data`` - a dictionary of values that were read from the section.
                     ``None`` means it was not readable.
        ``ignore`` - whether the section can be safely ignored.
        ``correct`` - whether the section is formated correctly.
        ``fixed_text`` - the repaired text of the section
        
        """
        raise NotImplemented()


class RegexFT(FormatingType):
    """
    A formating type that mostly uses regex to match.
    """

    def __init__(self, slug, regex, fix_func=None,
                 correct=False, readable=True, description='',
                 ignore=False, alert_class=None,
                 get_data=lambda section, groupdict: groupdict,
                 matching_func=None):
        """
        ``regex`` defines whether a piece of text is of this type.
        ``fix_func`` is applied to text of this type to correct it's
            formating.
        ``correct`` is whether the formating is correct.
        ``readable`` is whether this type can be read by the parser.
        ``ignore`` is whether this section can be ignored without loss of
            information.
         ``get_data`` a function that returns the data read from the section.
         ``matching_func`` a function that determines whether this formating type
            matches the section.  If it is not supplied matching the regex is sufficient.
        """
        super(RegexFT, self).__init__(slug=slug, description=description)
        self.regex = regex
        self.fix_func = fix_func
        self.correct = correct
        self.alert_class = alert_class
        self.pattern = re.compile(regex, re.UNICODE|re.DOTALL)
        self.readable = readable
        self.ignore = ignore
        self.get_data = get_data
        self.matching_func = matching_func

    def read(self, section):
        match = self.pattern.match(section.text)
        if not match:
            return None
        groupdict = match.groupdict()
        if self.matching_func is not None and not self.matching_func(section, groupdict):
            return None
        read_dict = {}
        read_dict['correct'] = self.correct
        read_dict['ignore'] = self.ignore
        if self.readable:
            data = self.get_data(section, groupdict)
            read_dict['data'] = data
            if not self.correct:
                read_dict['fixed_text'] = self.fix_func(data)
        else:
            if self.fix_func is not None or self.correct:
                raise FixingError()
            read_dict['data'] = None
        return read_dict
        
