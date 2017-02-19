#! /usr/bin/env python3

#import MySQLdb
import sys
import numpy as np
import csv
from collections import Counter

if __name__ == '__main__':
    # File read IN
    result = list()
    with open(sys.argv[1], 'r') as dbf:
        reader = csv.reader(dbf)
        for row in reader:
            result.append(row)
    print('Fetched {} records.'.format(len(result)))

    # 1. Remove duplicate records: all fields are required to be the same
    # 2. Merge individuals: directors + actors -> members (NO duplicates)
    records_tmp = dict()
    rm_dup = set()
    records = dict()
    for r in result:
        # id (key), title, year, votes, ratings, genres, directors, actors
        record = [r[1], r[2], r[3], r[4], r[5], r[6], r[7]]
        if str(record) not in rm_dup:
            rm_dup.add(str(record))
            # id (key) => title, year, votes, ratings, genres, members
            str_members = r[6] + '|' + r[7]
            members = list()
            for m in str_members.split('|'):
                if m not in members:
                    members.append(m)
            records_tmp[r[0]] = [r[1], r[2], r[3], r[4], r[5],
                    '|'.join(members)]
    print('{} records left after removing duplicates.'.format(len(records_tmp)))

    # Retrieve records of specific years only
    for k, record in records_tmp.items():
        year = int(record[1])
        if year >= int(sys.argv[3]) and year < int(sys.argv[4]):
            records[k] = record

    print('{} records in time interval {} - {}'.format(len(records), \
            sys.argv[3], sys.argv[4]))
    
    # Filtering data in an interative fashion
    MAX_ITERTATION_DEPTH = 50
    EPS_CONV = 1 / 1e06
    cnt_individuals = Counter()
    
    # 1. Eliminiate individuals with particating times < 5
    def elim_individuals():
        # 1.1 do counting
        cnt_individuals.clear()
        # id (key) => title, year, votes, ratings, genres, members
        for k, record in records.items():
            members = record[5].split('|')
            for m in members:
                cnt_individuals[m] += 1
        # 1.2 do elimination
        cnt_rm_individuals = 0
        # id (key) => title, year, votes, ratings, genres, members
        for k, record in records.items():
            members = record[5].split('|')
            members_left = list()
            for m in members:
                if cnt_individuals[m] >= 5:
                    members_left.append(m)

            # current record has changed (in team members)
            if len(members_left) < len(members):
                cnt_rm_individuals += 1
                records[k][5] = '|'.join(members_left)

        return cnt_rm_individuals


    # 2. Eliminate tasks (teams) with team size < 3
    def elim_movies():
        # 2.1 do elimination (no need for counting)
        cnt_rm_movies = 0
        elim_movie_key = list()
        # id (key) => title, year, votes, ratings, genres, members
        for k, record in records.items():
            members = record[5].split('|')
            # allow duplication existed in both directors & actors
            if len(members) < 3:
                # current record invalid (team size < 3)
                cnt_rm_movies += 1
                elim_movie_key.append(k)
        rate_rm_movies = cnt_rm_movies / len(records)

        if cnt_rm_movies > 0:
            for k in elim_movie_key:
                del records[k]

        return rate_rm_movies

    it = 0
    while True:
        it += 1
        print('Iteration #{}: '.format(it))
        cnt_rm_individuals = elim_individuals()
        delta_rate = elim_movies()
        print('delta rate: {}'.format(delta_rate))
        if it >= MAX_ITERTATION_DEPTH or delta_rate < EPS_CONV:
            break

    l_records = list()
    for k, record in records.items():
        # add movie id
        l_records.append([k] + record)

    l_records.sort(key=lambda x: int(x[2]))

    # Number genres, build new dataset
    result_final = list()
    Genres = dict()
    # id, title, year, votes, ratings, genres, members
    for record in l_records:
        m_genres = list()

        genres = record[5].split('|')
        for g in genres:
            if g not in Genres:
                Genres[g] = len(Genres) + 1

            m_genres.append(str(Genres[g])) 

        record_new = tuple((
            record[0], record[1], record[2], record[3], record[4],
            m_genres, record[6].split('|')))
        result_final.append(record_new)

    print('{} records left after processing.'.format(len(result_final)))

    # file write OUT
    with open(sys.argv[2], 'w') as f:
        # id, title, year, votes, ratings, genres, members
        f.write('MovieID\tYear\tScore\tTeam\tTeamSize\tMovieGenres\n')
        for record in result_final:
            f.write('{}\t{}\t{}\t[{}]\t{}\t[{}]\n'.format(
                record[0], record[2], record[4],
                ','.join([x.split('#')[1] for x in record[-1]]),
                len(record[-1]),
                ','.join(record[-2])))

