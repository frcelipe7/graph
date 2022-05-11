from turtle import distance
from django.urls import reverse
from django.shortcuts import render
from django.http import request, HttpResponse, HttpResponseRedirect, JsonResponse

from .models import *

def index_view(request):
    all_graphs = Graph.objects.all()
    all_routes = Route.objects.all()
    return render(request, "api_transporte/index.html", {
        #"all_graphs": all_graphs,
        #"all_routes": all_routes
    })


def new_graph_view(request):
    if request.method == "POST":
        routes = request.POST["routes"].split(",")

        route_quantity = len(routes)

        new_graph = Graph(numberOfRoutes=route_quantity)
        new_graph.save()

        for route in routes:
            route = route.strip().upper()
            source = route[0]
            target = route[1]
            distance = route[2]
            graphId = new_graph

            new_route = Route(source=source, target=target, distance=distance, graphId=graphId)

            all_registered_routes = Route.objects.all()
            if all_registered_routes:
                for registered_route in all_registered_routes:

                    if registered_route.source == new_route.source:
                        if registered_route.target == new_route.target:
                            if registered_route.graphId == new_route.graphId:
                                return render(request, "api_transporte/new_graph.html", {
                                    "message": "Error: This route alredy registered in this graph.",
                                    "status_code": 400,
                                    "route": new_route
                                })
                    else:
                        new_route.save()
            else:
                new_route.save()
        return render(request, "api_transporte/new_graph.html", {
            "message": "Success! Graph successfully created.",
            "status_code": 201
        })
    return render(request, "api_transporte/new_graph.html")

'''

## não precisa disso aqui
def graph_api_view(request):
    
    all_graphs_registered = Graph.objects.all()
    all_routes_registered = Route.objects.all()

    graphs_list = []
    graphs_dict = {""}
    for graph in all_graphs_registered:
        graph_dict = {"id": graph.id, "data": []}
        for route in all_routes_registered:
            if graph == route.graphId:
                graph_dict['data'].append(route.serialize())
        ## tenho que adicionar os dois graph_dict no graphs_dict
        graphs_list.append(graph_dict)
    print(f"{graphs_list} final")
    
    return JsonResponse(graphs_dict, safe=False)

'''

def graph_view(request, graphId):
    all_routes = Route.objects.filter(graphId=graphId)
    graph = {"id": graphId, "data": []}
    return JsonResponse({
        "message": "Error: Graph not found.",
        "status_code": 404
    }, safe=False)


def get_routes(graphId, town1, town2, maxStops, getDistance):
    town1 = town1.upper()
    town2 = town2.upper()
    # pega todas as rotas no graph informado pela url (graphId)
    all_routes_in_graph = Route.objects.filter(graphId=graphId)
    routes_list = []
    routes = {"routes": []}
    for route in all_routes_in_graph:
        # zera a variavel de distancia
        if getDistance == True:
            dict_route = {"route": "nothing_yet", "stops": 0, 'distance': 0}
        dict_route = {"route": "nothing_yet", "stops": 0}
        
        # verifica se a rota tem inicio em town1
        if route.source == town1:
            # a rota com inicio em town1 tem final em town2
            if route.target == town2:

                # sem paradas (town2 é considerada uma parada)
                dict_route['route'] = f"{route.source}{route.target}"
                dict_route['stops'] = 1
                if getDistance == True:
                    # determinando a distancia entre as rotas
                    dict_route['distance'] = int(route.distance)
                routes_list.append(dict_route)
            # se a rota não tiver final em town2
            else:
                if maxStops > 1:
                    # pega todas as rotas novamente
                    for route_stopOne in all_routes_in_graph:
                        # verifica se a route_stepOne tem inicio no final de route
                        if route_stopOne.source == route.target:
                            # verifica se route_stopOne tem target em town2
                            if route_stopOne.target == town2:
                                # determinando a distancia entre as rotas
                                #distance_route = int(route.distance) + int(route_stopOne.distance)

                                # com uma parada (2 paradas contando com town2)
                                dict_route['route'] = f"{route.source}{route_stopOne.source}{route_stopOne.target}"
                                dict_route['stops'] = 2
                                if getDistance == True:
                                    # determinando a distancia entre as rotas
                                    dict_route['distance'] = int(route.distance) + int(route_stopOne.distance)
                                routes_list.append(dict_route)
                            # se não tiver ela entra aqui
                            else:
                                if maxStops > 2:
                                    # pega todas as rotas mais uma vez
                                    for route_stopTwo in all_routes_in_graph:
                                        # verifica se route_stepOne termina onde a route_stepTwo começa para dar continuidade no percurso
                                        if route_stopTwo.source == route_stopOne.target:
                                            # verifica se route_stopTwo tem target em town2
                                            if route_stopTwo.target == town2:
                                                # com duas paradas (3 paradas contando com town2)
                                                #distance_route = int(route.distance) + int(route_stopOne.distance) + int(route_stopTwo.distance)

                                                dict_route['route'] = f"{route.source}{route_stopOne.source}{route_stopTwo.source}{route_stopTwo.target}"
                                                dict_route['stops'] = 3
                                                if getDistance == True:
                                                    # determinando a distancia entre as rotas
                                                    dict_route['distance'] = int(route.distance) + int(route_stopOne.distance) + int(route_stopTwo.distance)
                                                routes_list.append(dict_route)
    routes['routes'] = routes_list
    return routes


def routes_view(request, graphId, town1, town2):
    if town1 == town2:
        return JsonResponse(0, safe=False)
    maxStops = request.GET.get("maxStops", "")
    getDistance = False
    
    if maxStops:
        routes = get_routes(graphId, town1, town2, int(maxStops), getDistance)
        return JsonResponse(routes, safe=False)
    maxStops = 3
    
    routes = get_routes(graphId, town1, town2, maxStops, getDistance)
    return JsonResponse(routes, safe=False)


def min_distance_view(request, graphId, town1, town2):
    if town1 == town2:
        return JsonResponse(0, safe=False)
    getDistance = True
    maxStops = 3
    
    routes = get_routes(graphId, town1, town2, maxStops, getDistance)
    if routes['routes'] != []:
        # definindo rota de menor distancia
        rotaMenorDistancia = routes['routes'][0]
        for route in routes['routes']:
            # comparando a rota de menor distancia atual com as outras rotas em routes['routes'] pra ver se tem alguma menor
            if int(route['distance']) < int(rotaMenorDistancia['distance']):
                # se houver a rotaMenorDistancia vai ser atualizada (substituida)
                rotaMenorDistancia = route
        distance = rotaMenorDistancia['distance']
        path = []
        for town in rotaMenorDistancia['route']:
            path.append(str(town))
        return JsonResponse({"distance": distance, "path": path}, safe=False)
    
    # aqui eu inverto as cidades, pq a gente pode ir e voltar por uma mesma estrada (esta é a ideia)
    routes = get_routes(graphId, town2, town1, maxStops, getDistance)
    if routes['routes'] != []:
        # definindo rota de menor distancia
        rotaMenorDistancia = routes['routes'][0]
        for route in routes['routes']:
            # comparando a rota de menor distancia atual com as outras rotas em routes['routes'] pra ver se tem alguma menor
            if int(route['distance']) < int(rotaMenorDistancia['distance']):
                # se houver a rotaMenorDistancia vai ser atualizada (substituida)
                rotaMenorDistancia = route
        distance = rotaMenorDistancia['distance']
        path = []
        for town in rotaMenorDistancia['route']:
            path.append(str(town))
        return JsonResponse({"distance": distance, "path": path}, safe=False)

    return JsonResponse(-1, safe=False)


def api_graph_view(request):
    all_graphs = Graph.objects.all()
    all_routes = Route.objects.all()
    api_graph = []

    for graph in all_graphs:
        graph_and_routes = {"graphId": 1, "routes": ""}
        routes_list = []
        for route in all_routes:
            if route.graphId.id == graph.id:
                graph_and_routes['graphId'] = graph.id
                routes_list.append(route.serialize())
        graph_and_routes["routes"] = routes_list
        api_graph.append(graph_and_routes)
    return JsonResponse([graph_routes for graph_routes in api_graph], safe=False)
