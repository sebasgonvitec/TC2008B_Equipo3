"""
Python Flask server for connection with Unity
15-11-2022

Autores: Sebastián González,
         Andreína Sanánez,
         Karla Mondragón,
         Ana Paula Katsuda
"""

from flask import Flask, request, jsonify
from mesa import Agent, Model
from mesa.space import MultiGrid
from RobotAgents import RandomModel, BoxAgent, RobotAgent, StationAgent, ObstacleAgent

# Size of the board:
number_agents = 12
width = 20
height = 20
box_num = 20
randomModel = None
currentStep = 0

app = Flask("Traffic Example")

# @app.route('/', methods=['POST', 'GET'])

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel, number_agents, width, height, box_num

    if request.method == 'POST':
        number_agents = int(request.form.get('NAgents'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        box_num = int(request.form.get('box_num'))
        currentStep = 0

        #print(request.form)
        #print(number_agents, width, height)
        randomModel = RandomModel(number_agents, width, height, box_num)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        robotPositions = []
        for cell in randomModel.grid.coord_iter():
            cell_content, x, z = cell
            if cell_content:
                for agent in cell_content:
                    if isinstance(agent, RobotAgent):
                        robotPositions.append({"id": str(agent.unique_id), "x": x, "y": 1, "z": z})

        # print("Agents Positions: ", robotPositions)
        return jsonify({'positions':robotPositions})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global randomModel

    if request.method == 'GET':
        obsPositions = []
        for cell in randomModel.grid.coord_iter():
            cell_content, x, z = cell
            if cell_content:
                for agent in cell_content:
                    if isinstance(agent, ObstacleAgent):
                        obsPositions.append({"id": str(agent.unique_id), "x": x, "y": 1, "z": z})

        # print("Obstacle Positions: ", obsPositions)
        return jsonify({'positions':obsPositions})

@app.route('/getStations', methods=['GET'])
def getStations():
    global randomModel

    if request.method == 'GET':
        stationPositions = []
        for cell in randomModel.grid.coord_iter():
            cell_content, x, z = cell
            if cell_content:
                for agent in cell_content:
                    if isinstance(agent, StationAgent):
                        stationPositions.append({"id": str(agent.unique_id), "x": x, "y": 0, "z": z})

        return jsonify({'positions':stationPositions})

@app.route('/getBoxes', methods=['GET'])
def getBoxes():
    global randomModel

    if request.method == 'GET':
        boxPositions = []
        for cell in randomModel.grid.coord_iter():
            cell_content, x, z = cell
            if cell_content:
                station = None
                for agent in cell_content:
                    if isinstance(agent, StationAgent):
                        station = agent

                if(station != None):
                    for agent in cell_content:
                        if isinstance(agent, BoxAgent) and agent.inStation:
                            boxPositions.append({"id": str(agent.unique_id), "x": x, "y": station.get_num_boxes(), "z": z}) 
                else:
                    for agent in cell_content:
                        if isinstance(agent, BoxAgent):
                            boxPositions.append({"id": str(agent.unique_id), "x": x, "y": 1, "z": z})

        return jsonify({'positions':boxPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)
