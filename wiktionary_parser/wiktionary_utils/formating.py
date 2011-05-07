"""
>>> text = "(Remove the brackets (please))"
>>> print remove_enclosing_formating(text, '\(', '\)')
Remove the brackets (please)
>>> text = "(Don't) remove this (brackets)"
>>> print remove_enclosing_formating(text, '\(', '\)')
(Don't) remove this (brackets)
>>> text = "(Leave this ( alone because it's not clear)"
>>> print remove_enclosing_formating(text, '\(', '\)')
(Leave this ( alone because it's not clear)
>>> print remove_enclosing_formating(text, '\(', '\)', remove_half=True)
Leave this ( alone because it's not clear)
>>> text = " ( Whatever is going on (here) )  " 
>>> print remove_enclosing_formating(text, '\(', '\)', remove_half=True)
Whatever is going on (here) 
>>> text = " ( Whatever ) is ) going on )"
>>> print remove_enclosing_formating(text, '\(', '\)', remove_half=True)
 ( Whatever ) is ) going on 
>>> text = " ( Whatever ) is ) going ) (on )"
>>> print remove_enclosing_formating(text, '\(', '\)', remove_half=True)
 ( Whatever ) is ) going ) (on )
>>> text = "( Testing first ( bracket ) (now)"
>>> print remove_enclosing_formating(text, '\(', '\)', remove_half=True)
Testing first ( bracket ) (now)
>>> text = " Shouldn't (remove)"
>>> print remove_enclosing_formating(text, '\(', '\)', remove_half=True)
 Shouldn't (remove)
>>> text = "( Shouldn't) remove"
>>> print remove_enclosing_formating(text, '\(', '\)', remove_half=True)
( Shouldn't) remove
"""

import re


def remove_enclosing_formating(text, start, stop, remove_half=False):
    """
    Receives a piece of text and a starting tag and a stoping tag in
    regex format.  If the piece of text is encapsulated by the tags
    and the two tags correspond to one another the encapsulating tags
    are removed.  If ``remove_half`` is True then a starting or stopping
    tag at the beginning or end of the text without a corresponds opposite
    tag will also be removed.
    
    """
    # Check if text is contained by this
    regex = '^\s*{start}\s*(?P<cleaned>.*)\s*{stop}\s*$'
    regex_start = '^\s*{start}\s*(?P<cleaned>.*)$'.format(start=start)
    has_start_match = re.compile(regex_start, re.UNICODE).match(text)
    regex_stop = '^(?P<cleaned>.*)\s*{stop}\s*$'.format(stop=stop)
    has_stop_match = re.compile(regex_stop, re.UNICODE).match(text)
    if has_start_match:
        if has_stop_match:
            regex_full = regex.format(start=start, stop=stop)
            match = re.compile(regex_full, re.UNICODE).match(text)
            cleaned = match.group('cleaned')
        else:
            cleaned = has_start_match.group('cleaned')
    elif has_stop_match:
        cleaned = has_stop_match.group('cleaned')
    if not remove_half and not (has_stop_match and has_start_match):
        return text
    start_pattern = re.compile(start)
    stop_pattern = re.compile(stop)
    pieces = start_pattern.split(text)
    number_open_starts = 0
    open_surplus = 0
    max_open_surplus = 0
    if has_start_match:
        min_open_surplus = 1
    else:
        min_open_surplus = 0
    for piece, first, last in (
        [(pieces[0], True, False)] + 
        [(piece, False, False) for piece in pieces[1:-1]] + 
        [(pieces[-1], False, True)]):
        num_stops = len(stop_pattern.findall(piece))
        if first:
            open_surplus += -num_stops
        else:
            open_surplus += 1 - num_stops
        if not first and not last:
            max_open_surplus = max(max_open_surplus, open_surplus + 1)
            min_open_surplus = min(min_open_surplus, open_surplus)
    if (has_start_match and has_stop_match and 
        min_open_surplus > 0 and open_surplus == 0):
            return match.group('cleaned')
    if remove_half:
        if has_start_match and min_open_surplus > 0 and open_surplus > 0:
            return has_start_match.group('cleaned')
        if has_stop_match and open_surplus < min_open_surplus:
            return has_stop_match.group('cleaned')
    return text

if __name__ == "__main__":
    import doctest
    doctest.testmod()
