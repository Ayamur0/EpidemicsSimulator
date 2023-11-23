import random
import statistics
from typing import List, Optional

from .network import Network
from .node import Node


class NodeGroup:
    all_instances_by_id: dict[str, "NodeGroup"] = {}

    def __init__(
        self,
        network: Network,
        name: str,
        size: int,
        age: int,
        vaccination_rate: float,
        aic: int,
        dic: int,
    ):
        self.network = network
        self.name = name
        self.id: str = f"{network.group_id_counter}"  # auto set new id
        network.group_id_counter += 1
        self.node_id_counter: int = 0
        self.desired_size = size
        # spawn members for size
        self.create_members(size)
        self.members: List["Node"] = []
        self.avrg_int_con: int = aic
        self.delta_int_con: int = dic
        self.avrg_ext_con: dict = {}  # dict with id of other groups + conn
        self.delta_ext_con: dict = {}
        self.age = age
        self.vaccination_rate = vaccination_rate
        # other group properties, eg. age etc.
        NodeGroup.all_instances_by_id[self.id] = self
        self.active = True

    @property
    def size(self) -> int:
        return len(self.members)

    def add_external_connection(self, target_group_id: str, ac: int, dc: int) -> bool:
        # add to ext con dicts
        self.avrg_ext_con[target_group_id] = ac
        self.delta_ext_con[target_group_id] = dc

        return False
        pass

    def delete_external_connection(self, target_group_id: str) -> bool:
        # remove from ext con dicts
        pass

    def create_members(self, amount: int) -> None:
        for i in range(0, amount):
            self.members.append(Node(self))

    def _create_connection_number(self, average: int, delta: int):
        # num_of_con = -1 # This constantly hits the perfect delta
        # while num_of_con < 0:
        #     num_of_con = round(random.normalvariate(self.avrg_int_con, self.delta_int_con))
        # return num_of_con
        return random.randint(average - delta, average + delta)

    def _choose_target(self, available_nodes: list[Node]) -> Optional[Node]:
        while True:
            if len(available_nodes) == 0:
                return
            target = random.choice(available_nodes)
            if target.available_internal_connections == -1:
                target.available_internal_connections = self._create_connection_number(
                    self.avrg_int_con, self.delta_int_con
                )
                return target
            if not target.is_fully_internal_connected():
                return target
            available_nodes.remove(target)

    def _get_nodes_below_max_connections(
        self,
    ):  # if all nodes are full, select all nodes that are below the max limit and increase the border by one. This change will be reverted after all nodes are finished
        below_max_connections = []
        for member in self.members:
            if (
                member.get_num_of_connections()
                >= self.avrg_int_con + self.delta_int_con
            ):
                continue
            member.available_internal_connections += 1
            below_max_connections.append(member)
        return below_max_connections

    def _revert_border_increase(self, unaffected_nodes: list[Node]):
        for member in unaffected_nodes:
            if member.available_internal_connections == 0:
                continue  # Should not happen
            member.available_internal_connections -= 1

    def create_internal_connections(self) -> None:
        available_nodes = self.members.copy()
        nodes_were_adjusted = False
        for member in self.members:
            if member in available_nodes:
                available_nodes.remove(member)
            if len(available_nodes) == 0:
                available_nodes = self._get_nodes_below_max_connections()
                nodes_were_adjusted = True
            if member.available_internal_connections == -1:
                member.available_internal_connections = self._create_connection_number(
                    self.avrg_int_con, self.delta_int_con
                )
            num_of_con = member.available_internal_connections
            if num_of_con == 0:
                continue
            for i in range(0, num_of_con):
                target: Node = self._choose_target(available_nodes)
                if target is None:
                    available_nodes = self._get_nodes_below_max_connections()
                    nodes_were_adjusted = True
                    target = self._choose_target(available_nodes)
                member.add_connection(target.id)
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
        source_member: Node = self.get_member(member_id)
        return source_member.add_connection(target_member_id)

    def delete_connection(self, member_id: str, target_member_id: str) -> bool:
        # remove connection to target member id from member with member id
        source_member: Node = self.get_member(member_id)
        if source_member is None:
            return False
        source_member.remove_connection(target_member_id)

    def reset_connections(self) -> None:
        # clear all connections in members
        for member in self.members:
            member.clear_connections()

    def get_member(self, node_id: str) -> Optional[Node]:
        # return member with id
        for member in self.members:
            if member.id != node_id:
                continue
            return member
        return None

    def get_properties_dict(self):
        return {
            "name": self.name,
            "member count": self.desired_size,
            "average internal connections": self.avrg_int_con,
            "internal connection delta": self.delta_int_con,
            "age": self.age,
            "vaccination rate": self.vaccination_rate,
        }

    def __str__(self):
        con_list = []
        result = f'Group ID: {self.id}, Member:\n'
        for member in self.members:
            con_list.append(len(member.connections))
            result += f'\t{member},\n'
        result += f'Average: {statistics.mean(con_list)}\nDelta: {statistics.stdev(con_list)}'
        return result
