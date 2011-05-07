"""
We have two sets A and B and a matrix AB between them which identifies
which A is compatible with which B.  This routine accepts a matrix, a
2D dictionary, and returns a set of (A,B) pairs.  If there is not an
unambiguous set of pairs an exception is raised.  The number of pairs
returned is the maximum of the number of elements in sets A and B.
This routine is not rigorous and will probably return exceptions when
the problem is in fact solvable.

A very simple matrix
>>> M1 = {'a': {'A': True, 'B': False, 'C': False},
...       'b': {'A': False, 'B': True, 'C': False},
...       'c': {'A': False, 'B': False, 'C': True}}
>>> mm = MatchMatrix(M1)
>>> print mm.get_pairs()
set([('a', 'A'), ('b', 'B'), ('c', 'C')])

A slightly more complicated matrix
>>> M2 = {'a': {'A': True, 'B': True, 'C': False},
...       'b': {'A': False, 'B': True, 'C': False},
...       'c': {'A': False, 'B': True, 'C': True}}
>>> mm = MatchMatrix(M2)
>>> print mm.get_pairs()
set([('a', 'A'), ('b', 'B'), ('c', 'C')])

An assymetic matix
>>> M3 = {'a': {'A': True, 'B': True, 'C': False},
...       'b': {'A': False, 'B': True, 'C': False},
...       'c': {'A': False, 'B': True, 'C': True},
...       'd': {'A': False, 'B': True, 'C': False}}
>>> mm = MatchMatrix(M3)
>>> print mm.get_pairs()
set([('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'B')])

An assymetic ambiguous matix
>>> M4 = {'a': {'A': True, 'B': True, 'C': False},
...       'b': {'A': False, 'B': True, 'C': False},
...       'c': {'A': False, 'B': True, 'C': True},
...       'd': {'A': False, 'B': True, 'C': True}}
>>> mm = MatchMatrix(M4)
>>> try:
...     mm.get_pairs()
... except CannotPair:
...     print 'CannotPair'
CannotPair

"""

class MatchingError(Exception):
    """
    Generic exception for this util.
    """
    pass

class InvalidMatrix(MatchingError):
    """
    The matrix passed to the routine is invalid for some reason.
    """
    pass

class CannotPair(MatchingError):
    """
    This routine is not able to extract a set of pairs from the given matrix.
    """
    def __init__(self, pairs=None, A=None, B=None, *args, **kwargs):
        super(CannotPair, self).__init__(*args, **kwargs)
        self.pairs = pairs
        self.A = A
        self.B = B

class MatchMatrix(object):

    def __init__(self, dict2D):
        A = set(dict2D.keys())
        B = None
        # Check that matrix is well formed
        for a in A:
            keys = set(dict2D[a].keys())
            if B is None:
                B = keys
            elif B != keys:
                raise InvalidMatrix('Second level keys are not always the same.')        
        self.A = A
        self.B = B
        if len(A) == 0 or len(B) == 0:
            raise InvalidMatrix('Empty Matrix')
        self.dict2D = dict2D

    def matches(self, a=None, b=None):
        if a is not None and b is not None:
            raise MatchingError('Cannot specify both a and b.')
        if a is None and b is None:
            raise MatchingError('Must specify a or b.')
        if a is not None:
            c = a
            D = self.B
            dict2D = lambda c, d: self.dict2D[c][d] 
        else:
            c = b
            D = self.A
            dict2D = lambda c, d: self.dict2D[d][c] 
        ds = set([])
        for d in D:
            if dict2D(c,d):
                ds.add(d)
        return ds

    def remove(self, a, b):
        if len(self.A) < len(self.B):
            self.B.remove(b)
        elif len(self.A) == len(self.B):
            self.B.remove(b)
            self.A.remove(a)
        else:
            self.A.remove(a)
                
    def make_tuple(self, a, b):
        return (a, b)

    def get_pairs(self):
        pairs = set([])
        change_made = True
        while change_made:
            change_made = False
            for C, D, c_name, d_name in ((self.A, self.B, 'a', 'b'), (self.B, self.A, 'b', 'a')):
                for c in C:
                    ds = self.matches(**{c_name: c})
#                    if len(ds) == 0:
#                        raise CannotPair()
                    if len(ds) == 1:
                        d = ds.pop()
                        self.remove(**{c_name: c, d_name: d})
                        pair = self.make_tuple(**{c_name: c, d_name: d})
                        pairs.add(pair)
                        change_made = True
                        break
        if len(self.A) != 0 or len(self.B) != 0:
            raise CannotPair(pairs, self.A, self.B)
        return pairs
        

if __name__ == "__main__":
    import doctest
    doctest.testmod()


    
    
