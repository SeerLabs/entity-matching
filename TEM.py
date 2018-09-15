'''
This script is to predict the probability of titles being true.
"transform_vec(title_string)" is the function to transform a string of a title into a vector with 13 features
"load_DF('filename')" is the function to load the data of document frequency of all words except the stop words in a cerain 
   database, defined by "filename"
"print_all_words_DF()" is the function to check if the data of document frequency is loaded successfully
"load_clf('filename')" is the function to load the model being used in prediction. The model is defined by "filename"
"prob_title(classifier, title_vector)" is the function to return a float value, showing the probability if a title is a true title. 
   "classifier" is a trained model loaded by load_clf('filename'), and "title_vector" is a vector containing the features obtained by
   transform_vec(title_string). Pay attention, This function is used to predict a single title.
title_metrics('filename') is the funtion to transform all titles in a file 'filename' into a metrics in the form of [samples][features].
   the return metrics is a numpy array to be used in multi_prob_titles(title_metrics).
multi_prob_titles(classifier, title_metrics) is the function to be used to evaluate the probability of a group of titles. It returns 
   each titles' probability being a true title in the form of a numpy array([float])

'''

import numpy as np
from numpy import array
import csv
import argparse
import string
import collections
import operator
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn import naive_bayes
from sklearn.externals import joblib


punc_spc = string.punctuation + ' '
ascii_printable = set(string.printable)
special_words = ["Abstact", "LIST", "Acknowledgments", "NOTICES", 
 "CONTENTS", "Accepted", "CONTENT", "authors", "Author", "Authors","References",
 "NULL", "Chapter", "Discussions", "Summary", "OH", "TABLE",
 "ALERTS", "DESCRIPTION", "JOURNAL", "Received", "include",
 "SUMMARY", "Draft", "Author(s)", "Signature",
 "Keywords", "ACKNOWLEDGMENTS", "Syntax", "Fax" ]
stop_punc = set(stopwords.words('english'))|set(string.punctuation)
DF_all_words = {}
letter_type = [string.ascii_letters, punc_spc, string.digits]
count_in_genenal = lambda str_input, str_filter: len(list(filter(lambda c: c in str_filter, str_input)))
count_ascii_letters = lambda str_input: count_in_genenal(str_input, string.ascii_letters)
count_punctuations = lambda str_input: count_in_genenal(str_input, string.punctuation)
count_spaces = lambda str_input: count_in_genenal(str_input, " ")
count_digits = lambda str_input: count_in_genenal(str_input, string.digits)
def count_words(str_input):
	return len(str_input.split())

def count_consecutive_puc(str_input):
    count_cps = collections.defaultdict(int)
    for c_index in range(1, len(str_input)):
        if str_input[c_index-1] in punc_spc and str_input[c_index-1] == str_input[c_index]:
            count_cps[str_input[c_index-1]] += 1	
    return_value = 0
    if bool(count_cps):
    	return_value = max(count_cps.items(), key = operator.itemgetter(1))[1] + 1
    return return_value 

def count_non_ascii(str_input):
	count = 0
	for c in str_input:
		if c not in ascii_printable:
			count += 1
	return count

def first_letter_type(str_input):
	if not bool(str_input):
		return 4
	result = 3
	for i in range(3):
		if str_input[0] in letter_type[i]:
			result = i
	return result

def last_letter_type(str_input):
	if not bool(str_input):
		return 4
	result = 3
	for i in range(3):
		if str_input[-1] in letter_type[i]:
			result = i
	return result

def match_special_words(str_input):
	result = [0 for i in range(len(special_words))]
	for word in str_input.split():
		if word in special_words:
			index = special_words.index(word)
			result[index] = result[index] or 1
	return sum(result)

def DF_max_min_mean(str_input, stop_punctuation, DF_all_words):
	word_token = word_tokenize(str_input)
	filtered_title = [word for word in word_token if not word in stop_punctuation]
	word_DF=[]
	for word in filtered_title:
		if word in DF_all_words:
			word_DF.append(DF_all_words[word])
		else:
			word_DF.append(0.0)
	word_DF.sort()
	if len(word_DF) != 0:
		return (word_DF[-1], word_DF[0],word_DF[int(len(word_DF)/2)])
	else:
		return (0.0, 0.0, 0.0)

transform_vec = lambda str_input: [count_ascii_letters(str_input),
	count_words(str_input),
	count_punctuations(str_input), 
	count_spaces(str_input),
	count_consecutive_puc(str_input),
	count_non_ascii(str_input),
	count_digits(str_input),
	first_letter_type(str_input),
	last_letter_type(str_input),
	match_special_words(str_input),
	DF_max_min_mean(str_input, stop_punc, DF_all_words)[0],
	DF_max_min_mean(str_input, stop_punc, DF_all_words)[1],
	DF_max_min_mean(str_input, stop_punc, DF_all_words)[2]]

def load_DF(DF_file_name):
    global DF_all_words
    DF_words_truetitle_file = {}
    with open(DF_file_name, 'r') as csv_files:
        DF_input_file = csv.reader(csv_files, delimiter=',')
        for data in DF_input_file:
            DF_words_truetitle_file[data[0]] = float(data[1])
    DF_all_words = DF_words_truetitle_file

def print_all_words_DF():
    print(DF_all_words)

load_clf = lambda model_pkl: joblib.load(model_pkl)

def prob_title(classifier, title_vec):
    return classifier.predict_proba(np.array(title_vec).reshape(-1,13))[0][1]

def title_metrics(filename):
    input_title_list = []
    input_file = open(filename, 'r')
    for line in input_file:
        input_title_list.append(line.strip().rstrip('.'))
    input_file.close()
    input_title_metrics = []
    for line in input_title_list:
        input_title_metrics.append(transform_vec(line))
    return np.array(input_title_metrics).reshape(-1,13)

def multi_prob_titles(classifier, title_metrics):
    return classifier.predict_proba(title_metrics)[:,1]


