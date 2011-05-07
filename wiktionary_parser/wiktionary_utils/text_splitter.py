# -*- coding: utf-8 -*-

u"""
Utilities for breaking down a text file into smaller blocks.

This is a non-rigorous test to make sure it's working vaguely right.

>>> import StringIO

>>> file_string = \"""This is a test to see if <tag> tags work to divide </tag>
... the text into <tag></tag></tag> appropriate<tag>
... blocks.  I hope it works properly.
... But I think the chances are pretty slim the</tag> first
... time round.<tag>I'm also</tag>curious<tag>if</tag>I<tag>
... can</tag> get the doctest working.
... \"""

>>> file_obj = StringIO.StringIO()
>>> file_obj.write(file_string)

>>> class TagBlock(Block):
...     start_pattern = '<tag>'
...     stop_pattern = '</tag>'
...     slug = 'TagBlock'

>>> file_obj.seek(0)
>>> file_splitter = Splitter(file_obj, [TagBlock, ])
>>> for block in file_splitter:
...     print block.text
 tags work to divide 
<BLANKLINE>
<BLANKLINE>
blocks.  I hope it works properly.
But I think the chances are pretty slim the
I'm also
if
<BLANKLINE>
can

Test to see if filler blocks are working.

>>> file_obj.seek(0)
>>> file_splitter = Splitter(file_obj, [TagBlock, ], filler_blocks=True,
...     include_tags=True)
>>> for block in file_splitter:
...     if isinstance(block, FillerBlock):
...         print '--FILLER--',
...     else:
...         print '--BLOCK--',
...     print block.text
--FILLER-- This is a test to see if 
--BLOCK-- <tag> tags work to divide </tag>
--FILLER-- 
the text into 
--BLOCK-- <tag></tag>
--FILLER-- </tag> appropriate
--BLOCK-- <tag>
blocks.  I hope it works properly.
But I think the chances are pretty slim the</tag>
--FILLER--  first
time round.
--BLOCK-- <tag>I'm also</tag>
--FILLER-- curious
--BLOCK-- <tag>if</tag>
--FILLER-- I
--BLOCK-- <tag>
can</tag>
--FILLER--  get the doctest working.
<BLANKLINE>

Now testing for if start tag and stop tag are the same.

>>> class TagBlock2(Block):
...     start_pattern = '<tag>'
...     stop_pattern = '<tag>'
...     slug = 'TagBlock2'

>>> file_obj.seek(0)
>>> file_splitter2 = Splitter(file_obj, [TagBlock2, ])
>>> for block in file_splitter2:
...     print block.text
 tags work to divide </tag>
the text into 
<BLANKLINE>
blocks.  I hope it works properly.
But I think the chances are pretty slim the</tag> first
time round.
if</tag>I

Now checking what happens if we have two different block types.

>>> class IBlock(Block):
...     start_pattern = 'I'
...     stop_pattern = 'the'
...     slug = 'IBlock'

>>> file_obj.seek(0)
>>> file_splitter3 = Splitter(file_obj, [TagBlock, IBlock])
>>> for block in file_splitter3:
...     print block.text
 tags work to divide 
<BLANKLINE>
<BLANKLINE>
blocks.  I hope it works properly.
But I think the chances are pretty slim the
I'm also
if
<tag>
can</tag> get 

Now test Chopper.

>>> file_obj.seek(0)
>>> file_splitter4 = Chopper(file_obj, [TagBlock,], include_tags=True)
>>> for block in file_splitter4:
...     print block.text
<tag> tags work to divide </tag>
the text into 
<tag></tag></tag> appropriate
<tag>
blocks.  I hope it works properly.
But I think the chances are pretty slim the</tag> first
time round.
<tag>I'm also</tag>curious
<tag>if</tag>I
<tag>
can</tag> get the doctest working.
<BLANKLINE> 

Testing to see if filler_blocks option works with Chopper.  Should
keep the first piece of text before the first chop.

>>> file_string2 = \"""<tag> chopping it up <tag> into pieces
... to test if <tag> it's working.\"""
>>> file_obj2 = StringIO.StringIO()
>>> file_obj2.write(file_string2)

>>> file_string3 = \"""Still <tag> chopping it up <tag> into pieces
... to test if <tag> it's working.\"""
>>> file_obj3 = StringIO.StringIO()
>>> file_obj3.write(file_string3)

>>> file_string4 = \"""If there are no tags at all
... does it still return a FillerBlock.\"""
>>> file_obj4 = StringIO.StringIO()
>>> file_obj4.write(file_string4)

>>> file_obj2.seek(0)
>>> file_splitter = Chopper(file_obj2, [TagBlock,], include_tags=True,
...      filler_blocks=True)
>>> for block in file_splitter:
...     print block.text
<tag> chopping it up 
<tag> into pieces
to test if 
<tag> it's working.

>>> file_obj3.seek(0)
>>> file_splitter = Chopper(file_obj3, [TagBlock,], include_tags=True,
...      filler_blocks=True)
>>> for block in file_splitter:
...     print block.text
Still 
<tag> chopping it up 
<tag> into pieces
to test if 
<tag> it's working.

>>> file_obj4.seek(0)
>>> file_splitter = Chopper(file_obj4, [TagBlock,], include_tags=True,
...     filler_blocks=True)
>>> for block in file_splitter:
...     print block.text
If there are no tags at all
does it still return a FillerBlock.

Now test to see if it can handle quotes OK.
>>> file_string = \"""Can it snip up ''quotes'' correctly and can it 'sort
... single and double' quotes separately. What will happen ''if we '
... interleave them.'' Will it still work' or not.
... \"""
>>> file_obj5 = StringIO.StringIO()
>>> file_obj5.write(file_string)

>>> class SingleQuoteBlock(Block):
...     start_pattern = "'"
...     stop_pattern = "'"
...     slug = 'SingleQuoteBlock'

>>> class DoubleQuoteBlock(Block):
...     start_pattern = "''"
...     stop_pattern = "''"
...     slug = 'DoubleQuoteBlock'

>>> file_obj5.seek(0)
>>> file_splitter = Splitter(file_obj5, [DoubleQuoteBlock, SingleQuoteBlock])
>>> for block in file_splitter:
...     print block.text
quotes
sort
single and double
if we '
interleave them.
 or not.
<BLANKLINE>

Test to confirm it's OK with unicode
>>> file_string = u\"""How well will it wörk if unicode is involved.
... Will it wörk or not. Maybe not at äll.\"""
>>> file_obj6 = StringIO.StringIO()
>>> file_obj6.write(file_string)

>>> class WorkBlock(Block):
...     start_pattern = u'wör'
...     stop_pattern = u't_ä'
...     slug = 'WorkBlock'

>>> file_obj6.seek(0)
>>> file_splitter = Chopper(file_obj6, [WorkBlock])
>>> for block in file_splitter:
...     print block.text
k if unicode is involved.
Will it 
k or not. Maybe not at äll.
"""

import re
from StringIO import StringIO

class SplittingError(Exception):
    pass

class Block(object):
    
    """
    A block of text produced by a Splitter.
    """
 
    class BlockFinishedError(Exception):
        pass

    # The patterns should be set be subclasses.
    
    start_patterns = None
    stop_patterns = None
    slug = None

    def __init__(self):
        self.finished = False
        self.str_list = []
        self.text = None
        self.start_tag = None
        self.stop_tag = None

    def add_text(self, text):
        if self.finished:
            raise self.BlockFinishedError() 
        self.str_list.append(text)

    def finish(self):
        self.text = ''.join(self.str_list)
        self.finished = True



class FillerBlock(Block):
    """
    Holds the text from between matched blocks.
    """
    pass

class SplitterBase(object):

    class BlockClassesIncompatible(Exception):
        pass

    def __init__(self, source, block_classes, include_tags=False,
                 filler_blocks=False, filler_block_class = FillerBlock):
        try:
            source.readline
            self.source = source
        except AttributeError:
            self.source = StringIO()
            self.source.write(source)
            self.source.seek(0)
        self.current_string = ''
        self.block_classes = block_classes
        self.create_slug_to_bc()
        self.finished_blocks = []
        self.current_block = None
        self.filler_blocks = filler_blocks
        self.filler_block_class = filler_block_class
        self.filler_block = None
        self.start_pattern = re.compile(self.get_start_str(),
                                        re.UNICODE|re.DOTALL)
        self.include_tags = include_tags

    def create_slug_to_bc(self):
        self.slug_to_bc = {}
        self.max_num_lines = 1
        for bc in self.block_classes:
            no_lines = bc.start_pattern.count('\n') + 1
            if hasattr(bc,'stop_pattern'):
                no_lines = max(no_lines, bc.stop_pattern.count('\n') + 1)
            self.max_num_lines = max(no_lines, self.max_num_lines)
            if bc.slug in self.slug_to_bc:
                raise self.BlockClassesIncompatible()
            self.slug_to_bc[bc.slug] = bc

    def match_to_bc(self, match):
        gd = match.groupdict()
        for key, value in gd.items():
            if key[:5] == 'SLUG_' and value:
                return self.slug_to_bc[key[5:]]
        raise ValueError('match does not contain a slug')

    def top_up_current_string(self):
        if self.current_string == '':
            num_lines = 0
        else:
            # Don't count line breaks at end of the string
            num_lines = self.current_string[:-1].count('\n') + 1
        if self.max_num_lines > num_lines:
            new_lines = [self.current_string]
            for i in range(num_lines, self.max_num_lines):
                new_line = self.source.readline()
                if new_line:
                    new_lines.append(new_line)
            self.current_string = ''.join(new_lines)

    def process_groupdict(self, groupdict):
        before = groupdict['before']
        tag = groupdict['tag']
        remainder = groupdict['remainder']
        true_tag = groupdict.get('true_tag', tag)
        pre_tag = groupdict.get('pre_tag', '')
        post_tag = groupdict.get('post_tag', '')
        if tag != pre_tag + true_tag + post_tag:
            raise SplittingError()
        return {'before': before+pre_tag, 'tag': true_tag,
                'remainder': post_tag+remainder,}

    def get_start_str(self):
        options = ['(?P<%s>%s)' % ('SLUG_'+bc.slug, bc.start_pattern)
                   for bc in self.block_classes]
        options = '|'.join(options)
        start_string = '^(?P<before>.*?)(?P<tag>%s)(?P<remainder>.*)$' % options
        return start_string

    def chop_off_first_line(self):
        # Chop off first line from current_string
        # Not an efficient method I think.
        pattern = re.compile('(?P<chopped>.*?)\n(?P<remainder>.*)', re.UNICODE|re.DOTALL)
        match = pattern.search(self.current_string)
        if match:
            self.current_string = match.group('remainder')
            return match.group('chopped') + '\n'
        else:
            line = self.current_string
            self.current_string = ''
            return line

    def stop_pattern(self):
        return re.compile('^(?P<before>.*?)(?P<tag>%s)(?P<remainder>.*)$' %
                          self.current_block.stop_pattern,
                          re.UNICODE|re.DOTALL)
            

class Chopper(SplitterBase):
    """
    Splits text into blocks based on start patterns.
    """
    def find_start(self):
        finished_block = None
        matches = self.start_pattern.match(self.current_string)
        if matches:
            pgd = self.process_groupdict(matches.groupdict())
            remainder = pgd['remainder']
            before = pgd['before']
            tag = pgd['tag']
            block_class = self.match_to_bc(matches)
            if self.current_block:
                finished_block = self.current_block
            elif self.filler_blocks:
                if not self.filler_block:
                    if before != '':
                        self.filler_block = self.filler_block_class()
                if self.filler_block:
                    finished_block = self.filler_block
                    self.filler_block = None
            if finished_block:
                finished_block.add_text(before)
                finished_block.finish()
            self.current_block = block_class()
            self.current_block.start_tag = tag
            if self.include_tags:
                self.current_block.add_text(tag)
            self.current_string = remainder
        else:
            first_line = self.chop_off_first_line()
            if self.current_block:
                self.current_block.add_text(first_line)
            elif self.filler_blocks:
                if not self.filler_block:
                    self.filler_block = self.filler_block_class()
                self.filler_block.add_text(first_line)
                    
        return finished_block

    def __iter__(self):
        """
        Breaks the source down into the blocks and returns them
        one by one.
        """
        while True:
            self.top_up_current_string()
            if not self.current_string:
                if self.current_block:
                    self.current_block.finish()
                    yield self.current_block
                if self.filler_blocks and self.filler_block:
                    self.filler_block.finish()
                    yield self.filler_block
                break
            block = self.find_start()
            if block:
                yield block


class Splitter(SplitterBase):
    """
    Splits text into blocks based on start and stop patterns.
    
    Scans through text for first instance of a start pattern it finds.
    Continues through to the matching stop pattern.  Assigns that text
    to a block and yields the block.  Continues upon next iteration.

    Start pattern and stop pattern are simple text, not regex, although
    they can contain line ends.
    
    Based upon the python build-in regex.
    """
    
    def find_end(self):
        matches = self.stop_pattern().match(self.current_string)
        if matches:
            pgd = self.process_groupdict(matches.groupdict())
            remainder = pgd['remainder']
            contents = pgd['before']
            tag = pgd['tag']
            self.current_block.add_text(contents)
            if self.include_tags:
                self.current_block.add_text(tag)
            self.current_block.stop_tag = tag
            self.current_block.finish()
            self.current_string = remainder
        else:
            self.current_block.add_text(self.chop_off_first_line())
    
    def find_start(self):
        matches = self.start_pattern.match(self.current_string)
        if matches:
            pgd = self.process_groupdict(matches.groupdict())
            if self.filler_blocks:
                before = pgd['before']
                if before != '':
                    if not self.filler_block:
                        self.filler_block = self.filler_block_class()
                    self.filler_block.add_text(before)
                if self.filler_block:
                    self.filler_block.finish()
            remainder = pgd['remainder']
            tag = pgd['tag']
            block_class = self.match_to_bc(matches)
            assert not self.current_block
            self.current_block = block_class()
            self.current_block.start_tag = tag
            if self.include_tags:
                self.current_block.add_text(tag)
            self.current_string = remainder
        else:
            if self.filler_blocks:
                if not self.filler_block:
                    self.filler_block = self.filler_block_class()
                self.filler_block.add_text(self.chop_off_first_line())
            else:
                self.chop_off_first_line()

    def __iter__(self):
        """
        Breaks the source down into the blocks and returns them
        one by one.

        Any open blocks are returned at the end of the file.
        """
        while True:
            self.top_up_current_string()
            if not self.current_string:
                block = None
                if self.current_block:
                    block = self.current_block
                if self.filler_blocks and self.filler_block:
                    block = self.filler_block
                if block:
                    block.finish()
                    yield block
                break
            if self.current_block:
                self.find_end()
                if self.current_block.finished:
                    block = self.current_block
                    self.current_block = None
                    yield block
            else:
                self.find_start()
                if self.filler_blocks and self.filler_block and self.filler_block.finished:
                    block = self.filler_block
                    self.filler_block = None
                    yield block
    

if __name__ == "__main__":
    import sys
    reload(sys)
    sys.setdefaultencoding("UTF-8")
    import doctest
    doctest.testmod()
