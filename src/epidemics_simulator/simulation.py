import itertools
import random
from typing import List

from src.epidemics_simulator.storage import Disease, Node, SimStats


class Simulation:
    def __init__(self, network) -> None:
        self.healthy_color = network.healthy_color
        self.cured_color = network.cured_color
        self.vaccinated_color = network.vaccinated_color
        self.deceased_color = network.deceased_color
        self.diseases: List[Disease] = network.diseases
        self.network = network
        self.infected_nodes = []
        self.unvaccinated_nodes = []
        self.stats = SimStats(network)

    def simulate_step(self):
        self.stats.new_step()
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
                    self.stats.add_vaccination(node)
            else:
                self.unvaccinated_nodes.remove(node)
        node: Node
        random.shuffle(self.infected_nodes)
        for node in self.infected_nodes:
            disease: Disease = node.infected
            node.infected_time += 1
            if node.infected_time >= disease.duration:
                fatality = (
                    disease.vaccinated_fatality_rate if node.vaccinated else disease.fatality_rate
                )
                r = random.uniform(0, 1)
                if r <= fatality:
                    node.alive = False
                    self.stats.add_death(node)
                    if not node.vaccinated:
                        node.group.vaccinated_amount += 1
                    continue
                else:
                    self.stats.add_cure(node)
                node.infected = None
                node.infected_time = 0
                node.num_of_infections += 1
                self.infected_nodes.remove(node)
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
                    self.infected_nodes.append(target)
                    self.stats.add_infection(target)
        self.stats.finish_step()

    def create_color_seq(self):
        colors = {}
        all = []
        for group in self.network.groups:
            c = []
            node: Node
            for node in group.members:
                if not node.alive:
                    c.append(self.deceased_color)
                elif node.infected:
                    c.append(node.infected.color)
                elif node.vaccinated:
                    c.append(self.vaccinated_color)
                elif node.num_of_infections > 0:
                    c.append(self.cured_color)
                else:
                    c.append(self.healthy_color)
            colors[group.id] = c
            all.extend(c)
        return colors, all

    def init_simulation(self):
        self.infected_nodes.clear()
        self.stats = SimStats(self.network)
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
                self.stats.add_infection(node)
            self.infected_nodes.extend(infected)
            nodes = nodes[disease.initial_infection_count :]
        self.stats.finish_step()
