import itertools
from src.epidemics_simulator.visualization.networks import Individual
from src.epidemics_simulator.storage import Network, NodeGroup, Disease, Project
from src.epidemics_simulator.algorithms import CircleGrid
from src.epidemics_simulator.visualization.networks.dash_server import DashServer
import time
import plotly

if __name__ == "__main__":
    server = DashServer()
    n = Network()
    n.add_group(NodeGroup(n, "Test1", 100, 10, 0.005, 0.9, 5, 0, "red"))
    n.add_group(NodeGroup(n, "Test2", 100, 10, 0.005, 0.9, 5, 0, "blue"))
    n.add_group(NodeGroup(n, "Test3", 100, 10, 0.005, 0.9, 5, 0, "yellow"))
    d = Disease("Disease 1")
    d2 = Disease("Disease 2")
    d2.color = "yellow"
    n.add_disease(d)
    n.add_disease(d2)
    n.groups[0].add_external_connection("1", 5, 0)
    n.build()
    p = Project()
    p.network = n
    server.run_network_view(p)

    # i.plot(n)
