#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import csv
from collections import defaultdict

result = list()
with open(sys.argv[1], 'r') as dbf:
    reader = csv.reader(dbf)
    for row in reader:
        result.append(row)
print('Fetched {} records.'.format(len(result)))

records_tmp = dict()
rm_dup = set()
records = dict()
for r in result:
    # id, title, year, ratings, [terms_edh], [authors]
    record = r[1:]
    # title, year, ratings, [terms_edh], [authors]
    if str(record) not in rm_dup:
        rm_dup.add(str(record))
        records_tmp[r[0]] = record
    else:
        pass
print('{} records left after removing duplicates.'.format(len(records_tmp)))

for k, record in records_tmp.items():
    year = int(record[1])
    if year >= int(sys.argv[3]) and year < int(sys.argv[4]):
        records[k] = record
    else:
        pass
print('{} records in time interval {} - {}'.format(len(records), \
        sys.argv[3], sys.argv[4]))

cnt_individuals = defaultdict(lambda: 0)
ambiguated_individuals = defaultdict(lambda: 0)
for k, record in records.items():
    individuals = record[4].split('|')
    for p in individuals:
        ambiguated_individuals[p] += 1

def elim_individuals():
    # do elimination on individuals
    cnt_individuals.clear()
    # do counting
    for k, record in records.items():
        individuals = record[4].split('|')
        for p in individuals:
            cnt_individuals[p] += 1

    # eliminate
    cnt_rm_individuals = 0
    for k, record in records.items():
        individuals = record[4].split('|')
        individuals_left = list()
        for p in individuals:
            if cnt_individuals[p] >= 2:
                individuals_left.append(p)
            else:
                pass

        if len(individuals_left) < len(individuals):
            cnt_rm_individuals += 1
            records[k][4] = '|'.join(individuals_left)
        else:
            pass

    return (cnt_rm_individuals > 0)

def elim_articles():
    # do elimination on articles
    cnt_rm_articles = 0
    elim_articles_key = list()
    for k, record in records.items():
        ratings = float(record[2])
        terms = record[3].split('|')
        individuals = record[4].split('|')
        if ratings == 0.0 or len(individuals) < 3 or len(terms) == 0:
            cnt_rm_articles += 1
            elim_articles_key.append(k)
        else:
            pass

    if cnt_rm_articles > 0:
        for k in elim_articles_key:
            del records[k]
    else:
        pass
    return (cnt_rm_articles > 0)


for i in range(25):
    print(i)
    print(elim_individuals())
    print(elim_articles())

l_records = list()
for k, record in records.items():
    l_records.append(record)

l_records.sort(key=lambda x: int(x[1]))

# number confs & individuals, build new dataset
result_final = list()
Terms = dict()
Individuals = dict()
for record in l_records:
    m_terms = list()
    m_individuals = list()

    terms = record[3].split('|')
    for t in terms:
        if t in Terms:
            pass
        else:
            Terms[t] = len(Terms) + 1
        m_terms.append(str(Terms[t]))

    individuals = record[4].split('|')
    for p in individuals:
        if p in Individuals:
            pass
        else:
            Individuals[p] = len(Individuals) + 1
        m_individuals.append(str(Individuals[p]))

    record_new = tuple((record[0], record[1], record[2], ','.join(m_terms),
        ','.join(m_individuals)))
    result_final.append(record_new)

print('{} terms found.'.format(len(Terms)))
print('{} records left after processing.'.format(len(result_final)))

# Write to file
with open(sys.argv[2], 'w') as f:
    i = -1
    for record in result_final:
        i += 1
        f.write('{},{}\n'.format(i, record[0]))
        f.write('{},{}\n'.format(record[1], record[2]))
        f.write('{}\n'.format(record[3]))
        f.write('{}\n'.format(record[4]))

