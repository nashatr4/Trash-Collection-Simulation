from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from model import TrashSimulationModel
from agents import PersonAgent, TrashCanAgent, BoxAgent, TruckAgent

def agent_portrayal(agent):
    portrayal = {}

    if isinstance(agent, PersonAgent):
        portrayal = {"Shape": "circle", "Color": "blue", "Filled": "true", "r": 1, "Layer": 2}
    elif isinstance(agent, TrashCanAgent):
        portrayal = {"Shape": "rect", "Color": "green", "Filled": "true", "w": 2, "h": 2, "Layer": 1,
                     "text": agent.current_trash, "text_color": "white"}
    elif isinstance(agent, BoxAgent):
        portrayal = {
            "Shape": "rect",
            "Color": "grey",
            "Filled": "true",
            "w": 8,
            "h": 5,
            "Layer": 0,
            "text": agent.label,
            "text_color": "white"
        }
    elif isinstance(agent, TruckAgent):
        portrayal = {
            "Shape": "rect",
            "Color": "red",
            "Filled": "true",
            "w": 2,
            "h": 1,
            "Layer": 2,
            "text": agent.collected_trash,
            "text_color": "white"
        }

    return portrayal

grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

server = ModularServer(TrashSimulationModel,
                       [grid],
                       "Trash Collection Simulation",
                       {"width": 50, "height": 50, "initial_num_people": 500})

server.port = 8522  # Set the port for the server
server.launch()
