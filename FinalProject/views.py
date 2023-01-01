import xml.etree.ElementTree as ET
from django.shortcuts import render
from django.shortcuts import redirect   # redirect to the template file
from django.http import HttpResponse    # return data instead of rendering template
from django.core.files.storage import FileSystemStorage
from django.conf import settings
#from BIR.settings import PROJECT_ROOT
# Python program to read json file
from gensim.models import word2vec
from gettext import find
import json
import re
import pandas as pd
import numpy as np
import os
import sys
#from textblob import Word
from collections import Counter
from sklearn.metrics.pairwise import linear_kernel
from BIR.settings import PROJECT_ROOT

search_info = []


class searchInfo:
    def __init__(self, doc_id, doc_title, doc_content):
        self.doc_id = doc_id
        self.doc_title = doc_title
        self.doc_content = doc_content

def index(request):
    return render(request, 'index.html')

def search(request):
    if request.method == "POST":
        key_word = request.POST['keyword']
        way = request.POST['ranking']
        search_info = []
        articles_set = set()
        pos_5 = []
        neg_5 = []
        if way == "method_mesh":
            pass
        elif way == "method_sg":
            model = word2vec.Word2Vec.load(os.path.join(PROJECT_ROOT, 'sg_depression_data.model'))

            for item in model.wv.most_similar(key_word, topn=5):
                #print(item)
                pos_5.append(item)

            for item in model.wv.most_similar(negative=[key_word], topn=5):
                #print(item)
                neg_5.append(item)
            
        elif way == "method_cbow":
            model = word2vec.Word2Vec.load(os.path.join(PROJECT_ROOT, 'cbow_depression_data.model'))


            for item in model.wv.most_similar(key_word, topn=5):
                # print(item)
                pos_5.append(item)

            for item in model.wv.most_similar(negative=[key_word], topn=5):
                # print(item)
                neg_5.append(item)
            
        # Show the data
        with open(os.path.join(PROJECT_ROOT, 'depression_data.json'), "r", encoding="utf-8") as f:
            data = json.load(f)
            for (word, scores) in pos_5:
                for articles in data:
                    if word in articles["title"] and articles["PMID"] not in articles_set:
                        articles_set.add(articles["PMID"])
                        search_info.append(searchInfo(articles["PMID"], articles["title"], articles["content"]))
                    elif word in articles["content"] and articles["PMID"] not in articles_set:
                        articles_set.add(articles["PMID"])
                        search_info.append(searchInfo(articles["PMID"], articles["title"], articles["content"]))
            
            return render(request, 'index.html', {'search_infos': search_info})



