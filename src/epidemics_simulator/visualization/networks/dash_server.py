from src.epidemics_simulator.storage import Network
from .html_network_view import HTMLNetworkView
from .graph_3d import Graph3D
import threading
from flask import Flask
from wsgiref.simple_server import make_server


class DashServer:
    def __init__(self) -> None:
        self.reload_listener = []

    def on_reload(self):
        for listener in self.reload_listener:
            listener()

    def run_network_view(self, network: Network, run_in_thread=False):
        server = Flask(__name__)
        graph = Graph3D(network)
        html_view = HTMLNetworkView(
            graph.fig, network.groups, graph.hidden_groups, graph.on_reload, server
        )
        app = html_view.app
        html_view.on_grid_changed = graph.toggle_grid
        html_view.on_show_status_colors_changed = graph.toggle_color
        html_view.on_show_internal_edge_changed = graph.toggle_internal_edges
        html_view.on_show_external_edge_changed = graph.toggle_external_edges
        html_view.on_node_percent_changed = graph.change_visible_node_percent
        for group in network.groups:
            html_view.on_show_group_changed[group.id] = graph.hide_group
        graph.sim_test(app)

        app.run(debug=True, use_reloader=True)
