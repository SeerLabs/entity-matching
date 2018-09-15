import string
import queue
import matplotlib
import threading
from sklearn.externals import joblib
import requests
from xlrd import open_workbook
import mysql.connector
import csv
import time
import numpy as np
import json
import pymysql
import traceback
import sys
import subprocess
import numpy
from random import randint
#import header_based_model
from TEM import *
from CMM  import *
from HMM import *

###################################################################################################################
cmd_paperid = "select id from papers where id = '%s'"
cmd_total_paper = "select * from papers where id = '%s'"
csxdb = mysql.connector.connect(user='csx-prod', password='csx-prod', host='csxdb02', database='citeseerx', charset='utf8', use_unicode=True)
CSXcursor = csxdb.cursor( dictionary = True)
###################################################################################################################
# parameters
output_file = 'results.txt'
theta_tq = 0.01


def evaluate(gt):
    f = open(output_file,'r')
    tp = 0
    fp = 0
    for line in  f:
        splitted = line.split()
        if len(splitted)>1:
            if splitted[0] in gt:
                if splitted[1].strip() in gt[splitted[0]]:
                    tp +=1
                else:
                    fp +=1
                    print('FP:',splitted)
            else:
                fp +=1
                print('FP:',splitted)
    print('tp:',tp)
    print('fp:',fp)
    prec = round(tp/(tp+fp),3)
    rec =  round(tp /len(gt),3)
    f1 = round(2* prec* rec/(prec+rec),3)
    print('precision: ',prec ,'recall:' , rec,' F1:', f1 )
    return tp, fp


result = open(output_file,'w')
groundtruth = open('groundtruth.txt','r')
gt = {}
cit_tasks =[]
head_tasks =[]
clf = load_clf('./models/TEM.pkl')
l =0
cnt =0
t = time.time()
for line in groundtruth:
    l+=1
    splitted = line.split()
    CSXcursor.execute(cmd_total_paper % (splitted[0]))
    CSX_paper = CSXcursor.fetchone()
    try:
        if CSX_paper is not None :
            if CSX_paper['title'] is None or (CSX_paper['title'] is not None and prob_title(clf, transform_vec(CSX_paper['title']))<theta_tq):
                if len(splitted)>1:
                    gt[splitted[0]]=splitted[1]
                cit_tasks.append(splitted[0])
                head_tasks.append(splitted[0])
    except:
        print("-" * 60) 
        print(traceback.format_exc())
        print(sys.exc_info()[0])
        print("-" * 60)
result.close()
print('header len tasks:', len(head_tasks))
header_model(head_tasks)
for line in open(output_file,'r'):
    ss= line.split()
    cit_tasks.remove(ss[0])
print('citation len tasks:', len(cit_tasks))
citation_model(cit_tasks)
evaluate(gt)
print('cnt:',cnt)
print('totel time for is %s' % (time.time()-t))
