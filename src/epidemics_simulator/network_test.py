from storage import NodeGroup, Network


def main():
    n = Network()
    g1 = NodeGroup(n, "Test1", 100, 10, 0.1, 5, 2)
    g2 = NodeGroup(n, "Test2", 100, 10, 0.1, 5, 2)
    g3 = NodeGroup(n, "Test3", 100, 10, 0.1, 5, 2)
    g4 = NodeGroup(n, "Test4", 100, 10, 0.1, 5, 2)
    n.add_group(g1)
    n.add_group(g2)
    n.add_group(g3)
    n.add_group(g4)
    g1.create_internal_connections()
    g2.create_internal_connections()
    g3.create_internal_connections()
    g4.create_internal_connections()

    g1.add_external_connection(g2.id, -1, 2)
    g2.add_external_connection(g3.id, -2, 3)
    g3.add_external_connection(g4.id, -1, 2)


if __name__ == "__main__":
    main()
