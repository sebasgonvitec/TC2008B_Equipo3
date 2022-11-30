from heapq import heapify, heappush, heappop
import sys
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
from collections import deque
import json
    
class Graph(Model): 
    def __init__(self):
        self.inter_nodes = []
        

    
class RandomModel(Model):

    # TODO: Fix connections of the graph
    # TODO: Add weights to the graph (cars in route) for every re-route

    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
    """
    def __init__(self, N):

        dataDictionary = json.load(open("mapDictionary.json"))

        self.traffic_lights = []
        self.destinations = []
        #node: [[(coord1), (coord2), (coord3), (coord4)], [(Direction, connected node, weight)]]
        self.graph = {
            1: [[(0,24), (1,24), (0,23), (1,23)], [("Down", 2, 4)]],
            2: [[(0,18),(1,18),(0,17),(1,17)],[("Down", 3, 3), ("Down", 25, 2)]],
            3: [[(0,12),(1,12),(0,11),(1,11)],[("Down", 4, 1)]],
            4: [[(0,9),(1,9),(0,8),(1,8)],[("Down", 5, 6), ("Right", 8, 4)]],
            5: [[(0,1),(1,1),(0,0),(1,0)],[("Right", 9, 4)]],
            6: [[(6,18),(7,18),(6,17),(7,17)],[("Left", 2, 4), ("Left", 24, 3)]],
            7: [[(6,12),(7,12),(6,11),(7,11)],[("Up", 6, 4), ("Left", 3, 4), ("Up", 26, 3)]],
            8: [[(6,9),(7,9),(6,8),(7,8)],[("Right", 13, 5), ("Down", 9, 6), ("Right", 28, 3), ("Down", 27, 4)]],
            9: [[(6,1),(7,1),(6,0),(7,0)],[("Right", 14, 5)]],
            10: [[(13,24),(14,24),(13,23),(14,23)],[("Down", 11, 4), ("Left", 1, 11), ("Down", 29, 3), ("Left", 23, 10)]],
            11: [[(13,18),(14,18),(13,17),(14,17)],[("Left", 6, 5), ("Down", 12, 4), ("Down", 30, 2)]],
            12: [[(13,12),(14,12),(13,11),(14,11)],[("Left", 7, 5), ("Down", 13, 1)]],
            13: [[(13,9),(14,9),(13,8),(14,8)],[("Right", 17, 1), ("Down", 14, 6), ("Down", 31, 4)]],
            14: [[(13,1),(14,1),(13,0),(14,0)],[("Right", 18, 1)]],
            15: [[(16,24),(17,24),(16,23),(17,23)],[("Left", 10, 1)]],
            16: [[(16,12),(17,12),(16,11),(17,11)],[("Up", 15, 10), ("Left", 12, 1), ("Up", 33, 2), ("Up", 32, 8)]],
            17: [[(16,9),(17,9),(16,8),(17,8)],[("Right", 21, 4), ("Up", 16, 1)]],
            18: [[(16,1),(17,1),(16,0),(17,0)],[("Right", 22, 4), ("Right", 34, 2), ("Up", 17, 6)]],
            19: [[(22,24),(23,24),(22,23),(23,23)],[("Left", 15, 4), ("Left", 35, 1)]],
            20: [[(22,12),(23,12),(22,11),(23,11)],[("Up", 19, 10), ("Up", 35, 9),("Left", 16, 4)]],
            21: [[(22,9),(23,9),(22,8),(23,8)],[("Up", 20, 1)]],
            22: [[(22,1),(23,1),(22,0),(23,0)],[("Up", 21, 6), ("Up", 36, 4)]],
            23: [[(3,22)],[("Left", 1, 2)]],
            24: [[(3,19)],[("Left", 2, 2)]],
            25: [[(2,15)],[("Down", 3, 3)]],
            26: [[(5,15)],[("Up", 6, 2)]],
            27: [[(5,4)],[("Down", 9, 3)]],
            28: [[(10,7)],[("Right", 13, 3)]],
            29: [[(12,20)],[("Down", 11, 2)]],
            30: [[(12,15)],[("Down", 12, 3)]],
            31: [[(12,4)],[("Down", 14, 3)]],
            32: [[(18,20)],[("Up", 15, 3)]],
            33: [[(18,14)],[("Up", 15, 9)]],
            34: [[(19,2)],[("Right", 22, 3)]],
            35: [[(21,22)],[("Left", 15, 3), ("Up", 19, 1)]],
            36: [[(21,5)],[("Up", 21, 3)]],
        }
        self.graph_connections = {
            1: {2: 4},
            2: {3: 3, 25: 2},
            3: {4: 1},
            4: {5: 6, 8: 4},
            5: {9: 4},
            6: {2: 4, 24: 3},
            7: {6: 4, 3: 4, 26: 3},
            8: {13: 5, 9: 6, 28: 3, 27: 4},
            9: {14: 5},
            10: {11: 4, 1: 11, 29: 3, 23: 10},
            11: {6: 5, 12: 4, 30: 2},
            12: {7: 5, 13: 1},
            13: {17: 1, 14: 6, 31: 4},
            14: {18: 1},
            15: {10: 1},
            16: {15: 10, 12: 1, 33: 2, 32: 8},
            17: {21: 4, 16: 1},
            18: {22: 4, 34: 2, 17: 6},
            19: {15: 4, 35: 1},
            20: {19: 10, 35: 9, 16: 4},
            21: {20: 1},
            22: {21: 6, 36: 4},
            23: {1: 2},
            24: {2: 2},
            25: {3: 3},
            26: {6: 2},
            27: {9: 3},
            28: {13: 3},
            29: {11: 2},
            30: {12: 3},
            31: {14: 3},
            32: {15: 3},
            33: {15: 9},
            34: {22: 3},
            35: {15: 3, 19: 1},
            36: {21: 3}
        }
        self.directions = {
            # (axis, value)
            # axis: 0=x, 1=y
            # value: direction of movement
            "Up": (1,1),
            "Down": (1,-1),
            "Right": (0,1),
            "Left": (0,-1)
        }
        self.corners = []

        with open('2022_base.txt') as baseFile:
        #with open('base_prueba.txt') as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0])-1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus = False) 
            self.schedule = RandomActivation(self)

            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{c},{self.height - r - 1}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(f"tl_{c},{self.height - r - 1}", self, False if col == "S" else True, int(dataDictionary[col]))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{c},{self.height - r - 1}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{c},{self.height - r - 1}", self)
                        self.destinations.append((c, self.height - r - 1))
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                    elif col == "x": 
                        agent = Intersection(f"int_{c},{self.height - r - 1}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

        self.corners = [(0,0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]

        # # Create car agent and randomly asign destination
        # rand_dest = self.random.choice(self.destinations)
        # car = Car(1337, self, rand_dest)
        # self.schedule.add(car)
        # self.grid.place_agent(car, (23,24))

        self.num_agents = N
        self.running = True
        #print(self.graph.items())
        print(self.dijkstra_algorithm(1))
    
    # def generateIntersectionGraph(self): 
    #     for cell in self.grid.coord_iter():
    #         cell_contents, x, y, = cell
    #         current_node = [[],()]
    #         # Iterate through agent in cell contents
    #         for agent in cell_contents:
    #             if(isinstance(agent, Intersection)): 
    #                 print(agent.pos)
    #                 # neighbors = self.grid.get_neighbors((x,y), moore=True, include_center=True)
    #                 # print("neighbors: ", neighbors)
    #                 # for n in neighbors: 
    #                 #     print("Hey")

    def dijkstra_algorithm(self, start_node):
        distances = self.graph_connections
        nodes = [key for key in range(1, len(distances) + 1)]
        current = start_node
        # These are all the nodes which have not been visited yet
        unvisited = {node: None for node in nodes}
        # It will store the shortest distance from one node to another
        visited = {}
        # It will store the predecessors of the nodes
        currentDistance = 0
        unvisited[current] = currentDistance
        # Running the loop while all the nodes have been visited
        while True:
            # iterating through all the unvisited node
            for neighbour, distance in distances[current].items():
                # Iterating through the connected nodes of current_node (for 
                # example, a is connected with b and c having values 10 and 3
                # respectively) and the weight of the edges
                if neighbour not in unvisited: continue
                newDistance = currentDistance + distance
                if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:
                    unvisited[neighbour] = newDistance
            # Till now the shortest distance between the source node and target node 
            # has been found. Set the current node as the target node
            visited[current] = currentDistance
            del unvisited[current]
            if not unvisited: break
            candidates = [node for node in unvisited.items() if node[1]]
            # for i in candidates: 
            #     if i[0] == 3:
            #         print("heey")

            # print(unvisited)
            # print(current)
            #print(sorted(candidates, key = lambda x: x[1]))
            current, currentDistance = sorted(candidates, key = lambda x: x[1])[0]
        return visited
  
    # nodes = ('A', 'B', 'C', 'D', 'E')
    # distances = {
    #     'A': {'B': 5, 'C': 2},
    #     'B': {'C': 2, 'D': 3},
    #     'C': {'B': 3, 'D': 7},
    #     'D': {'E': 7},
    #     'E': {'D': 9}}
    # current = 'A'
    # print(dijkstra(current, nodes, distances))








        # graph = {
        #     'A': {'B': 2, 'C': 4}, 
        #     'B': {'A': 2, 'C': 3, 'D': 8}, 
        #     'C': {'A': 4, 'B': 3, 'E': 5, 'D': 2}, 
        #     'D': {'B': 8, 'C': 4}, 
        # }
        # print("First", self.graph_connections)
        # max_value = sys.maxsize
        # node_data = {}
        # info_dict = {"cost": max_value, "prev": []}
        # visited = []
        # temp = start_node
        # # graph_list = []
        # # unvisited_nodes = []
        # # unvisited_nodes[current]= current_distance
        # node_data[start_node] = {"cost": 0, "prev": []}
        # for i in range(1, len(graph)):
        #     #info_dict["cost"] = max_value
        #     node_data[i] = info_dict
        # print(node_data)
        # print("Graph",self.graph_connections)
        # for j in range(len(graph)): 
        #     if temp not in visited: 
        #         visited.append(temp)
        #         min_heap = []
        #         for k in graph[temp]: 
        #             print("k value: ", k)
        #             if k not in visited:
        #                 cost = node_data[temp]["cost"] + graph[temp][k]
        #                 if cost < node_data[k]["cost"]:    
        #                     print("siii", cost)
        #                     node_data[k]["cost"] = cost
        #                     node_data[k]["prev"] = node_data[temp]["prev"] + list(temp)
        #                 heappush(min_heap, (node_data[k]["cost"], k))
        #     heapify(min_heap)
        #     print(temp)
        #     print(min_heap)
        #     print(node_data)
        #     temp = min_heap[0][1]
            
        # print("Shortest distance: ", node_data[destination_node]["cost"])
        # print("Shortest path: ", node_data[destination_node]["prev"] )#+ list(destination_node))
        

            


    def step(self):
        '''Advance the model by one step.'''
        if self.schedule.steps % 10 == 0:
            for agent in self.traffic_lights:
                agent.state = not agent.state

        if(self.schedule.steps % 10 == 0 and self.num_agents > 0):
            rand_dest = self.random.choice(self.destinations)
            rand_corner = self.random.choice(self.corners)

            car = Car(self.num_agents + 1000, self, rand_dest)
            self.schedule.add(car)
            self.grid.place_agent(car, rand_corner)

            self.num_agents -= 1

        self.schedule.step()
