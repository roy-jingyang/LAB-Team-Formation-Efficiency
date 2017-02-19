#!/usr/env/bin python

import sys
import imdb
from csv import writer

if __name__ == '__main__':
    MIN_MOV_ID = int(sys.argv[1])
    MAX_MOV_ID = int(sys.argv[2])

    db = imdb.IMDb('sql', 'mysql://root:root@localhost/imdb')

    movs = list()

    for i in range(MIN_MOV_ID, MAX_MOV_ID + 1):
        if 0 == i % 100000:
            print '========================= %d =========================' % i 
        else:
            pass

        m = db.get_movie(i)
        if m is not None:
            if not m.get('kind') == 'movie':
                pass
                #print 'pass # %d [NOT A MOVIE]' % i
            elif m.get('rating') is None:
                pass
                #print 'pass # %d [NO RATING INFO]' % i
            elif m.get('year') is None:
                pass
                #print 'pass # %d [NO YEAR INFO]' % i
            elif m.get('genres') is None:
                pass
                #print 'pass # %d [NO GENRES INFO]' % i
            elif m.get('cast') is None:
                pass
                #print 'pass # %d [NO CAST INFO]' % i
            elif m.get('director') is None:
                pass
                #print 'pass # %d [NO DIRECTOR INFO]' % i
            else:
                pass
                msg_warning = '[WARNING: NO VOTES #]' \
                        if m.get('votes') is None else ''
                print 'add cnt # %d' % i, msg_warning
                movs.append(m)
        else:
            print 'pass cnt # %d [NO SUCH RECORD]' % i
        
        if 100 == len(movs):
            with open(sys.argv[3], 'a') as csvf:
                w = writer(csvf)
                for movie in movs:
                    row = list()
                    row.append(str(movie.getID()))
                    row.append(movie.get('title').encode('utf-8'))
                    row.append(str(movie.get('year')))
                    if movie.get('votes') is None:
                        row.append('-1')
                    else:
                        row.append(str(movie.get('votes')))
                    row.append(str(movie.get('rating')))
                    row.append('|'.join([str(x) for x in movie.get('genres')]))
                    directors = list()
                    for d in movie.get('director'):
                        dname = d.get('name').encode('utf-8') + '#' + \
                                str(d.getID())
                        directors.append(dname)
                    row.append('|'.join(directors))
                    cast = list()
                    for p in movie.get('cast'):
                        aname = p.get('name').encode('utf-8') + '#' + \
                                str(p.getID())
                        cast.append(aname)
                    row.append('|'.join(cast))
                    w.writerow(row)
            
            print 'Cache dumped to file.'
            del movs[:]

    if len(movs) > 0:
        with open(sys.argv[3], 'a') as csvf:
            w = writer(csvf)
            for movie in movs:
                row = list()
                row.append(str(movie.getID()))
                row.append(movie.get('title').encode('utf-8'))
                row.append(str(movie.get('year')))
                if movie.get('votes') is None:
                    row.append('-1')
                else:
                    row.append(str(movie.get('votes')))
                row.append(str(movie.get('rating')))
                row.append('|'.join([str(x) for x in movie.get('genres')]))
                row.append(movie.get('director')[0].get('name').encode( \
                        'utf-8'))
                cast = list()
                for p in movie.get('cast'):
                    newid = p.get('name').encode('utf-8') + str(p.getID())
                    cast.append(newid)
                row.append('|'.join(cast))
                w.writerow(row)
        
        print 'All dumped.'
        del movs[:]


