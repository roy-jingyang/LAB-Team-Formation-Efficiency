#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import re

name_list = list()
conf_by_abbr = dict()
conf_by_full = dict()
jour_by_abbr = dict()
jour_by_full = dict()

cnt_all = 0
cnt_all_index = 0

cnt_found = 0
cnt_found_index = 0
found_by_abbr = list()
found_by_full = list()

cnt_missing = 0
cnt_missing_index = 0
missing = list()

with open(sys.argv[1], 'r') as fname, open(sys.argv[2], 'r') as f_conf, \
        open(sys.argv[3], 'r') as f_jour:
            for row in csv.reader(fname):
                name_list.append((row[0], row[1]))
                cnt_all += int(row[1])
                cnt_all_index += 1
            for row in csv.reader(f_conf):
                if len(row[0].split(' - ')) > 1:
                    abbr = row[0].split(' - ')[0]
                    conf_by_abbr[abbr] = row[1:]
                    full = row[0].split(' - ')[1]
                else:
                    full = row[0]
                conf_by_full[full] = row[1:]
            for row in csv.reader(f_jour):
                if len(row[0].split(' - ')) > 1:
                    abbr = row[0].split(' - ')[0]
                    jour_by_abbr[abbr] = row[1:]
                    full = row[0].split(' - ')[1]
                else:
                    full = row[0]
                jour_by_full[full] = row[1:]

for name, count in name_list:
    count = int(count)
    record = [name]

    if name in conf_by_abbr:
        record.extend(conf_by_abbr[name])
        found_by_abbr.append(record)
        cnt_found += count
        cnt_found_index += 1
    elif name in jour_by_abbr:
        record.extend(jour_by_abbr[name])
        found_by_abbr.append(record)
        cnt_found += count
        cnt_found_index += 1
    else:
        found = False
        patt = re.compile('\\b' + name + '\\b')
        for full in conf_by_full.keys():
            if patt.search(full) is not None:
                record.extend([full])
                record.extend(conf_by_full[full])
                cnt_found += count if not found else 0
                cnt_found_index += 1 if not found else 0
                found = True
            else:
                pass
        for full in jour_by_full.keys():
            if patt.search(full) is not None:
                record.extend([full])
                record.extend(jour_by_full[full])
                cnt_found += count if not found else 0
                cnt_found_index += 1 if not found else 0
                found = True
            else:
                pass
        if found:
            found_by_full.append(record)
        else:
            cnt_missing += int(count)
            cnt_missing_index += 1
            missing.append(record)

print(cnt_all)
print('{} found: {:.2%}'.format(cnt_found, cnt_found / cnt_all))
print('{} indices found: {:.2%}'.format(cnt_found_index, \
        cnt_found_index / cnt_all_index))
print('{} NOT found: {:.2%}'.format(cnt_missing, cnt_missing / cnt_all))
print('{} indices NOT found: {:.2%}'.format(cnt_missing_index, \
        cnt_missing_index / cnt_all_index))

with open('found_by_abbr.csv', 'w') as f_found_attr, \
        open('found_by_full.csv', 'w') as f_found_full, \
        open('missing.csv', 'w') as f_missing:
            csv.writer(f_found_attr).writerows(found_by_abbr)
            csv.writer(f_found_full).writerows(found_by_full)
            csv.writer(f_missing).writerows(missing)

