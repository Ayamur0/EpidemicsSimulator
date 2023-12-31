from src.epidemics_simulator.storage import Network


class Project:
    def __init__(self) -> None:
        self.network: Network = None
        self.stats = []
