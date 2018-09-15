import pickle
import jellyfish
import codecs
import collections
from scipy import spatial
import math
import numpy as np
import os
from string import punctuation
import distance
import re
from simhash import Simhash
import hashlib
from unidecode import unidecode 
import string
from html.parser import HTMLParser
from normalizr  import Normalizr


def normalize2(text):
    lower = unidecode(text.lower())  #put it in lowercase
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation)) #gets rid of puncuation
    norm = lower.translate(translator)
    norm = re.sub(' +', ' ', norm) #get rid of extra spaces
    for r in (("'t ",""),("'s ",""),(' an ',' '),(' and ',' '),(' are ',' '),(' as ',' '),(' at ',' '),(' be ',' '),(' but ',' '),(' by ',' '),(' for ',' '),(' if ',' '),(' in ',' '),(' into ',' '),(' is ',' '),(' it ',' '),(' no ',' '),(' not ',' '),(' of ',' '),(' on ',' '),(' or ' ,' '),(' such ',' '),(' that ',' '),(' the ',' '),(' their ',' '),(' then ',' '),(' there ',' '),(' these ',' '),(' they ',' '),(' this ',' '),(' to ',' '),(' was ',' '),(' will ',' '),(' with ',' ')):
        norm = str(norm).replace(*r)
    return norm


def xstr(string):
    return string if string is not None else  ''  


def normalize(text):
    normalizr = Normalizr(language='en')
    normalizations = ['remove_extra_whitespaces',
        ('replace_punctuation', {'replacement': ' '}),
        'lower_case',
        ('remove_stop_words',{'ignore_case':'False'})]
    h = HTMLParser()
    text = normalizr.normalize(xstr(text), normalizations)
    return str(h.unescape(text))

def get_features(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]


class SimilarityProfile(object):
    """
    Class to generate feature vector for pairwise classifier
    """
    EPS = 2.2250738585072014e-308
    @staticmethod
    def calcFeatureVector(p1, a1s, p2, a2s):
        featVector = list()

        def calcBinaryAuthorFeats(a1, a2, featVector):
            feature = ''
            # first name
            if (a1['fname'] is None or a2['fname'] is None):
                feature += '0'
            else:
                if a1['fname'][:1]== a2['fname'][:1]:
                    feature = '1' + feature
                else:
                    feature = '0' + feature
            #middle name
            if (a1['mname'] is None or a2['mname'] is None):
                feature = '0' + feature
            else:
                if a1['mname'][:1] == a2['mname'][:1]:
                    feature = '1'+ feature
                else:
                    feature = '0'+ feature
            # last name
            if (a1['lname'] is None or a2['lname'] is None):
                feature = '0' + feature
            else:
                if a1['lname'] == a2['lname']:
                    feature = '1'+ feature
                else:
                    feature = '0'+ feature
            feature = '0b' + feature
            featVector.append(int(feature,2))


        # features related to author name and order
        def calcAuthorFeats(a1, a2, featVector):
            if (a1['lname'] is None or a2['lname'] is None):
                featVector.append(1.0)
            else:
                last1 = a1['lname'].lower()
                last2 = a2['lname'].lower()

                last = 0.0 
                if len(last1) == 0 or len(last2) == 0:
                    last = 1.0
                elif last1 == last2:
                    last = 3.0
                else:
                    last = 0.0
                featVector.append(last)
        # fetaures related to publication year
        def calcYearFeats(year1, year2, featVector):
            if year1 is None or year2 is None:
                featVector.append(-100)
                return
            if year1 < 1800 or year2 < 1800:
                j_year_diff = -100
            elif year1 > 2020 or year2 > 2020:
                j_year_diff = -100
            else:
                j_year_diff = abs(year1 - year2)
                if j_year_diff > 100:
                    j_year_diff = -100
            #featVector.append(j_year)
            featVector.append(float(j_year_diff))


        def jaccard_similarity(x,y):
            intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
            union_cardinality = len(set.union(*[set(x), set(y)]))
            if union_cardinality !=0:
                return intersection_cardinality/float(union_cardinality)
            else:
                return 0

        def xstr(string):
            return string if string is not None else  ''

        def calcBOWcosine(title1, title2, abstract1, abstract2, featVector):
            TF1 = collections.Counter(normalize(xstr(title1)+' '+ xstr(abstract1)).split())
            TF2 = collections.Counter(normalize(xstr(title2)+' '+ xstr(abstract2)).split())
            cordinality1 = math.sqrt(np.sum(np.square(np.array(list(TF1.values())))))
            cordinality2 = math.sqrt(np.sum(np.square(np.array(list(TF2.values())))))
            cosine = 0
            for term in TF1.keys():
                if term in TF2.keys():
                    cosine += TF1[term] * TF2[term]
            if cordinality1==0 or cordinality2==0:
                cosine = 0
            else:
                cosine = cosine/(cordinality1*cordinality2)
            featVector.append(1-cosine)


        def calcAbstractBOWjaccard(abstract1, abstract2, featVector):
            if abstract1 is None or abstract2 is None or abstract1=='' or abstract2=='':
                featVector.append(1)
                return
            bow1 = normalize(xstr(abstract1)).split()
            bow2 = normalize(xstr(abstract2)).split()
            jaccard = jaccard_similarity(bow1, bow2)
            featVector.append(jaccard)

        def calcTitleBOWjaccard(title1, title2, featVector):
            if title1 == '' or title2 =='' or title1 is None or title2 is None:
                featVector.append(1)
                return
            bow1 = normalize(xstr(title1)).split()
            bow2 = normalize(xstr(title2)).split()
            jaccard = jaccard_similarity(bow1, bow2)
            featVector.append(jaccard)
        def calcTitleFeats(title1, title2, featVector):
            if title1 is None or title2 is None or title1=='' or title2=='':
                featVector.append(1)
                return
            t2 = distance.nlevenshtein(title1, title2)
            featVector.append(t2)
        def calcAbstractFeats(abstract1, abstract2, featVector):
            if abstract1 is None or abstract2 is None or abstract1=='' or abstract2=='':
                featVector.append(1)
                return
            t2 = distance.nlevenshtein(abstract1, abstract2)
            featVector.append(t2) 

        def calcTitleHashFeats(title1, title2, featVector):
            if title1 is None or title2 is None or title1=='' or title2=='':
                featVector.append(1)
                return
            title1 = '%x' % Simhash(get_features(normalize(title1))).value
            title2 = '%x' % Simhash(get_features(normalize(title2))).value
            t2 = distance.nlevenshtein(title1, title2)
            featVector.append(t2)

        def calcAbstractHashFeats(abstract1, abstract2, featVector):
            if abstract1 is None or abstract2 is None or abstract1=='' or abstract2=='':
                featVector.append(1)
                return
            abstract1 = '%x' % Simhash(get_features(abstract1)).value
            abstract2 = '%x' % Simhash(get_features(abstract2)).value
            t2 = distance.nlevenshtein(abstract1, abstract2)
            featVector.append(t2)
        def authors_jaccord(a1s,a2s, featVector):
            a1_lasts = set()
            a2_lasts =  set()
            for a in a1s:
                if a['fname'] is not None and a['fname']!='':
                    a1_lasts.add(a['fname'])
                if a['mname'] is not None and a['mname']!='':
                    a1_lasts.add(a['mname'])
                if a['lname'] is not None and a['lname']!='':
                    a1_lasts.add(a['lname'])
            for a in a2s:
                if a['fname'] is not None and a['fname']!='':
                    a2_lasts.add(a['fname'])
                if a['mname'] is not None and a['mname']!='':
                    a1_lasts.add(a['mname'])
                if a['lname'] is not None and a['lname']!='':
                    a1_lasts.add(a['lname'])
            jaccord_value = compute_jaccard_index(a1_lasts, a2_lasts)
            featVector.append(jaccord_value)
        def compute_jaccard_index(set1, set2):
            n = len(set1.intersection(set2))
            return n / float(len(set1) + len(set2) - n + SimilarityProfile.EPS)
        def normalize_authors(authors):
            for author in authors:
                if author['fname'] is not None:
                    author['fname'] = normalize(author['fname'])
                if author['mname'] is not None:
                    author['mname'] = normalize(author['mname'])
                if author['lname'] is not None:
                    author['lname'] = normalize(author['lname'])
        if a1s is None or a2s is None or len(a1s) ==0 or len(a2s)==0:
            featVector.append(0)
            featVector.append(0)
            featVector.append(0)
            featVector.append(0)
            featVector.append(0)
        else:
            normalize_authors(a1s)
            normalize_authors(a2s)
            calcAuthorFeats(a1s[0], a2s[0], featVector)# first author features
            calcAuthorFeats(a1s[len(a1s)-1], a2s[len(a2s)-1], featVector)# last author features
            calcBinaryAuthorFeats(a1s[0], a2s[0], featVector)
            calcBinaryAuthorFeats(a1s[len(a1s)-1], a2s[len(a2s)-1], featVector)
            authors_jaccord(a1s,a2s, featVector)

        calcYearFeats(p1['year'], p2['year'], featVector)
        calcTitleHashFeats(p1['title'], p2['title'], featVector) 
        calcAbstractHashFeats(p1['abstract'], p2['abstract'], featVector)
        calcTitleBOWjaccard(p1['title'], p2['title'], featVector)
        calcAbstractBOWjaccard(p1['abstract'], p2['abstract'], featVector)
        return featVector





