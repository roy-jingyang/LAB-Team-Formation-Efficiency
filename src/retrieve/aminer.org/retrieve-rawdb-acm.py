#!/usr/bin/env python3

import sys
import csv
import copy

cache = list()
record = dict()

with open(sys.argv[1], 'r') as fin, open(sys.argv[2], 'w') as fout:
    cnt = 0
    writer = csv.writer(fout)

    while True:
        line = fin.readline()
        if '' == line:
            for r in cache:
                writer.writerow([r['indexid'], r['title'], \
                        r['year'], r['citation'], \
                        r['conf'], r['authors']])
            writer.writerow([record['indexid'], record['title'], \
                    record['year'], record['citation'], \
                    record['conf'], record['authors']])
            break
        else:
            pass

        if line.startswith('#*'):
            if cnt == 0:
                pass
            else:
                cache.append(copy.deepcopy(record))
                record.clear()

                if 0 == len(cache) % 10000:
                    for record in cache:
                        writer.writerow([record['indexid'], record['title'], \
                                record['year'], record['citation'], \
                                record['conf'], record['authors']])
                    del cache[:]
                    print('Cache flushed. count = {}'.format(cnt))
                else:
                    pass
            
            cnt += 1
            record['title'] = line[2:-1]

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

