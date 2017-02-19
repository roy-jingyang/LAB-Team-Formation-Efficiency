#!/usr/env/bin python3

import sys
import numpy as np
from collections import defaultdict
from math import exp


''' Define global variables '''
tr_movie_num = list()
te_movie_num = list()

tr_movie_info = list()
te_movie_info = list()

tr_movie_ratings = list()
tr_movie_genres = list()
tr_movie_members = list()

te_movie_ratings = list()
te_movie_genres = list()
te_movie_members = list()

skillset_directors = defaultdict(lambda: [[0] * 29, [0] * 29])
skillset_actors = defaultdict(lambda: [[0] * 29, [0] * 29])
sociogram = defaultdict(lambda: defaultdict(lambda: [0, 0]))

''' end definition '''

def load_data_from_file(fn, tr_start, tr_end, te_start, te_end):
    global tr_movie_num
    global te_movie_num

    global tr_movie_info
    global te_movie_info

    global tr_movie_ratings
    global tr_movie_genres
    global tr_movie_members

    global te_movie_ratings
    global te_movie_genres
    global te_movie_members

    with open(fn, 'r') as f:
        while True:
            movie_num_nm = f.readline()
            if movie_num_nm is None or '' == movie_num_nm:
                break
            else:
                movie_num_nm = movie_num_nm.split(',')
                year_count_ratings = f.readline().split(',')
                year = int(year_count_ratings[0])
                count = int(year_count_ratings[1])
                ratings = float(year_count_ratings[2])
                genres = [int(x) for x in f.readline().split(',')]
                members = [int(x) for x in f.readline().split(',')]

                if year >= tr_start and year < tr_end:
                    tr_movie_num.append(int(movie_num_nm[0]))
                    tr_movie_info.append([movie_num_nm[1], year])
                    tr_movie_ratings.append(ratings)
                    tr_movie_genres.append(genres)
                    tr_movie_members.append(members)

                if year >= te_start and year < te_end:
                    te_movie_num.append(int(movie_num_nm[0]))
                    te_movie_info.append([movie_num_nm[1], year])
                    te_movie_ratings.append(ratings)
                    te_movie_genres.append(genres)
                    te_movie_members.append(members)


def init_skillset():
    global tr_movie_ratings
    global tr_movie_genres
    global tr_movie_members
    global skillset_directors
    global skillset_actors

    for k in range(len(tr_movie_members)):
        for i in range(len(tr_movie_members[k])):
            member = tr_movie_members[k][i]
            if 0 == i:
                for g in tr_movie_genres[k]:
                    skillset_directors[member][0][g] += 1
                    skillset_directors[member][1][g] += tr_movie_ratings[k]
            else:
                for g in tr_movie_genres[k]:
                    skillset_actors[member][0][g] += 1
                    skillset_actors[member][1][g] += tr_movie_ratings[k]


def init_sociogram():
    global tr_movie_ratings
    global tr_movie_members
    global sociogram
    
    for k in range(len(tr_movie_members)):
        N = len(tr_movie_members[k])
        for i in range(N - 1):
            u = tr_movie_members[k][i]
            for j in range(i + 1, N):
                v = tr_movie_members[k][j]
                sociogram[u][v][0] += 1
                sociogram[u][v][1] += tr_movie_ratings[k]
                sociogram[v][u][0] += 1
                sociogram[v][u][1] += tr_movie_ratings[k]


def measure_skill_level(team, req_skills):
    global skillset_directors
    global skillset_actors

    wt_skills = [1 / len(req_skills)] * len(req_skills)
    team_skill_level = 0
    for i in range(len(team)):
        member = team[i]
        if 0 == i:
            for j in range(len(req_skills)):
                sk = req_skills[j]
                if skillset_directors[member][0][sk] >= 1:
                    team_skill_level += skillset_directors[member][1][sk] / \
                            skillset_directors[member][0][sk] * wt_skills[j]
                else:
                    pass
        else:
            for j in range(len(req_skills)):
                sk = req_skills[j]
                if skillset_actors[member][0][sk] >= 1:
                    team_skill_level += skillset_actors[member][1][sk] / \
                            skillset_actors[member][0][sk] * wt_skills[j]
                else:
                    pass

    return team_skill_level / len(team)


def measure_collaboration_level(team):
    global sociogram
    team_size = len(team)
    N = len(team)
    team_collaboration_level = 0
    for i in range(N - 1):
        u = team[i]
        for j in range(i + 1, N):
            v = team[j]
            if sociogram[u][v][0] == 0:
                pass
            else:
                team_collaboration_level += sociogram[u][v][1] / \
                        sociogram[u][v][0]

    return team_collaboration_level / (team_size * (team_size - 1) / 2)


def normalize(nparr):
    return 1 + \
            9 * ((nparr - np.amin(nparr)) / (np.amax(nparr) - np.amin(nparr)))
    #return (nparr - np.amin(nparr)) / (np.amax(nparr) - np.amin(nparr))


if __name__ == '__main__':
    input_filename = sys.argv[1]
    tr_start = int(sys.argv[2])
    tr_end = int(sys.argv[3])
    te_start = int(sys.argv[4])
    te_end = int(sys.argv[5])

    load_data_from_file(input_filename, tr_start, tr_end, te_start, te_end)
    print('Input data successfully loaded.')

    # TRAINING
    init_skillset()
    '''
    # evaluate individual skill set
    skillset_total = defaultdict(lambda: [0] * 29)
    for p, l_sk in skillset_directors.items():
        for g in range(29):
            if l_sk[0][g] >= 1:
                skillset_total[p][g] += 1
    for p, l_sk in skillset_actors.items():
        for g in range(29):
            if l_sk[0][g] >= 2:
                skillset_total[p][g] += 1
    cnt_individual_skills = 0
    for p, l_sk in skillset_total.items():
        for g in l_sk:
            if g > 0:
                cnt_individual_skills += 1
    print('Avg # of Skills per Individual: {}'.format(cnt_individual_skills / \
            len(skillset_total)))
    '''
    # evaluate individual skill set

    init_sociogram()

    # TESTING
    index_skill_level = list()
    index_collaboration_level = list()
    for t in range(len(te_movie_ratings)):
        required_skills = te_movie_genres[t]
        team = te_movie_members[t]
        index_skill_level.append(measure_skill_level(team, required_skills))
        index_collaboration_level.append(measure_collaboration_level(team))
    
    # TODO
    te_samples_idx = list()
    cnt_missing_sk_level = 0
    cnt_missing_co_level = 0
    for i in range(len(index_skill_level)):
        if index_skill_level[i] == 0.0 or index_collaboration_level[i] == 0.0:
            if index_skill_level[i] == 0.0:
                cnt_missing_sk_level += 1
            if index_collaboration_level[i] == 0.0:
                cnt_missing_co_level += 1
        else:
            te_samples_idx.append(i)

    print('Generating test data')
    print('\nSkill level: {} / {} ({}%)'.format(cnt_missing_sk_level,
        len(index_skill_level),
        cnt_missing_sk_level / len(index_skill_level) * 100))
    print('\nCollaboration level: {}/{} ({}%)'.format(cnt_missing_co_level,
        len(index_collaboration_level),
        cnt_missing_co_level / len(index_collaboration_level) * 100))

    print('\nLeft with: {}'.format(len(te_samples_idx)))
    index_skill_level = normalize(index_skill_level)
    index_collaboration_level = normalize(index_collaboration_level)
    te_movie_ratings = normalize(te_movie_ratings)

    output_filename = 'tr{}-{}_te{}-{}.csv'.format(tr_start, tr_end,
            te_start, te_end)
    with open(output_filename, 'w') as outf:
        for i in te_samples_idx:
            outf.write('{},{},{}\n'.format(
                index_skill_level[i],
                index_collaboration_level[i],
                te_movie_ratings[i]))

