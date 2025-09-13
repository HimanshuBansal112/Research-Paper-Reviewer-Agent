import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from .shared_variable import llm, papers
from .models import Paper_Output_List
from .paper_processing import fetch_papers, unread_paper
from .agent import agent

def index(request):
    return render(request, "MainApp/index.html")

def fetch(request):
    offset = 0
    while len(unread_paper())<10:
        fetch_papers(offset)
        offset += 100
    return render(request, "MainApp/paper_process.html", {"papers":unread_paper()[:10]})

def display(request):
    return render(request, "MainApp/display.html", {"papers":Paper_Output_List.instance().get_papers()})

@require_POST
def process(request):
    if request.method == "POST":
        data = json.loads(request.body)
        title = data.get('title')
        pdf = data.get('pdf')
        done = False
        
        offset = len(papers.papers)
        batch_size = 100
        for i, paper in enumerate(papers.papers):
            title_paper = " ".join(line.strip() for line in paper.title.splitlines())
            if title_paper.strip() == title.strip() and paper.pdf.strip() == pdf.strip():
                paper_index = i
                done = True
        while not done:
            fetch_papers(offset)
            offset += batch_size
            if offset >= 2000:
                print("Paper isn't getting found")
                json_data = json.dumps([paper.to_dict() for paper in papers.papers])
                with open("paper.json", "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=4, ensure_ascii=False)
                return JsonResponse({"done": False, "message": "Paper isn't getting found"})
            for i, paper in enumerate(papers.papers[-batch_size:]):
                title_paper = " ".join(line.strip() for line in paper.title.splitlines())
                if title_paper.strip() == title.strip() and paper.pdf.strip() == pdf.strip():
                    paper_index = len(papers.papers) - batch_size + i
                    done = True
                    break
        
        try:
            agent(paper_index)
            return JsonResponse({"done": True})
        except Exception as e:
            return JsonResponse({"done": False, "message": str(e)})
    return HttpResponse("Invalid Request")