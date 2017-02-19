#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
import requests
import re
import time
from bs4 import BeautifulSoup

cursor = 0
start_pos = int(sys.argv[2])

with open(sys.argv[1], 'r') as fin, open(sys.argv[3], 'a') as fout:
    reader = csv.reader(fin)
    writer = csv.writer(fout)
    for row in reader:
        cursor += 1
        if cursor < start_pos:
            print('LINE {} IGNORED'.format(cursor))
            continue
        else:
            print('LINE {}: {}, {}'.format(cursor, row[0], row[1]), end='')
            url = row[-1]
            custom_headers = {
                    'Accept': 'text/html,application/xhtml+xml,' +
                    'application/xml;q=0.9,image/webp,*/*;q=0.8',

                    'Accept-Encoding': 'gzip, deflate. sdch',

                    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',

                    'Cache-control': 'max-age=0',

                    'Connection': 'close',

                    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) ' + 
                    'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                    'Chrome/51.0.2704.63 Safari/537.36'
                    }
            r = requests.get(url, headers=custom_headers)
            if 200 == r.status_code:
                html = r.text
                soup = BeautifulSoup(html, 'lxml')

                citation_keywords = soup.head.find('meta', \
                        attrs={'name': 'citation_keywords'})
                if citation_keywords is None:
                    keywords = []
                else:
                    keywords = [w.lstrip() for w \
                            in citation_keywords['content'].split(';')]

                patt_edh = re.compile('<a class="boxedh"' + \
                        ' href="[?.=&/\w]+">[\s\w]+</a>')
                patt_edl = re.compile('<a class="boxedl"' + \
                        ' href="[?.=&/\w]+">[\s\w]+</a>')

                a_edh = patt_edh.findall(soup.head.text)
                patt_terms = re.compile('>[.,;\s\w]+</a>')

                terms_edh = list()
                for a in a_edh:
                    match = patt_terms.search(a)
                    terms_edh.append(a[match.start()+1:match.end()-4])

                a_edl = patt_edl.findall(soup.head.text)
                terms_edl = list()
                for a in a_edl:
                    match = patt_terms.search(a)
                    terms_edl.append(a[match.start()+1:match.end()-4])

                newrow = list(row[:-1])
                if len(keywords) > 0:
                    keywords = '|'.join(keywords)
                    keywords.replace('\n', '')
                else:
                    keywords = ''
                if len(terms_edh) > 0:
                    terms_edh = '|'.join(terms_edh)
                    terms_edh.replace('\n', '')
                else:
                    terms_edh = ''
                if len(terms_edl) > 0:
                    terms_edl = '|'.join(terms_edl)
                    terms_edl.replace('\n', '')
                else:
                    terms_edl = ''

                newrow.extend([keywords, terms_edh, terms_edl])
                writer.writerow(newrow)

                print('\t\t... DONE SUCCESSFULLY.')
                time.sleep(3)
            else:
                print('\t\t... FAILED (status not ok).')
                print('{}\t{}'.format(r.status_code, r.url))

