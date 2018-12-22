{\rtf1\ansi\ansicpg1252\cocoartf1671\cocoasubrtf100
{\fonttbl\f0\fnil\fcharset0 Monaco;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;\red255\green255\blue255;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;\cssrgb\c100000\c100000\c100000;}
\margl1440\margr1440\vieww25100\viewh13240\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf2 \cb3 Header-based paper matching (HMM): \
\
This section shows the procedure to run the HMM model. \
\
1. Reference and target papers should be stored in the database with the following of format:\
papers table format:\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0
\cf2 \CocoaLigature0 +-----------------+---------------------+------+-----+---------------------+----------------+\
| Field           | Type                | Null | Key | Default             | Extra          |\
+-----------------+---------------------+------+-----+---------------------+----------------+\
| rid             | int(11)             | NO   | PRI | NULL                | auto_increment |\
| id              | varchar(100)        | NO   | MUL | NULL                |                |\
| doi             | varchar(255)        | YES  |     | NULL                |                |\
| title           | varchar(255)        | YES  | MUL | NULL                |                |\
| abstract        | text                | YES  |     | NULL                |                |\
| year            | int(11)             | YES  | MUL | NULL                |                |\
| venue           | varchar(255)        | YES  |     | NULL                |                |\
| pages           | varchar(20)         | YES  |     | NULL                |                |\
| volume          | int(11)             | YES  |     | NULL                |                |\
| number          | int(11)             | YES  |     | NULL                |                |\
+-----------------+---------------------+------+-----+---------------------+----------------+\CocoaLigature1 \
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf2 authors table format:\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0
\cf2 \CocoaLigature0 +---------+---------------------+------+-----+---------+----------------+\
| Field   | Type                | Null | Key | Default | Extra          |\
+---------+---------------------+------+-----+---------+----------------+\
| id      | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |\
| name    | varchar(100)        | NO   | MUL | NULL    |                |\
| lname   | varchar(100)        | YES  | MUL | NULL    |                |\
| mname   | varchar(100)        | YES  |     | NULL    |                |\
| fname   | varchar(100)        | YES  | MUL | NULL    |                |\
| affil   | varchar(255)        | YES  |     | NULL    |                |\
| address | varchar(255)        | YES  |     | NULL    |                |\
| email   | varchar(100)        | YES  |     | NULL    |                |\
| ord     | tinyint(4)          | NO   |     | NULL    |                |\
| paperid | varchar(100)        | NO   | MUL | NULL    |                |\
+---------+---------------------+------+-----+---------+----------------+\CocoaLigature1 \
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf2 \
2. Reference papers must be indexed by Elastic search\
\
Reference papers are indexed with the [\CocoaLigature0 index_reference_papers.py](index_reference_papers.py) Python script and this file can run by :\
$ python index_reference_papers.py \
Don\'92t forget to set configuration settings at the beginning of the file for the database credentials. \
\CocoaLigature1 \
3. Configurations in \'91header_configurations.txt\'92 must be set:\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0
\cf2 \
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf2 These configurations are defined in 'configurations.txt'. \
This file contains the following information:\
 	1. Reference and target database credentials \
	2. Name and the port of the reference index in Elastic search. \
\
4. model can run with the following command:\
	python HMM.py\
\
Required packages are:\
\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0
\cf2 \CocoaLigature0 elasticsearch_dsl==5.3.0\
scipy==1.0.0\
Unidecode==1.0.22\
PyMySQL==0.7.11\
numpy==1.13.3\
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0
\cf2 Distance==0.1.3\ul                                                                                                                                                                     \ulnone \
elasticsearch==5.4.0\
regex==2017.9.23\
simhash==1.8.0\
jellyfish==0.5.6\
mysql_connector_repackaged==0.3.1\
scikit_learn==0.20.2\
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0
\cf2 \CocoaLigature1 \
\
}