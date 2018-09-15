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

ref_index = 'wos2017'
ref_index_port = 9208
###################################################################################################################
#cmd_paperids = "select id from papers"
cmd_paper = "select * from papers where id='%s'; "
cmd_author = "select fname, mname, lname from authors where paperid = '%s'"
cmd_REFauthor = "select fname, mname, lname from wosauthors where paperid = '%s'"
cmd_REFpaper= "select * from wospapers where id = '%s'"
csxdb = mysql.connector.connect(user='csx-devel', password='csx-devel', host='csxstaging01', database='citeseerx2', charset='utf8', use_unicode=True)
CSXcursor = csxdb.cursor( dictionary = True)
###################################################################################################################
t1 = time.time()
def find_match(queue, clf):
    # connection to target and reference database
    client = Elasticsearch(timeout = 200, port = ref_index_port)
    csxdb = mysql.connector.connect(user='csx-devel', password='csx-devel', host='csxstaging01', database='citeseerx2', charset='utf8', use_unicode=True)
    CSXcursor = csxdb.cursor( dictionary = True)
    CSXauthorCursor = csxdb.cursor( dictionary = True)
    REFdb = mysql.connector.connect(user='csx-devel', password='csx-devel', host='csxstaging01', database='wos2017_12', charset='utf8', use_unicode=True)
    REFcursor =  REFdb.cursor(dictionary = True)




    while(True):
        if queue.empty():
            break
        try:
            csxID = queue.get()
            if csxID is None:
                queue.task_done()
                break
            CSXcursor.execute(cmd_paper % (csxID))
            CSXPaper = CSXcursor.fetchone()
            if CSXPaper is None:
                queue.task_done()
                continue
            CSXauthorCursor.execute(cmd_author % (csxID))
            CSXauthors = CSXauthorCursor.fetchall()
            s = Search(using=client, index=ref_index)
            if CSXPaper['title'] is None or len(CSXPaper['title'])<20:
                if len(CSXauthors)>0 and  CSXauthors[0]['lname'] is not None  and CSXPaper['year'] is not None:
                    s.query = Q('bool', should=[Q('match', year=CSXPaper['year']), Q('match',authors = CSXauthors[0]['lname'])])
                else:
                    if CSXPaper['abstract'] is not None:
                        s = s.query("match", abstract=CSXPaper['abstract'])
                    else:
                        queue.task_done()
                        continue
            else:
                s = s.query("match", title=CSXPaper['title'])
            response = s.execute()
            for hit in response:
                REFcursor.execute(cmd_REFpaper % (hit['id']))
                REFpaper = REFcursor.fetchone()
                REFcursor.execute(cmd_REFauthor % (hit['id']))
                REFauthors = REFcursor.fetchall()
                features = SimilarityProfile.calcFeatureVector(REFpaper, REFauthors, CSXPaper, CSXauthors)
                label = clf.predict([features])
                if label ==1:
                    with open("results.txt", "a") as g:
                        fcntl.flock(g, fcntl.LOCK_EX)
                        g.write(csxID + '\t' + hit['id']+'\n')
                        fcntl.flock(g, fcntl.LOCK_UN)
                    break
            queue.task_done()
        except:
            queue.task_done()
            print("-" * 60)
            print(csxID)
            print(traceback.format_exc())
            print(sys.exc_info()[0])
            print("-" * 60)



def header_model(tasklist):
    t1 = time.time()
    q = multiprocessing.JoinableQueue()
    for id  in tasklist:
        q.put(id)
    clf = joblib.load('./models/HMM.pkl')

    processes =[]
    for i in range(5):
        p = Process(target=find_match, args=(q,clf, ))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    q.join()
    print('total time:',time.time()-t1)
