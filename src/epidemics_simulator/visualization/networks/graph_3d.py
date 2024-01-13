from src.epidemics_simulator.storage import Network
from .plotly_wrapper import PlotlyWrapper
import plotly.graph_objs as go
import random
from dash import callback
from dash.dependencies import Input, Output
from src.epidemics_simulator.simulation import Simulation
from .legend import Legend
from src.epidemics_simulator.visualization.id_factory import id_factory


class Graph3D:
    def __init__(self, network: Network) -> None:
        self.network: Network = network
        self.healthy_color = network.healthy_color
        self.cured_color = network.cured_color
        self.vaccinated_color = network.vaccinated_color
        self.deceased_color = network.deceased_color
        self.fig = None
        self.legend = Legend(network)
        self.show_grid = True
        self.colors = []
        self.hidden_groups = []
        self.status_colors = []
        self.status_colors_group_map = {}
        self.show_status_colors = True
        self.show_internal_edges = False
        self.show_external_edges = True
        self.visible_node_percent = 1
        (
            self.group_coords,
            self.node_id_map,
            self.Xn,
            self.Yn,
            self.Zn,
        ) = PlotlyWrapper.calculate_network_coords(self.network, self.visible_node_percent)
        self.build()

    def update_network(self, network):
        self.network = network
        self.healthy_color = network.healthy_color
        self.cured_color = network.cured_color
        self.vaccinated_color = network.vaccinated_color
        self.deceased_color = network.deceased_color
        self.legend = Legend(self.network)

    def update_status_colors(self, colors_map):
        self.status_colors_group_map = colors_map
        self.status_colors.clear()
        for group in self.network.groups:
            if group.id not in self.hidden_groups:
                if group.id in self.status_colors_group_map:
                    self.status_colors.extend(
                        self.status_colors_group_map[group.id][: len(self.group_coords[group.id])]
                    )
                else:
                    self.status_colors.extend(
                        [self.healthy_color] * len(self.group_coords[group.id])
                    )
        self.fig.update_traces(selector=dict(name="nodes"), marker=dict(color=self.status_colors))
        self.fig["layout"]["uirevision"] = "0"
        return self.fig

    def toggle_grid(self, visible):
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
            aspectmode="data",
            aspectratio=dict(x=1, y=1, z=1),
        )
        return self.fig

    def toggle_color(self, use_status_color):
        self.show_status_colors = use_status_color
        self.build()
        return self.fig

    def toggle_internal_edges(self, visible):
        self.show_internal_edges = visible
        self.build()
        return self.fig

    def toggle_external_edges(self, visible):
        self.show_external_edges = visible
        self.build()
        return self.fig

    def hide_group(self, id):
        if id in self.hidden_groups:
            self.hidden_groups.remove(id)
        elif id not in self.hidden_groups:
            self.hidden_groups.append(id)
        self.build()
        return self.fig

    def change_visible_node_percent(self, percent):
        self.visible_node_percent = percent / 100.0
        (
            self.group_coords,
            self.node_id_map,
            self.Xn,
            self.Yn,
            self.Zn,
        ) = PlotlyWrapper.calculate_network_coords(self.network, self.visible_node_percent)
        self.build()
        return self.fig

    def on_reload(self, show_status_colors):
        (
            self.group_coords,
            self.node_id_map,
            self.Xn,
            self.Yn,
            self.Zn,
        ) = PlotlyWrapper.calculate_network_coords(self.network, self.visible_node_percent)
        self.show_internal_edges = False
        self.show_external_edges = True
        self.show_grid = True
        self.show_status_colors = show_status_colors
        self.hidden_groups.clear()
        self.visible_node_percent = 1
        self.build()
        return self.network.groups, self.hidden_groups

    def build(self):
        aXn, aYn, aZn = [], [], []
        self.colors.clear()
        self.status_colors.clear()
        for group in self.network.groups:
            if group.id not in self.hidden_groups:
                x, y, z = zip(*self.group_coords[group.id])
                aXn.extend(x)
                aYn.extend(y)
                aZn.extend(z)
                self.colors.extend([group.color] * len(x))
                if group.id in self.status_colors_group_map:
                    self.status_colors.extend(self.status_colors_group_map[group.id][: len(x)])
                else:
                    self.status_colors.extend([self.healthy_color] * len(x))
        aXe, aYe, aZe = PlotlyWrapper.calculate_edge_coords(
            self.network,
            self.show_internal_edges,
            self.show_external_edges,
            self.hidden_groups,
            self.node_id_map,
            self.Xn,
            self.Yn,
            self.Zn,
        )

        trace1 = go.Scatter3d(
            x=aXn,
            y=aYn,
            z=aZn,
            mode="markers",
            name="nodes",
            marker=dict(
                symbol="circle",
                size=6,
                color=self.status_colors if self.show_status_colors else self.colors,
                line=dict(color="rgb(50,50,50)", width=0.5),
            ),
            uirevision="0",
            showlegend=False,
        )

        trace2 = go.Scatter3d(
            x=aXe,
            y=aYe,
            z=aZe,
            mode="lines",
            uirevision="0",
            line=dict(color="rgb(125,125,125)", width=1),
            hoverinfo="none",
            showlegend=False,
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
            title=self.network.name,
            showlegend=True,
            margin=dict(t=100),
            hovermode="closest",
            paper_bgcolor="#353535",
            font={"color": "azure"},
            scene=dict(
                xaxis=dict(axis),
                yaxis=dict(axis),
                zaxis=dict(axis),
                aspectmode="data",
                aspectratio=dict(x=1, y=1, z=1),
            ),
            legend={"bgcolor": "#404040"},
        )
        lgd = self.legend.status_legend if self.show_status_colors else self.legend.group_legend
        data = [trace1, trace2, *lgd]
        self.fig = go.Figure(data=data, layout=layout)
        self.fig.update_layout(title_x=0.5)
        self.fig["layout"]["uirevision"] = "0"
