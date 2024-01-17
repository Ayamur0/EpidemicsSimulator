import math
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
        vaccination_rate: int,
        max_vaccination_rate: int,
        aic: int,
        dic: int,
        color: str,
        id: str = None,
    ):
        if dic > aic:
            raise ValueError("Delta has to be smalller then average")
        self.network = network
        self.name = name
        if not id:
            self.id: str = f"{network.group_id_counter}"  # auto set new id
            network.group_id_counter += 1
        else:
            self.id = id
        self.node_id_counter: int = 0
        # spawn members for size
        self.members: List["Node"] = []
        self.create_members(size)
        self.avrg_int_con: int = aic
        self.delta_int_con: int = dic
        self.avrg_ext_con: dict = {}  # dict with id of other groups + conn
        self.delta_ext_con: dict = {}
        self.age: int = age
        self.vaccination_rate: float = vaccination_rate
        self.max_vaccination_rate: float = max_vaccination_rate
        self.max_vaccination_amount: int = math.ceil(max_vaccination_rate * size)
        self.vaccinated_amount = 0
        self.color: str = color
        self.active: bool = True
        self.internal_edges = set()
        self.external_edges = {}

    @property
    def size(self) -> int:
        return len(self.members)

    def add_internal_edge(self, _from: str, to: str):
        self.internal_edges.add(f"{_from}/{to}")

    def add_external_edge(self, _from: str, to: str):
        to_group = to.split("-")[0]
        if to_group not in self.external_edges:
            self.external_edges[to_group] = set()
        self.external_edges[to_group].add(f"{_from}/{to}")

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
        self.internal_edges.clear()
        self.external_edges.clear()
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
            "color": self.color,
            "member count": self.size,
            "average internal connections": self.avrg_int_con,
            "internal connection delta": self.delta_int_con,
            "age": self.age,
            "vaccination rate": self.vaccination_rate,
            "max vaccination rate": self.max_vaccination_rate
            
        }

    def get_values_from_dict(value_dict: dict):
        name = str(value_dict.get("name"))
        color = str(value_dict.get("color"))
        member_count = int(value_dict.get("member count"))
        aic = int(value_dict.get("average internal connections"))
        dic = int(value_dict.get("internal connection delta"))
        age = int(value_dict.get("age"))
        vaccination_rate = float(value_dict.get("vaccination rate"))
        max_vaccination_rate = float(value_dict.get("max vaccination rate"))
        

        return name, member_count, age, vaccination_rate, max_vaccination_rate, aic, dic, color

    def set_from_dict(self, value_dict: dict):
        (
            name,
            member_count,
            age,
            vaccination_rate,
            max_vaccination_rate,
            aic,
            dic,
            color
            
        ) = NodeGroup.get_values_from_dict(value_dict)
        if dic > aic:
            raise ValueError("Delta has to be smalller then average")
        self.name = name
        if member_count != self.size:
            self.members.clear()
            self.create_members(member_count)
        self.age = age
        self.vaccination_rate = vaccination_rate
        self.max_vaccination_rate = max_vaccination_rate
        self.avrg_int_con = aic
        self.delta_int_con = dic
        self.color = color

    def init_from_dict(network, value_dict):
        (
            name,
            member_count,
            age,
            vaccination_rate,
            max_vaccination_rate,
            aic,
            dic,
            color
        ) = NodeGroup.get_values_from_dict(value_dict)
        return NodeGroup(
            network,
            name,
            member_count,
            age,
            vaccination_rate,
            max_vaccination_rate,
            aic,
            dic,
            color
        )

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "size": len(self.members),
            "node_id_counter": self.node_id_counter,
            "avrg_int_con": self.avrg_int_con,
            "delta_int_con": self.delta_int_con,
            "avrg_ext_con": self.avrg_ext_con,
            "delta_ext_con": self.delta_ext_con,
            "age": self.age,
            "vaccination_rate": self.vaccination_rate,
            "max_vaccination_rate": self.max_vaccination_rate,
            "max_vaccination_amount": self.max_vaccination_amount,
            "vaccinated_amount": self.vaccinated_amount,
            "color": self.color,
            "active": self.active
        }

    @classmethod
    def from_dict(cls, data, network):
        instance = cls(
            network=network,
            name=data["name"],
            size=data["size"],
            aic=data["avrg_int_con"],
            dic=data["delta_int_con"],
            age=data["age"],
            vaccination_rate=data["vaccination_rate"],
            max_vaccination_rate=data["max_vaccination_rate"],
            color=data["color"],
            id=data["id"]
        )
        instance.avrg_int_con = data["avrg_int_con"]
        instance.delta_int_con = data["delta_int_con"]
        instance.avrg_ext_con = data["avrg_ext_con"]
        instance.delta_ext_con = data["delta_ext_con"]
        instance.age = data["age"]
        instance.vaccination_rate = data["vaccination_rate"]
        instance.max_vaccination_rate = data["max_vaccination_rate"]
        instance.max_vaccination_amount = data["max_vaccination_amount"]
        instance.vaccinated_amount = data["vaccinated_amount"]
        instance.color = data["color"]
        instance.active = data["active"]
        return instance
