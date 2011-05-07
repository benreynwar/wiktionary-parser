from text_splitter import TextSplitter

file1 = ['This is a test to see if <tag> tags work to divide </tag>',
         'the text into <tag></tag></tag> appropriate<tag>',
         'blocks.  I hope it works properly.',
         'But I think the chances are pretty slim the</tag> first',
         'time round.<tag>I am also</tag>curious<tag>if</tag>I<tag>',                                                    
         'can</tag> get the doctest working.',                                                                           
         ]                          
file1_splitter = TextSplitter(file1, '<tag>', '</tag>')                                                                  
for block in file1_splitter:                                                                                             
    print block 
