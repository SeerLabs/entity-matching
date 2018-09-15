from multiprocessing import Process
import multiprocessing
import string
import queue
from unidecode import unidecode
import matplotlib
import threading
from simhash import Simhash
from similarityProfile import *
from sklearn.externals import joblib
import requests
from xlrd import open_workbook
import mysql.connector
import csv
from sklearn.metrics import precision_recall_curve, auc
import numpy as np
from sklearn.metrics import jaccard_similarity_score
import json
import pymysql
import traceback
import sys
from sklearn.naive_bayes import GaussianNB
import subprocess
from imblearn.pipeline import make_pipeline
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match, Q
import numpy
import time
from name_parser import *
from sklearn.ensemble import RandomForestClassifier
from random import randint
from html.parser import HTMLParser

# paramaters
WoS_citations_index = "wos_citations2017"
WoS_citations_index_port = 9208
theta_title = 0.35
theta_ref = 0.5
output_file = "results.txt"
###################################################################################################################
cmd_paperid = "select id from papers where id = '%s'"
cmd_total_paper = "select * from papers where id = '%s'"
cmd_citations = "select * from citations where paperid = '%s' "# this command gives all of the citations of paperid
cmd_citers = "select * from papers where uid ='%s'" # this command gives all of the papers that cited paperid
cmd_cited = "select * from citations where paperid ='%s'"
###################################################################################################################

client = Elasticsearch(host="0.0.0.0", timeout = 200, port = WoS_citations_index_port)  
page = 100
clf = joblib.load('./models/HMM.pkl')
def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]
def mystring(item):
    if item is None:
        return ''
    else:
         return str(item)
def normalize(text):
    if text is None:
        return None
    if text[:5] == 'orcid':
        text = text.split('>')[1]
    h = HTMLParser()
    text = str(h.unescape(text))
    normalizr = Normalizr(language='en')
    normalizations = [('replace_punctuation', {'replacement': ' '}),  
        'lower_case',
        ('remove_stop_words',{'ignore_case':'False'}),
        'remove_extra_whitespaces']
    text = normalizr.normalize(text, normalizations)
    return text


def jaccard_similarity(x,y):
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    if union_cardinality !=0:
        return intersection_cardinality/float(union_cardinality)
    else:
        return 0

def compare_jaccard_citations(wos,csx_bow):
    wos_citations_titles = ' '.join(mystring(w['citedTitle']) for w in wos)
    wos_bow = normalize(wos_citations_titles).split()
    return jaccard_similarity(csx_bow, wos_bow)



def find_match(queue,id):
    # queue has a list of tasks assigned to CMM model
    # connection to wos ans csx databases
    csxdb = mysql.connector.connect(user='csx-prod', password='csx-prod', host='csxdb02', database='citeseerx', charset='utf8', use_unicode=True)
    wosdb = mysql.connector.connect(user='wos-user', password='#uHbG9LA', host='heisenberg', database='wos_tiny', charset='utf8', use_unicode=True)
    CSXcursor = csxdb.cursor( dictionary = True)
    WOScursor = wosdb.cursor( dictionary = True)
    CSXCitationsCursor = csxdb.cursor( dictionary = True)
    while(True):
        if queue.empty():
            break
        shared_cit = 0
        prevID = None
        checkedList = set()
        csx_paperID = queue.get()
        if csx_paperID is None:
            break
        try:
            #print(csx_paperID)
            CSXCitationsCursor.execute(cmd_citations % (csx_paperID))
            CSXcitations = CSXCitationsCursor.fetchall()
            # making bow of csx reference titles    
            csx_citations_titles = ' '.join(mystring(c['title']) for c in CSXcitations)
            csx_bow = normalize(csx_citations_titles).split()
            counter = 0
            brk = False
            for csx_citation in CSXcitations:
                counter += 1
                # we only process 30 citatins due to efficiency
                if counter > 30:
                    break
                csx_citation['authors'] = parse_csx_authors(csx_citation['authors'])
                csx_citation['abstract'] = ''
                start = 0
                label = 1
                if csx_citation['title'] is not None:
                    s = Search(using=client, index=WoS_citations_index).query("match", citedTitle=csx_citation['title'])
                    # we process at most 1000 candidate citations
                    while brk == False  and label ==1 and start < 1000:
                        s = s[start:start+page]
                        response = s.execute()
                        if len(response) == 0:
                            brk = True
                        for hit in response:
                            if hit['paperid'] not in checkedList:
                                checkedList.add(hit['paperid'])
                                wos_citation = {}
                                wos_citation['title']=hit['citedTitle']
                                wos_citation['year']=hit['year']
                                wos_citation['abstract']= ''
                                wos_citation['pages']=hit['page']
                                wos_citation['volume']=hit['volume']
                                # check citation matching
                                features = SimilarityProfile.calcFeatureVector(csx_citation, csx_citation['authors'], wos_citation, parse_wos_authors(hit['citedAuthor']))
                                label = clf.predict([features])[0]
                                if label==1:
                                    WOScursor.execute(cmd_citers % (hit['paperid']))
                                    WOS_paper = WOScursor.fetchall()[0]
                                    CSXcursor.execute(cmd_total_paper % (csx_paperID) )
                                    CSX_paper = CSXcursor.fetchall()[0]
                                    # check for title similarity
                                    title1 = '%x' % Simhash(get_features(normalize(mystring(CSX_paper['title'])))).value 
                                    title2 = '%x' % Simhash(get_features(normalize(mystring(WOS_paper['title'])))).value 
                                    dist = distance.nlevenshtein(title1, title2)
                                    if  dist < theta_title:
                                        with open(output_file, 'a') as match_file:
                                            match_file.write(CSX_paper['id']+' '+WOS_paper['uid'] +'\n')
                                            match_file.flush()
                                            brk = True
                                            break
                                    # check for reference titles similarity
                                    else:
                                        WOScursor.execute(cmd_cited % (WOS_paper['uid']))
                                        WOScitations = WOScursor.fetchall()
                                        citations_similarity = compare_jaccard_citations(WOScitations,csx_bow)
                                        if citations_similarity > theta_ref :
                                            with open(output_file, 'a') as match_file:
                                                match_file.write(CSX_paper['id']+' '+WOS_paper['uid'] +'\n')
                                                match_file.flush()
                                                brk = True
                                                break
                        start= start +len(response)
                if brk == True:
                    break
            queue.task_done()
        except:
            queue.task_done()
            print("-" * 60)
            print('csx paper id:', csx_paperID)
            print(str(traceback.format_exc()))
            print(str(sys.exc_info()[0]))
            print("-" * 60)
            csxdb.close()
            wosdb.close()

def citation_model(tasklist):
    q = multiprocessing.JoinableQueue()
    cnt = 0
    for task in tasklist:
        q.put(task)
    processes =[]
    for i in range(18):
        p = Process(target=find_match, args=(q,i,))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
    q.join()

