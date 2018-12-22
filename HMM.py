import json
import pymysql
import traceback
import sys
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match, Q
import numpy
from similarityProfile import *
import mysql.connector
import queue
from sklearn.externals import joblib
from multiprocessing import Process
import multiprocessing
import threading
import time
import fcntl

def load_configuration():
    configurations = dict()
    for line in open('HMM_configuration.txt','r'):
        if not line.startswith('#'):
            key,value = line[:-1].split('=')
            configurations[key] = value
    return configurations
conf = load_configuration()
print(conf)
# #################################################################################################################
cmd_paperids = "select id from " + conf['target_papers_table']  + " limit 1000000"
cmd_paper = "select * from " + conf['target_papers_table'] + "  where id='%s'; "
cmd_author = "select fname, mname, lname from " + conf['target_authors_table'] + "  where paperid = '%s'"
cmd_refauthor = "select fname, mname, lname from " + conf['ref_authors_table'] + " where paperid = '%s'"
cmd_refpaper= "select * from " + conf['ref_papers_table'] + " where id = '%s'"
###################################################################################################################
# retreiving all of the papers and putting them in the queue for finding matches
t1 = time.time()
target_db = mysql.connector.connect(user=conf['target_username'], password=conf['target_password'], \
    host=conf['target_host'], database=conf['target_database'], charset='utf8', use_unicode=True)
target_cursor = target_db.cursor( dictionary = True)
cmd_paperids = "select id from papers limit " + conf['numberOfPapers']
q = multiprocessing.JoinableQueue()
target_cursor.execute(cmd_paperids)
IDs = target_cursor.fetchall()
for id  in IDs:
    q.put(id['id'])


print('put done')
def find_match(queue, clf):
    try:
        elastic_client = Elasticsearch(timeout = 200, port = conf['reference_index_port'])
        target_db = mysql.connector.connect(user=conf['target_username'], password=conf['target_password'], host=conf['target_host'], database=conf['target_database'], charset='utf8', use_unicode=True)
        target_cursor = target_db.cursor( dictionary = True)
        target_authorCursor = target_db.cursor( dictionary = True)
        refdb = mysql.connector.connect(user=conf['ref_username'], password=conf['ref_password'], host=conf['ref_host'], database=conf['ref_database'], charset='utf8', use_unicode=True)
        refcursor =  refdb.cursor(dictionary = True)
    except:
        print("-" * 60)
        print(traceback.format_exc())
        print(sys.exc_info()[0])
        print("-" * 60)
    while(True):
        if queue.empty():
            break
        try:
            target_ID = queue.get()
            if target_ID is None:
                queue.task_done()
                break
            target_cursor.execute(cmd_paper % (target_ID))
            target_Paper = target_cursor.fetchone()
            # logging number of papers processed
            if int(target_Paper['rid']) % 1000 ==0:
                print(target_Paper['rid'])
            target_authorCursor.execute(cmd_author % (target_ID))
            target_authors = target_authorCursor.fetchall()
            # search the elasticsearch index of the reference data set to retrieve candidate matching papers
            s = Search(using=elastic_client, index=conf['reference_index'])
            if target_Paper['title'] is None or len(target_Paper['title'])<20:
                if len(target_authors)>0 and  target_authors[0]['lname'] is not None  and target_Paper['year'] is not None:
                    s.query = Q('bool', should=[Q('match', year=target_Paper['year']), Q('match',authors = target_authors[0]['lname'])])
                else:
                    if target_Paper['abstract'] is not None:
                        s = s.query("match", abstract=target_Paper['abstract'])
                    else:
                        queue.task_done()
                        continue
            else:
                s = s.query("match", title=target_Paper['title'])
            # retreive search results
            response = s.execute()
            for hit in response:
                refcursor.execute(cmd_refpaper % (hit['id']))
                refpaper = refcursor.fetchone()
                refcursor.execute(cmd_refauthor % (hit['id']))
                refauthors = refcursor.fetchall()
                features = SimilarityProfile.calcFeatureVector(refpaper, refauthors, target_Paper, target_authors)
                # check if papers match using the matcher classifier
                label = clf.predict([features])
                if label ==1:
                    with open(conf['output_file'], "a") as g:
                        fcntl.flock(g, fcntl.LOCK_EX)
                        g.write(target_ID + '\t' + hit['id']+'\n')
                        fcntl.flock(g, fcntl.LOCK_UN)
                    break
            queue.task_done()
        except:
            queue.task_done()
            print("-" * 60)
            print(target_ID)
            print(traceback.format_exc())
            print(sys.exc_info()[0])
            print("-" * 60)

clf = joblib.load('HMM.pkl')

processes =[]
for i in range(int(conf['numberOfParallelProcesses'])):
    p = Process(target=find_match, args=(q,clf, ))
    processes.append(p)
    p.start()
for p in processes:
    p.join()
q.join()
print('total time:',time.time()-t1)
