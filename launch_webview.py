from src.epidemics_simulator.storage import Network, Project
from src.epidemics_simulator.visualization.dash_server import DashServer

if __name__ == "__main__":
    server = DashServer()
    p = Project(None)
    p.network = Network()
    server.run_network_view(p)
