from mesa import Agent

class Car(Agent):

    # TODO: Fix loops
    # TODO: Fix diagnonal movement in traffic lights

    """
    Agent that simulates the behaviour of a car in traffic
    Attributes:
        unique_id: Agent's ID 
        destination (tuple): Coordinates of the destination
    """
    def __init__(self, unique_id, model, destination):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            destination: Coordinates of the destination
        """
        super().__init__(unique_id, model)
        self.destination = destination
        self.route = None
        self.calculated_route = False
        self.moving = False

        print("Cars destination: ", self.destination)

    def move(self):
        """
        Moves the agent to the next node in the route
        """
        # Rule for Traffic Lights
        cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        for agent in cell_contents:
            if isinstance(agent, Traffic_Light):
                if agent.state == False:
                    self.moving = False
                    return
                    
        if(not len(self.route) == 0):
            next_move = self.route.pop(0)

            # Rule for Car in next_move
            next_move_contents = self.model.grid.get_cell_list_contents(next_move)
            if(self.pos[0] != next_move[0] and self.pos[1] != next_move[1]):
                for agent in cell_contents:
                    if isinstance(agent, Road):
                        if agent.direction == "Left" or agent.direction == "Right":
                            side_cell_contents = self.model.grid.get_cell_list_contents((self.pos[0], next_move[1]))
                            for side_agent in side_cell_contents:
                                if isinstance(side_agent, Car):
                                    self.moving = False
                                    return
                        else:
                            side_cell_contents = self.model.grid.get_cell_list_contents((self.pos[1], next_move[0]))
                            for side_agent in side_cell_contents:
                                if isinstance(side_agent, Car):
                                    self.moving = False
                                    return

            for agent in next_move_contents:
                if isinstance(agent, Car) and not agent.moving:
                    self.moving = False
                    return 

            self.moving = True
            self.model.grid.move_agent(self, next_move)
        else:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            
    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        if not self.calculated_route:
            self.route = self.get_route()
            self.calculated_route = True
            self.move()
        else:
            self.move()
    
    def get_route(self):
        """
        Determines the route that the agent will take using neighboring cells and distance.
        """
        path =[]
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])

        for agent in cell_contents:
            if isinstance(agent, Road):
                current_node = agent
            if isinstance(agent, Traffic_Light):
                current_node = agent
    
        path.append(self.pos)
        while(current_node.pos != self.destination):
            possible_steps = []
            distances = []

            neighbors = self.model.grid.get_neighbors(
                current_node.pos, 
                moore = True,
                include_center = False
            )

            if(isinstance(current_node, Road)):
                for n in neighbors:                 
                    if(not isinstance(n, Obstacle)):
                        if(isinstance(n, Destination) and n.pos != self.destination):
                            continue
                        elif((n.pos[self.model.directions[current_node.direction][0]] == current_node.pos[self.model.directions[current_node.direction][0]] + self.model.directions[current_node.direction][1])):
                            print("Current: ", current_node.pos, "Neighbor: ", n.pos)
                            if(isinstance(n, Destination) and (n not in path and len(path) != 0)):
                                possible_steps.append(n)
                            elif(self.model.directions[current_node.direction][0] == 0):
                                if(n.pos[1] == current_node.pos[1]-1 and isinstance(n, Road) and n.direction != "Up" and (n not in path and len(path) != 0)):
                                    possible_steps.append(n)
                                elif(n.pos[1] == current_node.pos[1]+1 and isinstance(n, Road) and n.direction != "Down" and (n not in path and len(path) != 0)):
                                    possible_steps.append(n)
                                elif(n.pos[1] == current_node.pos[1] and (isinstance(n, Traffic_Light) or isinstance(n, Destination) or isinstance(n, Road)) and (n not in path and len(path) != 0)):
                                    possible_steps.append(n)

                            else:
                                if(n.pos[0] == current_node.pos[0]-1 and isinstance(n, Road) and n.direction != "Right" and (n not in path and len(path) != 0)):
                                    possible_steps.append(n)
                                elif(n.pos[0] == current_node.pos[0]+1 and isinstance(n, Road) and n.direction != "Left" and (n not in path and len(path) != 0)):
                                    possible_steps.append(n)
                                elif(n.pos[0] == current_node.pos[0] and (isinstance(n, Traffic_Light) or isinstance(n, Destination) or isinstance(n, Road)) and (n not in path and len(path) != 0 )):
                                    possible_steps.append(n)
        

            if(isinstance(current_node, Traffic_Light)):
                for n in neighbors:
                    if(not isinstance(n, Obstacle) and not isinstance(n, Traffic_Light) and (n not in path and len(path) != 0)):
                        if(isinstance(n, Destination) and n.pos != self.destination):
                            continue
                        elif((n.pos[self.model.directions[previous_node.direction][0]] == current_node.pos[self.model.directions[previous_node.direction][0]] + self.model.directions[previous_node.direction][1])):
                            possible_steps.append(n)
            
            # Calculate manhattan distances from possible moves to point
            for step in possible_steps:
                distances.append(abs(step.pos[0] - self.destination[0]) + abs(step.pos[1] - self.destination[1]))
            
            print("Possible steps: ", possible_steps)
            print("Distances: ", distances)

            # Minimun distance from list
            min_distance = min(distances)
            
            # Set next move to corresponding minimum distance
            previous_node = current_node
            current_node = possible_steps[distances.index(min_distance)]

            path.append(current_node.pos) 
            print("Path: ", path)

            if(len(path) > 200):
                print("Path too long")
                return path

        return path
    

    

class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """
    def __init__(self, unique_id, model, state = False, timeToChange = 10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

    def step(self):
        """ 
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        # if self.model.schedule.steps % self.timeToChange == 0:
        #     self.state = not self.state
        pass

class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass

class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass

class Intersection(Agent):
    """
    Intersection agent. Determines where the cars can move, and in which directions.
    """
    def __init__(self, unique_id, model, direction= "Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)

    def step(self):
        pass