import os
from dash import Dash, html, dcc, callback_context, MATCH, ALL, callback, exceptions
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from .html_sidebar import HTMLSidebar
from src.epidemics_simulator.visualization.id_factory import id_factory
from .graph_3d import Graph3D


class HTMLNetworkView:
    BACKGROUND_COLOR = "#272727"
    ENABLED_COLOR = "#545454"

    def __init__(self, graph: Graph3D, page: str = "view") -> None:
        self.on_grid_changed = graph.toggle_grid
        self.on_show_status_colors_changed = graph.toggle_color
        self.on_show_internal_edge_changed = graph.toggle_internal_edges
        self.on_show_external_edge_changed = graph.toggle_external_edges
        self.on_node_percent_changed = graph.change_visible_node_percent
        self.on_show_group_changed = graph.hide_group
        self.graph = graph
        self.needs_build = False
        self.id_factory = id_factory(page)

        self.sidebar = HTMLSidebar(True, False, True, True, self.id_factory)
        self.set_callbacks()
        self.build_layout()

    def build_layout(self):
        content = html.Div(
            [
                dcc.Graph(
                    figure=self.graph.fig,
                    id=self.id_factory("live-graph"),
                    style={"height": "100vh"},
                ),
                dcc.Interval(
                    id=self.id_factory("build-request"),
                    interval=0.5 * 1000,
                    n_intervals=0,
                    disabled=False,
                ),
            ],
            style={"height": "80vh"},
            id=self.id_factory("page-content"),
        )
        self.layout = html.Div([self.sidebar, content])

    def reset(self):
        groups, hidden_groups = self.graph.on_reload()
        self.sidebar.show_grid = True
        self.sidebar.show_internal_edges = False
        self.sidebar.show_external_edges = True
        self.sidebar.show_status_colors = True
        self.sidebar.rebuild()
        self.sidebar.update_group_divs(groups, hidden_groups)
        self.build_layout()

    def set_callbacks(self):
        @callback(
            Output(self.id_factory("submenu-collapse"), "is_open"),
            [Input(self.id_factory("submenu"), "n_clicks")],
            [State(self.id_factory("submenu-collapse"), "is_open")],
        )
        def toggle_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        @callback(
            Output(self.id_factory("submenu"), "className"),
            [Input(self.id_factory("submenu-collapse"), "is_open")],
        )
        def set_navitem_class(is_open):
            if is_open:
                return "open"
            return ""

        @callback(
            [
                Output(self.id_factory("grid-button"), "style"),
                Output(self.id_factory("live-graph"), "figure", allow_duplicate=True),
            ],
            [Input(self.id_factory("grid-button"), "n_clicks")],
            prevent_initial_call=True,
        )
        def toggle_grid(_):
            self.sidebar.show_grid = not self.sidebar.show_grid
            if self.on_grid_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if self.sidebar.show_grid
                    else self.BACKGROUND_COLOR
                }, self.on_grid_changed(self.sidebar.show_grid)

        @callback(
            [
                Output(self.id_factory("color-button"), "style"),
                Output(self.id_factory("live-graph"), "figure", allow_duplicate=True),
            ],
            [Input(self.id_factory("color-button"), "n_clicks")],
            prevent_initial_call=True,
        )
        def toggle_color(_):
            self.sidebar.show_status_colors = not self.sidebar.show_status_colors
            if self.on_show_status_colors_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if self.sidebar.show_status_colors
                    else self.BACKGROUND_COLOR
                }, self.on_show_status_colors_changed(self.sidebar.show_status_colors)

        @callback(
            [
                Output(self.id_factory("internal-edge-button"), "style"),
                Output(self.id_factory("live-graph"), "figure", allow_duplicate=True),
            ],
            [Input(self.id_factory("internal-edge-button"), "n_clicks")],
            prevent_initial_call=True,
        )
        def toggle_internal_edges(_):
            self.sidebar.show_internal_edges = not self.sidebar.show_internal_edges
            if self.on_show_internal_edge_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if self.sidebar.show_internal_edges
                    else self.BACKGROUND_COLOR
                }, self.on_show_internal_edge_changed(self.sidebar.show_internal_edges)

        @callback(
            [
                Output(self.id_factory("external-edge-button"), "style"),
                Output(self.id_factory("live-graph"), "figure", allow_duplicate=True),
            ],
            [Input(self.id_factory("external-edge-button"), "n_clicks")],
            prevent_initial_call=True,
        )
        def toggle_external_edges(_):
            self.sidebar.show_external_edges = not self.sidebar.show_external_edges
            if self.on_show_external_edge_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if self.sidebar.show_external_edges
                    else self.BACKGROUND_COLOR
                }, self.on_show_external_edge_changed(self.sidebar.show_external_edges)

        @callback(
            Output(self.id_factory("live-graph"), "figure", allow_duplicate=True),
            [Input(self.id_factory("percentage-slider"), "value")],
            prevent_initial_call=True,
        )
        def change_node_percent(percent):
            if self.on_node_percent_changed:
                return self.on_node_percent_changed(percent)

        @callback(
            Output({"index": MATCH, "type": self.id_factory("group-button")}, "style"),
            Input({"index": MATCH, "type": self.id_factory("group-button")}, "n_clicks"),
            prevent_initial_call=True,
        )
        def toggle_group_button(_):
            id = callback_context.triggered_id["index"]
            self.sidebar.toggle_group(id)
            return {
                "background-color": self.ENABLED_COLOR
                if self.sidebar.is_visible(id)
                else self.BACKGROUND_COLOR
            }

        @callback(
            Output(self.id_factory("live-graph"), "figure"),
            Input({"index": ALL, "type": self.id_factory("group-button")}, "n_clicks"),
            prevent_initial_call=True,
        )
        def toggle_group(_):
            id = callback_context.triggered_id["index"]
            return self.on_show_group_changed(id)

        @callback(
            Output(self.id_factory("live-graph"), "figure", allow_duplicate=True),
            Input(self.id_factory("build-request"), "n_intervals"),
            prevent_initial_call=True,
        )
        def check_for_update(_):
            if self.needs_build:
                self.needs_build = False
                self.graph.rebuild_legend()
                self.graph.build()
                return self.graph.fig
            else:
                raise exceptions.PreventUpdate()

        # @server.route("/update", methods=["POST"])

        # def update(object):
        # run two python services, one for QT one for Dash
        # QT service hosts network object on url
        # QT service sends request to localhost:8050/update
        # r = requests.get(f'http://XXX') host the network object somewhere so this service can get it
        # return
