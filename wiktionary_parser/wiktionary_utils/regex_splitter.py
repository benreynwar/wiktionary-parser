def chop(text, pattern, instance=0):
    """
    Takes a pieces of text and finds the ``instance`` + 1 instance of
    of ``pattern`` in the text.  Splits the text into two halfs cut at
    this point and returns the halfs.  If ``instance`` is not possible it
    returns None.
    """
    pieces = pattern.split(text)
    last_piece_in_before = instance*2
    if len(pieces) - 1 < last_piece_in_before + 2:
        return None
    counter = 0
    befores = []
    afters = []
    for piece in pieces:
        if counter <= last_piece_in_before:
            befores.append(piece)
        elif counter > last_piece_in_before + 1:
            afters.append(piece)
        counter += 1
    if not afters or not befores:
        raise StandardError('Doh')
    before = ''.join(befores)
    after = ''.join(afters)
    return before, after
