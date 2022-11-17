"""
Modelos de Agente y ambiente (alamacen)
Movimiento de robots en el grid
15-11-2022

Autores: Sebastián González,
         Andreína Sanánez,
         Karla Mondragón,
         Ana Paula Katsuda
"""

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid

class RobotAgent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.direction = 1
        self.carry_box = True

    def move(self):
        """ 
        Determines if the agent can move in the direction that was chosen
        """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right).
            include_center=True) 
        
        # Checks which grid cells are empty
        freeSpaces = list(map(self.model.grid.is_cell_empty, possible_steps))
        print(freeSpaces)

        # if(self.carry_box):
        #     min_distance = abs(self.pos[0] - freeSpaces[0][0]) + abs(self.pos[1] - freeSpaces[0][1])
        #     for space in freeSpaces:
        #         current_distance = abs(self.pos[0] - space[0]) + abs(self.pos[1] - space[1])
        #         if(current_distance < min_distance):
        #             min_distance = current_distance
        #             next_move = space
        #             self.model.grid.move_agent(self, next_move) 
        # else:
        #     # If the cell is empty, moves the agent to that cell; otherwise, it stays at the same position
        #     if freeSpaces[self.direction]:
        #         self.model.grid.move_agent(self, possible_steps[self.direction])
        #         print(f"Se mueve de {self.pos} a {possible_steps[self.direction]}; direction {self.direction}")
        #     else:
        #         print(f"No se puede mover de {self.pos} en esa direccion.")
                           

    def find_closest_station(self):
        """
        Finds the closest station to the agent. Returns a list of possible stations
        """
        # TODO: Hacerlo con list comprehension y scheduler

        stations = [] # list of all existing stations
        closest_station = () # coordinates for the closest station
        
        # Find all Stations and store their coordinates in a list
        for cell in self.grid.coord_iter():
            cell_contents, x, y, = cell
            for agent in cell_contents:
                if isinstance(agent, StationAgent):
                    if(agent.num_boxes < 5):
                        stations.append(list(x, y))
                
        # Initialize minimum distance with distance from agent to first station in list        
        min_distance = abs(self.pos[0] - stations[0][0]) + abs(self.pos[1] - stations[0][1])
        
        # Find the coordinates of the closest station from list of station
        for station in stations:
            current_distance = abs(self.pos[0] - station[0]) + abs(self.pos[1] - station[1])
            if(current_distance < min_distance):
                min_distance = current_distance
                closest_station = tuple(station)

        return closest_station
    
    def pickup_box(self):
        if(not self.carry_box):
            agents = self.model.grid.get_cell_list_contents([self.pos])
            for i in agents:
                if(isinstance(i, BoxAgent)):
                    self.carry_box = True

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        self.direction = self.random.randint(0,8)
        print(f"Agente: {self.unique_id} movimiento {self.direction}")
        self.move()

class ObstacleAgent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass   

class BoxAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        self.move_with_robot()
    
    def move_with_robot(self):
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for i in cell_contents:
            if(isinstance(i, RobotAgent)):
                self.model.grid.move_agent(self, i.pos)


class StationAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.num_boxes = 0
    
    def step(self): 
        pass

class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, N, box_num, width, height):
        self.num_agents = N
        self.grid = MultiGrid(width,height,torus = False) 
        self.schedule = RandomActivation(self)
        self.running = True
        self.box_num = box_num

        # Creates the border of the grid
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]

        for pos in border:
            obs = ObstacleAgent(pos, self)
            #self.schedule.add(obs)
            self.grid.place_agent(obs, pos)

        # Add the station to a random empty grid cell
        for i in range(self.box_num // 5):
            a = StationAgent(i+2000, self) 
            self.schedule.add(a)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(a, pos)

        # Add the robot to a random empty grid cell
        for i in range(self.num_agents):
            a = RobotAgent(i+1000, self) 
            self.schedule.add(a)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(a, pos)

        # Add the box to a random empty grid cell
        for i in range(self.box_num):
            a = BoxAgent(i+3000, self) 
            self.schedule.add(a)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(a, pos)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()