from django.db import models
from .paper import Paper_Output

class Paper_Output_List(models.Model):
    papers = models.JSONField(default=list)
    
    @classmethod
    def instance(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj
    def get_papers(self):
        return [Paper_Output(**paper) for paper in (self.papers or [])]
    def exist(self, paper: Paper_Output) -> bool:
        return paper in self.get_papers()
    def add(self, paper: Paper_Output) -> bool:
        if paper in self.get_papers():
            return False
        self.papers.append({
            "title": paper.title, 
            "authors": paper.authors, 
            "published": paper.published.isoformat() if paper.published else None,
            "pdf": paper.pdf, 
            "rating": paper.rating, 
            "genuinity": paper.genuinity, 
            "summary": paper.summary
        })
        self.save()
        return True