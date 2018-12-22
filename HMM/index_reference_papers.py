
               NEVER RUN THIS CODE



from elasticsearch import Elasticsearch
import requests
import mysql.connector
import json
import pymysql
import traceback
import sys

# ################## configurations ###################
elastic_port=9208
ref_username=csx-devel
ref_password=csx-devel
ref_host=csxstaging01
ref_database=wos2017_12

papers_table='wospapers'
authors_table='wosauthors'
es = Elasticsearch(timeout = 100, port = elastic_port)
cmd_paper= "select id, title, year, venue, pages, volume from " + papers_table
cmd_author = "select name, affil, address, email, ord from " + authors_table + " where paperid = '%s';"
db = mysql.connector.connect(user=ref_username, password=ref_password, host=ref_host,pool_name = "mypool",
                                  pool_size = 10, database=ref_database, charset='utf8', use_unicode=True)

db2 = mysql.connector.connect(user=ref_username, password=ref_password, host=ref_host,pool_name = "mypool",
                                  pool_size = 10, database=ref_database, charset='utf8', use_unicode=True)
try:
    cursor = db.cursor( dictionary=True)
    authorCursor = db2.cursor( dictionary=True)
except Exception as e:
    print("could not get cursor")
    print("-" * 60)
    print(traceback.format_exc())
    print(sys.exc_info()[0])
    print("-" * 60)
i=0
error_file = open('error.txt', 'w')
try:
    cursor.execute(cmd_paper)
    row = cursor.fetchone()
    while row is not None:
        try:
            authorCursor.execute(cmd_author % (row['id']))
            authors = authorCursor.fetchall()
            row['authors'] = ""
            for author in authors:
                name =''
                affil=''
                email=''
                ord =''
                if author['name'] is not None:
                    name = author['name']

                if author['affil'] is not None:
                    affil = author['affil']

                if author['email'] is not None:
                    email = author['email']


                row['authors'] += '['+name + " " + affil + " " + email + ']' + " ;  "
            es.index(index='wos2017', doc_type='paper', id=i, body=row)
            if i%100000==0:
                print(i)
            i+=1
            row = cursor.fetchone()
        except:
            row = cursor.fetchone()
            error_file.write("-" * 60)
            error_file.write('id:'+ str(row['id']))
            error_file.write(traceback.format_exc())
            error_file.write(str(sys.exc_info()[0]))
            error_file.write("-" * 60)
            error_file.flush()
            
    cursor.close()
    db.close()
    authorCursor.close()
    db2.close()
except:
    print(" could not read all retreived data")
    print("-" * 60)
    print(traceback.format_exc())
    print(sys.exc_info()[0])
    print(i)
    print("-" * 60)
