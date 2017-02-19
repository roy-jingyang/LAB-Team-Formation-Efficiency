#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import random
from bs4 import BeautifulSoup
from collections import defaultdict
import sys
import csv

BASE_URL = 'http://academic.research.microsoft.com/RankList'
parameters = {
        'entitytype': None,
        'topDomainID': 2,
        'subDomainID': 0,
        'last': 0,
        'start': None,
        'end': None,
        'orderby': None
        }

with open('ranklist_conferences.csv', 'w') as fout:
    parameters['entitytype'] = 3
    writer = csv.writer(fout)
    records = defaultdict(lambda: dict())

    for i in range(36):
        parameters['start'] = 100 * i + 1
        parameters['end'] = 100 * (i + 1)
        for order in [1, 6]:
            parameters['orderby'] = order
            
            r = requests.get(BASE_URL, params=parameters)
            soup = BeautifulSoup(r.text, 'lxml')
            if requests.codes.ok == r.status_code:
                data_table = soup.find('table', class_='staticTable').tbody
                for row in data_table.find_all('tr'):
                    title = row.find('td', 'rank-content').a.text
                    publication_count = row.find_all('td', \
                            'staticOrderCol')[0].text
                    k = title + '_' + publication_count

                    if 1 == order:
                        records[k]['title'] = title
                        records[k]['publication_count'] = \
                                int(publication_count)
                        citation_count = row.find_all('td', \
                                'staticOrderCol')[1].text
                        records[k]['citation_count'] = \
                                int(citation_count)
                    else:
                        field_rating = row.find_all('td', \
                                'staticOrderCol')[1].text
                        records[k]['field_rating'] = int(field_rating)
            else:
                pass

    for k, kv in records.items():
        writer.writerow([kv['title'], kv['publication_count'], \
                kv['citation_count'], kv['field_rating']])

