# entity-matching


Match entities between CiteSeerX and other digital libraries


In this project, we attempt to develop a machine learning (ML) based method to match paper entities between CiteSeerX and other digital libraries, including but not limited to the IEEE Xplore (IEEE hereafter), DBLP, Web of Science (WoS hereafter). Like most ML-based methods, data preprocessing takes substantial efforts. The purpose of creating this codebase is to centralize working programs that accomplish different tasks so they can be reused for future people that take over corresponding roles.

Models:

[HMM](HMM.py) (Header Matching Model): This model tries to match paper entities across data bases using information existing in the header of the papers including title, abstract, list of authors and venue. This model is used for matching CiteSeerX to digital libraries without citation information such as DBLP, IEEE and Medline.

[CMM](CMM.py) (Citation Matching Model): This model leverages citations for matching of the papers if citation information exists. 

[TEM](TEM.py) (Title Evaluation Model): This model evaluates quality of the title. If title has a high quality, HMM model is used otherwise combination of CMM and HMM model is applied for the matching process. 

[IMM](IMM.py) (Integrated Matching Model): This model integrates HMM and CMM with the help of TEM. 


-----------------------------------------------------------------------------------------------------
Files:

[ground truth](groundtruth.txt): This files contains a list of matching papers between CiteSeerX and WoS. 

[Similarity Profile](similarityProfile.py): This file compares profiles of two papers from different data sources and measures their similarity score. This model has different features for variety of information in header. 



# HMM
Header-based paper matching (HMM): 

This section shows the procedure to run the HMM model. 

1. Reference and target papers should be stored in the database with the following of format:
papers table format:
+-----------------+---------------------+------+-----+---------------------+----------------+
| Field           | Type                | Null | Key | Default             | Extra          |
+-----------------+---------------------+------+-----+---------------------+----------------+
| rid             | int(11)             | NO   | PRI | NULL                | auto_increment |
| id              | varchar(100)        | NO   | MUL | NULL                |                |
| doi             | varchar(255)        | YES  |     | NULL                |                |
| title           | varchar(255)        | YES  | MUL | NULL                |                |
| abstract        | text                | YES  |     | NULL                |                |
| year            | int(11)             | YES  | MUL | NULL                |                |
| venue           | varchar(255)        | YES  |     | NULL                |                |
| pages           | varchar(20)         | YES  |     | NULL                |                |
| volume          | int(11)             | YES  |     | NULL                |                |
| number          | int(11)             | YES  |     | NULL                |                |
+-----------------+---------------------+------+-----+---------------------+----------------+
authors table format:
+---------+---------------------+------+-----+---------+----------------+
| Field   | Type                | Null | Key | Default | Extra          |
+---------+---------------------+------+-----+---------+----------------+
| id      | bigint(20) unsigned | NO   | PRI | NULL    | auto_increment |
| name    | varchar(100)        | NO   | MUL | NULL    |                |
| lname   | varchar(100)        | YES  | MUL | NULL    |                |
| mname   | varchar(100)        | YES  |     | NULL    |                |
| fname   | varchar(100)        | YES  | MUL | NULL    |                |
| affil   | varchar(255)        | YES  |     | NULL    |                |
| address | varchar(255)        | YES  |     | NULL    |                |
| email   | varchar(100)        | YES  |     | NULL    |                |
| ord     | tinyint(4)          | NO   |     | NULL    |                |
| paperid | varchar(100)        | NO   | MUL | NULL    |                |
+---------+---------------------+------+-----+---------+----------------+

2. Reference papers must be indexed by Elastic search

Reference papers are indexed with the [index_reference_papers.py](index_reference_papers.py) Python script and this file can run by :
$ python index_reference_papers.py 
Don’t forget to set configuration settings at the beginning of the file for the database credentials. 

3. Configurations in ‘header_configurations.txt’ must be set:

These configurations are defined in 'configurations.txt'. 
This file contains the following information:
 	1. Reference and target database credentials 
	2. Name and the port of the reference index in Elastic search. 

4. model can run with the following command:
	python HMM.py

Required packages are:

elasticsearch_dsl==5.3.0
scipy==1.0.0
Unidecode==1.0.22
PyMySQL==0.7.11
numpy==1.13.3
Distance==0.1.3                                                                                                                                                                    
elasticsearch==5.4.0
regex==2017.9.23
simhash==1.8.0
jellyfish==0.5.6
mysql_connector_repackaged==0.3.1
scikit_learn==0.20.2


