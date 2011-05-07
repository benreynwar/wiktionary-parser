# -*- coding: utf-8 -*-

"""
>>> m = Memory('memory_test.txt')    
>>> m.clear()
>>> m['a'] = [2, 4, 5]
>>> m['b'] = 3
>>> m.save()
>>> n = Memory('memory_test.txt')
>>> print n
{'a': [2, 4, 5], 'b': 3}
"""

import pickle

class Memory(dict):

    def __init__(self, file_name):
        self.file_name = file_name
        stored_dict = self._read()
        if stored_dict is None:
            stored_dict = {}
        for k, v in stored_dict.items():
            self[k] = v

    def save(self):
        storing_dict = {}
        for k, v in self.items():
            storing_dict[k] = v
        pickle.dump(storing_dict, file(self.file_name, 'w'))

    def _read(self):
        try:
            return pickle.load(file(self.file_name, 'r'))
        except EOFError:
            return None


class FixMemory(Memory):
    """
    This is a permanent dictionary, saved to file, whose keys are page
    titles, and whose values are Tuples containing (delta, code).
    Where ``delta`` is the change the parser wants to make to the page and
    ``code`` is the current status of this change.

    """
    ALREADY_FIXED = 'AF'
    DONT_FIX = 'DF'
    FIX = 'F'
    NEEDS_APPROVAL = 'NA'
    NO_INFO = 'NI'

    def mark_fixed(self, word, delta):
        self[word] = (delta, self.ALREADY_FIXED)

    def approve(self, word, delta):
        if not (word in self and self[word][0] == delta and self[word][1] == self.ALREADY_FIXED):
            self[word] = (delta, self.FIX)
            
    def reject(self, word, delta):
        if not (word in self and self[word][0] == delta and self[word][1] == self.ALREADY_FIXED):
            self[word] = (delta, self.DONT_FIX)

    def mark_needs_approval(self, word, delta):
        if not (word in self and self[word][0] == delta):
            self[word] = (delta, self.NEEDS_APPROVAL)
        
    def remove(self, word, delta):
        if (word in self and self[word][0] == delta and self[word][1] == self.ALREADY_FIXED):
            self.pop(word)

    def all_needing_approval(self):
        ana = []
        for word, info in self.items():
            if info[1] == self.NEEDS_APPROVAL:
                ana.append((word, info[0]))
        return ana

    def in_memory(self, word, delta):
        if word in self and self[word][0] == delta:
            return True
        else:
            return False

    


if __name__ == "__main__":
    import doctest
    doctest.testmod()
