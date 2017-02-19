#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import requests

from bs4 import BeautifulSoup
from collections import defaultdict
from time import sleep
from random import randint

base_uri = 'http://apps.webofknowledge.com'

custom_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;' +
        'q=0.9,image/webp,*/*;q=0.8',

        'Accept-Encoding': 'gzip, deflate. sdch',

        'Accept-Language': 'en;q=0.6',

        'Cache-control': 'max-age=0',


        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' +
        '(KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
        }

'''
        'colName': 'WOS',
        'formValue(summary_mode)': 'GeneralSearch',
        'update_back2search_link_param': 'yes',
'''
payload = {
        'product': 'WOS',
        'search_mode': 'GeneralSearch',
        'SID': None,
        'page': None,
        'doc': None,
        'qid': None
        }


term_query = {
        'InformationRetrieval': {
            'page_count': 1251,
            'doc_count': 12505
            },
        'DocumentRetrieval': {
            'page_count': 449,
            'doc_count': 4486
            },
        'DataRetrieval': {
            'page_count': 746,
            'doc_count': 7454
            },
        'ImageRetrieval': {
            'page_count': 653,
            'doc_count': 6528
            },
        'TextRetrieval': {
            'page_count': 340,
            'doc_count': 3399
            },
        'Content-basedRetrieval': {
            'page_count': 141,
            'doc_count': 1409
            },
        'QueryProcessing': {
            'page_count': 737,
            'doc_count': 7367
            },
        'DatabaseQuery': {
            'page_count': 848,
            'doc_count': 8480
            },
        'QueryLanguages': {
            'page_count': 441,
            'doc_count': 4402
            },
        'RelevanceFeedback': {
            'page_count': 133,
            'doc_count': 1329
            }
        }

def fetch_page_info(html):
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find('div', 'l-content')

    title = content.find('div', 'title').value.get_text().replace('\n', '')

    page_info = defaultdict(lambda: None)
    page_info['title'] = title

    print(title)

    fr_fields = content.find_all('p', 'FR_field')

    for fr_field in fr_fields:
        fr_label = fr_field.find('span', 'FR_label')
        if fr_label is None:
            pass
        else:
            label_text = fr_label.get_text().strip()
            if label_text == 'DOI:':
                page_info['doi'] = fr_field.find('value').get_text()
            elif label_text == 'Published:':
                page_info['date'] = fr_field.find('value').get_text()
                #print(date)
            elif label_text == 'KeyWords Plus:':
                page_info['keywords'] = list()
                for a in fr_field.find_all('a'):
                    page_info['keywords'].append(a.get_text())
                #print(keywords)
            elif label_text == 'E-mail Addresses:':
                page_info['email_addr'] = list()
                for a in fr_field.find_all('a'):
                    page_info['email_addr'].append(a.get_text())
                #print(email_addr)
            elif label_text == \
                    'Times Cited in Web of Science Core Collection:':
                page_info['citation_count'] = \
                        int(fr_field.find('a').get_text())
                #print(citation_count)
            else:
                pass

    if page_info['doi'] is None:
        page_info['doi'] = ''
    if page_info['date'] is None:
        page_info['date'] = ''
    info = (
            page_info['title'],
            page_info['doi'],
            page_info['date'],
            '|'.join(page_info['keywords']),
            '|'.join(page_info['email_addr']),
            page_info['citation_count'])

    if any(val is None for val in info):
        print('Failed. Record not complete.')
        return None
    else:
        print('Succeeded.')
        return info


if __name__ == '__main__':
    area_term = sys.argv[1]
    payload['SID'] = sys.argv[2]
    payload['qid'] = int(sys.argv[3])
    starting_count = int(sys.argv[4]) if len(sys.argv) > 4 else 0

    if area_term not in term_query:
        exit('Wrong term of area given')

    # Init
    payload['page'] = 1
    payload['doc'] = 1
    data_rows = list()
    cnt = 0

    with open(area_term + '.csv', 'a') as fout, \
            open(area_term + '1.log', 'a') as flog1, \
            open(area_term + '2.log', 'a') as flog2:
        writer = csv.writer(fout)
        flog1.write('ERROR_PAGE_REQUEST\n')
        flog2.write('ERROR_PAGE_PARSING\n')

        for count in range(starting_count, term_query[area_term]['doc_count']):
            t = randint(2, 10)
            sleep(t)
            print('{}\t'.format(count + 1), end='')
            payload['doc'] = count + 1
            payload['page'] = int(count / 10) + 1
            r = requests.get(base_uri + '/full_record.do',
                    params=payload, headers=custom_headers)

            if 200 == r.status_code:
                try: 
                    fetched = fetch_page_info(r.text)
                    if fetched is not None: 
                        data_rows.append(fetched)
                        cnt += 1
                except:
                    print('Failed. Unable to parse requested page.')
                    flog2.write('{}\t'.format(count + 1) + r.url + '\n')
            else:
                print(r.status_code)
                print('Failed. Unable to request page.')
                flog1.write('{}\t'.format(count + 1) + r.url + '\n')

            if len(data_rows) % 20 == 0:
                writer.writerows(data_rows)
                del data_rows[:]

        if len(data_rows) > 0:
            writer.writerows(data_rows)

    print('{} / {} fetched.'.format(cnt, term_query[area_term]['doc_count']))

