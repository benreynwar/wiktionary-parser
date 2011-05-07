class NotImplemented(Exception):
    pass
class ParsingError(Exception):
    pass
class FixingError(Exception):
    pass
class InconsistentEntry(Exception):
    def __init__(self, old_value, new_value):
        self.old_value = old_value
        self.new_value = new_value
    def __str__(self):
        return '%s is old value. %s is new value.' % (repr(self.old_value), repr(self.new_value))

class NotParsedYet(Exception):
    pass
