import matplotlib
import random
from sklearn.externals import joblib
matplotlib.use('Agg')
import requests
import mysql.connector
import matplotlib.pyplot as plt
import csv
from sklearn.metrics import precision_recall_curve, auc
import json
import pymysql
import traceback
import sys
from sklearn.naive_bayes import GaussianNB
from jaccard_SimilarityProfile import SimilarityProfile
import subprocess
from imblearn.pipeline import make_pipeline
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import MultiMatch, Match, Q
from sklearn import svm
from sklearn.model_selection import cross_val_score
from sklearn.utils import shuffle
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.model_selection import GridSearchCV
from sklearn import linear_model
import numpy
from sklearn.ensemble import RandomForestClassifier
from random import randint


class wos_matcher:
    def __init__(self):
        self.client = Elasticsearch(timeout = 100, port = 9202)
        self.cmd_author = "select fname, mname, lname from authors where paperid = '%s';"
        self.cmd_paper= "select * from papers where id = '%s'"
        self.cmd_wos_author = "select fname, mname, lname from wosauthors where paperid = '%s';"
        self.cmd_wos_paper= "select * from wospapers where id = '%s'"
        self.db = mysql.connector.connect(user='csx-devel', password='csx-devel', host='csxstaging01', database='citeseerx2', charset='utf8', use_unicode=True)
        self.WoSdb = mysql.connector.connect(user='csx-devel', password='csx-devel', host='csxstaging01', database='wos2017_12', charset='utf8', use_unicode=True)
        self.CSXcursor = self.db.cursor( dictionary = True)
        self.CSXauthorCursor = self.db.cursor( dictionary = True)
        self.WoScursor =  self.WoSdb.cursor(dictionary = True)
        self.clf = joblib.load('jaccardModel.pkl')
        self.client = Elasticsearch(timeout = 40, port = 9202)
    def predict(self, csxID):
        try:
            self.CSXcursor.execute(self.cmd_paper % (csxID))
            CSXPaper = self.CSXcursor.fetchone()
            if CSXPaper is None:
                #print(csxID,'is none from db')
                return csxID, None
            self.CSXauthorCursor.execute(self.cmd_author % (csxID))
            CSXauthors = self.CSXauthorCursor.fetchall()

            s = Search(using=self.client, index="wos_papers")
            if CSXPaper['title'] is None or len(CSXPaper['title'])<20:
                if len(CSXauthors)>0 and CSXPaper['year'] is not None:
                    s.query = Q('bool', should=[Q('match', year=CSXPaper['year']), Q('match',authors = CSXauthors[0]['lname'])])
                else:
                    if CSXPaper['abstract'] is not None:
                        s = s.query("match", abstract=CSXPaper['abstract'])
                    #else:
                    #    print(csxID," does not have author or year or abstract")
            else:
                s = s.query("match", title=CSXPaper['title'])

            response = s.execute()
            for hit in response:
                self.WoScursor.execute(self.cmd_wos_paper % (hit['id']))
                WoSpaper = self.WoScursor.fetchone()
                self.WoScursor.execute(self.cmd_wos_author % (hit['id']))
                WoSauthors = self.WoScursor.fetchall()
                features = SimilarityProfile.calcFeatureVector(WoSpaper, WoSauthors, CSXPaper, CSXauthors)
                if self.clf.predict([features]) ==1 :
                    return csxID, hit['id']
            return csxID, None
        except:
            print("-" * 60)
            print(traceback.format_exc())
            print(sys.exc_info()[0])
            print("-" * 60)
