"""
Agents and storage models
Robots movements in the grid
15-11-2022

Authors: Sebastián González, A01029746
         Andreína Sanánez, A01024927
         Karla Mondragón, A01025108
         Ana Paula Katsuda, A01025303
"""

# Imports
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid

# Class for robot agents 
class RobotAgent(Agent):
    """
    Agent that moves randomly unless a box is detected or grabbed.
    Agent moves towards box when it detects one and is not grabbing anything.
    Agent moves towards closest station when grabbing a box 
    Attributes:
        unique_id: Agent's ID 
        
    """
    def __init__(self, unique_id, model):
        """
        Creates a new robot agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        # Definition of attributes
        self.carry_box = False # Indicates if agent is carrying box
        self.box = None # Points to a box agent
        self.unique_id = unique_id # Defines agent id
        self.last_move = None # Indicates agent's previous move
        self.steps_taken = 0 # Indicates the number of steps taken by agent
        self.grabbed_boxes = 0 # Indicates the number of boxes grabbed by agent

    # Definition of robot movement
    def move(self):
        """ 
        Determines the direction in which agents needs to move
        """
        # Define possible steps 
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, # Current position
            moore=False, # Only allow Von Neumann movement (only up/down/left/right).
            include_center=True) # Current position is an option
        
        # Checks which grid cells are empty
        freeSpaces = list(map(self.model.grid.is_cell_empty, possible_steps))
        
        # Gets possible moves considering empty coordinates
        next_moves = [p for p,f in zip(possible_steps, freeSpaces) if f == True]
    
        # List of neighbor agents --> considering Von Neumann and current position (center)
        neighList = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True)

        # If the agent has possible moves
        if(len(next_moves) > 0):
            # move to a random cell
            next_move = self.random.choice(next_moves)
        # If the agent doesn't have possible moves
        else:
            # Stay in current position
            next_move = self.pos

        # Iterate through neighbor list
        for neighbor in neighList:
            # if the robot agent is in the same position as a box agent
            if(isinstance(neighbor, BoxAgent) and neighbor.pos == self.pos):
                # Grab the box
                self.grab_box()
            # if the robot agent is not carrying a box, the box detected isn't in station and the agent isn't in the same cell as box
            elif(isinstance(neighbor, BoxAgent) and neighbor.pos != self.pos and not self.carry_box and not neighbor.inStation):
                # move towards box
                next_move = neighbor.pos
        
        # If the robot is carrying box
        if(self.carry_box):
            print("Closest station: ", self.find_closest_station())
            # Define its closest station
            station = self.find_closest_station() 
            # Determine cell to move to (cell that implies the min distance to station)
            next_move= self.move_to_cell(station)
            # Move box to next position
            self.box.model.grid.move_agent(self.box, next_move)
            # If the next move coords are the same as station coords
            if(next_move == station):
                #Keep agent in its current position 
                next_move = self.pos
                # stop carrying box
                self.carry_box = False
                self.box.inStation = True
                self.grabbed_boxes+=1
                self.model.picked_boxes+=1
        
        if(next_move != self.pos):
            self.model.grid.move_agent(self, next_move) 
            self.steps_taken+=1
            

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
                    if(agent.get_num_boxes() < 5):
                        stations.append((x, y))
                        #print("Station number of boxes: ", agent.get_num_boxes())
        
        #print("stations1: ", stations)
        # Initialize minimum distance with distance from agent to first station in list        
        min_distance = abs(self.pos[0] - stations[0][0]) + abs(self.pos[1] - stations[0][1])
        closest_station = stations[0]

        # Find the coordinates of the closest station from list of stations
        for station in stations:
            print("Self: ", self.pos)
            print("Station: ", station)
            current_distance = abs(self.pos[0] - station[0]) + abs(self.pos[1] - station[1])
            print("Current Distance", current_distance)
            #print("Closest Station: ", closest_station)
            if(current_distance <= min_distance):
                #print("Distance updated")
                min_distance = current_distance
                closest_station = tuple(station)
                print("new closest station: ", closest_station)

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
        neighList = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True)

                
        # Stores all possible moves
        next_moves = [p for p,f in zip(possible_steps, freeSpaces) if f == True]
        for neighbor in neighList:
            if(isinstance(neighbor, StationAgent)):
                next_moves.append(neighbor.pos)
        distances = []
        
        if len(next_moves) == 0:
            next_moves.append(self.pos)

        print("Last move: ", self.last_move)
        print("Next moves: ", next_moves)

        if(not (len(next_moves) == 1) and self.last_move in next_moves):
            if self.last_move != None:
                next_moves.remove(self.last_move)

        # Calculate manhattan distances from possible moves to point
        for move in next_moves:
            distances.append(abs(move[0] - cell[0]) + abs(move[1] - cell[1]))

        # Minimun distance from list
        min_distance = min(distances)
        # print(min_distance)

        # Set last move to current position before moving to new cell
        self.last_move = self.pos
        # Set next move to corresponding minimum distance
        next_move = next_moves[distances.index(min_distance)] 
    
        return next_move

        
    def grab_box(self):
        """
        Method to check if there is a box in same position as self and grab it.
        """
        if(not self.carry_box):
            agents = self.model.grid.get_cell_list_contents([self.pos])
            for i in agents:
                if(isinstance(i, BoxAgent) and not i.taken and not i.inStation):
                    self.box = i
                    self.box.taken = True
                    self.carry_box = True
                    break

    def step(self):
        """ 
        Moves the robot agent.
        """
        self.move()
        #self.move_to_cell((10, 1))
        #self.find_closest_station()

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
        self.inStation = False

    def step(self):
        pass
    

class StationAgent(Agent):
    """
    Station agent. 
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
    
    def get_num_boxes(self):
        boxes = 0
        agents = self.model.grid.get_cell_list_contents([self.pos])
        for i in agents:
            if(isinstance(i, BoxAgent)):
                boxes += 1
        print("Number of boxes: ", boxes)
        return boxes
        
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
        self.steps = 0
        self.picked_boxes = 0
       

        self.datacollector = DataCollector( 
        model_reporters={"Global Steps": lambda m: self.steps},
        agent_reporters={"Steps": lambda a: a.steps_taken if isinstance(a, RobotAgent) else 0, "Grabbed Boxes": lambda b: b.grabbed_boxes if isinstance(b, RobotAgent) else 0})
        

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
            a = BoxAgent(i+2000, self) 
            self.schedule.add(a)

            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)
            self.grid.place_agent(a, pos)

    def step(self):
        '''Advance the model by one step.'''

        #Evaluate if all the boxes have been placed in a station
        if(self.picked_boxes == self.box_num):
            
            #Print Robot data
            for cell in self.grid.coord_iter():
                cell_content, x, y = cell
                for agent in cell_content:
                    if isinstance(agent, RobotAgent):
                        print("Robot ", agent.unique_id)
                        print("Steps: ", agent.steps_taken)
                        print("Grabbed Boxes", agent.grabbed_boxes)
                        print("\n")
            
            #Print Time/Global Steps
            print("Time/Global Steps: ", self.steps)

            self.running = False #stop the program
                        
        self.schedule.step()
        self.steps+=1
