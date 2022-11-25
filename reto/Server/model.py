from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json

class RandomModel(Model):

    # TODO: Add node connections in list to allow mutiple per node
    # TODO: A * Algorithm

    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
    """
    def __init__(self, N):

        dataDictionary = json.load(open("mapDictionary.json"))

        self.traffic_lights = []
        self.destinations = []

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
        #rand_dest = self.random.choice(self.destinations)
        #car = Car(1337, self, rand_dest)
        #self.schedule.add(car)
        #self.grid.place_agent(car, (0,0))

        print(self.create_adjacency_list())
        self.num_agents = N
        self.running = True
        
    def create_adjacency_list(self):
        """
        Returns a dictionary of the adjacency list of the grid.
        """
        adjacency_list = {}

        for cell in self.grid.coord_iter():
            cell_content, x, y = cell
            if cell_content:
                for agent in cell_content:
                    if isinstance(agent, Road):
                        neighbors = self.grid.get_neighbors(agent.pos, moore = False, include_center = False)
                        for n in neighbors:
                            if n:
                                if isinstance(n, Road):
                                    # Node edeges for Road Facing Left
                                    if(agent.direction == "Left"):
                                        # Get 1st and 3rd neighbors
                                        if(n.pos[1] == agent.pos[1] + 1 or n.pos[1] == agent.pos[1] - 1):
                                            if(n.direction != agent.direction or isinstance(n, Traffic_Light) or isinstance(n, Destination)):
                                                adjacency_list[agent.unique_id] = n.unique_id
                                        # # Get 2nd neighbor
                                        elif(n.pos[0] == agent.pos[0]+1):
                                            pass
                                        # Get 4th neighbor
                                        elif(n.pos[0] == agent.pos[0]-1):
                                            adjacency_list[agent.unique_id] = n.unique_id
                                    # Node edeges for Road Facing Left
                                    elif(agent.direction == "Right"):
                                        # Get 1st and 3rd neighbors
                                        if(n.pos[1] == agent.pos[1] + 1 or n.pos[1] == agent.pos[1] - 1):
                                            if(n.direction != agent.direction or isinstance(n, Traffic_Light) or isinstance(n, Destination)):
                                                adjacency_list[agent.unique_id] = n.unique_id
                                        # # Get 4nd neighbor
                                        elif(n.pos[0] == agent.pos[0]-1):
                                            pass
                                        # Get 2th neighbor
                                        elif(n.pos[0] == agent.pos[0]+1):
                                            adjacency_list[agent.unique_id] = n.unique_id
                                    # Node edeges for Road Facing Up
                                    elif(agent.direction == "Up"):
                                        # Get 2nd and 4th neighbors
                                        if(n.pos[0] == agent.pos[0] + 1 or n.pos[0] == agent.pos[0] - 1):
                                            if(n.direction != agent.direction or isinstance(n, Traffic_Light) or isinstance(n, Destination)):
                                                adjacency_list[agent.unique_id] = n.unique_id
                                        # # Get 3rd neighbor
                                        elif(n.pos[1] == agent.pos[1]-1):
                                            pass
                                        # Get 1st neighbor
                                        elif(n.pos[1] == agent.pos[1]+1):
                                            adjacency_list[agent.unique_id] = n.unique_id
                                    
                                    # Node edeges for Road Facing Down
                                    elif(agent.direction == "Down"):
                                        # Get 2nd and 4th neighbors
                                        if(n.pos[0] == agent.pos[0] + 1 or n.pos[0] == agent.pos[0] - 1):
                                            if(n.direction != agent.direction or isinstance(n, Traffic_Light) or isinstance(n, Destination)):
                                                adjacency_list[agent.unique_id] = n.unique_id
                                        # # Get 3rd neighbor
                                        elif(n.pos[1] == agent.pos[1]+1):
                                            pass
                                        # Get 3rd neighbor
                                        elif(n.pos[1] == agent.pos[1]-1):
                                            adjacency_list[agent.unique_id] = n.unique_id
                                elif isinstance(n, Traffic_Light):
                                    adjacency_list[agent.unique_id] = n.unique_id
                                elif isinstance(n, Destination):
                                    adjacency_list[agent.unique_id] = n.unique_id
                                    print("Destination found: ", n.unique_id)
                                else:
                                    pass

                    elif isinstance(agent, Traffic_Light):
                        neighbors = self.grid.get_neighbors(agent.pos, moore = False, include_center = False)
                        for n in neighbors:
                            if n:
                                if isinstance(n, Road):
                                    # Get 1st neighbor
                                    if(n.pos[1] == agent.pos[1] + 1):
                                        if(n.direction != "Down"):
                                            adjacency_list[agent.unique_id] = n.unique_id
                                    # Get 3rd neighbor
                                    elif(n.pos[1] == agent.pos[1] - 1):
                                        if(n.direction != "Up"):
                                            adjacency_list[agent.unique_id] = n.unique_id
                                    # Get 2nd neighbor
                                    elif(n.pos[0] == agent.pos[0]+1):
                                       if(n.direction != "Left"):
                                            adjacency_list[agent.unique_id] = n.unique_id
                                    # Get 4th neighbor
                                    elif(n.pos[0] == agent.pos[0]-1):
                                        if(n.direction != "Right"):
                                            adjacency_list[agent.unique_id] = n.unique_id
                    else:
                        pass
                    
        return adjacency_list
                


    def step(self):
        '''Advance the model by one step.'''
        if self.schedule.steps % 10 == 0:
            for agent in self.traffic_lights:
                agent.state = not agent.state
        self.schedule.step()