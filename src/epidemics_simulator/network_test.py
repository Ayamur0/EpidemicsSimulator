from storage import NodeGroup, Network


def main():
    n = Network()
    g = NodeGroup(n, 'IDK', 10, 10, 0.1, 5, 2)
    n.add_group(g)
    g.create_members(10000)
    for i in range(0, 1):
        g.create_internal_connections()
        print(g)
        g.reset_connections()
    print(g)


if __name__ == "__main__":
    main()
