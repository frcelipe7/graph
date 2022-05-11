from pyexpat import model
from django.db import models

# Create your models here.
class Graph(models.Model):
    numberOfRoutes = models.IntegerField(default=1, blank=False)

    def __str__(self):
        return f"{self.id}"


class Route(models.Model):
    source = models.CharField(max_length=1, blank=False, null=False, default="A")
    target = models.CharField(max_length=1, blank=False, null=False, default="B")
    distance = models.IntegerField(default=6, blank=False)
    graphId = models.ForeignKey(Graph, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.source + self.target + str(self.distance)}"

    def serialize(self):
        return {
            "source":   self.source,
            "target":   self.target,
            "distance": self.distance,
            "graphId":  str(self.graphId)
        }

allModels = [
    Graph,
    Route
]