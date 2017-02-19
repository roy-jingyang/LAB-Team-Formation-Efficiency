#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from lxml import etree

split_target_filename = sys.argv[1]
split_file_num = int(sys.argv[2])
fn_out = sys.argv[3]

parser = etree.XMLParser(dtd_validation=True)
with open(fn_out, 'w') as fout:
    for fi in range(split_file_num):
        part_fn = split_target_filename + '.part{}'.format(fi)
        print(part_fn)

        doc = etree.parse(part_fn, parser)

        for entry in doc.iter('article', 'inproceedings', 'proceedings', \
                'book', 'incollection', 'phdthesis', 'mastersthesis', 'www'):
            title = [t.text for t in entry.iter('title', 'booktitle')]
            authors = [a.text for a in entry.iter('author')]
            year = [y.text for y in entry.iter('year')]
            ee = [ee.text for ee in entry.iter('ee')]

            if len(title) > 0 and len(authors) > 0 and len(year) > 0 and \
                    len(ee) > 0 and title[0] and year[0] and ee[0]:
                        fout.write(title[0] + '\n')
                        fout.write(year[0] + '\n')
                        fout.write('|'.join(authors) + '\n')
                        fout.write(ee[0] + '\n')
            else:
                pass

