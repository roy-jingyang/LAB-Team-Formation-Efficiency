#! /usr/bin/env python3

import sys
import numpy as np
from collections import defaultdict

if __name__ == '__main__':
    cnt = 0

    distr_article_num = dict()

    cnt_authors = dict()
    distr_article_author = dict()

    distr_team_size = dict()

    distr_task_skills = dict()

    individuals = set()
    skills = set()

    sociogram = defaultdict(lambda: defaultdict(lambda: 0))
    distr_coop_times = dict()

    cnt_article_tags = 0
    with open(sys.argv[1], 'r') as f:
        while True:
            article = f.readline()
            if not article:
                break
            else:
                cnt += 1
                # year, rating
                year_ratings = f.readline().split(',')
                year = int(year_ratings[0])
                if int(year_ratings[0]) not in distr_article_num:
                    distr_article_num[year] = 1
                else:
                    distr_article_num[year] += 1

                # tags
                tags = f.readline().split(',')
                cnt_article_tags += len(tags)
                for t in tags:
                    skills.add(int(t))
                if len(tags) in distr_task_skills:
                    distr_task_skills[len(tags)] += 1
                else:
                    distr_task_skills[len(tags)] = 1

                # team
                authors = f.readline().split(',')
                if len(authors) in distr_team_size:
                    distr_team_size[len(authors)] += 1
                else:
                    distr_team_size[len(authors)] = 1

                for a in authors[1:]:
                    if int(a) not in cnt_authors:
                        cnt_authors[int(a)] = 1
                    else:
                        cnt_authors[int(a)] += 1
                    individuals.add(int(a))

                for i in range(len(authors) - 1):
                    u = authors[i]
                    for j in range(i + 1, len(authors)):
                        v = authors[j]
                        sociogram[u][v] += 1

    cnt_not_valid_authors = 0
    print('Authors not validated:')
    for k, v in cnt_authors.items():
        if v < 3:
            #print(k)
            cnt_not_valid_authors += 1
        else:
            pass
    print('{} not valid'.format(cnt_not_valid_authors / len(cnt_authors)))
    print(cnt_authors)

    for k, v in cnt_authors.items():
        if v in distr_article_author:
            distr_article_author[v] += 1
        else:
            distr_article_author[v] = 1

    size_pairs = 0
    for d in sociogram.values():
        size_pairs += len(d)
        for k, v in d.items():
            if v in distr_coop_times:
                distr_coop_times[v] += 1
            else:
                distr_coop_times[v] = 1

    print('Total: {} individuals'.format(len(individuals)))
    print('Total: {} skills'.format(len(skills)))

    years = list()
    cumsums = list()
    distr_article_num = [(k, distr_article_num[k]) for k in \
            sorted(distr_article_num.keys())]
    for year, count in distr_article_num:
        years.append(year)
        cumsums.append(count)
    cumsums = np.cumsum(cumsums)
    for i in range(len(years)):
        print('{}:\t{:.2%}({})'.format(years[i],cumsums[i] / cnt, cumsums[i]))

    print('\nSkills authors possessed:')
    size_author = len(cnt_authors)
    distr_article_author = list((k, distr_article_author[k]) for k in \
            sorted(distr_article_author.keys()))
    #for k, v in distr_article_author:
    #    print('{} times: {} ({:.2%})'.format(k, v, v / size_author))
    print('Avg: {:.3} per author'.format(\
            sum(list(k * v for k, v in distr_article_author)) / size_author))

    print('\nTeam size')
    distr_team_size = list((k, distr_team_size[k]) for k in \
            sorted(distr_team_size.keys()))
    #for k, v in distr_team_size:
    #    print('size {}: {} ({:.2%})'.format(k, v, v / cnt))
    print('Avg: {:.3} team size'.format(\
            sum(list(k * v for k, v in distr_team_size)) / cnt))

    print('\nSkills required by tasks:')
    distr_task_skills = list((k, distr_task_skills[k]) for k in \
            sorted(distr_task_skills.keys()))
    #for k, v in distr_task_skills:
    #    print('require {}: {} ({:.2%})'.format(k, v, v / cnt))
    print('Avg: {:.3} skills per task'.format(cnt_article_tags / cnt))
    
    print('\nCooperation time between any pair of individuals:')
    distr_coop_times = list((k, distr_coop_times[k]) for k in \
            sorted(distr_coop_times.keys()))
    print('Avg: {:.3} times for pair of individuals'.format(\
            sum(list(k * v for k, v in distr_coop_times)) / size_pairs))
    print('REAL Avg: {:.3} times'.format(\
            sum(list(k * v for k, v in distr_coop_times)) / \
            (0.5 * len(individuals) * (len(individuals) - 1))))

