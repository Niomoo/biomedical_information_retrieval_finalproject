from Bio import Entrez
import json
import csv

def read_file(filename, num):
    results = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            l = line.split('\t')
            results.append(l[0])
            if len(results) == num: break
        return results
# print(results)

def fetch_covid(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'jennyliu.lyh@iir.csie.ncku.edu.tw'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results

def save_file(filename, results, category):
    papers = fetch_covid(results)
    abstractText = []
    for i, paper in enumerate(papers['PubmedArticle']):
        if 'Abstract' in paper['MedlineCitation']['Article']:
            id = paper['MedlineCitation']['PMID']
            title = paper['MedlineCitation']['Article']['ArticleTitle']
            content = ''
            mesh = {}
            for text in paper['MedlineCitation']['Article']['Abstract']['AbstractText']:
                content += text
            if 'MeshHeadingList' in paper['MedlineCitation']:
                for terms in paper['MedlineCitation']['MeshHeadingList']:
                    for term in terms['QualifierName']:
                        if term not in mesh:
                            mesh[term] = 1
                        else:
                            mesh[term] += 1
                    if terms['DescriptorName'] not in mesh:
                        mesh[terms['DescriptorName']] = 1
                    else:
                        mesh[terms['DescriptorName']] += 1         
            abstractText.append({'PMID': id, 'title': title, 'category': category, 'content': content, 'MeSHterm': mesh})
    with open(filename, 'w') as f:
        json.dump(abstractText, f, indent=2)

results = read_file('data/covid_search.results.litcovid.tsv', 5000)
save_file('data/covid_data.json', results, 'covid')
results = read_file('data/depression_search.results.litcovid.tsv', 2000)
save_file('data/depression_data.json', results, 'depression')