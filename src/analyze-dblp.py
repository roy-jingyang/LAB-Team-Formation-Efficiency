#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import scipy
import math
import numpy as np
import csv
import networkx as nx
from collections import defaultdict
from scipy.stats import pearsonr, spearmanr
from scipy.optimize import curve_fit
from sklearn import preprocessing
from sklearn import linear_model

years = list()
ratings = list()
tags = list()
members = list()

te_years = list()
te_ratings = list()
te_tags = list()
te_members = list()

skillset = dict()
sociogram = dict()
params_byyear = dict()


# FILE IO
def load_data_all(fn, start, end):
    global years
    global ratings
    global tags
    global members

    with open(fn, 'r') as f:
        while True:
            id_title = f.readline()
            if '' == id_title:
                break
            else:
                year_ratings = f.readline().split(',')
                year = int(year_ratings[0])

                if year >= start and year < end:
                    years.append(year)
                    ratings.append(float(year_ratings[-1]))
                    tags.append([int(x) for x in f.readline().split(',')])
                    members.append([int(x) for x in f.readline().split(',')])
                else:
                    f.readline()
                    f.readline()


def load_data_test(fn ,te_start, te_end):
    global te_years
    global te_ratings
    global te_tags
    global te_members

    with open(fn, 'r') as f:
        while True:
            id_title = f.readline()
            if '' == id_title:
                break
            else:
                year_ratings = f.readline().split(',')
                year = int(year_ratings[0])

                if year >= te_start and year < te_end:
                    te_years.append(year)
                    te_ratings.append(float(year_ratings[-1]))
                    te_tags.append([int(x) for x in f.readline().split(',')])
                    te_members.append([int(x) 
                        for x in f.readline().split(',')])
                else:
                    f.readline()
                    f.readline()


# INIT
def init_containers(start, end):
    global skillset
    global sociogram
    global params_byyear

    skillset.clear()
    sociogram.clear()
    params_byyear.clear()

    for i in range(end - start):
        skillset[start + i] = defaultdict(
                lambda: [defaultdict(lambda: 0), defaultdict(lambda: 0)])
        sociogram[start + i] = defaultdict(
                lambda: defaultdict(lambda: [0, 0]))
        params_byyear[start + i] = np.random.random(2)


def build_skillset():
    global years
    global ratings
    global tags
    global members
    global skillset

    # foreach record
    for i in range(len(ratings)):
        year = years[i]
        # foreach member
        for j in range(len(members[i])): 
            member = members[i][j]
            for t in tags[i]:
                skillset[year][member][0][t] += 1
                skillset[year][member][1][t] += ratings[i]


def build_sociogram():
    global years
    global ratings
    global members
    global sociogram

    # foreach record
    for i in range(len(ratings)):
        year = years[i]
        N = len(members[i])
        # foreach pair of members
        for j in range(N - 1):
            p = members[i][j]
            for k in range(j + 1, N):
                q = members[i][k]
                sociogram[year][p][q][0] += 1
                sociogram[year][p][q][1] += ratings[i]
                sociogram[year][q][p][0] += 1
                sociogram[year][q][p][1] += ratings[i]



# CALC
def measure_skill_level(team, year, req_skills):
    global skillset

    wt_skills = [1 / len(req_skills)] * len(req_skills)
    team_skill_level = 0.0
    # foreach member
    for member in team:
        # foreach required skill
        for i in range(len(req_skills)):
            sk = req_skills[i]
            sk_sum = 0.0
            sk_cnt = 0
            # foreach year before
            for yb, v in skillset.items():
                if yb < year and v[member][0][sk] >= 1:
                    sk_sum += v[member][1][sk]
                    sk_cnt += v[member][0][sk]
                else:
                    pass
            team_skill_level += 0 if 0 == sk_cnt \
                    else sk_sum / sk_cnt * wt_skills[i]
    team_skill_level /= len(team) 
    return team_skill_level


def measure_skill_level1(team, year, req_skills):
    global skillset

    wt = 1 / len(req_skills)
    team_skill_level = 0.0
    for i in range(len(req_skills)):
        sk = req_skills[i]
        max_v = -1
        for member in team:
            sk_sum = 0.0
            sk_cnt = 0
            for yb, v in skillset.items():
                if yb < year and v[member][0][sk] >= 2:
                    sk_sum += v[member][1][sk]
                    sk_cnt += v[member][0][sk]
            if sk_cnt != 0:
                value = sk_sum / sk_cnt
                max_v = value if max_v < value else max_v

        max_v = 0 if max_v == -1 else max_v
        team_skill_level += wt * max_v
    return team_skill_level


def measure_coop_level0(team, year):
    global sociogram

    N = len(team)
    team_coop_level = 0.0
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        for j in range(i + 1, N):
            q = team[j]
            #p_cnt = 0
            #q_cnt = 0
            pq_sum = 0.0
            pq_cnt = 0
            # foreach year before
            for yb, v in sociogram.items():
                '''
                for value in v[p].values():
                    p_cnt += value[0]
                for value in v[q].values():
                    q_cnt += value[0]
                '''
                if yb < year:
                    if v[p][q][0] != 0:
                        pq_sum += v[p][q][1]
                        pq_cnt += v[p][q][0]
            team_coop_level += 0 if 0 == pq_cnt else pq_sum / pq_cnt
            #team_coop_level += 0 if pq_cnt == p_cnt + q_cnt else \
            #        pq_cnt / (p_cnt + q_cnt - pq_cnt)
    
    #team_coop_level /= N * (N - 1) / 2
    return team_coop_level


def measure_coop_level1(team, year):
    global sociogram

    graph = nx.Graph()
    N = len(team)
    #team_coop_level = 0.0
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        for j in range(i + 1, N):
            q = team[j]
            for yb, v in sociogram.items():
                if yb < year:
                    if v[p][q][0] > 0:
                        #graph.add_edge(p, q)
                        #graph.add_edge(p, q, weight=v[p][q][0])
                        graph.add_edge(p, q, weight=v[p][q][1] / v[p][q][0])

    #v_measure = list(nx.degree_centrality(graph).values())
    v_measure = list()
    for n, nbrs in graph.adjacency_iter():
        weight_deg = 0.0
        for nbr, attr in nbrs.items():
            weight_deg += attr['weight']
        v_measure.append(weight_deg)
    centralization = 0.0
    if len(v_measure) > 0:
        max_degree_centrality = max(v_measure)
        for i in range(len(v_measure)):
            centralization += max_degree_centrality - v_measure[i]
        centralization = centralization / (N - 2)
        
    team_coop_level = centralization
    return team_coop_level


def measure_coop_level(team, year):
    global sociogram

    graph = nx.Graph()
    N = len(team)
    team_coop_level = 0.0
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        for j in range(i + 1, N):
            q = team[j]
            for yb, v in sociogram.items():
                if yb < year:
                    if v[p][q][0] > 0:
                        graph.add_edge(p, q, weight=v[p][q][1] / v[p][q][0])

    mst = nx.minimum_spanning_edges(graph, data=True)
    for uvd in list(mst):
        team_coop_level += uvd[-1]['weight']
    return team_coop_level


# FIT PARAM
def obtain_params():
    global years
    global ratings
    global tags
    global members
    global params_byyear


    measured_skills = list()
    measured_coops = list()
    ratings_values = list()

    # foreach record in (start, end)
    # measure skill level & coop level
    starting_flag = True
    for i in range(len(ratings)):
        if starting_flag is False and years[i] != years[i - 1]:
            xdata = np.array([
                rescale(measured_skills.copy()),
                rescale(measured_coops.copy())],
                np.float64)
            ydata = rescale(ratings_values.copy())
            popt, pconv = curve_fit(f_team_evaluation,
                    xdata, ydata, p0=np.random.random(2),
                    method='trf', check_finite=True)
            params_byyear[years[i]] = [
                    popt[0] / (popt[0] + popt[1]),
                    popt[1] / (popt[0] + popt[1])#,
                    #popt[2]
                    ]
            '''
            clf = linear_model.LinearRegression()
            clf.fit(xdata.T, ydata)
            params_byyear[years[i]] = [
                    clf.coef_[0] / (clf.coef_[0] + clf.coef_[1]),
                    clf.coef_[1] / (clf.coef_[0] + clf.coef_[1])]
            '''

        if 0 != i and years[i] != years[i - 1]:
            starting_flag = False

        if starting_flag is True:
            pass
        else:
            measured_skills.append(
                    measure_skill_level(members[i], years[i], tags[i]))
            measured_coops.append(
                    measure_coop_level(members[i], years[i]))
            ratings_values.append(ratings[i])


# UTILITIES
def rescale(arr):
    l = len(arr)
    scaler = preprocessing.MinMaxScaler(feature_range=(0.1, 0.9))
    arr = np.array(arr, np.float64).reshape(-1, 1)
    return scaler.fit_transform(arr).reshape(l)


def f_team_evaluation(x, w1, w2):
    return w1 * x[0,:] + w2 * x[1,:] if x.ndim > 1 \
            else w1 * x[0] + w2 * x[1]
'''
def f_team_evaluation(x, w1, w2, c):
    return w1 * x[0,:] + w2 * x[1,:] + c if x.ndim > 1 \
            else w1 * x[0] + w2 * x[1] + c
'''


# wrapper for FUNCTION f_team_evaluation
def predict_measure(team_skill_levels, team_coop_levels, params, real_v, fn):
    prediction = list()
    real = list()

    team_skill_levels = rescale(team_skill_levels)
    team_coop_levels = rescale(team_coop_levels)
    
    for i in range(len(team_skill_levels)):
        prediction.append(f_team_evaluation(
            np.array([team_skill_levels[i], team_coop_levels[i]]),
            params[i][0], params[i][1]))
            #params[i][0], params[i][1], params[i][2]))
        real.append(real_v[i])

    measure_error(prediction, real, fn)


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
    # use evaluate script to help set the parameter
    auto_mode = True if sys.argv[1] == 'a' else False
    input_fn = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])
    te_start = int(sys.argv[5])
    te_end = int(sys.argv[6])
    top_pct = float(sys.argv[7]) if len(sys.argv) > 7 else None

    load_data_all(input_fn, start, end)
    print('Data loaded, {} in year [{}, {})'.format(len(ratings), start, end))
    print('\nWARNING:\tThe earliest year of all the records loaded currently' +
            ' is YEAR {}.'.format(start))
    print('\t\tDO NOT set a starting point <= YEAR {}'.format(start) + 
            ', in order to avoid bound error.\n')
    init_containers(start, end)
    print('\nContainers flushed.\n')

    build_skillset()
    build_sociogram()
    print('\nSkillset & Sociogram built.\n')

    if auto_mode:
        obtain_params()
        print('\nParameters (upto year) obtained.')
        print(params_byyear)

    load_data_test(input_fn, te_start, te_end)
    print('Test samples loaded, {} in year [{}, {})'.format(
        len(te_ratings), te_start, te_end))

    team_skill_levels = list()
    team_coop_levels = list()
    params = list()
    for i in range(len(te_ratings)):
        team_skill_levels.append(measure_skill_level(
                te_members[i], te_years[i], te_tags[i]))
        team_coop_levels.append(measure_coop_level(
                te_members[i], te_years[i]))
        params.append(params_byyear[te_years[i]])

    if auto_mode:
        print('\nAuto mode ON, presenting results of analysis.')
        print('\nFor ALL test samples:')
        print('Correlation between SKILL & ratings:')
        measure_correlation(team_skill_levels, te_ratings)
        print('Correlation between RELATIONS & ratings:')
        measure_correlation(team_coop_levels, te_ratings)
        predict_measure(team_skill_levels, team_coop_levels, params,
                te_ratings, 'all.txt')

        if top_pct is not None:
            idx_sorted_te_ratings = [x[0] for x in sorted(
                enumerate(te_ratings), key=lambda x: x[1], reverse=True)]
            del team_skill_levels[:]
            del team_coop_levels[:]
            del params[:]
            print('\nFor test samples with TOP-{:.0%} ratings:'.format(
                top_pct))
            top_n = math.floor(len(te_ratings) * top_pct)
            top_n_te_ratings = list()
            for j in range(top_n):
                i = idx_sorted_te_ratings[j]
                top_n_te_ratings.append(te_ratings[i])
                team_skill_levels.append(measure_skill_level(
                        te_members[i], te_years[i], te_tags[i]))
                team_coop_levels.append(measure_coop_level(
                        te_members[i], te_years[i]))
                params.append(params_byyear[te_years[i]])

            print('Correlation between SKILL & ratings:')
            measure_correlation(team_skill_levels, top_n_te_ratings)
            print('Correlation between RELATIONS & ratings:')
            measure_correlation(team_coop_levels, top_n_te_ratings)
            predict_measure(team_skill_levels, team_coop_levels, params,
                    top_n_te_ratings, 'TOP-{:.0%}.txt'.format(top_pct))

    else:
        print('Auto mode OFF. Check "out.csv".')
        team_skill_levels = rescale(team_skill_levels)
        team_coop_levels = rescale(team_coop_levels)
        te_ratings = rescale(te_ratings)
        with open('out.csv', 'w') as fout:
            writer = csv.writer(fout)
            for i in range(len(te_ratings)):
                writer.writerow([
                    team_skill_levels[i],
                    team_coop_levels[i],
                    te_ratings[i]])

