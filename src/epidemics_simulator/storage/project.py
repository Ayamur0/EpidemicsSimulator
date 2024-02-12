from src.epidemics_simulator.storage import Network
import json
import os


class Project:
    NETWORK_FILE_NAME = "network.json"
    STAT_FILE_FOLDER = "stats"

    def __init__(self, file_location) -> None:
        self.network: Network = None
        self.file_location = file_location
        if not file_location:
            return
        if not os.path.exists(file_location):
            os.mkdir(file_location)

        if not os.path.exists(os.path.join(self.file_location, self.STAT_FILE_FOLDER)):
            os.mkdir(os.path.join(self.file_location, self.STAT_FILE_FOLDER))

    @property
    def stat_file_names(self):
        if not self.file_location:
            return []
        return os.listdir(os.path.join(self.file_location, self.STAT_FILE_FOLDER))

    @property
    def network_file_location(self):
        return os.path.join(self.file_location, self.NETWORK_FILE_NAME)

    @property
    def stat_file_location(self):
        return os.path.join(self.file_location, self.STAT_FILE_FOLDER)

    def add_stat_file(self, stats):
        self.stats.append(stats.name)

    def remove_stats_file(self, name):
        self.stats = list(self.stats.filter(lambda x: x != name, self.stats))

    def load_stats(self, name):
        from src.epidemics_simulator.storage import SimStats

        return SimStats.from_csv(os.path.join(self.file_location, self.STAT_FILE_FOLDER, name))

    def save_to_file(self):
        with open(self.network_file_location, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=4)

    @classmethod
    def load_from_file(_, file_location):
        with open(
            os.path.join(file_location, Project.NETWORK_FILE_NAME), "r", encoding="utf-8"
        ) as f:
            data = json.load(f)
        return Project.from_dict(data)

    def to_dict(self):
        return {
            "network": self.network.to_dict() if self.network else None,
            "file_location": self.file_location,
        }

    @classmethod
    def from_dict(cls, data):
        from src.epidemics_simulator.storage import SimStats

        try:
            file_location = data["file_location"]
        except KeyError as e:
            return None

        project = cls(file_location)

        # Handle network
        if "network" in data and data["network"]:
            project.network = Network.from_dict(data["network"])

        return project