from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents import BoxAgent, PersonAgent, TrashCanAgent, TruckAgent

class TrashSimulationModel(Model):
    def __init__(self, width, height, initial_num_people):
        self.num_people = initial_num_people
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.datacollector = DataCollector(
            agent_reporters={"CurrentTrash": lambda agent: agent.current_trash if isinstance(agent, TrashCanAgent) else 0}
        )
        self.steps = 0

        box_coordinates = [(27, 2, 'DTGD'), (10, 10, "DTSL"), (18, 20, "DTNTF"), (12, 28, "DTGL"),
                           (14, 37, "DTETI"), (40, 11, "DTAP"), (39, 22, "DTK"), (40, 32, "DTMI"), (32, 40, "TPA")]
        self.box_positions = [(27, 2), (10, 10), (18, 20), (12, 28), (14, 37), (40, 11), (39, 22), (40, 32), (32, 40)]

        for i, (x, y, label) in enumerate(box_coordinates):
            box = BoxAgent(f"box_{i}", self, label)
            self.grid.place_agent(box, (x, y))
            self.schedule.add(box)

        # Create initial people agents
        for i in range(self.num_people):
            person = PersonAgent(i, self)
            self.schedule.add(person)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(person, (x, y))

        # Create trash can agents
        self.trash_cans = []
        trash_coordinates = [(21, 2), (4, 10), (12, 20), (12, 31), (8, 38), (34, 35), (39, 25), (40, 14)]
        department_labels = ["DTGD", "DTSL", "DTNTF", "DTGL", "DTETI", "DTAP", "DTK", "DTMI"]

        for i, (x, y) in enumerate(trash_coordinates):
            trash_can = TrashCanAgent(i + self.num_people, self, capacity=100, department_label=department_labels[i])
            self.schedule.add(trash_can)
            self.grid.place_agent(trash_can, (x, y))
            self.trash_cans.append(trash_can)

        self.truck_agent = None
        self.running = True

    def step(self):
        self.steps += 1
        self.datacollector.collect(self)
        self.schedule.step()

        # Remove all PersonAgents after step 61
        if self.steps == 61:
            self.remove_person_agents()
            self.initialize_truck_agent()

        # Stop the truck and end simulation at step 70
        if self.steps == 70:
            self.truck_agent.is_stopped = True
            self.running = False

        # Check total trash collected by each trash can
        if not self.running:
            total_trash_cans = [trash_can.current_trash for trash_can in self.trash_cans]
            total_trash = sum(total_trash_cans)
            print("Total trash collected by each trash can:", total_trash)

    def remove_person_agents(self):
        person_agents = [agent for agent in self.schedule.agents if isinstance(agent, PersonAgent)]
        for agent in person_agents:
            self.grid.remove_agent(agent)
            self.schedule.remove(agent)

    def initialize_truck_agent(self):
        # Sort trash cans by the amount of trash collected in descending order
        sorted_trash_cans = sorted(self.trash_cans, key=lambda x: x.current_trash, reverse=True)

        # Define truck path based on sorted trash cans
        truck_path = [trash_can.pos for trash_can in sorted_trash_cans]

        # Create truck agent and set its path
        self.truck_agent = TruckAgent(self.num_people + len(self.trash_cans), self)
        self.schedule.add(self.truck_agent)
        self.grid.place_agent(self.truck_agent, truck_path[0])
        self.truck_agent.set_path(truck_path)
