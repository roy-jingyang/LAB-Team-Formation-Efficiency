#!/usr/bin/env python3

import sys
import csv
import copy
from collections import defaultdict

ee_dict = defaultdict(lambda: dict())
cache = list()
record = dict()

with open(sys.argv[2], 'r') as feein:
    while True:
        line = feein.readline()
        if '' == line:
            break
        else:
            title = line
            title = title[:-1] if '\n' == title[-1] else title
            year = int(feein.readline())
            ee_dict[title]['year'] = int(year)
            authors = feein.readline()
            authors = authors[:-1] if '\n' == authors[-1] else authors
            ee_dict[title]['authors'] = authors
            ee = feein.readline()
            ee = ee[:-1] if '\n' == ee[-1] else ee
            ee_dict[title]['ee'] = ee

print('EE info read.')

with open(sys.argv[1], 'r') as fin, open(sys.argv[3], 'w') as fout:
    cnt = 0
    flushed_cnt = 0
    writer = csv.writer(fout)

    while True:
        line = fin.readline()
        if '' == line:
            for r in cache:
                writer.writerow([r['indexid'], r['title'], \
                        r['year'], r['citation'], r['authors'], \
                        r['conf'], r['ee']])
                flushed_cnt += 1
            if record['title'] in ee_dict and \
                int(record['year']) == ee_dict[title]['year'] and \
                record['authors'] == ee_dict[title]['authors']:
                    record['ee'] = ee_dict[title]['ee']
                    writer.writerow([record['indexid'], record['title'], \
                            record['year'], record['citation'], \
                            record['authors'], record['conf'], record['ee']])
                    flushed_cnt += 1
            else:
                pass

            print('Cache flushed. count = {}'.format(flushed_cnt))
            break
        else:
            pass

        if line.startswith('#*'):
            if cnt == 0:
                pass
            else:
                title = record['title']
                if title in ee_dict and \
                        int(record['year']) == ee_dict[title]['year'] and \
                        record['authors'] == ee_dict[title]['authors']:
                            record['ee'] = ee_dict[title]['ee']
                            cache.append(copy.deepcopy(record))
                else:
                    pass
                record.clear()

                if len(cache) > 0 and 0 == len(cache) % 10000:
                    for r in cache:
                        writer.writerow([r['indexid'], r['title'], \
                                r['year'], r['citation'], r['authors'], \
                                r['conf'], r['ee']])
                    del cache[:]
                    flushed_cnt += 10000
                    print('Cache flushed. count = {}'.format(flushed_cnt))
                else:
                    pass
            
            cnt += 1
            record['title'] = line[2:-1]
            record['title'] = record['title'][:-1] \
                    if record['title'][-1] == ',' else record['title']

        if line.startswith('#@'):
            record['authors'] = '|'.join(line[2:-1].split(','))
        elif line.startswith('#year'):
            record['year'] = line[5:-1]
        elif line.startswith('#conf'):
            record['conf'] = line[5:-1]
        elif line.startswith('#citation'):
            record['citation'] = line[9:-1]
        elif line.startswith('#index'):
            record['indexid'] = line[6:-1]
        else:
            pass

