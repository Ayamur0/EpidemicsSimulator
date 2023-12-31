import itertools
import random
from typing import List

from src.epidemics_simulator.storage import Disease, Node


class Simulation:
    HEALTHY = "rgb(0.043, 0.388, 0.082)"
    CURED = "rgb(0.192, 0.961, 0.573)"
    INFECTED = "rgb(0.659, 0, 0)"
    VACCINATED = "rgb(0.067, 0, 0.941)"
    DECEASED = "rgb(0.012, 0.012, 0.012)"

    def __init__(self, network) -> None:
        self.diseases: List[Disease] = network.diseases
        self.network = network
        self.infected_nodes = {}
        self.unvaccinated_nodes = []

    def simulate(self):
        pass

    def simulate_step(self):
        for node in list(self.unvaccinated_nodes):
            if (
                not node.vaccinated
                and node.group.vaccinated_amount < node.group.max_vaccination_amount
            ):
                r = random.uniform(0, 1)
                if r <= node.group.vaccination_rate:
                    node.vaccinated = True
                    node.group.vaccinated_amount += 1
                    self.unvaccinated_nodes.remove(node)
            else:
                self.unvaccinated_nodes.remove(node)
        for disease in self.diseases:
            node: Node
            for node in self.infected_nodes[disease.id]:
                node.infected_time += 1
                if node.infected_time >= disease.duration:
                    fatality = (
                        disease.vaccinated_fatality_rate
                        if node.vaccinated
                        else disease.fatality_rate
                    )
                    r = random.uniform(0, 1)
                    if r <= fatality:
                        node.alive = False
                        if not node.vaccinated:
                            node.group.vaccinated_amount += 1
                        continue
                    node.infected = None
                    node.infected_time = 0
                    node.num_of_infections += 1
                    self.infected_nodes[disease.id].remove(node)
                target: Node
                for target in itertools.chain(node.int_connections, node.ext_connections):
                    if not target.alive or target.infected is not None:
                        continue
                    if node.vaccinated:
                        infection_rate = disease.vaccinated_infection_rate
                    elif node.num_of_infections > 0:
                        infection_rate = disease.reinfection_rate
                    else:
                        infection_rate = disease.infection_rate
                    r = random.uniform(0, 1)
                    if r <= infection_rate:
                        target.infected = disease
                        self.infected_nodes[disease.id].append(target)

    def create_color_seq(self):
        colors = {}
        all = []
        for group in self.network.groups:
            c = []
            node: Node
            for node in group.members:
                if not node.alive:
                    c.append(self.DECEASED)
                elif node.infected:
                    c.append(node.infected.color)
                elif node.vaccinated:
                    c.append(self.VACCINATED)
                elif node.num_of_infections > 0:
                    c.append(self.CURED)
                else:
                    c.append(self.HEALTHY)
            colors[group.id] = c
            all.extend(c)
        return colors, all

    def init_simulation(self):
        nodes = []
        for group in self.network.groups:
            nodes.extend(group.members)
            group.vaccinated_amount = 0
        for node in nodes:
            node.alive = True
            node.infected = None
            node.infected_time = 0
            node.num_of_infections = 0
            node.vaccinated = False
        self.unvaccinated_nodes = nodes.copy()
        for disease in self.diseases:
            random.shuffle(nodes)
            infected = nodes[: disease.initial_infection_count]
            for node in infected:
                node.infected = disease
            self.infected_nodes[disease.id] = infected
            nodes = nodes[disease.initial_infection_count :]
