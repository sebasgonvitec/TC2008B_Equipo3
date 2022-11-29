from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent_graph import *
from collections import deque
import json

class Graph:
    def __init__(self, adjacency_list):
        self.adjacency_list = adjacency_list
        print("Graphs adjacency list: ", self.adjacency_list)

    def get_neighbors(self, v):
        return self.adjacency_list[v]

    # heuristic function with equal values for all nodes
    def h(self, n):
        H = {}
        values = self.adjacency_list.values()
        for value in values:
            for node in value:
                H[node] = 1

        return H[n]

    def a_star_algorithm(self, start_node, stop_node):
        # open_list is a list of nodes which have been visited, but who's neighbors
        # haven't all been inspected, starts off with the start node
        # closed_list is a list of nodes which have been visited
        # and who's neighbors have been inspected
        open_list = set([start_node])
        closed_list = set([])

        # g contains current distances from start_node to all other nodes
        # the default value (if it's not found in the map) is +infinity
        g = {}

        g[start_node] = 0

        # parents contains an adjacency map of all nodes
        parents = {}
        parents[start_node] = start_node

        while len(open_list) > 0:
            n = None

            # find a node with the lowest value of f() - evaluation function
            for v in open_list:
                if n == None or g[v] + self.h(v) < g[n] + self.h(n):
                    n = v;

            if n == None:
                print('Path does not exist!')
                return None

            # if the current node is the stop_node
            # then we begin reconstructin the path from it to the start_node
            if n == stop_node:
                reconst_path = []

                while parents[n] != n:
                    reconst_path.append(n)
                    n = parents[n]

                reconst_path.append(start_node)

                reconst_path.reverse()

                print('Path found: {}'.format(reconst_path))
                return reconst_path

            # for all neighbors of the current node do
            for (m) in self.get_neighbors(n):
                # if the current node isn't in both open_list and closed_list
                # add it to open_list and note n as it's parent
                if m not in open_list and m not in closed_list:
                    open_list.add(m)
                    parents[m] = n
                    g[m] = g[n] + 1

                # otherwise, check if it's quicker to first visit n, then m
                # and if it is, update parent data and g data
                # and if the node was in the closed_list, move it to open_list
                else:
                    if g[m] > g[n] + 1:
                        g[m] = g[n] + 1
                        parents[m] = n

                        if m in closed_list:
                            closed_list.remove(m)
                            open_list.add(m)

            # remove n from the open_list, and add it to closed_list
            # because all of his neighbors were inspected
            open_list.remove(n)
            closed_list.add(n)

        print('Path does not exist!')
        return None
        
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
        self.graph = None
        self.directions = {
            "Up": (1,1),
            "Down": (1,-1),
            "Right": (0,1),
            "Left": (0,-1)
        }

        #with open('2022_base.txt') as baseFile:
        with open('base_prueba.txt') as baseFile:
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

        # Create car agent and randomly asign destination
        rand_dest = self.random.choice(self.destinations)
        car = Car(1337, self, rand_dest)
        self.schedule.add(car)
        self.grid.place_agent(car, (0,1))

        print(self.create_adjacency_list())
        self.graph = Graph(self.create_adjacency_list())
        self.graph.a_star_algorithm((0,1), (4,3))
        #self.graph.a_star_algorithm((6,1), (4,3))

        self.num_agents = N
        self.running = True

        
        
    def create_adjacency_list(self):
        """
        Returns a dictionary of the adjacency list of the grid.
        """
        adjacency_list = {}

        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            for agent in cell_content:
                if isinstance(agent, Road):
                    neighbors = self.grid.get_neighbors(agent.pos, moore = True, include_center = False)
                    for n in neighbors:
                        if(not isinstance(n, Obstacle)):
                            if(n.pos[self.model.directions[agent.direction][0]] == agent.pos[self.model.directions[agent.direction][0]] + self.model.directions[agent.direction][1]):
                                if(agent.pos in adjacency_list):
                                    adjacency_list[agent.pos].append(n.pos)
                                else:
                                    adjacency_list[agent.pos] = [n.pos]
                
                elif isinstance(agent, Traffic_Light):
                    neighbors = self.grid.get_neighbors(agent.pos, moore = True, include_center = False)
                    for n in neighbors:
                        if(not isinstance(n, Obstacle) and not isinstance(n, Traffic_Light)):
                            if(agent.pos in adjacency_list):
                                adjacency_list[agent.pos].append(n.pos)
                            else:
                                adjacency_list[agent.pos] = [n.pos]
                
                    
        return adjacency_list


    def step(self):
        '''Advance the model by one step.'''
        if self.schedule.steps % 10 == 0:
            for agent in self.traffic_lights:
                agent.state = not agent.state
        self.schedule.step()