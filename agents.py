import random
from mesa import Agent

class BoxAgent(Agent):
    """A static box agent that doesn't move."""
    def __init__(self, unique_id, model, label):
        super().__init__(unique_id, model)
        self.label = label

    def step(self):
        pass  # BoxAgent does not do anything in each step


class PersonAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        # Move to a random neighboring cell
        self.move()
        # Randomly decide to dispose trash based on 80% probability
        if random.random() < 0.7:
            self.dispose_trash()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def dispose_trash(self):
        # Get all agents in the same cell as the agent
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        # Filter out only the TrashCanAgent objects
        trash_cans = [agent for agent in cellmates if isinstance(agent, TrashCanAgent)]
        # Check if there are any trash cans in the same cell
        if trash_cans:
            # Select the first trash can found in the cell
            trash_can = trash_cans[0]
            # Add trash to the selected trash can
            trash_can.add_trash()



class TrashCanAgent(Agent):
    def __init__(self, unique_id, model, capacity, department_label):
        super().__init__(unique_id, model)
        self.capacity = capacity
        self.current_trash = 0
        self.department_label = department_label

    def step(self):
        pass

    def add_trash(self):
        if self.current_trash < self.capacity:
            self.current_trash += 1

    def empty_trash(self):
        trash = self.current_trash
        self.current_trash = 0
        return trash


class TruckAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.path = []
        self.path_index = 0
        self.visited_boxes = set()  # Set to store visited box nodes
        self.is_stopped = False  # Flag to indicate if the truck has stopped
        self.collected_trash = 0  # Amount of trash collected

    def step(self):
        if not self.is_stopped and self.path:
            next_position = self.path[self.path_index]
            self.model.grid.move_agent(self, next_position)
            self.path_index = (self.path_index + 1) % len(self.path)
            self.collect_trash(next_position)
            self.check_department_visit(next_position)

            # If all nodes have been visited, move to TPA and stop
            if self.model.steps >= 70:
                self.model.grid.move_agent(self, (28, 40))
                self.is_stopped = True

    def set_path(self, path):
        self.path = path
        self.path_index = 0

    def collect_trash(self, position):
        cellmates = self.model.grid.get_cell_list_contents([position])
        trash_cans = [agent for agent in cellmates if isinstance(agent, TrashCanAgent)]
        for trash_can in trash_cans:
            if trash_can.current_trash > 0:
                self.collected_trash += trash_can.empty_trash()

    def check_department_visit(self, position):
        if position in self.model.box_positions:
            department_label = self.model.grid.get_cell_list_contents([position])[0].label
            # Check if the node box has been visited
            if department_label not in self.visited_boxes:
                self.visited_boxes.add(department_label)

            # If all node boxes have been visited, add the stop point at (32, 40) (TPA)
            if len(self.visited_boxes) == len(self.model.box_positions):
                self.path.append((32, 40))
                self.is_stopped = True