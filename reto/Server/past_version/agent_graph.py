from mesa import Agent
import random

class Car(Agent):
    # TODO: Add beheavior for obstacle and car evasion 
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
        self.prevPos = None
        self.time = 0
        self.next_move = None

        print("Cars destination: ", self.destination)

    def move(self):
        """
        Moves the agent to the next node in the route
        """
        # TODO: Behaviour for car evasion
        # TODO: Behaviour for traffic lights

        activate_alternative = False
        
        if(self.route):
            
            next_move_contents = self.model.grid.get_cell_list_contents([self.next_move])

            for agent in next_move_contents:

                if isinstance(agent, Car):
                    print("There is a car in the next move", self.next_move)
                    neighbors = self.model.grid.get_neighbors(self.pos, moore = True, include_center = False)
                    curr_contents = self.model.grid.get_cell_list_contents([self.pos])

                    for agent in curr_contents:
                        if(isinstance(agent, Road)):
                            front_neighbors =[]
                            for n in neighbors:
                                if(isinstance(n, Car)):
                                    if(n.pos[self.model.directions[agent.direction][0]] == self.pos[self.model.directions[agent.direction][0]]):
                                        return
                                if(not isinstance(n, Obstacle)):
                                    if(n.pos[self.model.directions[agent.direction][0]] == self.pos[self.model.directions[agent.direction][0]] + self.model.directions[agent.direction][1]):
                                        front_neighbors.append(n.pos)

                            front_neighbors = [*set(front_neighbors)]
                            
                            if(len(front_neighbors) < 3):
                                if(front_neighbors[0] != self.next_move):
                                    alternative = front_neighbors[0]
                                else:
                                    alternative = front_neighbors[1]
                            
                                alternative_contents = self.model.grid.get_cell_list_contents([alternative])
                                for agent in alternative_contents:
                                    if isinstance(agent, Car):
                                        print("There is a car in the next move", alternative)
                                        return
                                    else:
                                        if random.randint(0, 20) < 15:
                                            self.next_move = alternative

                if isinstance(agent, Traffic_Light) and not agent.state:
                    print("There is a traffic light in the next move")
                    return
                if isinstance(agent, Car):
                    print("There is a traffic light in the next move")
                    return
            
            self.prevPos = self.pos
            self.model.grid.move_agent(self, self.next_move)
            self.next_move = self.route.pop(0)
            self.time = 0

        else:
            self.prevPos = self.pos
            self.model.grid.move_agent(self, self.next_move)
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.time = 0
            
        # Rules for Traffic Lights:
        # cell_contents = self.model.grid.get_cell_list_contents(self.pos)
        # for agent in cell_contents:
        #     if isinstance(agent, Traffic_Light):
        #         if agent.state == False:
        #             self.moving = False
        #             return
                    
        # if(self.route):
        #     next_move = self.route.pop(0)

        #     # Rule for Car in next_move
        #     next_move_contents = self.model.grid.get_cell_list_contents(next_move)
        #     if(self.pos[0] != next_move[0] and self.pos[1] != next_move[1]):
        #         for agent in next_move_contents:
        #             if isinstance(agent, Road):
        #                 if agent.direction == "Left" or agent.direction == "Right":
        #                     side_cell_contents = self.model.grid.get_cell_list_contents((self.pos[0], next_move[1]))
        #                     for side_agent in side_cell_contents:
        #                         if isinstance(side_agent, Car):
        #                             self.moving = False
        #                             return
        #                 else:
        #                     side_cell_contents = self.model.grid.get_cell_list_contents((self.pos[1], next_move[0]))
        #                     for side_agent in side_cell_contents:
        #                         if isinstance(side_agent, Car):
        #                             self.moving = False
        #                             return
        #     for agent in next_move_contents:
        #         if isinstance(agent, Car) and not agent.moving:
        #             self.moving = False
        #             return 

        #     self.moving = True
        #     self.model.grid.move_agent(self, next_move)
        # else:
        #     self.model.grid.remove_agent(self)
        #     self.model.schedule.remove(self)

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        if not self.calculated_route:
            self.route = self.get_route_bfs()
            self.next_move = self.route.pop(0)
            self.calculated_route = True
            # Update Moving Sate
            if(self.prevPos == self.pos):
                self.time+=1
            self.move()
        else:
            # Update Moving Sate
            if(self.prevPos == self.pos):
                self.time+=1
            self.move()
    
    def get_route(self):
        """
        Determines the route that the agent will take 
        """
        return self.model.graph.a_star_algorithm(self.pos, self.destination)        
        
    def get_route_bfs(self):
        """
        Determines the route that the agent will take using BFS
        """
        route = self.model.graph.bfs(self.pos, self.destination)
        route.pop(0)
        return route

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