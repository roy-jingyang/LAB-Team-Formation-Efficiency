#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

split_target_filename = sys.argv[1]
split_file_num = int(sys.argv[2])

XML_HEADER = '<?xml version="1.0" encoding="ISO-8859-1"?>\n' + \
        '<!DOCTYPE dblp SYSTEM "dblp.dtd">\n' + \
        '<dblp>\n'
XML_FOOTER = '</dblp>\n'

ENTRY_TYPE = ['article', 'inproceedings', 'proceedings', 'book', \
        'incollection', 'phdthesis', 'mastersthesis', 'www']

cnt = 0
fi = 0
with open(split_target_filename, 'r') as fin:
    fout = open(split_target_filename + '.part{}'.format(fi), 'w')
    while True:
        line = fin.readline()
        if '' == line:
            print('EOF')
            fout.close()
            break
        else:
            fout.write(line)

        if line[2:-2] in ENTRY_TYPE:
            cnt += 1
        else:
            pass

        if 484800 == cnt:
            if fi + 1 < split_file_num:
                fout.write(XML_FOOTER)
                fout.close()
                fi += 1
                cnt = 0
                fout = open(split_target_filename + '.part{}'.format(fi), 'w')
                fout.write(XML_HEADER)
            else:
                pass

print(cnt)

