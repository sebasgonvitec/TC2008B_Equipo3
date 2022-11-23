from RobotAgents import RandomModel, ObstacleAgent, BoxAgent, RobotAgent, StationAgent
from mesa.visualization.modules import CanvasGrid, BarChartModule, PieChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

def agent_portrayal(agent):
    if agent is None: return

    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}

    if(isinstance(agent, ObstacleAgent)):
        portrayal["Color"] = "black"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2

    if(isinstance(agent, BoxAgent)):
        portrayal["Color"] = "blue"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2

    if(isinstance(agent, StationAgent)):
        portrayal["Color"] = "green"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.5
        
    return portrayal

user_width = int(input("Enter width of the grid: "))
user_height = int(input("Enter height of the grid: "))

model_params = {
    "N":UserSettableParameter("slider", "Robot Num", 5, 1, 50, 1), 
    "width": user_width,
    "height": user_height,
    "box_num": UserSettableParameter("slider", "Box Num", 20, 1, 50, 1)
    #"box_num": 30
    }

grid = CanvasGrid(agent_portrayal, user_width, user_height, 500, 500)


server = ModularServer(RandomModel, [grid], "Robot Agent", model_params)

server.port = 8521
server.launch()
