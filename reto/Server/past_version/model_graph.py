from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent_graph import *
from collections import deque
import json

# TODO: Add rules for Traffic Lights and Destinations that are not your destination

class Graph:
    def __init__(self, adjacency_list, model):
        self.adjacency_list = adjacency_list
        self.model = model
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
        """
        Determines the route that the agent will take using A*
        """
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

    def bfs(self, start_node, stop_node):
        """
        Determines the route that the agent will take using BFS
        """
        # Create a queue for BFS
        queue = deque()
        queue.append(start_node)

        visited = set()
        visited.add(start_node)

        parents = {}
        parents[start_node] = start_node

        while queue:
            s = queue.popleft()
            if s == stop_node:
                reconst_path = []
                while parents[s] != s:
                    reconst_path.append(s)
                    s = parents[s]
                reconst_path.append(start_node)
                reconst_path.reverse()
                print('Path found: {}'.format(reconst_path))
                return reconst_path

            for i in self.get_neighbors(s):
                if i not in visited:
                    cell_contents = self.model.grid.get_cell_list_contents([i])
                    curr_cell_contents = self.model.grid.get_cell_list_contents([s])
                    for agent in cell_contents:
                        if isinstance(agent, Traffic_Light):
                            for curr_agent in curr_cell_contents:
                                if isinstance(curr_agent, Road) and agent.pos[self.model.directions[curr_agent.direction][2]] == curr_agent.pos[self.model.directions[curr_agent.direction][2]]:
                                    #print("Found traffic light in same direction")
                                    queue.append(i)
                                    visited.add(i)
                                    parents[i] = s
                                else:
                                    break
                        if isinstance(agent, Destination) and agent.pos != stop_node:
                            continue
                        else:
                            for agent in cell_contents:
                                if not isinstance(agent, Traffic_Light):
                                    queue.append(i)
                                    visited.add(i)
                                    parents[i] = s
                                 
        print("No path found")
        return None
        
class RandomModel(Model):
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
            #(eje de relevancia, hacia que direccion,contrario eje de relevancia)
            "Up": (1,1,0),
            "Down": (1,-1,0),
            "Right": (0,1,1),
            "Left": (0,-1,1)
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

        self.corners = [(0,0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]
        
        # Create car agent and randomly asign destination
        # rand_dest = self.random.choice(self.destinations)
        # car = Car(1337, self, (21, 5))
        # self.schedule.add(car)
        # self.grid.place_agent(car, (0,0))

        #print(self.create_adjacency_list())
        self.graph = Graph(self.create_adjacency_list(), self)
        #print("Path to destination: ",self.graph.a_star_algorithm((0,1), (4,3)))
        #self.graph.a_star_algorithm((6,1), (4,3))

        self.num_agents = N
        self.running = True

        
    def create_adjacency_list(self):
        """
        Returns a dictionary of the adjacency list of the grid.
        """
        adjacency_list = {} # position of node : [list of possible steps in coords]

        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            for agent in cell_content:
                # Rules for when the agent we are checking is a road
                if isinstance(agent, Road):
                    neighbors = self.grid.get_neighbors(agent.pos, moore = True, include_center = False)
                    for n in neighbors:
                        if(not isinstance(n, Obstacle)):
                            #Check that the neighbor is of interest (is in the front row relative to direction)
                            if(n.pos[self.directions[agent.direction][0]] == agent.pos[self.directions[agent.direction][0]] + self.directions[agent.direction][1]):
                                
                                #Conditions to check special cases like v>> where some of the front row tiles shouldnt be considered
                                #Condition to only add traffic lights directly in front of you (not diagonals)
                                if(self.directions[agent.direction][0] == 0):
                                    if(n.pos[1] == agent.pos[1]-1 and isinstance(n, Road) and n.direction != "Up"):
                                        if(agent.pos in adjacency_list):
                                            adjacency_list[agent.pos].append(n.pos)
                                        else:
                                            adjacency_list[agent.pos] = [n.pos]
                                    elif(n.pos[1] == agent.pos[1]+1 and isinstance(n, Road) and n.direction != "Down"):
                                        if(agent.pos in adjacency_list):
                                            adjacency_list[agent.pos].append(n.pos)
                                        else:
                                            adjacency_list[agent.pos] = [n.pos]
                                    elif(n.pos[1] == agent.pos[1] and (isinstance(n, Traffic_Light) or isinstance(n, Road))):
                                        if(agent.pos in adjacency_list):
                                            adjacency_list[agent.pos].append(n.pos)
                                        else:
                                            adjacency_list[agent.pos] = [n.pos]
                                else:
                                    if(n.pos[0] == agent.pos[0]-1 and isinstance(n, Road) and n.direction != "Right"):
                                        if(agent.pos in adjacency_list):
                                            adjacency_list[agent.pos].append(n.pos)
                                        else:
                                            adjacency_list[agent.pos] = [n.pos]
                                    elif(n.pos[0] == agent.pos[0]+1 and isinstance(n, Road) and n.direction != "Left"):
                                        if(agent.pos in adjacency_list):
                                            adjacency_list[agent.pos].append(n.pos)
                                        else:
                                            adjacency_list[agent.pos] = [n.pos]
                                    elif(n.pos[0] == agent.pos[0] and (isinstance(n, Traffic_Light) or isinstance(n, Road))):
                                        if(agent.pos in adjacency_list):
                                            adjacency_list[agent.pos].append(n.pos)
                                        else:
                                            adjacency_list[agent.pos] = [n.pos]
                                if isinstance(n, Destination): 
                                    if(agent.pos in adjacency_list):
                                            adjacency_list[agent.pos].append(n.pos)
                                    else:
                                        adjacency_list[agent.pos] = [n.pos]
                                # if(agent.pos in adjacency_list):
                                #     adjacency_list[agent.pos].append(n.pos)
                                # else:
                                #     adjacency_list[agent.pos] = [n.pos]
                            # # Directly in front
                            # if(n.pos[self.directions[agent.direction][0]] == agent.pos[self.directions[agent.direction][0]] + self.directions[agent.direction][1] and n.pos[self.directions[agent.direction][0]] == agent.pos[self.directions[agent.direction][0]]):
                            #     if(agent.pos in adjacency_list):
                            #         adjacency_list[agent.pos].append(n.pos)
                            #     else:
                            #         adjacency_list[agent.pos] = [n.pos]
                            # # Sides of the agent
                            # # TODO: check if conditions for when side is other direction are needed
                            # if(n.pos[self.directions[agent.direction][2]] == agent.pos[self.directions[agent.direction][2]] and n.pos[self.directions[agent.direction][0]] == agent.pos[self.directions[agent.direction][0]]):
                            #     if(not isinstance(n, Traffic_Light)):
                            #         if(agent.pos in adjacency_list):
                            #             adjacency_list[agent.pos].append(n.pos)
                            #         else:
                            #             adjacency_list[agent.pos] = [n.pos]

                            # # Diagonals of the agent
                            # if(n.pos[self.directions[agent.direction][0]] == agent.pos[self.directions[agent.direction][0]] + self.directions[agent.direction][1] and not (n.pos[self.directions[agent.direction][0]] == agent.pos[self.directions[agent.direction][0]])):
                            #     if(isinstance(n, Road)):
                            #         if(n.direction == agent.direction):
                            #             if(agent.pos in adjacency_list):
                            #                 adjacency_list[agent.pos].append(n.pos)
                            #             else:
                            #                 adjacency_list[agent.pos] = [n.pos]
                
                #Traffic lights adds all of its neighbors minus obstacles (graph takes care of the shortest path according to connections)
                elif isinstance(agent, Traffic_Light):
                    neighbors = self.grid.get_neighbors(agent.pos, moore = True, include_center = False)
                    for n in neighbors:
                        if(not isinstance(n, Obstacle) and not isinstance(n, Traffic_Light)):
                            if(agent.pos in adjacency_list):
                                adjacency_list[agent.pos].append(n.pos)
                            else:
                                adjacency_list[agent.pos] = [n.pos]

                # Erase this part when only cars destination is added o
                elif isinstance(agent, Destination):
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

        if(self.schedule.steps % 1 == 0 and self.num_agents > 0):
            rand_dest = self.random.choice(self.destinations)
            rand_corner = self.random.choice(self.corners)

            car = Car(self.num_agents + 1000, self, rand_dest)
            self.schedule.add(car)
            self.grid.place_agent(car, rand_corner)

            self.num_agents -= 1

        self.schedule.step()