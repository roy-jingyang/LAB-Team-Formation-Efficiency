#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import sys
import csv

with open(sys.argv[1], 'r') as fin, open(sys.argv[2], 'w') as fout:
    df = pd.read_csv(fin, header=None, \
            names=['id', 'title', 'year', 'cites', 'authors', 'publication', \
            'keywords', 'terms_pri', 'terms_sec'])
    #grouped = df.groupby(['year', 'publication'])
    grouped = df.groupby('publication')
    writer = csv.writer(fout)
    cnt = 0
    for name, group in grouped:
        writer.writerow([name, len(group)])
        cnt += len(group)
    print(cnt)

