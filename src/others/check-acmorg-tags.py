#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
from collections import defaultdict

cnt_keywords = defaultdict(lambda: 0)
cnt_terms_edh = defaultdict(lambda: 0)
cnt_terms_edl = defaultdict(lambda: 0)
cnt_terms = defaultdict(lambda: 0)
cnt_missing_terms = 0

with open(sys.argv[1], 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        keywords = row[-3].split('|')
        terms_edh = row[-2].split('|')
        terms_edl = row[-1].split('|')

        if 0 == len(terms_edh) and 0 == len(terms_edl) or \
                '' == terms_edh[0] and '' == terms_edl[0]:
            cnt_missing_terms += 1
        else:
            pass

        for w in keywords:
            # TODO
            keyword = w.lower().replace('-', '').replace(' ', '')
            cnt_keywords[keyword] += 1

        for t in terms_edh:
            term_edh = t.lower().replace('-', '').replace(' ', '')
            cnt_terms_edh[term_edh] += 1
            cnt_terms[term_edh] += 1

        for t in terms_edl:
            term_edl = t.lower().replace('-', '').replace(' ', '')
            cnt_terms_edl[term_edl] += 1
            cnt_terms[term_edl] += 1

num_keywords = len(cnt_keywords)
cnt_keywords = [(k, v) for k, v in cnt_keywords.items()]
cnt_keywords = sorted(cnt_keywords, key=lambda x: x[1], reverse=True)

num_terms_edh = len(cnt_terms_edh)
cnt_terms_edh = [(k, v) for k, v in cnt_terms_edh.items()]
cnt_terms_edh = sorted(cnt_terms_edh, key=lambda x: x[1], reverse=True)

num_terms_edl = len(cnt_terms_edl)
cnt_terms_edl = [(k, v) for k, v in cnt_terms_edl.items()]
cnt_terms_edl = sorted(cnt_terms_edl, key=lambda x: x[1], reverse=True)

num_terms = len(cnt_terms)
cnt_terms = [(k, v) for k, v in cnt_terms.items()]
cnt_terms = sorted(cnt_terms, key=lambda x: x[1], reverse=True)

'''
print('\nKeywords:')
for k, v in cnt_keywords:
    print('{}: {}'.format(k, v))
print('-------------------------------------------------------------------')
print('\nTerms edh:')
for k, v in cnt_terms_edh:
    print('{}: {}'.format(k, v))
print('-------------------------------------------------------------------')
print('\nTerms edl:')
for k, v in cnt_terms_edl:
    print('{}: {}'.format(k, v))
'''
print('\nKeywords:')
print('\nTerms:')
for k, v in cnt_terms:
    print('{}: {}'.format(k, v))
print('-------------------------------------------------------------------')
print('-------------------------------------------------------------------')

print(num_keywords)
print(num_terms_edh)
print(num_terms_edl)
print(num_terms)
print(cnt_missing_terms)

