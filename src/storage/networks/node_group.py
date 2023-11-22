import statistics
import sys
import time
from typing import List, Optional
import node
import random
# node import Node

class NodeGroup:
    all_instances_by_id: dict[str, 'NodeGroup'] = {}
    def __init__(self, network: 'Network', size: int, aic: float, dic: float):
        self.parent_network = network
        self.group_id: str = f'{network.group_id_counter}' # auto set new id
        network.group_id_counter += 1
        self.node_id_counter: int = 0
        self.desired_size = size
        # spawn members for size
        self.members: List[str] = []
        self.avrg_int_con: int = aic
        self.delta_int_con: int = dic
        self.avrg_ext_con: dict = {} # dict with id of other groups + conn
        self.delta_ext_con: dict = {}
        # other group properties, eg. age etc.
        NodeGroup.all_instances_by_id[self.group_id] = self

    @property
    def size(self) -> int:
        return len(self.members)
    
    def add_external_connection(self, target_group: str, ac: int, dc: int) -> bool:
        # add to ext con dicts
        pass

    def delete_external_connection(self, target_group: str) -> bool:
        # remove from ext con dicts
        pass
    
    def create_members(self, amount: int) -> None:
        for i in range(0, amount):
            tmp_member = node.Node(self)
            self.members.append(tmp_member.node_id)

    def _create_connection_number(self, average: int, delta: int):
        # num_of_con = -1 # This constantly hits the perfect delta
        # while num_of_con < 0:
        #     num_of_con = round(random.normalvariate(self.avrg_int_con, self.delta_int_con))
        # return num_of_con
        return random.randint(average - delta, average + delta)

    def _choose_target(self, available_nodes: list['Node']) -> Optional[str]:
        while True:
            if len(available_nodes) == 0:
                return
            target = random.choice(available_nodes)
            target_obj = node.Node.all_instances_by_id[target]  # Not using get_member becase of performance (0.013s vs 0.8s)
            if target_obj.available_connections == -1:
                target_obj.available_connections = self._create_connection_number(self.avrg_int_con, self.delta_int_con)
                return target
            if not target_obj.is_fully_connected():
                return target
            available_nodes.remove(target)

    def _get_nodes_below_max_connections(self): # if all nodes are full, select all nodes that are below the max lemit and increase the border by one. This change will be revertetd after all nodes are finished
        below_max_connections = []
        for member in self.members:
            member_obj = node.Node.all_instances_by_id[member]  # Not using get_member becase of performance (0.013s vs 0.8s)
            if member_obj.get_num_of_connections() >= self.avrg_int_con + self.delta_int_con:
                continue
            member_obj.available_connections += 1
            below_max_connections.append(member)
        return below_max_connections

    def _revert_border_increase(self, unaffacted_nodes: list['Node']):
        for member in unaffacted_nodes:
            member_obj = node.Node.all_instances_by_id[member]  # Not using get_member becase of performance (0.013s vs 0.8s)
            if member_obj.available_connections == 0:
                continue # Should not happen
            member_obj.available_connections -= 1

    def create_internal_connections(self) -> None:
        available_nodes = self.members.copy()
        nodes_were_adjusted = False
        for member in self.members:
            if member in available_nodes:
                available_nodes.remove(member)
            if len(available_nodes) == 0:
                available_nodes = self._get_nodes_below_max_connections()
                nodes_were_adjusted = True
            member_obj = node.Node.all_instances_by_id[member]  # Not using get_member becase of performance (0.013s vs 0.8s)
            if member_obj.available_connections == -1:
                member_obj.available_connections = self._create_connection_number(self.avrg_int_con, self.delta_int_con)
            num_of_con = member_obj.available_connections
            if num_of_con == 0:
                continue
            for i in range(0, num_of_con):
                target = self._choose_target(available_nodes)
                if target is None:
                    available_nodes = self._get_nodes_below_max_connections()
                    nodes_were_adjusted = True
                    target = self._choose_target(available_nodes)
                member_obj.add_connection(target)
        if nodes_were_adjusted:
            self._revert_border_increase(available_nodes)



    def create_external_connections(self) -> None:
        # create external connections with avrg and delta for each group
        # ensure connections between group a and b are only created by a or b not two times
        # but are added to both groups members
        pass

    def add_connection(self, member_id: str, target_member_id: str) -> bool:
        # add connection to target member id to member with member id
        # true if connection was added, false if it already existed
        source_member: 'node.Node' = self.get_member(member_id)
        return source_member.add_connection(target_member_id)

    def delete_connection(self, member_id: str, target_member_id: str) -> bool:
        # remove connection to target member id from member with member id
        source_member: 'node.Node' = self.get_member(member_id)
        if source_member is None:
            return False
        source_member.remove_connection(target_member_id)

    def reset_connections(self) -> None:
        # clear all connections in members
        for member in self.members:
            self.get_member(member).clear_connections()

    def get_member(self, node_id: str) -> Optional['node.Node']:
        # return member with id
        if node_id not in self.members:
            return None
        return node.Node.all_instances_by_id[node_id]





    def __str__(self):
        con_list = []
        result = f'Group ID: {self.group_id}, Member:\n'
        for member in self.members:
            tmp = node.Node.all_instances_by_id[member]
            con_list.append(len(tmp.connections))
            result += f'\t{tmp},\n'
        result += f'Average: {statistics.mean(con_list)}\nDelta: {statistics.stdev(con_list)}'
        return result


