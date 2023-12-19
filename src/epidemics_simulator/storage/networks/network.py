from typing import List


class Network:
    def __init__(self) -> None:
        self.group_id_counter: int = 0
        self.groups = []

    def add_group(self, group) -> bool:
        if group in self.groups:
            return False
        self.groups.append(group)
        return True

    def delete_group(self, group_id: str) -> bool:
        ret = any(g.id == group_id for g in self.groups)
        self.groups = [group for group in self.groups if group.id != group_id]
        return ret

    def get_group_by_id(self, id: str):
        for group in self.groups:
            if group.id == id:
                return group
        return None
