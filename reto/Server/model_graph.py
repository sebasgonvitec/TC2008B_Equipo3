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


    def get_neighbors(self, v):
        """
        Function to get the neighbors of a node in the adjacency list
        """
        return self.adjacency_list[v]


    def bfs(self, start_node, stop_node):
        """
        Determines the route that the agent will take using BFS
        """
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
                #print('Path found: {}'.format(reconst_path))
                return reconst_path

            for i in self.get_neighbors(s):
                if i not in visited:
                    cell_contents = self.model.grid.get_cell_list_contents([i])
                    curr_cell_contents = self.model.grid.get_cell_list_contents([s])
                    for agent in cell_contents:
                        if isinstance(agent, Traffic_Light):
                            for curr_agent in curr_cell_contents:
                                if isinstance(curr_agent, Road) and agent.pos[self.model.directions[curr_agent.direction][2]] == curr_agent.pos[self.model.directions[curr_agent.direction][2]]:
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
    
        self.graph = Graph(self.create_adjacency_list(), self)

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
        """
        Advance the model by one step.
        """
        if self.schedule.steps % 10 == 0:
            for agent in self.traffic_lights:
                agent.state = not agent.state

        if(self.schedule.steps % 3 == 0 and self.num_agents > 0):
            if(self.num_agents > 0):
                # rand_dest = self.random.choice(self.destinations)
                # rand_corner = self.random.choice(self.corners)

                # car = Car(self.num_agents + 1000, self, rand_dest)
                # self.schedule.add(car)
                # self.grid.place_agent(car, rand_corner)

                # self.num_agents -= 1
                
                rand_dest = self.random.choice(self.destinations)
                rand_corner = self.corners[0]

                car = Car(self.num_agents + 1000, self, rand_dest)
                self.schedule.add(car)
                self.grid.place_agent(car, rand_corner)

                self.num_agents -= 1

                rand_dest = self.random.choice(self.destinations)
                rand_corner = self.corners[1]

                car = Car(self.num_agents + 1000, self, rand_dest)
                self.schedule.add(car)
                self.grid.place_agent(car, rand_corner)

                self.num_agents -= 1

                rand_dest = self.random.choice(self.destinations)
                rand_corner = self.corners[2]

                car = Car(self.num_agents + 1000, self, rand_dest)
                self.schedule.add(car)
                self.grid.place_agent(car, rand_corner)

                self.num_agents -= 1

                rand_dest = self.random.choice(self.destinations)
                rand_corner = self.corners[3]

                car = Car(self.num_agents + 1000, self, rand_dest)
                self.schedule.add(car)
                self.grid.place_agent(car, rand_corner)

                self.num_agents -= 1

        self.schedule.step()