from src.epidemics_simulator.visualization.networks import Individual
from src.epidemics_simulator.storage import Network, NodeGroup
from src.epidemics_simulator.algorithms import CircleGrid

if __name__ == "__main__":
    i = Individual()
    # i.host()
    # print(i.generate_offsets(12, 9))
    n = Network()
    n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 5, 0, "red"))
    n.add_group(NodeGroup(n, "Test2", 100, 10, 0.1, 1, 5, 0, "blue"))
    n.add_group(NodeGroup(n, "Test3", 100, 10, 0.1, 1, 5, 0, "yellow"))
    i.add_network_points(n)
    # print(i.nodes)
    # print(i.nodes)
    # i.host()
    i.plot()
    # i.flask()
    import math

    points = CircleGrid.get_points(149)
    # print(len(points))
