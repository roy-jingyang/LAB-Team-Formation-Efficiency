#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import sys
import datetime
import numpy as np
import networkx as nx
from collections import defaultdict
from copy import deepcopy
from random import shuffle
from math import log, log2
from scipy.stats import pearsonr, spearmanr
from sklearn import preprocessing

data_train = dict()
data_test = dict()
skillset = defaultdict(lambda: defaultdict(lambda: [0, 0]))
sociogram = defaultdict(lambda: defaultdict(lambda: [0, 0]))
G = nx.Graph()

def retrieve(fn, split=0.7):
    global data_train
    global data_test

    records = defaultdict(lambda: defaultdict(lambda: list()))
    keys = list()
    with open(fn, 'r') as fin:
        pass_header = False
        for row in csv.reader(fin):
            if pass_header:
            #if pass_header and row[4] in ['Variant 1', 'Variant 2']:
                case_id = row[0]
                if case_id not in records:
                    keys.append(case_id)
                records[case_id]['time'].append(datetime.datetime.strptime(
                        row[3], '%Y/%m/%d %X'))
                records[case_id]['execute'].append((row[1], row[2]))
            else:
                pass_header = True

    # obtain ratings
    rm_keys = list()
    for case_id in records.keys():
        duration = records[case_id]['time'][-1] - records[case_id]['time'][0]
        if duration.total_seconds() == 0:
            rm_keys.append(case_id)
        else:
            records[case_id]['ratings'] = 1 / log(duration.total_seconds())

    for k in rm_keys:
        del records[k]
        keys.remove(k)

    shuffled_keys = keys

    total_length = len(shuffled_keys)
    train_length = int(total_length * split)
    print('Train: {}'.format(train_length))
    print('Test: {}'.format(total_length - train_length))

    for case_id in shuffled_keys[:train_length]:
        data_train[case_id] = deepcopy(records[case_id])
    for case_id in shuffled_keys[train_length:]:
        data_test[case_id] = deepcopy(records[case_id])


# generate skillset info
def gen_skillset():
    global data_train
    global skillset

    for case_id in data_train.keys():
        ratings = data_train[case_id]['ratings']
        for activity, actor in data_train[case_id]['execute']:
            skillset[actor][activity][0] += 1
            skillset[actor][activity][1] += ratings


# generate sociogram info
def gen_sociogram():
    global data_train
    global sociogram
    global G

    for case_id in data_train.keys():
        ratings = data_train[case_id]['ratings']
        participators = list()
        for activity, actor in data_train[case_id]['execute']:
            participators.append(actor)
        for i in range(len(participators) - 1):
            u = participators[i]
            for j in range(i + 1, len(participators)):
                v = participators[j]
                sociogram[u][v][0] += 1
                sociogram[u][v][1] += ratings
                sociogram[v][u][0] += 1
                sociogram[v][u][1] += ratings
    # ADD
    for u, d in sociogram.iter():
        for v, values in d.iter():
            G.add_edge(u, v, values[1] / values[0])
    sociogram.clear()


# COPY here the evaluation program
def measure_skill_level(team, req_skills):
    global skillset

    wt = 1 / len(req_skills)
    team_skill_level = 0.0
    for sk in req_skills:
        max_v = -1
        for member in team:
            if skillset[member][sk][0] > 0:
                v = skillset[member][sk][1] / skillset[member][sk][0]
                max_v = v if max_v < v else max_v
        max_v = 0 if max_v == -1 else max_v
        team_skill_level += wt * max_v
    '''
    for member in team:
        for sk in req_skills:
            if skillset[member][sk][0] > 0:
                team_skill_level += skillset[member][sk][1] / \
                        skillset[member][sk][0] * wt
    '''
    return team_skill_level


def measure_coop_level(team):
    '''
    global sociogram

    N = len(team)
    team_coop_level = 0
    for i in range(N - 1):
        u = team[i]
        for j in range(i + 1, N):
            v = team[j]
            if sociogram[u][v][0] > 0:
                team_coop_level += sociogram[u][v][1] / sociogram[u][v][0]

    return team_coop_level / (N * (N - 1) / 2)
    '''
    global G



def rescale(arr):
    l = len(arr)
    scaler = preprocessing.MinMaxScaler(feature_range=(0.1, 0.9))
    arr = np.array(arr, np.float64).reshape(-1, 1)
    return scaler.fit_transform(arr).reshape(l)


def measure_correlation(arr_left, arr_right):
    print('\tPearson correlation:\t', end='')
    print(pearsonr(arr_left, arr_right))
    print('\tSpearman correlation:\t', end='')
    print(spearmanr(arr_left, arr_right))


def measure_error(arr_prediction, arr_real, fn_output=None):
    arr_prediction = rescale(arr_prediction)
    arr_real = rescale(arr_real)

    print('Mean value of prediction:\t{}'.format(np.mean(arr_prediction)))
    print('Mean value of real:\t\t{}'.format(np.mean(arr_real)))
    print('[Mean of difference]\t\t{}'.format(np.mean(arr_prediction -
        arr_real)))
    print('[SD of difference]\t\t{}'.format(np.std(arr_prediction - 
        arr_real)))

    error = np.fabs(arr_prediction - arr_real)
    print('Mean TEST error by abs():\t\t{:.5}'.format(np.mean(error)))
    error_pct = error / arr_real
    print('Mean error rate:\t\t{:.2%}'.format(np.mean(error_pct)))
    if fn_output is not None:
        with open(fn_output, 'w') as fout:
            writer = csv.writer(fout)
            for i in range(len(error)):
                writer.writerow([arr_real[i], arr_prediction[i],
                error[i]])


if __name__ == '__main__':
    retrieve(sys.argv[1])
    gen_skillset()
    gen_sociogram()

    team_skill_levels = list()
    team_coop_levels = list()
    real = list()

    if sys.argv[2] == 'train':
        # TRAINING
        for case_id in data_train.keys():
            req_skills = list()
            team = list()
            for activity, actor in data_train[case_id]['execute']:
                req_skills.append(activity)
                team.append(actor)
            v_skill = measure_skill_level(team, req_skills)
            v_coop = measure_coop_level(team)
            team_skill_levels.append(v_skill)
            team_coop_levels.append(v_coop)
            real.append(data_train[case_id]['ratings'])

    elif sys.argv[2] == 'test':
        # TESTING
        for case_id in data_test.keys():
            req_skills = list()
            team = list()
            for activity, actor in data_test[case_id]['execute']:
                req_skills.append(activity)
                team.append(actor)
            v_skill = measure_skill_level(team, req_skills)
            v_coop = measure_coop_level(team)
            team_skill_levels.append(v_skill)
            team_coop_levels.append(v_coop)
            real.append(data_test[case_id]['ratings'])

        print('Correlation skill')
        measure_correlation(team_skill_levels, real)
        print('Correlation coop')
        measure_correlation(team_coop_levels, real)

    team_skill_levels = rescale(team_skill_levels)
    team_coop_levels = rescale(team_coop_levels)
    real = rescale(real)

    with open('out.csv', 'w') as fout:
        writer = csv.writer(fout)
        for i in range(len(real)):
            writer.writerow([
                team_skill_levels[i], team_coop_levels[i], real[i]])

    if sys.argv[2] == 'test':
        # TESTING
        weight1 = float(sys.argv[3])
        weight2 = float(sys.argv[4])
        predict = list()
        for i in range(len(real)):
            predict.append(weight1 * team_skill_levels[i] +
                    weight2 * team_coop_levels[i])
        measure_error(predict, real)

