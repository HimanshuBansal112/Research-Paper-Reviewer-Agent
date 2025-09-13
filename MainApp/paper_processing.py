import feedparser
import urllib.parse
import time

import requests
from io import BytesIO
from langchain_community.document_loaders import PyPDFLoader
import tempfile

from .shared_variable import papers
from .models import Paper_Output_List
from .paper import Paper, Paper_Output, Paper_List

def fetch_papers(offset: int):
    base_url = "https://export.arxiv.org/api/query"
    search_query = urllib.parse.quote("cat:cs.AI OR cat:cs.LG OR cat:stat.ML OR cat:cs.MA OR cat:cs.NE")
    start = offset
    max_results = 100
    sort_by = "submittedDate"
    sort_order = "descending"

    query = (
        f"{base_url}?search_query={search_query}"
        f"&start={start}&max_results={max_results}"
        f"&sortBy={sort_by}&sortOrder={sort_order}"
    )

    feed = feedparser.parse(query)
    tries = 0
    while len(feed.entries) == 0:
        if tries>=10:
            break
        start += 1
        max_results -= 1
        query = (
            f"{base_url}?search_query={search_query}"
            f"&start={start}&max_results={max_results}"
            f"&sortBy={sort_by}&sortOrder={sort_order}"
        )
        feed = feedparser.parse(query)
    for entry in feed.entries:
        papers.add(Paper(title=entry.title, authors=[author.name for author in entry.authors], published=entry.published, pdf=entry.links[1].href))
        #if papers.add(Paper(title=entry.title, authors=[author.name for author in entry.authors], published=entry.published, pdf=entry.links[1].href)):
        #    print("✅ New found")
        #else:
        #    print("❌ Existing/old found")

def grab_paper(papers: Paper_List, index: int):
    response = requests.get(papers.papers[index].pdf)
    pdf_file = BytesIO(response.content)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.getbuffer())
        temp_path = tmp_file.name
    
    loader = PyPDFLoader(temp_path)
    documents = loader.load()
    return documents
def combine_pdf(document):
    return "\n".join(page.page_content for page in document)
    
def unread_paper():
    papers_output = Paper_Output_List.instance().get_papers()
    return [x for x in papers.papers if x not in papers_output]
    
def get_paper(index: int) -> str:
    return combine_pdf(grab_paper(papers,index))