#! /usr/env/bin python3

import sys
import numpy as np
from collections import defaultdict, Counter

if __name__ == '__main__':
    cnt = 0
    
    cnt_teams = 0
    cnt_undersize_teams = 0
    cnt_individuals = Counter()
    '''
    distr_movie_num = dict()

    cnt_directors = dict()
    cnt_actors = dict()
    distr_movie_director = dict()
    distr_movie_actor = dict()
    '''

    distr_team_size = Counter()
    sociogram = defaultdict(lambda: defaultdict(lambda: 0))
    distr_coop_times = Counter()
    individuals = set()

    '''
    distr_task_skills = dict()

    sociogram = defaultdict(lambda: defaultdict(lambda: 0))

    cnt_movie_genres = 0

    skills = set()
    '''

    is_header_line = True
    with open(sys.argv[1], 'r') as f:
        '''
        for line in f:
            if is_header_line:
                is_header_line = False
            else:
                row = line.split('\t')
                # id, year, score, team, teamsize
                members = row[3][1:-1].split(',')
        '''
        while True:
            movie = f.readline()
            if not movie:
                break
            else:
                f.readline()
                f.readline()
                members = f.readline().split(',')
                cnt_teams += 1
                if len(members) < 3:
                    cnt_undersize_teams += 1
                for m in members:
                    individuals.add(m)
                    cnt_individuals[m] += 1
                distr_team_size[len(members)] += 1
                for i in range(len(members) - 1):
                    u = members[i]
                    for j in range(i + 1, len(members)):
                        v = members[j]
                        sociogram[u][v] += 1
                
        '''
        while True:
            movie = f.readline()
            if not movie:
                break
            else:
                cnt += 1
                # year, votes, rating
                year_votes_rating = f.readline().split(',')
                year = int(year_votes_rating[0])
                if int(year_votes_rating[0]) not in distr_movie_num:
                    distr_movie_num[int(year_votes_rating[0])] = 1
                else:
                    distr_movie_num[int(year_votes_rating[0])] += 1

                # genres
                genres = f.readline().split(',')
                cnt_movie_genres += len(genres)
                for g in genres:
                    skills.add(int(g))
                if len(genres) in distr_task_skills:
                    distr_task_skills[len(genres)] += 1
                else:
                    distr_task_skills[len(genres)] = 1

                # team
                actors = f.readline().split(',')
                if len(actors) in distr_team_size:
                    distr_team_size[len(actors)] += 1
                else:
                    distr_team_size[len(actors)] = 1

                if int(actors[0]) not in cnt_directors:
                    cnt_directors[int(actors[0])] = 1
                else:
                    cnt_directors[int(actors[0])] += 1
                individuals.add(int(actors[0]))
                for a in actors[1:]:
                    if int(a) not in cnt_actors:
                        cnt_actors[int(a)] = 1
                    else:
                        cnt_actors[int(a)] += 1
                    individuals.add(int(a))

                for i in range(len(actors) - 1):
                    u = actors[i]
                    for j in range(i + 1, len(actors)):
                        v = actors[j]
                        sociogram[u][v] += 1
        '''

    print('{:.1%} teams undersize'.format(cnt_undersize_teams / cnt_teams))
    cnt_invalid_individuals = 0
    for k, v in cnt_individuals.items():
        if v < 5:
            cnt_invalid_individuals += 1
    print('{:.1%} individuals invalid'.format(
        cnt_invalid_individuals / len(cnt_individuals)))

    print('Total: {} tasks (teams), {} individuals'.format(
        cnt_teams, len(cnt_individuals)))
    '''
    cnt_not_valid_directors = 0
    print('Directors not validated:')
    for k, v in cnt_directors.items():
        if v < 3:
            #print(k)
            cnt_not_valid_directors += 1
        else:
            pass
    print('{} not valid'.format(cnt_not_valid_directors / \
            len(cnt_directors)))

    cnt_not_valid_actors = 0
    print('Actors not validated:')
    for k, v in cnt_actors.items():
        if v < 3:
            #print(k)
            cnt_not_valid_actors += 1
        else:
            pass
    print('{} not valid'.format(cnt_not_valid_actors / \
            len(cnt_actors)))

    for k, v in cnt_directors.items():
        if v in distr_movie_director:
            distr_movie_director[v] += 1
        else:
            distr_movie_director[v] = 1

    for k, v in cnt_actors.items():
        if v in distr_movie_actor:
            distr_movie_actor[v] += 1
        else:
            distr_movie_actor[v] = 1


    years = list()
    cumsums = list()
    for year, count in distr_movie_num.items():
        years.append(year)
        cumsums.append(count)
    cumsums = np.cumsum(cumsums)
    for i in range(len(years)):
        print('{}:\t{:.2%}({})'.format(years[i],cumsums[i] / cnt, cumsums[i]))

    print('Skills directors possessed:')
    size_director = len(cnt_directors)
    distr_movie_director = list((k, distr_movie_director[k]) for k in \
            sorted(distr_movie_director.keys()))
    #for k, v in distr_movie_director:
    #    print('{} times: {} ({:.2%})'.format(k, v, v / size_director))
    print('Avg: {:.3} per director'.format(\
            sum(list(k * v for k, v in distr_movie_director)) / size_director))

    print('\nSkills actors possessed:')
    size_actor = len(cnt_actors)
    distr_movie_actor = list((k, distr_movie_actor[k]) for k in \
            sorted(distr_movie_actor.keys()))
    #for k, v in distr_movie_actor:
    #    print('{} times: {} ({:.2%})'.format(k, v, v / size_actor))
    print('Avg: {:.3} per actor'.format(\
            sum(list(k * v for k, v in distr_movie_actor)) / size_actor))

    '''
    print('\nTeam size')
    distr_team_size = list((k, distr_team_size[k]) for k in \
            sorted(distr_team_size.keys()))
    print('Avg: {:.3} team size'.format(\
            sum(list(k * v for k, v in distr_team_size)) / cnt_teams))

    '''
    print('\nSkills required by tasks:')
    distr_task_skills = list((k, distr_task_skills[k]) for k in \
            sorted(distr_task_skills.keys()))
    #for k, v in distr_task_skills:
    #    print('require {}: {} ({:.2%})'.format(k, v, v / cnt))
    print('Avg: {:.3} skills per task'.format(cnt_movie_genres / cnt))
    '''

    size_pairs = 0
    for d in sociogram.values():
        size_pairs += len(d)
        for k, v in d.items():
            distr_coop_times[v] += 1

    print('Total: {} individuals'.format(len(individuals)))
    
    print('\nCooperation time between any pair of individuals:')
    distr_coop_times = list((k, distr_coop_times[k]) for k in \
            sorted(distr_coop_times.keys()))
    print('Avg: {:.3} times for pair of individuals'.format(\
            sum(list(k * v for k, v in distr_coop_times)) / size_pairs))
    print('REAL Avg: {:.3} times'.format(\
            sum(list(k * v for k, v in distr_coop_times)) / \
            (0.5 * len(individuals) * (len(individuals) - 1))))

