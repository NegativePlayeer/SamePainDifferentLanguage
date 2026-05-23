import requests
from lxml import etree
import json
import time


def search_pubmed(query, max_results):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}

    response = requests.get(url, params=params)
    data = response.json()
    return data["esearchresult"]["idlist"]


def fetch_abstract(pubmed_id):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": pubmed_id, "retmode": "xml", "rettype": "abstract"}

    response = requests.get(url, params=params)

    content = response.content
    content = content.replace(
        b'<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2025//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_250101.dtd">',
        b"",
    )

    tree = etree.fromstring(content)
    abstract = tree.find(".//AbstractText")

    if abstract is not None:
        return abstract.text
    return "Text does not exist"


def get_abstracts(query, max_results=50):
    ids = search_pubmed(query=query, max_results=max_results)

    abstracts = []

    for id in ids:
        abstract = fetch_abstract(id)
        if abstract:
            abstracts.append(abstract)
        time.sleep(0.5)
    return abstracts


# depression_abstracts = get_abstracts("depression", max_results=50)


def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# save_to_json(depression_abstracts, "data/raw/pubmed_depression.json")


for feature in ["depression", "chronic pain", "neurology brain"]:
    save_to_json(
        get_abstracts(feature, max_results=50),
        f"data/raw/pubmed_{feature.replace(' ', '_')}.json",
    )
