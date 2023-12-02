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
        if dic > aic:
            raise ValueError
        self.network = network
        self.name = name
        self.id: str = f"{network.group_id_counter}"  # auto set new id
        network.group_id_counter += 1
        self.node_id_counter: int = 0
        # spawn members for size
        self.members: List["Node"] = []
        self.create_members(size)
        self.avrg_int_con: int = aic
        self.delta_int_con: int = dic
        self.avrg_ext_con: dict = {}  # dict with id of other groups + conn
        self.delta_ext_con: dict = {}
        self.age = age
        self.vaccination_rate = vaccination_rate
        self.active = True

    @property
    def size(self) -> int:
        return len(self.members)

    def add_external_connection(self, target_group_id: str, ac: int, dc: int) -> bool:
        if dc > ac:
            raise ValueError
        if (target := self.network.get_group_by_id(target_group_id)) is None:
            raise KeyError
        self.avrg_ext_con[target_group_id] = ac
        self.delta_ext_con[target_group_id] = dc
        target.avrg_ext_con[self.id] = ac
        target.delta_ext_con[self.id] = dc
        return True

    def delete_external_connection(
        self, target_group_id: str, removed_on_target: bool = False
    ) -> bool:
        # remove from ext con dicts
        if (target := self.network.get_group_by_id(target_group_id)) is None:
            raise KeyError
        if target_group_id not in self.avrg_ext_con.keys():
            return False
        del self.avrg_ext_con[target_group_id]
        del self.delta_ext_con[target_group_id]
        del target.avrg_ext_con[target_group_id]
        del target.delta_ext_con[target_group_id]
        return True

    def create_members(self, amount: int) -> None:
        for _ in range(0, amount):
            self.members.append(Node(self))

    def clear_connections(self) -> None:
        # clear all connections in members
        for member in self.members:
            member.clear_connections()

    def get_member(self, node_id: str) -> Optional[Node]:
        for member in self.members:
            if member.id == node_id:
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
        result = f"Group ID: {self.id}, Member:\n"
        for member in self.members:
            con_list.append(len(member.connections))
            result += f"\t{member},\n"
        result += f"Average: {statistics.mean(con_list)}\nDelta: {statistics.stdev(con_list)}"
        return result
