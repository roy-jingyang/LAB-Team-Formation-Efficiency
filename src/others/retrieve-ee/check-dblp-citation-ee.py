#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
from urllib.parse import urlparse
from collections import defaultdict

locs = defaultdict(lambda: 0)
postfixes = defaultdict(lambda: 0)
count = 0
bad_count = 0

with open(sys.argv[1], 'r') as fin:
    reader = csv.reader(fin)
    for row in reader:
        count += 1
        title = row[1]
        year = row[2]

        authors = row[4].split('|')
        ee = row[-1]
        o = urlparse(ee)
        
        loc = o.netloc
        if '' == loc:
            bad_count += 1
        else:
            loc = loc[:-1] if '\n' == loc[-1] else loc
            locs[loc] += 1

            postfix = o.path.split('/')[-1]
            if 'html' == postfix.split('.')[-1]:
                postfixes['html'] += 1
            elif 'pdf' == postfix.split('.')[-1]:
                postfixes['pdf'] += 1
            else:
                postfixes['others'] += 1

locs = [(k, v) for k, v in locs.items()]
locs = sorted(locs, key=lambda x: x[1])
print('LOCs:')
for k, v in locs:
    print('{}: {}'.format(k, v))

print('\nPOSTFIXes:')
for k, v in postfixes.items():
    print('{}: {}'.format(k, v))

print(count)
print(bad_count)
print('\nBad count:{:.2%}'.format(bad_count / count))

