from django.urls import path
from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("graph", views.new_graph_view, name="new_graph"),
    path("graph/<int:graphId>", views.graph_view, name="graph"),
    path("routes/<int:graphId>/from/<str:town1>/to/<str:town2>", views.routes_view,  name="routes"),
    path("distance/<int:graphId>/from/<str:town1>/to/<str:town2>", views.min_distance_view,  name="min_distance"),
    path("graph/api", views.api_graph_view, name="api_graph"),
]
