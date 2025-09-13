from datetime import datetime

class Paper:
    def __init__(self, title: str, authors: list, published: str, pdf: str):
        self.title = title
        self.authors = authors
        if type(published)==str:
            self.published = datetime.fromisoformat(published.replace("Z", "+00:00"))
        else:
            self.published = published
        self.pdf = pdf
    def __eq__(self, other):
        return ((isinstance(other, Paper) or isinstance(other, Paper_Output))
         and self.title == other.title
         and self.authors == other.authors
         and self.published == other.published
         and self.pdf == other.pdf)
    
    def to_dict(self):
        return {
            "title": self.title,
            "authors": self.authors,
            "published": self.published.isoformat() if hasattr(self.published, "isoformat") else str(self.published),
            "pdf": self.pdf
        }

class Paper_Output:
    def __init__(self, **kwargs):
        paper = kwargs.get("paper", None)

        if paper:
            self.title = paper.title
            self.authors = paper.authors
            if isinstance(paper.published, datetime):
                self.published = paper.published
            elif isinstance(paper.published, str):
                self.published = datetime.fromisoformat(paper.published)
            self.pdf = paper.pdf
        else:
            self.title = kwargs.get("title")
            self.authors = kwargs.get("authors")
            self.published = datetime.fromisoformat(kwargs.get("published"))
            self.pdf = kwargs.get("pdf")

        self.rating = kwargs.get("rating")
        self.genuinity = kwargs.get("genuinity")
        self.summary = kwargs.get("summary")
    def __eq__(self, other):
        return ((isinstance(other, Paper) or isinstance(other, Paper_Output))
         and self.title == other.title
         and self.authors == other.authors
         and self.published == other.published
         and self.pdf == other.pdf)

class Paper_List:
    def __init__(self):
        self.papers = []
    def exist(self, paper: Paper) -> bool:
        return paper in self.papers
    def add(self, paper: Paper) -> bool:
        if paper not in self.papers:
            self.papers.append(paper)
            return True
        else:
            return False
    def reset_to_output(self, papers:Paper_Output):
        self.papers = []
        for paper in papers:
            self.add(Paper(paper.title, paper.authors, paper.published, paper.pdf))