"""
Python Flask server for connection with Unity
15-11-2022

Autores: Sebastián González, A01029746
         Andreína Sanánez, A01024927
         Karla Mondragón, A01025108
         Ana Paula Katsuda, A01025303
"""

# Imports
from flask import Flask, request, jsonify
from mesa import Agent, Model
from mesa.space import MultiGrid
from agent_graph import Car
from model_graph import RandomModel

# Size of the board:
number_cars = 20


randomModel = None
currentStep = 0

app = Flask("Traffic Visualization")

# @app.route('/', methods=['POST', 'GET'])

# initialize endpoint
@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel, number_cars
    if request.method == 'POST':
        number_cars = int(request.form.get('NCars'))
        currentStep = 0

        #print(request.form)
        #print(number_agents, width, height)
        randomModel = RandomModel(number_cars)

        return jsonify({"message":"Parameters recieved, model initiated."})

# Endpoint for cars
@app.route('/getCars', methods=['GET'])
def getCars():
    global randomModel

    if request.method == 'GET':
        carPositions = []
        for cell in randomModel.grid.coord_iter():
            cell_content, x, z = cell
            if cell_content:
                for agent in cell_content:
                    if isinstance(agent, Car):
                        carPositions.append({"id": str(agent.unique_id), "x": x, "y": 1, "z": z})

        # print("Agents Positions: ", robotPositions)
        return jsonify({'positions':carPositions})

# Endpoint for update
@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)
