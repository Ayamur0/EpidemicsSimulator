from src.epidemics_simulator.storage import Network
import json


class Project:
    def __init__(self) -> None:
        self.network: Network = None
        self.stats = {}
        self.file_location = "project.json"

    def save_to_file(self):
        dicts = []
        dicts.append(self.network.to_dict())
        stats_dict = {}
        for name, stat in self.stats.items():
            stats_dict[name] = stat.to_json()
        dicts.append(stats_dict)
        with open(self.file_location, "w", encoding="utf-8") as f:
            json.dump(dicts, f, ensure_ascii=False, indent=4)

    @classmethod
    def load_from_file(cls, file_location):
        from src.epidemics_simulator.storage import SimStats

        instance = cls()
        with open(file_location, "r", encoding="utf-8") as f:
            dicts = json.load(f)
        instance.network = Network.from_dict(dicts[0])
        stats_dict = dicts[1]
        for name, stat in stats_dict.items():
            instance.stats[name] = SimStats.from_json(stat)
        return instance

    def to_dict(self):
        stats_dict = {key: value.to_dict() for key, value in self.stats.items()}

        return {
            "network": self.network.to_dict() if self.network else None,
            "stats": stats_dict,
            "file_location": self.file_location,
        }

    @classmethod
    def from_dict(cls, data):
        from src.epidemics_simulator.storage import SimStats

        project = cls()

        # Handle network
        if "network" in data and data["network"]:
            project.network = Network.from_dict(data["network"])

        # Handle stats
        stats_dict = data.get("stats", {})
        project.stats = {key: SimStats.from_dict(value) for key, value in stats_dict.items()}

        # Handle other attributes
        project.file_location = data.get("file_location", "project.json")

        return project
