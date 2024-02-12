import itertools
from src.epidemics_simulator.storage import Network, NodeGroup, Disease, Project, SimStats
from src.epidemics_simulator.algorithms import CircleGrid
from src.epidemics_simulator.visualization.dash_server import DashServer
import time
import random

if __name__ == "__main__":
    server = DashServer()
    n = Network()
    # n.add_group(NodeGroup(n, "Test1", 100, 10, 0.005, 0.9, 5, 0, "red"))
    # n.add_group(NodeGroup(n, "Test2", 100, 10, 0.005, 0.9, 5, 0, "blue"))
    # n.add_group(NodeGroup(n, "Test3", 100, 10, 0.005, 0.9, 5, 0, "yellow"))
    n.add_group(NodeGroup(n, "Test3", 100, 10, 0.005, 0.9, 4, 2, "yellow"))
    n.add_group(NodeGroup(n, "Test3", 100, 10, 0.005, 0.9, 4, 2, "yellow"))
    # for i in range(100):
    #     size = random.randint(5, 10)
    #     n.add_group(NodeGroup(n, "Test", 100, size, 0, 0, 4, 0, "red"))
    # for group in n.groups:
    #     targets = random.choices(n.groups, k=4)
    #     targets = [x.id for x in targets]
    #     if group.id in targets:
    #         targets.remove(group.id)
    #     for target in targets:
    #         group.add_external_connection(target, 0, 1)
    d = Disease(
        "Disease 1",
        color="yellow",
        fatality_rate=0,
        vaccinated_fatality_rate=0,
        infection_rate=0.04,
        reinfection_rate=0.04,
        vaccinated_infection_rate=0.02,
        duration=5,
        cure_chance=0.2,
        immunity_period=8,
        infectiousness_factor=1,
        initial_infection_count=10,
    )
    d2 = Disease(
        "Disease 2",
        color="yellow",
        fatality_rate=0,
        vaccinated_fatality_rate=0,
        infection_rate=0.04,
        reinfection_rate=0.04,
        vaccinated_infection_rate=0.02,
        duration=5,
        cure_chance=0.2,
        immunity_period=8,
        infectiousness_factor=1,
        initial_infection_count=10,
    )
    d2 = Disease("Disease 2")
    d2.color = "yellow"
    n.add_disease(d)
    # n.add_disease(d2)
    # n.groups[0].add_external_connection("1", 5, 0)
    n.build()
    p = Project("test_project")
    # p.stats["test"] = SimStats.from_json("test.json")
    p.network = n
    # p.save_to_file()
    # p = Project.load_from_file("muliple_diseases - Kopie.json")
    # p.network.build()
    server.run_network_view(p)

    # i.plot(n)
