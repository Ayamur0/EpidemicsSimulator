import random
from typing import List
from src.epidemics_simulator.storage import Network, NodeGroup, Node


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

    def _get_nodes_with_lowest_conns(self, remaining_nodes):
        lowest = remaining_nodes[0].int_conn_amount
        for n in remaining_nodes:
            if n.int_conn_amount < lowest:
                lowest = n.int_conn_amount
        return [n for n in remaining_nodes if n.int_conn_amount == lowest]

    def _create_int_conn(self, group: NodeGroup):
        max_per_node = group.avrg_int_con + group.delta_int_con
        min_per_node = group.avrg_int_con - group.delta_int_con

        # choose random amount of total connections to be created
        total = random.randint(min_per_node * group.size, max_per_node * group.size)

        # all nodes with less connections than they must have
        below_min = group.members.copy()

        # create connections until each node has more than the minimum
        while len(below_min) >= 2:
            _from = random.choice(below_min)
            l = below_min.copy()
            l.remove(_from)
            lowest_conn_nodes = self._get_nodes_with_lowest_conns(l)
            to = random.choice(lowest_conn_nodes)
            if not _from.add_int_connection(to.id):
                continue
            for n in [_from, to]:
                if n.int_conn_amount >= min_per_node:
                    below_min.remove(n)
            total -= 2
        below_max = group.members.copy()

        # one node may have less than the minimum, but no partner with less than minimum remains
        # add one connections with another node, that already has the minimum of connections
        # if delta = 0 and group has odd number of nodes, one node will have one connection to many
        if below_min:
            target = random.choice(below_max)
            below_min[0].add_int_connection(target.id)
            # remove from max if target now exceeds max (only for delta = 1)
            # source can never exceed max (only = max if delta = 0)
            if target.int_conn_amount >= max_per_node:
                below_max.remove(target)
            total -= 2

        # add more connections until total is reached
        # if total is odd, one less connections is created, since each connections creates two ( a -> b + b -> a)
        while total >= 2:
            if len(below_max) < 2:
                raise ValueError
            selected: List[Node] = random.sample(below_max, 2)
            if not selected[0].add_int_connection(selected[1].id):
                continue
            for n in selected:
                if n.int_conn_amount >= max_per_node:
                    below_max.remove(n)
            total -= 2

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
            smaller_group_size = _from.size
            below_min_smaller = _from.members.copy()
            below_max_smaller = _from.members.copy()
            below_min_bigger = to.members.copy()
            below_max_bigger = to.members.copy()
        else:
            smaller_group_size = to.size
            below_min_smaller = to.members.copy()
            below_max_smaller = to.members.copy()
            below_min_bigger = _from.members.copy()
            below_max_bigger = _from.members.copy()

        # calculate total connections
        # depends on smaller group, larger group max have less than minimum of connections
        total = random.randint(min * smaller_group_size, max * smaller_group_size)

        # create connections until each node in the smaller group has more than the minimum
        while len(below_min_smaller) >= 2:
            source = random.choice(below_min_smaller)
            target = random.choice(below_min_bigger)
            if not source.add_ext_connection(target.id):
                continue
            if source.get_ext_conn_amount(to.id) >= min:
                below_min_smaller.remove(source)
            if target.get_ext_conn_amount(_from.id) >= min:
                below_min_bigger.remove(target)
            total -= 2

        # one node in the smaller group may have less than the minimum, but no partner with less than minimum remains, if both group sizes are equal
        # add one connections with another node, that already has the minimum of connections
        if below_min_smaller:
            source = below_min_smaller[0]
            # choose target from nodes of bigger group that dont have min amount of connections if there are some left
            if below_min_bigger:
                target = random.choice(below_min_bigger)
                if target.get_ext_conn_amount(_from.id) >= max:
                    below_min_bigger.remove(target)
            # else choose target from nodes of bigger group that have less than max connections
            else:
                target = random.choice(below_max_bigger)
                if target.get_ext_conn_amount(_from.id) >= max:
                    below_max_bigger.remove(target)
            source.add_ext_connection(target.id)
            total -= 2

        # add more connections until total is reached
        # if total is odd, one less connections is created, since each connections creates two ( a -> b + b -> a)
        while total >= 2:
            if len(below_max_smaller) < 1:
                raise ValueError
            source = below_max_smaller[0]
            # choose target from nodes of bigger group that dont have min amount of connections if there are some left
            if below_min_bigger:
                target = random.choice(below_min_bigger)
                if target.get_ext_conn_amount(_from.id) >= max:
                    below_min_bigger.remove(target)
            # else choose target from nodes of bigger group that have less than max connections
            else:
                target = random.choice(below_max_bigger)
                if target.get_ext_conn_amount(_from.id) >= max:
                    below_max_bigger.remove(target)
            if not source.add_ext_connection(target.id):
                continue
            if source.get_ext_conn_amount(to.id) >= max:
                below_min_smaller.remove(source)
            total -= 2

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
