from Bio import Entrez
import json
import csv

results = []
count = 0
with open("data/depression_search.results.litcovid.tsv", "r", encoding="utf-8") as file:
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

with open('data/depression_data.json', 'w') as f:
    json.dump(abstractText, f, indent=2)
    # print("{}) {}".format(i+1, paper['MedlineCitation']['Article']['ArticleTitle']))