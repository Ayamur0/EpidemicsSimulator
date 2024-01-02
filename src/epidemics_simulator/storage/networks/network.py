from typing import List


class Network:
    def __init__(self) -> None:
        from src.epidemics_simulator.network_builder import NetworkBuilder

        self.name = "TODO SET NAME"  # TODO set name from UI
        self.group_id_counter: int = 0
        self.diseases = []
        self.groups = []
        self.builder = NetworkBuilder(self)
        self.healthy_color = "rgb(0.043, 0.388, 0.082)"
        self.cured_color = "rgb(0.192, 0.961, 0.573)"
        self.vaccinated_color = "rgb(0.067, 0, 0.941)"
        self.deceased_color = "rgb(0.012, 0.012, 0.012)"

    def add_disease(self, disease) -> bool:
        if disease in self.diseases:
            return False
        self.diseases.append(disease)
        return True

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

    def get_disease_by_id(self, id: str):
        for disease in self.diseases:
            if disease.id == id:
                return disease
        return None

    def build(self):
        self.builder.build()
