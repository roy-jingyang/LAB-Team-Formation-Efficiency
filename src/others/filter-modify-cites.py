#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
import pandas as pd
from collections import defaultdict
from math import log
import numpy as np

def normalize(nparr):
    return (nparr - np.amin(nparr)) / (np.amax(nparr) - np.amin(nparr))

with open(sys.argv[1], 'r') as fin, open(sys.argv[2], 'r') as fdict, \
        open(sys.argv[3], 'w') as fout:
    records = list()
    cnt = 0
    for row in csv.reader(fin):
        # id, title, year, cites
        # authors, publication, keywords, terms_pri,
        # terms_sec (9)
        valid_flag = True
        col_ind = [0, 1, 2, 3, 4, 5, 7]
        # NEED: id, title, year, cites, authors, publication, terms_pri (7)
        for i in col_ind:
            if '' == row[i]:
                valid_flag = False
            else:
                pass
        if valid_flag:
            cnt += 1
            records.append([row[0], row[1], row[2], row[3], row[4], row[5], \
                    row[7]])
        else:
            pass
    print(cnt)

    '''
    writer = csv.writer(fout)
    for record in records:
        modified_row = [x for x in record[:3]]
        modified_row.append(str(0 if record[3] in ['0', '-1'] else \
                log(int(record[3]))))
        modified_row.append(record[6])
        modified_row.append(record[4])
        writer.writerow(modified_row)

    '''
    pub_dict = dict()
    for row in csv.reader(fdict):
        if '' == row[-1]:
            pub_dict[row[0]] = row[-5:-3]
            #pub_dict[row[0]] = row[-2]
        else:
            pub_dict[row[0]] = row[-4:-2]
            #pub_dict[row[0]] = row[-1]
    # alpha: publication related factor
    tmp_pub_dict = list()
    for k, v in pub_dict.items():
        alpha = 0.0 if 0 == int(v[0]) else int(v[1]) / int(v[0])
        #alpha = 0.0 if -1 == int(v) else int(v)
        tmp_pub_dict.append((k, alpha))
    v_alphas = normalize([v for k, v in tmp_pub_dict])
    for i in range(len(tmp_pub_dict)):
        k = tmp_pub_dict[i][0]
        pub_dict[k] = v_alphas[i]

    df = pd.DataFrame(records, columns=['id', 'title', 'year', 'cites', \
            'authors', 'publication', 'terms_pri'])
    df.index = df['id']
    df['cites'] = df['cites'].apply(pd.to_numeric)
    
    writer = csv.writer(fout)
    grouped = df.groupby(['year', 'publication'])
    cnt_ignored = 0

    # beta: article related factor
    for name, group in grouped:
        '''
        annual_max = int(group['cites'].max())
        for record in group.itertuples():
            beta = 0.0 if annual_max in [-1, 0] or -1 == int(record[4]) \
                    else int(record[4]) / annual_max
            modified_row = [x for x in record[1:4]]
            modified_row.append(str(beta))
            modified_row.append(record[7])
            modified_row.append(record[5])
            writer.writerow(modified_row)
        '''

        if name[1] not in pub_dict:
            cnt_ignored += 1
            continue
        else:
            alpha = pub_dict[name[1]]
            annual_max = int(group['cites'].max())
            for record in group.itertuples():
                beta = 0.0 if annual_max in [-1, 0] or -1 == int(record[4]) \
                        else int(record[4]) / annual_max
                modified_row = [x for x in record[1:4]]
                modified_row.append(str(alpha * beta))
                modified_row.append(record[7])
                modified_row.append(record[5])
                writer.writerow(modified_row)

    print('{} out of {} ignored'.format(cnt_ignored, len(grouped)))

