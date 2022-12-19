from Bio import Entrez
import json

def search(query):
    Entrez.email = 'jennyliu.lyh@iir.csie.ncku.edu.tw'
    handle = Entrez.esearch(db='pubmed', 
                            sort='relevance', 
                            retmax='200',
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
