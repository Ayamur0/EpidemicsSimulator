from typing import List
from storage.graphs.node import Node
from storage.graphs.network import Network

class NodeGroup:
    def __init__(self, network: Network, size: int, aic: float, dic: float):
        self.parent_network = network
        self.id: str = 'a' # auto set new id
        # spawn members for size
        self.members: List[Node] = []
        self.avrg_int_con: float = aic
        self.delta_int_con: float = dic
        self.avrg_ext_con: float = {} # dict with id of other groups + conn
        self.delta_ext_con: float = {}
        # other group properties, eg. age etc.

    @property
    def size(self) -> int:
        return len(self.members)
    
    def add_external_connection(self, target_group: str, ac: float, dc: float):
        # add to ext con dicts
        pass

    def delete_external_connection(self, target_group: str):
        # remove from ext con dicts
        pass
    
    def create_members(self, amount: int) -> None:
        pass

    def create_internal_connections(self) -> None:
        # create internal connections according to average and delta
        pass

    def create_external_connections(self) -> None:
        # create external connections with avrg and delta for each group
        # ensure connections between group a and b are only created by a or b not two times
        # but are added to both groups members
        pass

    def add_connection(self, member_id: str, target_member_id: str) -> bool:
        # add connection to target member id to member with member id
        # true if connection was added, false if it already existed
        pass

    def delete_connection(self, member_id: str, target_member_id: str) -> bool:
        # remove connection to target member id from member with member id
        pass

    def reset_connections(self) -> None:
        # clear all connections in members
        pass

    def get_member(self, id: str) -> Node:
        # return member with id
        pass



