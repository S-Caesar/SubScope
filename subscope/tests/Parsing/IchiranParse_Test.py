# -*- coding: utf-8 -*-

# IchiranParse test file

import IchiranParse as ip



parseInput = ['1',
              '00:00:05,046 --> 00:00:09,634', 
              '（岡部倫太郎(おかべりんたろう)）宇宙には',
              '始まりはあるが 終わりはない',
              '',
              '2',
              '00:00:10,135 --> 00:00:11,386',
              '無限',
              '',
              '3',
              '00:00:13,847 --> 00:00:17,517',
              '星にもまた 始まりがあるが―']


parseInput = ip.prepParseInput(parseInput)