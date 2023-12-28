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
import plotly.graph_objs as go


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
        self.Xn = []
        self.Yn = []
        self.Zn = []
        self.nodes = []
        self.colors = []
        self.group_coords = {}
        self.hidden_groups = []
        self.node_id_map = {}
        self.edges_map = {}
        self.show_internal_edges = False
        self.show_external_edges = True
        self.show_grid = True
        self.show_status_colors = False
        self.visible_node_percent = 1
        self.fig = None

    def plot(self, network: Network):
        self.add_network_points(network)
        self.fig = self.build(network)

        def on_reload():
            self.add_network_points(network)
            self.show_internal_edges = False
            self.show_external_edges = True
            self.show_grid = True
            self.show_status_colors = False
            self.hidden_groups.clear()
            self.fig = self.build(network)
            self.visible_node_percent = 1
            return network.groups, self.hidden_groups

        html_view = HTMLNetworkView(
            self.fig,
            network.groups,
            self.hidden_groups,
            on_reload,
        )
        app = html_view.app

        def change_grid(visible):
            self.show_grid = visible
            axis = dict(
                showbackground=visible,
                showline=visible,
                zeroline=visible,
                showgrid=visible,
                showticklabels=visible,
                title="",
            )
            self.fig["layout"]["scene"] = dict(
                xaxis=dict(axis),
                yaxis=dict(axis),
                zaxis=dict(axis),
            )
            return self.fig

        def change_color(use_status_color):
            self.show_status_colors = use_status_color
            if use_status_color:
                pass  # TODO set to color array for status
            else:
                self.fig.update_traces(marker=dict(color=self.colors))
            return self.fig

        def change_internal_edges(visible):
            self.show_internal_edges = visible
            self.fig = self.build(network)
            return self.fig

        def change_external_edges(visible):
            self.show_external_edges = visible
            self.fig = self.build(network)
            return self.fig

        def hide_group(id, visible):
            if visible:
                self.hidden_groups.remove(id)
            elif id not in self.hidden_groups:
                self.hidden_groups.append(id)
            self.fig = self.build(network)
            return self.fig

        def change_visible_node_percent(percent):
            self.visible_node_percent = percent / 100.0
            print("node percent " + str(self.visible_node_percent))
            self.add_network_points(network)
            self.fig = self.build(network)
            return self.fig

        html_view.on_grid_changed = change_grid
        html_view.on_show_status_colors_changed = change_color
        html_view.on_show_internal_edge_changed = change_internal_edges
        html_view.on_show_external_edge_changed = change_external_edges
        html_view.on_node_percent_changed = change_visible_node_percent
        for group in network.groups:
            html_view.on_show_group_changed[group.id] = hide_group

        @app.callback(
            Output("live-graph", "figure", allow_duplicate=True),
            [Input("update-color", "n_intervals"), Input("update-button", "n_clicks")],
            prevent_initial_call=True,
        )
        def update_graph_scatter(n_intervals, x):
            trigger_id = callback_context.triggered_id
            if trigger_id and "update-button" in trigger_id:
                new_color_sequence = random.choices(["purple", "blue"], k=len(self.Xn))
            elif trigger_id and "update-color" in trigger_id:
                new_color_sequence = random.choices(
                    [self.CURED, self.HEALTHY, self.VACCINATED, self.INFECTED, self.DECEASED],
                    k=len(self.Xn),
                )
                # new_color_sequence = self.color_seq
            else:
                new_color_sequence = random.choices(["pink"], k=len(self.X))
            self.fig.update_traces(marker=dict(color=new_color_sequence))
            self.fig["layout"]["uirevision"] = "0"
            return self.fig

        app.run_server(debug=True, use_reloader=True)

    def build(self, network: Network):
        aXn, aYn, aZn = [], [], []
        self.colors.clear()
        for group in network.groups:
            if group.id not in self.hidden_groups:
                x, y, z = zip(*self.group_coords[group.id])
                aXn.extend(x)
                aYn.extend(y)
                aZn.extend(z)
                self.colors.extend([group.color] * len(x))
        aXe, aYe, aZe = self.add_edges(network)

        trace1 = go.Scatter3d(
            x=aXn,
            y=aYn,
            z=aZn,
            mode="markers",
            marker=dict(
                symbol="circle",
                size=6,
                color=self.colors,
                line=dict(color="rgb(50,50,50)", width=0.5),
            ),
            uirevision="0",
        )

        trace2 = go.Scatter3d(
            x=aXe,
            y=aYe,
            z=aZe,
            mode="lines",
            uirevision="0",
            line=dict(color="rgb(125,125,125)", width=1),
            hoverinfo="none",
        )

        axis = dict(
            showbackground=self.show_grid,
            showline=self.show_grid,
            zeroline=self.show_grid,
            showgrid=self.show_grid,
            showticklabels=self.show_grid,
            title="",
        )

        layout = go.Layout(
            title=network.name,
            showlegend=False,
            margin=dict(t=100),
            hovermode="closest",
            scene=dict(
                xaxis=dict(axis),
                yaxis=dict(axis),
                zaxis=dict(axis),
            ),
        )

        data = [trace1, trace2]
        fig = go.Figure(data=data, layout=layout)
        fig["layout"]["uirevision"] = "0"
        return fig

    def add_edges(self, network: Network):
        aXe, aYe, aZe = [], [], []
        for group in network.groups:
            if group.id in self.hidden_groups:
                continue
            if self.show_internal_edges:
                edges = list(group.internal_edges)
            else:
                edges = []
            if self.show_external_edges:
                for target in group.external_edges:
                    if target not in self.hidden_groups:
                        edges.extend(group.external_edges[target])
            for edge in edges:
                _from, to = edge.split("/")
                if not (_from in self.node_id_map and to in self.node_id_map):
                    continue
                from_ind = self.node_id_map[_from]
                to_ind = self.node_id_map[to]
                aXe.extend([self.Xn[from_ind], self.Xn[to_ind], None])
                aYe.extend([self.Yn[from_ind], self.Yn[to_ind], None])
                aZe.extend([self.Zn[from_ind], self.Zn[to_ind], None])
        return aXe, aYe, aZe

    def get_cube_coords(self, network: Network):
        max_group_size = 0
        group_num = 0
        for group in network.groups:
            if group.active:
                group_num += 1
            if group.size > max_group_size:
                max_group_size = group.size
        max_group_size = math.ceil(max_group_size * self.visible_node_percent)

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
        self.group_coords.clear()
        self.node_id_map.clear()
        cube_coords = self.get_cube_coords(network)
        for group in network.groups:
            node_coords = CircleGrid.get_points_3D(
                math.ceil(self.visible_node_percent * group.size)
            )
            node_coords = self.adjust_node_coords(cube_coords, node_coords)
            self.group_coords[group.id] = node_coords
            for i, node in zip(range(len(self.Xn), len(self.Xn) + len(node_coords)), group.members):
                self.node_id_map[node.id] = i
            x, y, z = zip(*node_coords)
            self.Xn.extend(x)
            self.Yn.extend(y)
            self.Zn.extend(z)
