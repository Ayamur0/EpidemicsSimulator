import itertools
from src.epidemics_simulator.visualization.networks import Individual
from src.epidemics_simulator.storage import Network, NodeGroup
from src.epidemics_simulator.algorithms import CircleGrid
import time

if __name__ == "__main__":
    i = Individual()
    n = Network()
    n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 5, 0, "red"))
    n.add_group(NodeGroup(n, "Test2", 100, 10, 0.1, 1, 5, 0, "blue"))
    n.add_group(NodeGroup(n, "Test3", 100, 10, 0.1, 1, 5, 0, "yellow"))
    n.groups[0].add_external_connection("1", 5, 0)
    n.build()
    # i.hidden_groups.append("0")

    # i.add_network_points(n)
    # i.hidden_groups.extend(["0"])
    i.plot(n)
