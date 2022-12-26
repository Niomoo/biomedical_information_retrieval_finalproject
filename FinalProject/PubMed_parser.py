from Bio import Entrez
import json
import csv

def search(query):
    Entrez.email = 'jennyliu.lyh@iir.csie.ncku.edu.tw'
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax='1000',
                            retmode='xml', 
                            term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'jennyliu.lyh@iir.csie.ncku.edu.tw'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results

def run():
    results = search('hemodialysis')
    id_list = results['IdList']
    papers = fetch_details(id_list)
    abstractText = []
    for i, paper in enumerate(papers['PubmedArticle']):
        if 'Abstract' in paper['MedlineCitation']['Article']:
            id = paper['MedlineCitation']['PMID']
            title = paper['MedlineCitation']['Article']['ArticleTitle']
            category = 'hemodialysis'
            content = ''
            for text in paper['MedlineCitation']['Article']['Abstract']['AbstractText']:
                content += text
            abstractText.append({'PMID': id, 'title': title, 'category': category, 'content': content})

    with open('hw4/data/hemodialysis.json', 'w') as f:
        json.dump(abstractText, f, indent=2)
        # print("{}) {}".format(i+1, paper['MedlineCitation']['Article']['ArticleTitle']))

results = []
count = 0
with open("depression_search.results.litcovid.tsv", "r", encoding="utf-8") as file:
    for line in file:
        l = line.split('\t')
        results.append(l[0])
        if len(results) == 5000: break
# print(results)

def fetch_covid(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'jennyliu.lyh@iir.csie.ncku.edu.tw'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results

papers = fetch_covid(results)
abstractText = []
for i, paper in enumerate(papers['PubmedArticle']):
    if 'Abstract' in paper['MedlineCitation']['Article']:
        id = paper['MedlineCitation']['PMID']
        title = paper['MedlineCitation']['Article']['ArticleTitle']
        category = 'depression'
        content = ''
        mesh = []
        for text in paper['MedlineCitation']['Article']['Abstract']['AbstractText']:
            content += text
        if 'MeshHeadingList' in paper['MedlineCitation']:
            mesh = paper['MedlineCitation']['MeshHeadingList']
        abstractText.append({'PMID': id, 'title': title, 'category': category, 'content': content, 'MeSHterm': mesh})

with open('depression_data.json', 'w') as f:
    json.dump(abstractText, f, indent=2)
    # print("{}) {}".format(i+1, paper['MedlineCitation']['Article']['ArticleTitle']))