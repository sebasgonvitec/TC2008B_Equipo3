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

# TODO: Ir a la estación después de agarrar una caja
# TODO: Dejar la caja en la estación y continuar comportamiento random

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
        #self.direction = 1
        self.carry_box = False
        self.box = None
        self.unique_id = unique_id

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

        next_moves = [p for p,f in zip(possible_steps, freeSpaces) if f == True]
    
        # Lista de agentes vecinos
        neighList = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True)

        # if(self.carry_box):
        #     min_distance = abs(next_moves[0][0] - self.find_closest_station()[0]) + abs(next_moves[0][1] - self.find_closest_station()[1])
        #     for move in next_moves:
        #          current_distance = abs(move[0] - self.find_closest_station()[0]) + abs(move[1] - self.find_closest_station()[1])
        #          if(current_distance < min_distance):
        #              min_distance = current_distance
        #              next_move = move
        #              print("Next Move station:", next_move)
        #              self.model.grid.move_agent(self, next_move) 

        # else:
        #     if(len(next_moves) > 0):
        #         next_move = self.random.choice(next_moves)
        #     else:
        #         next_move = self.pos
        #     # 
        #     for neighbor in neighList:
        #         if(isinstance(neighbor, BoxAgent) and neighbor.pos == self.pos):
        #             self.grab_box()
        #         elif(isinstance(neighbor, BoxAgent) and neighbor.pos != self.pos and not self.carry_box):
        #             next_move = neighbor.pos

        #     self.model.grid.move_agent(self, next_move)      
        #     if(self.carry_box):
        #         self.box.model.grid.move_agent(self.box, next_move)

        if(len(next_moves) > 0):
            next_move = self.random.choice(next_moves)
        else:
            next_move = self.pos

        for neighbor in neighList:
            if(isinstance(neighbor, BoxAgent) and neighbor.pos == self.pos):
                self.grab_box()
            elif(isinstance(neighbor, BoxAgent) and neighbor.pos != self.pos and not self.carry_box):
                next_move = neighbor.pos
            
        self.model.grid.move_agent(self, next_move)      
        if(self.carry_box):
            self.box.model.grid.move_agent(self.box, next_move)

        if(self.carry_box):
            print("Closest station: ", self.find_closest_station())

    def find_closest_station(self):
        """
        Finds the closest station to the agent. Returns a list of possible stations
        """
        # TODO: Hacerlo con list comprehension y scheduler
        # TODO: Hacerlo igual que método para mover a una celda

        stations = [] # list of all existing stations
        closest_station = () # coordinates for the closest station
        
        # Find all Stations and store their coordinates in a list
        for cell in self.model.grid.coord_iter():
            cell_contents, x, y, = cell
            for agent in cell_contents:
                if isinstance(agent, StationAgent):
                    if(agent.num_boxes < 5):
                        stations.append((x, y))
        
        # Initialize minimum distance with distance from agent to first station in list        
        min_distance = abs(self.pos[0] - stations[0][0]) + abs(self.pos[1] - stations[0][1])

        # Find the coordinates of the closest station from list of stations
        for station in stations:
            #print("Station: ", station)
            current_distance = abs(self.pos[0] - station[0]) + abs(self.pos[1] - station[1])
            #print("Current Distance", current_distance)
            if(current_distance <= min_distance):
                #print("Distance updated")
                min_distance = current_distance
                closest_station = tuple(station)

        return closest_station
    
    def move_to_cell(self, cell):
        """
        Method to move agent to a certain cell
        """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, # Boolean for whether to use Moore neighborhood (including diagonals) or Von Neumann (only up/down/left/right).
            include_center=True) 
        
        # Checks which grid cells are empty
        freeSpaces = list(map(self.model.grid.is_cell_empty, possible_steps))

        # Stores all possible moves
        next_moves = [p for p,f in zip(possible_steps, freeSpaces) if f == True]
        distances = []

        # Calculate manhattan distances from possible moves to point
        for move in next_moves:
            distances.append(abs(move[0] - cell[0]) + abs(move[1] - cell[1]))

        # Minimun distance from list
        min_distance = min(distances)
       
        # Set next move to corresponding minimum distance
        next_move = next_moves[distances.index(min_distance)]
    
        self.model.grid.move_agent(self, next_move)   

        
    def grab_box(self):
        """
        Method to check if there is a box in same position as self and grab it.
        """
        if(not self.carry_box):
            agents = self.model.grid.get_cell_list_contents([self.pos])
            for i in agents:
                if(isinstance(i, BoxAgent) and not i.taken):
                    self.box = i
                    self.box.taken = True
                    self.carry_box = True
                    break

    def step(self):
        """ 
        Moves the robot agent.
        """
        #self.move()
        #self.move_to_station((10, 1))

class ObstacleAgent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass   

class BoxAgent(Agent):
    """
    Box agent. 
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.taken = False

    def step(self):
        pass
    

class StationAgent(Agent):
    """
    Station agent. 
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.num_boxes = 0
    
    def step(self): 
        pass

#########################################################################################################################################

class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, N, width, height, box_num):
        self.num_agents = N
        self.grid = MultiGrid(width,height,torus = False) 
        self.schedule = RandomActivation(self)
        self.running = True 
        self.box_num = box_num
        self.station_num = box_num // 5

        #Calculate Number of Stations
        if(box_num % 5 != 0):
            self.station_num+=1

        # Creates the border of the grid
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]
        
        # Build Border
        for pos in border:
            obs = ObstacleAgent(pos, self)
            self.schedule.add(obs)
            self.grid.place_agent(obs, pos)

        # Place Stations
        sides = [0, 0, 0, 0]
        indx = 0

        #Determine number of stations per side
        for i in range(self.station_num):
            if(indx<=3):
                sides[indx]+=1
                indx+=1
            else:
                indx=0
                sides[indx]+=1
                indx+=1
        #Determine coords for each side
        station_coords = []
        y_up = False
        x_left = False
        y=1
        x=1

        #Iterate over every side
        for i in range(len(sides)):
            if(sides[i]!=0):
                #For horizontal sides
                if(i < 2):
                    if(y_up):
                        y = self.grid.height-2
                    div = self.grid.width // sides[i] 
                    res = div // 2
                    for j in range(sides[i]):
                        station_coords.append((res, y))
                        y_up=True
                        res+=div

                #For vertical sides
                if(i >= 2):
                    if(x_left):
                        x = self.grid.width-2
                    div = self.grid.height // sides[i] 
                    res = div // 2
                    for j in range(sides[i]):
                        station_coords.append((x, res))
                        x_left=True
                        res+=div

        #Instanciate Station Agent
        for pos in station_coords:
            station = StationAgent(pos, self)
            self.schedule.add(station)
            self.grid.place_agent(station, pos)


        # Add the agent to a random empty grid cell
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