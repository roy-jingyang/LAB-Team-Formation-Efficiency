#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import scipy
import math
import numpy as np
import csv
import networkx as nx
from collections import defaultdict
from scipy.optimize import curve_fit
from scipy.stats import pearsonr, spearmanr
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

skillset_dir = dict()
skillset_act = dict()
sociogram = dict()
params_byyear = dict()

def load_data_all(fn, start, end):
    global years
    global ratings
    global tags
    global members
    '''
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
    '''
    is_header_line = True
    with open(fn, 'r') as f:
        while True:
            line = f.readline()
            if is_header_line:
                is_header_line = False
            elif line is not '':
                row = line.strip().split('\t')
                # id, year, ratings, members, size(members), genres
                year = int(row[1])
                if year >= start and year < end:
                    years.append(year)
                    ratings.append(float(row[2]))
                    #tags.append([int(x) for x in row[-1][1:-1].split(',')])
                    members.append([int(x) for x in row[-3][1:-1].split(',')])
            else:
                break


def load_data_test(fn ,te_start, te_end):
    global te_years
    global te_ratings
    global te_tags
    global te_members
    '''
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
    '''
    is_header_line = True
    with open(fn, 'r') as f:
        while True:
            line = f.readline()
            if is_header_line:
                is_header_line = False
            elif line is not '':
                row = line.strip().split('\t')
                # id, year, ratings, members, size(members), genres
                year = int(row[1])
                if year >= te_start and year < te_end:
                    te_years.append(year)
                    te_ratings.append(float(row[2]))
                    #te_tags.append([int(x) for x in row[-1][1:-1].split(',')])
                    te_members.append([int(x) 
                        for x in row[-3][1:-1].split(',')])
            else:
                break


def init_containers(start, end):
    #global skillset_dir
    #global skillset_act
    global sociogram
    global params_byyear

    sociogram.clear()
    params_byyear.clear()

    for i in range(end - start):
        #skillset_dir[start + i] = defaultdict(
        #        lambda: [defaultdict(lambda: 0), defaultdict(lambda: 0)])
        #skillset_act[start + i] = defaultdict(
        #        lambda: [defaultdict(lambda: 0), defaultdict(lambda: 0)])
        sociogram[start + i] = defaultdict(
                lambda: defaultdict(lambda: [0, 0]))
        params_byyear[start + i] = np.random.random(2)


def build_skillset():
    global years
    global ratings
    global tags
    global members
    global skillset_dir
    global skillset_act

    # foreach record
    for i in range(len(ratings)):
        year = years[i]
        # foreach member
        for j in range(len(members[i])): 
            member = members[i][j]
            if 0 == j:
                for t in tags[i]:
                    skillset_dir[year][member][0][t] += 1
                    skillset_dir[year][member][1][t] += ratings[i]
            else:
                for t in tags[i]:
                    skillset_act[year][member][0][t] += 1
                    skillset_act[year][member][1][t] += ratings[i]


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


def measure_skill_level(team, year, req_skills):
    global skillset_dir
    global skillset_act

    wt_skills = [1 / len(req_skills)] * len(req_skills)
    team_skill_level = 0.0
    # foreach member
    for j in range(len(team)):
        member = team[j]
        if 0 == j:
            # foreach required skill
            for i in range(len(req_skills)):
                sk = req_skills[i]
                sk_sum = 0.0
                sk_cnt = 0
                # foreach year before
                for yb, v in skillset_dir.items():
                    if yb < year and v[member][0][sk] >= 1:
                        sk_sum += v[member][1][sk]
                        sk_cnt += v[member][0][sk]
                    else:
                        pass
                team_skill_level += 0 if 0 == sk_cnt \
                        else sk_sum / sk_cnt * wt_skills[i]
        else:
            # foreach required skill
            for i in range(len(req_skills)):
                sk = req_skills[i]
                sk_sum = 0.0
                sk_cnt = 0
                # foreach year before
                for yb, v in skillset_act.items():
                    if yb < year and v[member][0][sk] >= 1:
                        sk_sum += v[member][1][sk]
                        sk_cnt += v[member][0][sk]
                    else:
                        pass
                team_skill_level += 0 if 0 == sk_cnt \
                        else sk_sum / sk_cnt * wt_skills[i]


    return team_skill_level / len(team)


# Density
def measure_coop_level(team, year):
    global sociogram

    N = len(team)
    team_coop_level = 0.0
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        for j in range(i + 1, N):
            q = team[j]
            pq_sum = 0.0
            pq_cnt = 0
            # foreach year before
            for yb, v in sociogram.items():
                if yb < year:
                    if v[p][q][0] != 0:
                        pq_sum += v[p][q][1]
                        pq_cnt += v[p][q][0]
            team_coop_level += 0 if 0 == pq_cnt else pq_sum / pq_cnt
    
    team_coop_level /= N * (N - 1) / 2
    return team_coop_level

# Cc-R (Graph diameter, i.e. longest shorted path length)
def measure_coop_level0(team, year):
    global sociogram

    graph = nx.Graph()
    N = len(team)
    team_coop_level = 0.0
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        graph.add_node(p)
        for j in range(i + 1, N):
            q = team[j]
            graph.add_node(q)
            for yb, v in sociogram.items():
                if yb < year:
                    if v[p][q][0] > 0:
                        graph.add_edge(p, q, 
                                weight=(10 - v[p][q][1] / v[p][q][0]))
    if nx.number_of_nodes(graph) == 0:
        return -1
    if nx.is_connected(graph) == False:
        return -1
    shortest_path_lengths = nx.shortest_path_length(graph, weight='weight')
    diameter = -1
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        for j in range(i + 1, N):
            q = team[j]
            if shortest_path_lengths[p][q] > diameter:
                diameter = shortest_path_lengths[p][q]
    team_coop_level = diameter
    return team_coop_level


# Cc-Steiner (Sum of edges of MST)
def measure_coop_level1(team, year):
    global sociogram

    graph = nx.Graph()
    N = len(team)
    team_coop_level = 0.0
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        graph.add_node(p)
        for j in range(i + 1, N):
            q = team[j]
            graph.add_node(q)
            for yb, v in sociogram.items():
                if yb < year:
                    if v[p][q][0] > 0:
                        graph.add_edge(p, q,
                                weight=(10 - v[p][q][1] / v[p][q][0]))
    if nx.number_of_nodes(graph) == 0:
        return -1
    if nx.is_connected(graph) == False:
        return -1
    mse = nx.minimum_spanning_edges(graph, data=True)
    for uvd in list(mse):
        team_coop_level += uvd[-1]['weight']
    return team_coop_level


# Cc-SD (Shortest Distance)
def measure_coop_level2(team, year):
    global sociogram

    graph = nx.Graph()
    N = len(team)
    team_coop_level = 0.0
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        graph.add_node(p)
        for j in range(i + 1, N):
            q = team[j]
            graph.add_node(q)
            for yb, v in sociogram.items():
                if yb < year:
                    if v[p][q][0] > 0:
                        graph.add_edge(p, q,
                                weight=(10 - v[p][q][1] / v[p][q][0]))
    if nx.number_of_nodes(graph) == 0:
        return -1
    if nx.is_connected(graph) == False:
        return -1
    shortest_path_lengths = nx.shortest_path_length(graph, weight='weight')
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        for j in range(i + 1, N):
            q = team[j]
            team_coop_level += shortest_path_lengths[p][q]
    return team_coop_level


# Cc-LD (Leader Distance)
def measure_coop_level3(team, year):
    global sociogram

    graph = nx.Graph()
    N = len(team)
    team_coop_level = 0.0
    # foreach pair of members
    for i in range(N - 1):
        p = team[i]
        graph.add_node(p)
        for j in range(i + 1, N):
            q = team[j]
            graph.add_node(q)
            for yb, v in sociogram.items():
                if yb < year:
                    if v[p][q][0] > 0:
                        graph.add_edge(p, q,
                                weight=(10 - v[p][q][1] / v[p][q][0]))
    if nx.number_of_nodes(graph) == 0:
        return -1
    if nx.is_connected(graph) == False:
        return -1
    shortest_path_lengths = nx.shortest_path_length(graph, weight='weight')
    leader_distances = list()
    for member, qd in shortest_path_lengths.items():
        leader_distances.append((member, sum([v for k, v in qd.items()])))
    leader = min(leader_distances, key=lambda x: x[1])
    team_coop_level = leader[1]
    return team_coop_level


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
    # TODO
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
                    popt[1] / (popt[0] + popt[1])
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


def rescale(arr):
    l = len(arr)
    scaler = preprocessing.MinMaxScaler(feature_range=(1, 10))
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
    print('[SD of difference]\t\t{}'.format(np.std(arr_prediction - 
        arr_real)))

    error = np.fabs(arr_prediction - arr_real)
    if fn_output is not None:
        with open(fn_output, 'w') as fout:
            writer = csv.writer(fout)
            for i in range(len(error)):
                writer.writerow([arr_real[i], arr_prediction[i],
                error[i]])
    print('Mean TEST error by abs():\t\t{:.5}'.format(np.mean(error)))
    error_pct = error / arr_real
    print('Mean error rate:\t\t{:.2%}'.format(np.mean(error_pct)))


if __name__ == '__main__':
    # use evaluate script to help set the parameter
    if sys.argv[1] in ['a', 'm']:
        auto_mode = True if sys.argv[1] == 'a' else False
    else:
        exit('Mode: [a]uto / [m]anual')
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

    #build_skillset()
    build_sociogram()
    #print('\nSkillset & Sociogram built.\n')
    print('\nSociogram built.\n')

    if auto_mode:
        obtain_params()
        print('\nParameters (upto year) obtained.')
        print(params_byyear)

    load_data_test(input_fn, te_start, te_end)
    print('Test samples loaded, {} in year [{}, {})'.format(
        len(te_ratings), te_start, te_end))

    #team_skill_levels = list()
    team_coop_levels = list()
    params = list()
    for i in range(len(te_ratings)):
        #team_skill_levels.append(measure_skill_level(
        #        te_members[i], te_years[i], te_tags[i]))
        team_coop_levels.append(measure_coop_level3(
                te_members[i], te_years[i]))
        if auto_mode:
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
                team_coop_levels.append(measure_coop_level3(
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
        #team_skill_levels = rescale(team_skill_levels)
        #team_coop_levels = rescale(team_coop_levels)
        #te_ratings = rescale(te_ratings)
        with open('out.csv', 'w') as fout:
            writer = csv.writer(fout)
            for i in range(len(te_ratings)):
                writer.writerow([
                    #team_skill_levels[i],
                    team_coop_levels[i],
                    te_ratings[i]])
        print('end')
        exit()

