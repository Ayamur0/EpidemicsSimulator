import random
from typing import List
from src.epidemics_simulator.storage import Network, NodeGroup, Node
from src.epidemics_simulator.algorithms import HavelHakimi, HavelHakimiDual

# https://networkx.org/documentation/stable/reference/generated/networkx.generators.degree_seq.havel_hakimi_graph.html
# https://www.quora.com/Is-it-possible-to-construct-the-graph-with-12-nodes-such-that-2-of-the-nodes-have-degree-3-and-the-remaining-nodes-have-a-degree-of-4
# https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93Gallai_theorem
# https://en.wikipedia.org/wiki/Havel%E2%80%93Hakimi_algorithm#%3A~%3Atext%3DThe%20Havel%E2%80%93Hakimi%20algorithm%20is%2Csequence%20is%20exactly%20this%20list%3F


class NetworkBuilder:
    def __init__(self, network):
        self.network: Network = network

    def build(self):
        self.clear()
        for group in self.network.groups:
            self._create_int_conn(group)
        self._create_ext_conns()

    def clear(self):
        for group in self.network.groups:
            group.clear_connections()

    def _create_int_conn(self, group: NodeGroup):
        h = HavelHakimi(
            group.size,
            group.avrg_int_con - group.delta_int_con,
            group.avrg_int_con + group.delta_int_con,
        )
        h.run()
        for node_id in h.edges.keys():
            source_node: Node = group.get_member(group.id + "-" + str(node_id))
            for target_node_id in h.edges[node_id]:
                # target_node: Node = group.get_member(group.id + "-" + str(target_node_id))
                source_node.add_int_connection(group.id + "-" + str(target_node_id))
                # target_node.add_int_connection(group.id + "-" + str(node_id))

    def _create_ext_conns(self):
        all = self._collect_ext_conns(self.network)
        for from_id in all.keys():
            for params in all[from_id]:
                target_id = params[0]
                avrg = params[1]
                delta = params[2]
                self._add_ext_conn(
                    _from=self.network.get_group_by_id(from_id),
                    to=self.network.get_group_by_id(target_id),
                    min=avrg - delta,
                    max=avrg + delta,
                )
                # remove connections from target -> source so it isn't created twice
                all[target_id] = [i for i in all[target_id] if i[0] != from_id]

    def _add_ext_conn(self, _from: NodeGroup, to: NodeGroup, min: int, max: int):
        if _from.size <= to.size:
            key_group = _from
            value_group = to
        else:
            key_group = to
            value_group = _from
        h = HavelHakimiDual(_from.size, to.size, min, max)
        h.run()
        for node_id in h.edges.keys():
            source_node: Node = key_group.get_member(key_group.id + "-" + str(node_id))
            for target_node_id in h.edges[node_id]:
                # target_node: Node = value_group.get_member(
                #     value_group.id + "-" + str(target_node_id)
                # )
                source_node.add_ext_connection(value_group.id + "-" + str(target_node_id))
                # target_node.add_ext_connection(key_group.id + "-" + str(node_id))

    # creates dict of all connections between groups
    # contains tuples of (target_id, avrg, delta)
    def _collect_ext_conns(self, network: Network):
        all = {}
        for group in network.groups:
            x = []
            for target in group.avrg_ext_con.keys():
                x.append((target, group.avrg_ext_con[target], group.delta_ext_con[target]))
            all[group.id] = x
        return all
