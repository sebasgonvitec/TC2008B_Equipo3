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
                # Set box so it indicates it is in station
                self.box.inStation = True
                # Count one more box as grabbed
                self.grabbed_boxes+=1
                # Count one more as picked boxes
                self.model.picked_boxes+=1
        # If next move isn't current position
        if(next_move != self.pos):
            # move agent
            self.model.grid.move_agent(self, next_move) 
            # count agent step
            self.steps_taken+=1
            
    # Function to find the coords of the closest station
    def find_closest_station(self):
        """
        Finds the closest station to the agent. Returns coordinates of the station
        """
        
        stations = [] # list of all existing stations
        closest_station = () # coordinates for the closest station
        
        # Find all Stations and store their coordinates in a list
        for cell in self.model.grid.coord_iter():
            # Cell information
            cell_contents, x, y, = cell
            # Iterate through agent in cell contents
            for agent in cell_contents:
                # if the agent is a station
                if isinstance(agent, StationAgent):
                    # if the station contains less than 5 boxes
                    if(agent.get_num_boxes() < 5):
                        # Add station to list of possible stations
                        stations.append((x, y))
        
        # Initialize minimum distance with distance from agent to first station in list        
        min_distance = abs(self.pos[0] - stations[0][0]) + abs(self.pos[1] - stations[0][1])
        # Initialize closest station with first station in list
        closest_station = stations[0]

        # Find the coordinates of the closest station from list of stations
        for station in stations:
            print("Self: ", self.pos)
            print("Station: ", station)
            # Determine the current distance from agent to the station
            current_distance = abs(self.pos[0] - station[0]) + abs(self.pos[1] - station[1])
            print("Current Distance", current_distance)
            # if the current distance is smaller than the minimum distance
            if(current_distance <= min_distance):
                #Set current distance as new minimum distance
                min_distance = current_distance
                # Set new closest station
                closest_station = tuple(station)
                print("new closest station: ", closest_station)

        return closest_station
    
    # Function that decides which cell to move to given target cell coords
    def move_to_cell(self, cell):
        """
        Method to move agent to a certain cell
        """
        # Define possible steps
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, # current position
            moore=False, # Allow Von Neumann movement (only up/down/left/right).
            include_center=True) # include current position as possible step
        
        # Checks which grid cells are empty
        freeSpaces = list(map(self.model.grid.is_cell_empty, possible_steps))
        
        # Create list of neighbor agents
        neighList = self.model.grid.get_neighbors(self.pos, moore=False, include_center=True)

                
        # Stores all possible moves
        next_moves = [p for p,f in zip(possible_steps, freeSpaces) if f == True]
        
        # iterate through neighbor list
        for neighbor in neighList:
            # If neighbor is a station
            if(isinstance(neighbor, StationAgent)):
                # add station position to next moves list
                next_moves.append(neighbor.pos)
        
        # array for possible distances 
        distances = []
        
        # if next moves list is empty
        if len(next_moves) == 0:
            # Add current position to it
            next_moves.append(self.pos)

        print("Last move: ", self.last_move)
        print("Next moves: ", next_moves)

        # if next moves doesn't have only one option
        # and the last move is part of next moves 
        if(not (len(next_moves) == 1) and self.last_move in next_moves):
            # if last move exists
            if self.last_move != None:
                # delete last move from next moves list
                next_moves.remove(self.last_move)

        # Calculate manhattan distances from possible moves to point
        for move in next_moves:
            distances.append(abs(move[0] - cell[0]) + abs(move[1] - cell[1]))

        # Minimun distance from list
        min_distance = min(distances)

        # Set last move to current position before moving to new cell
        self.last_move = self.pos
        # Set next move to corresponding minimum distance
        next_move = next_moves[distances.index(min_distance)] 
    
        return next_move

    # Function used to grab box
    def grab_box(self):
        """
        Method to check if there is a box in same position as self and grab it.
        """
        # If robot isn't carrying box
        if(not self.carry_box):
            # get list of agents in cell corresponding to current position
            agents = self.model.grid.get_cell_list_contents([self.pos])
            # iterate through agents list
            for i in agents:
                # If the agent is a box, box isn't taken and box isn't in station
                if(isinstance(i, BoxAgent) and not i.taken and not i.inStation):
                    self.box = i # set agent's box pointer
                    self.box.taken = True # set box as taken
                    self.carry_box = True # indicate agent is carrying box
                    break
    # Step
    def step(self):
        """ 
        Moves the robot agent.
        """
        self.move()

# Define obstacle agent
class ObstacleAgent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    # Initialize
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    # Step
    def step(self):
        pass   

# Define box agent
class BoxAgent(Agent):
    """
    Box agent. 
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.unique_id = unique_id # agent's id
        self.taken = False # define if it was taken
        self.inStation = False # define if it is in station 

    # Step
    def step(self):
        pass
    
# define station agent
class StationAgent(Agent):
    """
    Station agent. 
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
    
    # Get number of boxes in station
    def get_num_boxes(self):
        boxes = 0 # initialize counter
        # get agents list for current position
        agents = self.model.grid.get_cell_list_contents([self.pos])
        # iterate throguh agents
        for i in agents:
            # if the agent is a box
            if(isinstance(i, BoxAgent)):
                # count box
                boxes += 1
        print("Number of boxes: ", boxes)
        return boxes
    # steps
    def step(self): 
        pass

#########################################################################################################################################

# Define random model
class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, N, width, height, box_num):
        self.num_agents = N # number of robots
        self.grid = MultiGrid(width,height,torus = False) # define grid with width and height
        self.schedule = RandomActivation(self) # define schedule
        self.running = True # run simulation
        self.box_num = box_num # number of boxes
        self.station_num = box_num // 5 # number of stations
        self.steps = 0 # steps taken
        self.picked_boxes = 0 # picked boxes
        

        #Calculate Number of Stations
        if(box_num % 5 != 0):
            self.station_num+=1 # add 1 to station number

        # Creates the border of the grid
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]
        
        # Build Border
        for pos in border:
            # create obstacle agent
            obs = ObstacleAgent(pos, self)
            self.schedule.add(obs)
            self.grid.place_agent(obs, pos) # add to grid

        # Place Stations
        sides = [0, 0, 0, 0] # array that defines number of station per side
        # sides [x, x, y, y]
        indx = 0

        #Determine number of stations per side
        for i in range(self.station_num):
            if(indx<=3): # index range will always be 0-3
                sides[indx]+=1 # add 1 to side count
                indx+=1 # add one to index
            else:
                indx=0 # restart index
                sides[indx]+=1 # add 1 to side count
                indx+=1 # add one to index
        #Determine coords for each side
        station_coords = [] # array of station coordinates
        # controllers for stations positions
        y_up = False 
        x_left = False
        y=1
        x=1

        #Iterate over every side
        for i in range(len(sides)):
            if(sides[i]!=0):
                #For horizontal sides
                if(i < 2):
                    if(y_up): # top side
                        y = self.grid.height-2
                    div = self.grid.width // sides[i] 
                    res = div // 2
                    for j in range(sides[i]):
                        station_coords.append((res, y)) # place station coords
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
