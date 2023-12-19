import itertools
import math
import random
import time
from dash import Dash, html, dcc, callback_context
import plotly.express as px
from dash.dependencies import Input, Output
from src.epidemics_simulator.storage import Network, NodeGroup
import matplotlib.pyplot as plt
from src.epidemics_simulator.algorithms import CircleGrid
import threading
import dash_bootstrap_components as dbc
import os
from .html_network_view import HTMLNetworkView


# https://stackoverflow.com/questions/69498713/how-to-update-a-networkx-drawing
# https://pygraphviz.github.io/documentation/stable/install.html
# https://community.plotly.com/t/set-specific-color-to-scatter-3d-points/67443
# https://community.plotly.com/t/updating-colours-on-an-animation-using-html-and-then-refreshing-the-animation-slider/70911


class Individual:
    HEALTHY = "rgb(0.043, 0.388, 0.082)"
    CURED = "rgb(0.192, 0.961, 0.573)"
    INFECTED = "rgb(0.659, 0, 0)"
    VACCINATED = "rgb(0.067, 0, 0.941)"
    DECEASED = "rgb(0.012, 0.012, 0.012)"

    PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    def __init__(self) -> None:
        self.X = []
        self.Y = []
        self.Z = []
        self.color_seq = []
        self.nodes = []
        self.stylesheet = []
        self.next_node_id = 0

    def flask(self):
        from flask import Flask, render_template
        import time
        import json

        x = []
        y = []
        z = []
        pts = CircleGrid.get_points_3D(100)
        x, y, z = zip(*pts)

        app = Flask(__name__)

        @app.route("/")
        def index():
            # Create the initial scatter plot
            fig3 = px.scatter_3d(x=x, y=y, z=z, color_discrete_sequence=["red"] * 100)

            # Convert Plotly figure to JSON
            initial_plot = fig3.to_json()

            return render_template("index.html", initial_plot=initial_plot)

        app.run(debug=True)

    def plot(self, network: Network):
        self.X.clear()
        self.Y.clear()
        self.Z.clear()
        self.add_network_points(network)
        fig = px.scatter_3d(
            x=self.X,
            y=self.Y,
            z=self.Z,
            color_discrete_sequence=self.color_seq
            # color=elem,
            # color_discrete_sequence=[
            #     "rgb(1.0,0.2663545845364998,0.0)",
            #     "rgb(0.6694260712462251,0.7779863207340414,1.0)",
            #     "rgb(1.0,0.9652869470673199,0.9287833665638421)",
            # ],
        )
        fig["layout"]["uirevision"] = "0"

        html_view = HTMLNetworkView(fig)
        app = html_view.app

        @app.callback(
            Output("live-graph", "figure"),
            [Input("update-color", "n_intervals"), Input("update-button", "n_clicks")],
            prevent_initial_call=True,
        )
        def update_graph_scatter(n_intervals, x):
            print(n_intervals)
            print(x)
            trigger_id = callback_context.triggered_id
            if trigger_id and "update-button" in trigger_id:
                new_color_sequence = random.choices(["purple", "blue"], k=len(self.X))
            elif trigger_id and "update-color" in trigger_id:
                new_color_sequence = random.choices(
                    [self.CURED, self.HEALTHY, self.VACCINATED, self.INFECTED, self.DECEASED],
                    k=len(self.X),
                )
                # new_color_sequence = self.color_seq
            else:
                new_color_sequence = random.choices(["pink"], k=len(self.X))
            fig.update_traces(marker=dict(color=new_color_sequence))
            fig["layout"]["uirevision"] = "0"
            return fig

        app.run_server(debug=True, use_reloader=True)

        plt.pause(1)

    def get_cube_coords(self, network: Network):
        max_group_size = 0
        group_num = 0
        for group in network.groups:
            if group.active:
                group_num += 1
            if group.size > max_group_size:
                max_group_size = group.size

        max_sphere_radius = CircleGrid.calculate_radius_3D(max_group_size)
        side_length = math.ceil(max_sphere_radius * 2 * 1.25)
        offset = math.ceil(max_sphere_radius * 2 * 0.125)

        points = []
        for z, y, x in itertools.product(range(math.ceil(group_num ** (1 / 3))), repeat=3):
            point = (x * side_length + offset, y * side_length + offset, z * side_length + offset)
            points.append(point)
        return points

    def adjust_node_coords(self, cube_coords, node_coords):
        offset = cube_coords.pop(random.randrange(len(cube_coords)))
        return [
            [coord[0] + offset[0], coord[1] + offset[1], coord[2] + offset[2]]
            for coord in node_coords
        ]

    def add_network_points(self, network: Network):
        cube_coords = self.get_cube_coords(network)
        for group in network.groups:
            self.color_seq.extend([group.color] * group.size)
            node_coords = CircleGrid.get_points_3D(group.size)
            node_coords = self.adjust_node_coords(cube_coords, node_coords)
            x, y, z = zip(*node_coords)
            self.X.extend(x)
            self.Y.extend(y)
            self.Z.extend(z)
