from src.epidemics_simulator.visualization.networks import Individual
from src.epidemics_simulator.storage import Network, NodeGroup

if __name__ == "__main__":
    i = Individual()
    # i.host()
    # print(i.generate_offsets(12, 9))
    n = Network()
    n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 5, 0, "red"))
    n.add_group(NodeGroup(n, "Test2", 100, 10, 0.1, 1, 5, 0, "blue"))
    n.add_group(NodeGroup(n, "Test3", 100, 10, 0.1, 1, 5, 0, "yellow"))
    i.add_network_points(n)
    i.host()
    x = [1, 2, 3]
    print(x[:2])
