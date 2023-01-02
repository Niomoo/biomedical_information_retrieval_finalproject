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
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io

search_info = []


class searchInfo:
    def __init__(self, doc_id, doc_title, doc_content):
        self.doc_id = doc_id
        self.doc_title = doc_title
        self.doc_content = doc_content

def index(request):
    sorted_list = get_sorted_MeSHTerm()
    image_bytes = get_mesh_img('covid', sorted_list[:10])
    return render(request, 'index.html', {
        'covid_img': image_bytes,
    })

def get_value(sort_list, key):
    return [v for k, v in sort_list if key == k]
    
def get_index(sort_list, key):
    for i, item in enumerate(sort_list):
        if item[0] == key:
            return i

def get_sorted_MeSHTerm():
    filepath = os.path.join(PROJECT_ROOT, 'covid_data.json')
    MeSHterm = {}
    with open(filepath) as file:
        jsondata = json.loads(file.read())
        for article in jsondata:
            if len(article['MeSHterm']) != 0:
                for terms in article['MeSHterm']:
                    if terms not in MeSHterm:
                        MeSHterm[terms] = 1
                    else:
                        MeSHterm[terms] += article['MeSHterm'][terms]         
    sorted_MeSHterm = sorted(MeSHterm.items(), key=lambda x: x[1], reverse=True)
    return sorted_MeSHterm

def get_mesh_img(key_word, draw_list):

    fig, ax = plt.subplots(figsize=(15, 8))

    relationships = pd.DataFrame({'from': [key_word, key_word, key_word, key_word, key_word, key_word, key_word, key_word, key_word, key_word], 
                'to':   draw_list})

    # Create DF for node characteristics
    carac = pd.DataFrame({'ID':[key_word, draw_list[0], draw_list[1], draw_list[2], draw_list[3], draw_list[4], draw_list[5], draw_list[6], draw_list[7], draw_list[8], draw_list[9]], 
                'type':['point', 'big', 'big', 'big', 'big', 'mid', 'mid', 'mid', 'sml', 'sml', 'sml']})

    # Create graph object
    G = nx.from_pandas_edgelist(relationships, 'from', 'to', create_using=nx.Graph())

    # Make types into categories
    carac = carac.set_index('ID')
    carac = carac.reindex(G.nodes())

    carac['type'] = pd.Categorical(carac['type'])
    carac['type'].cat.codes

    # Specify colors
    cmap = matplotlib.colors.ListedColormap(['red', 'orange', 'yellow', 'lightgreen'])

    nx.draw(G, with_labels=True, node_color=carac['type'].cat.codes, cmap=cmap, 
            node_size=[2000 if v == 'sml' else 4000 for v in carac['type']])
    buf = io.BytesIO()
    plt.savefig(buf, format='svg', bbox_inches='tight')
    image_bytes = buf.getvalue().decode('utf-8')
    buf.close()
    plt.close()
    return image_bytes

def search(request):
    if request.method == "POST":
        key_word = request.POST['keyword']
        way = request.POST['ranking']
        search_info = []
        articles_set = set()
        pos_5 = []
        neg_5 = []
        if way == "method_mesh":
            filepath = os.path.join(PROJECT_ROOT, 'covid_data.json')
            MeSHterm = {}
            with open(filepath) as file:
                jsondata = json.loads(file.read())
                for article in jsondata:
                    if len(article['MeSHterm']) != 0:
                        if key_word in article['MeSHterm']:
                            for terms in article['MeSHterm']:                          
                                if terms not in MeSHterm:
                                    MeSHterm[terms] = 1
                                else:
                                    MeSHterm[terms] += article['MeSHterm'][terms]            
            sorted_mesh = sorted(MeSHterm.items(), key=lambda x: x[1], reverse=True)
            index = get_index(sorted_mesh, key_word)
            image_bytes = get_mesh_img(key_word, sorted_mesh[index:index+10])
            pos_5 = sorted_mesh[index:index+5]
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

        # Draw graph
        fig, ax = plt.subplots(figsize=(15, 8))

        if way == 'method_mesh':
            pass
        else:
            relationships = pd.DataFrame({'from': [key_word, key_word, key_word, key_word, key_word, key_word, key_word, key_word, key_word, key_word], 
                    'to':   [pos_5[0][0], pos_5[1][0], pos_5[2][0], pos_5[3][0], pos_5[4][0], neg_5[0][0], neg_5[1][0], neg_5[2][0], neg_5[3][0], neg_5[4][0]]})

            # Create DF for node characteristics
            carac = pd.DataFrame({'ID':[key_word, pos_5[0][0], pos_5[1][0], pos_5[2][0], pos_5[3][0], pos_5[4][0], neg_5[0][0], neg_5[1][0], neg_5[2][0], neg_5[3][0], neg_5[4][0]], 
                        'type':['points', 'number', 'number', 'number', 'number', 'number', 'Letter', 'Letter', 'Letter', 'Letter', 'Letter']})

            # Create graph object
            G = nx.from_pandas_edgelist(relationships, 'from', 'to', create_using=nx.Graph())

            # Make types into categories
            carac = carac.set_index('ID')
            carac = carac.reindex(G.nodes())

            carac['type'] = pd.Categorical(carac['type'])
            carac['type'].cat.codes
            # Specify colors
            cmap = matplotlib.colors.ListedColormap(['C0', 'darkorange', 'red'])
            # Set node sizes
            node_sizes = 4000
            # Draw graph
            nx.draw(G, with_labels=True, node_color=carac['type'].cat.codes, cmap=cmap, 
                    node_size=node_sizes)
            buf = io.BytesIO()
            plt.savefig(buf, format='svg', bbox_inches='tight')
            image_bytes = buf.getvalue().decode('utf-8')
            buf.close()
            plt.close()

        # my_chart = image_bytes

        sorted_list = get_sorted_MeSHTerm()
        covid_img = get_mesh_img('covid', sorted_list[:10])

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
            
            return render(request, 'index.html', {
                'search_infos': search_info, 
                'graph':image_bytes,
                'covid_img': covid_img,
            })



