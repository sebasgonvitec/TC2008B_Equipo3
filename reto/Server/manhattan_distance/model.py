from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
from collections import deque
import json
        
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

        self.corners = [(0,0), (0, self.height - 1), (self.width - 1, 0), (self.width - 1, self.height - 1)]

        # # Create car agent and randomly asign destination
        # rand_dest = self.random.choice(self.destinations)
        # car = Car(1337, self, rand_dest)
        # self.schedule.add(car)
        # self.grid.place_agent(car, (23,24))

        self.num_agents = N
        self.running = True

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
