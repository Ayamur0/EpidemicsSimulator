import random
import sys
import unittest
from src.epidemics_simulator.network_builder import NetworkBuilder
from src.epidemics_simulator.storage import Network, NodeGroup


class TestInternalConnections(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestInternalConnections, self).__init__(*args, **kwargs)
        self.seed = random.randrange(sys.maxsize)
        # random.seed(self.seed)
        random.seed(1165860770936024366)  # runall = infinite loop
        print("Testing with seed " + str(self.seed))

    def test_0_delta(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 5, 0, "red"))
        builder = NetworkBuilder(n)
        builder.build()
        for node in n.groups[0].members:
            self.assertEqual(
                node.int_conn_amount,
                5,
                "Wrong amount of internal connections, should be exactly 5, seed was: "
                + str(self.seed),
            )

    def test_0_delta_odd(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 101, 10, 0.1, 1, 5, 0, "red"))
        builder = NetworkBuilder(n)
        builder.build()
        node_4_conn = 0
        for node in n.groups[0].members:
            if node.int_conn_amount == 4:
                node_4_conn += 1
        # One node should have 4 connections, since the group has an odd number of members
        self.assertEqual(node_4_conn, 1, "Wrong amount of nodes with 6 connections")
        # check if all other nodes have 5 connections
        for node in n.groups[0].members:
            if node.int_conn_amount == 4:
                continue
            self.assertEqual(
                node.int_conn_amount,
                5,
                "Wrong amount of internal connections, should always be exactly 5",
            )

    def test_big_delta(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 15, 10, "red"))
        builder = NetworkBuilder(n)
        builder.build()
        for node in n.groups[0].members:
            self.assertGreaterEqual(
                node.int_conn_amount,
                5,
                "Wrong amount of internal connections, should be at least 5",
            )
            self.assertLessEqual(
                node.int_conn_amount, 25, "Wrong amount of internal connections, should be max 25"
            )

    def test_delta_equal_avrg(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 15, 15, "red"))
        builder = NetworkBuilder(n)
        builder.build()
        for node in n.groups[0].members:
            self.assertGreaterEqual(
                node.int_conn_amount,
                0,
                "Wrong amount of internal connections, should be at least 0",
            )
            self.assertLessEqual(
                node.int_conn_amount, 30, "Wrong amount of internal connections, should be max 30"
            )

    def test_delta_bigger_avrg(self):
        n = Network()
        with self.assertRaises(ValueError):
            n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 15, 20, "red"))


class TestExternalConnections(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestExternalConnections, self).__init__(*args, **kwargs)
        self.seed = random.randrange(sys.maxsize)
        random.seed(self.seed)
        print("Testing with seed " + str(self.seed))

    def test_0_delta(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 5, 0, "red"))
        n.add_group(NodeGroup(n, "Test2", 100, 10, 0.1, 1, 5, 0, "red"))
        n.groups[0].add_external_connection("1", 5, 0)
        builder = NetworkBuilder(n)
        builder.build()
        for node in n.groups[0].members + n.groups[1].members:
            self.assertEqual(
                node.get_ext_conn_amount(),
                5,
                "Wrong amount of external connections, should be exactly 5, seed was "
                + str(self.seed),
            )

    def test_0_delta_odd(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 101, 10, 0.1, 1, 5, 0, "red"))
        n.add_group(NodeGroup(n, "Test2", 100, 10, 0.1, 1, 5, 0, "red"))
        n.groups[0].add_external_connection("1", 5, 0)
        builder = NetworkBuilder(n)
        builder.build()
        node_4_conn = 0
        for node in n.groups[0].members + n.groups[1].members:
            if node.get_ext_conn_amount() <= 4:
                node_4_conn += 1
        # One node should have 6 connections, since the group has an odd number of members
        self.assertLessEqual(node_4_conn, 5, "Wrong amount of nodes with 4 connections")
        # check if all other nodes have 5 connections
        for node in n.groups[0].members + n.groups[1].members:
            if node.get_ext_conn_amount() <= 4:
                continue
            self.assertEqual(
                node.get_ext_conn_amount(),
                5,
                "Wrong amount of external connections, should always be exactly 5",
            )

    def test_big_delta(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 5, 0, "red"))
        n.add_group(NodeGroup(n, "Test2", 100, 10, 0.1, 1, 5, 0, "red"))
        n.groups[0].add_external_connection("1", 15, 10)
        builder = NetworkBuilder(n)
        builder.build()
        for node in n.groups[0].members + n.groups[1].members:
            self.assertGreaterEqual(
                node.get_ext_conn_amount(),
                5,
                "Wrong amount of external connections, should be at least 5",
            )
            self.assertLessEqual(
                node.get_ext_conn_amount(),
                25,
                "Wrong amount of external connections, should be max 25",
            )

    def test_delta_equal_avrg(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 5, 0, "red"))
        n.add_group(NodeGroup(n, "Test2", 100, 10, 0.1, 1, 5, 0, "red"))
        n.groups[0].add_external_connection("1", 15, 15)
        builder = NetworkBuilder(n)
        builder.build()
        for node in n.groups[0].members + n.groups[1].members:
            self.assertGreaterEqual(
                node.get_ext_conn_amount(),
                0,
                "Wrong amount of external connections, should be at least 0",
            )
            self.assertLessEqual(
                node.get_ext_conn_amount(),
                30,
                "Wrong amount of external connections, should be max 30",
            )

    def test_multiple_groups(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 5, 0, "red"))
        n.add_group(NodeGroup(n, "Test2", 100, 10, 0.1, 1, 5, 0, "red"))
        n.add_group(NodeGroup(n, "Test3", 100, 10, 0.1, 1, 5, 0, "red"))
        n.groups[0].add_external_connection("1", 15, 10)
        n.groups[0].add_external_connection("2", 15, 10)
        n.groups[1].add_external_connection("2", 15, 10)
        builder = NetworkBuilder(n)
        builder.build()
        for node in n.groups[0].members + n.groups[1].members + n.groups[2].members:
            self.assertGreaterEqual(
                node.get_ext_conn_amount(),
                10,
                "Wrong amount of external connections, should be at least 15",
            )
            self.assertLessEqual(
                node.get_ext_conn_amount(),
                50,
                "Wrong amount of external connections, should be max 75",
            )
        for node in n.groups[0].members:
            self.assertEqual(node.get_ext_conn_amount("0"), 0)
            self.assertGreaterEqual(node.get_ext_conn_amount("1"), 5)
            self.assertLessEqual(node.get_ext_conn_amount("1"), 25)
            self.assertGreaterEqual(node.get_ext_conn_amount("2"), 5)
            self.assertLessEqual(node.get_ext_conn_amount("2"), 25)

        for node in n.groups[1].members:
            self.assertEqual(node.get_ext_conn_amount("1"), 0)
            self.assertGreaterEqual(node.get_ext_conn_amount("0"), 5)
            self.assertLessEqual(node.get_ext_conn_amount("0"), 25)
            self.assertGreaterEqual(node.get_ext_conn_amount("2"), 5)
            self.assertLessEqual(node.get_ext_conn_amount("2"), 25)

        for node in n.groups[2].members:
            self.assertEqual(node.get_ext_conn_amount("2"), 0)
            self.assertGreaterEqual(node.get_ext_conn_amount("0"), 5)
            self.assertLessEqual(node.get_ext_conn_amount("0"), 25)
            self.assertGreaterEqual(node.get_ext_conn_amount("1"), 5)
            self.assertLessEqual(node.get_ext_conn_amount("1"), 25)

    def test_delta_bigger_avrg(self):
        n = Network()
        n.add_group(NodeGroup(n, "Test1", 100, 10, 0.1, 1, 5, 0, "red"))
        n.add_group(NodeGroup(n, "Test2", 100, 10, 0.1, 1, 5, 0, "red"))
        with self.assertRaises(ValueError):
            n.groups[0].add_external_connection("1", 15, 20)


if __name__ == "__main__":
    unittest.main()


# def main():
#     n = Network()
#     g1 = NodeGroup(n, "Test1", 100, 10, 0.1, 5, 2)
#     g2 = NodeGroup(n, "Test2", 100, 10, 0.1, 5, 2)
#     g3 = NodeGroup(n, "Test3", 100, 10, 0.1, 5, 2)
#     g4 = NodeGroup(n, "Test4", 100, 10, 0.1, 5, 2)
#     n.add_group(g1)
#     n.add_group(g2)
#     n.add_group(g3)
#     n.add_group(g4)
#     g1.create_internal_connections()
#     g2.create_internal_connections()
#     g3.create_internal_connections()
#     g4.create_internal_connections()

#     g1.add_external_connection(g2.id, -1, 2)
#     g2.add_external_connection(g3.id, -2, 3)
#     g3.add_external_connection(g4.id, -1, 2)


# if __name__ == "__main__":
#     main()
