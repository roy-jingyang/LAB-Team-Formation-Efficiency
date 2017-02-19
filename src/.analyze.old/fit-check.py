#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import csv
import numpy as np

from random import random
from scipy.stats import pearsonr
from scipy.stats import spearmanr
from scipy.optimize import curve_fit

def f_team_evaluation(xdata, w):
    x = xdata.T
    return w * x[0,:] + (1 - w) * x[1,:]

trainset = list()
with open(sys.argv[1], 'r') as ftrain:
    for row in csv.reader(ftrain):
        trainset.append(row)

trainset = np.array(trainset, np.float64)
print(trainset.shape)

popt, pconv = curve_fit(f_team_evaluation, 
        trainset[:,:2], trainset[:,2], p0=random(),
        bounds=(0, 1), method='trf', check_finite=True)

print(popt)
print(pconv)

testset = list()
with open(sys.argv[2], 'r') as ftest:
    for row in csv.reader(ftest):
        testset.append(row)

testset = np.array(testset, np.float64)
print(testset.shape)

print('Correlation between COL#1 (SKILL RELAVANT) & COL#3 (RATINGS):')
print('\tPearson correlation:\t', end='')
print(pearsonr(testset[:,0], testset[:,2]))
print('\tSpearsman correlation:\t', end='')
print(spearmanr(testset[:,0], testset[:,2]))

print('Correlation between COL#2 (SOCIAL RELATIONS RELEVANT) ' + \
        '& COL#3 (RATINGS):')
print('\tPearson correlation:\t', end='')
print(pearsonr(testset[:,1], testset[:,2]))
print('\tSpearsman correlation:\t', end='')
print(spearmanr(testset[:,1], testset[:,2]))

'''
weight = [float(sys.argv[2])]
weight.append(1 - weight[0])
weight = np.array(weight)

prediction = np.dot(testset[:,:2], weight)
'''

