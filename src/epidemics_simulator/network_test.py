from storage import NodeGroup, Network


def main():
    n = Network()
    g1 = NodeGroup(n, "Test1", 10, 10, 0.1, 5, 2)
    g2 = NodeGroup(n, "Test2", 20, 10, 0.1, 5, 2)
    g3 = NodeGroup(n, "Test3", 30, 10, 0.1, 5, 2)
    g4 = NodeGroup(n, "Test4", 40, 10, 0.1, 5, 2)
    n.add_group(g1)
    n.add_group(g2)
    n.add_group(g3)
    n.add_group(g4)
    g1.create_internal_connections()
    g2.create_internal_connections()
    g3.create_internal_connections()
    g4.create_internal_connections()

    g1.add_external_connection(g2.id, 3, 1)

    print(g1)
    print(g2)

    g1.delete_external_connection(g2.id)

    print(g1)
    print(g2)


if __name__ == "__main__":
    main()
