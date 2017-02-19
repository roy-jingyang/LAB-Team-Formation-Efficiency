#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from time import sleep
from selenium import webdriver

driver = '/home/yjingasd/Downloads/chromedriver'
os.environ['webdriver.chrome.driver'] = driver
browser = webdriver.Chrome(driver)
browser.get('https://cn.aminer.org/ranks/conf')

sleep(10)
rows = browser.find_elements(webdriver.common.by.By.TAG_NAME, 'tr')

print(len(rows))

records = list()
for elem in rows[1:]:
    row = list()
    for td in elem.find_elements_by_tag_name('td')[1:]:
        row.append(td.text)
    records.append(row)

with open('PUB-CONF-H5INDEX.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(records)

