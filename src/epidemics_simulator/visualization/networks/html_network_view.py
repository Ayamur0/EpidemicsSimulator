import os
from dash import Dash, html, dcc, callback_context, MATCH, ALL
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from .html_sidebar import HTMLSidebar


class HTMLNetworkView:
    BACKGROUND_COLOR = "#272727"
    ENABLED_COLOR = "#545454"

    def __init__(self, figure, groups, hidden_groups, on_reload, server) -> None:
        self.app = Dash(
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            assets_folder=os.getcwd() + "/assets",
            server=server,
        )
        self.on_grid_changed = None
        self.on_show_status_colors_changed = None
        self.on_show_internal_edge_changed = None
        self.on_show_external_edge_changed = None
        self.on_node_percent_changed = None
        self.on_show_group_changed = {}
        self.on_reload = on_reload

        sidebar = HTMLSidebar(True, False, True, True)
        self.set_callbacks(sidebar)

        self.app.layout = lambda: self.get_layout(figure, sidebar)

    def get_layout(self, figure, sidebar: HTMLSidebar):
        if not self.on_reload:
            raise ValueError
        groups, hidden_groups = self.on_reload()
        sidebar.show_grid = True
        sidebar.show_internal_edges = False
        sidebar.show_external_edges = True
        sidebar.show_status_colors = True
        sidebar.rebuild()
        sidebar.update_group_divs(groups, hidden_groups)

        content = html.Div(
            [
                dcc.Graph(
                    figure=figure,
                    id="live-graph",
                    style={"height": "100vh"},
                ),
                dcc.Interval(id="update-color", interval=10 * 1000, n_intervals=0),
            ],
            style={"height": "80vh"},
        )
        return html.Div([dcc.Location(id="url"), sidebar, content])

    def set_callbacks(self, sidebar):
        def toggle_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        def set_navitem_class(is_open):
            if is_open:
                return "open"
            return ""

        def toggle_grid(_):
            sidebar.show_grid = not sidebar.show_grid
            if self.on_grid_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if sidebar.show_grid
                    else self.BACKGROUND_COLOR
                }, self.on_grid_changed(sidebar.show_grid)

        def toggle_color(_):
            sidebar.show_status_colors = not sidebar.show_status_colors
            if self.on_show_status_colors_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if sidebar.show_status_colors
                    else self.BACKGROUND_COLOR
                }, self.on_show_status_colors_changed(sidebar.show_status_colors)

        def toggle_internal_edges(_):
            sidebar.show_internal_edges = not sidebar.show_internal_edges
            if self.on_show_internal_edge_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if sidebar.show_internal_edges
                    else self.BACKGROUND_COLOR
                }, self.on_show_internal_edge_changed(sidebar.show_internal_edges)

        def toggle_external_edges(_):
            sidebar.show_external_edges = not sidebar.show_external_edges
            if self.on_show_external_edge_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if sidebar.show_external_edges
                    else self.BACKGROUND_COLOR
                }, self.on_show_external_edge_changed(sidebar.show_external_edges)

        def change_node_percent(percent):
            if self.on_node_percent_changed:
                return self.on_node_percent_changed(percent)

        def toggle_group_button(_):
            id = callback_context.triggered_id["index"]
            sidebar.toggle_group(id)
            if id in self.on_show_group_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if sidebar.is_visible(id)
                    else self.BACKGROUND_COLOR
                }

        def toggle_group(_):
            id = callback_context.triggered_id["index"]
            return self.on_show_group_changed[id](id)

        self.app.callback(
            Output(f"submenu-collapse", "is_open"),
            [Input(f"submenu", "n_clicks")],
            [State(f"submenu-collapse", "is_open")],
        )(toggle_collapse)

        self.app.callback(
            Output(f"submenu", "className"),
            [Input(f"submenu-collapse", "is_open")],
        )(set_navitem_class)

        self.app.callback(
            [
                Output("grid-button", "style"),
                Output("live-graph", "figure", allow_duplicate=True),
            ],
            [Input("grid-button", "n_clicks")],
            prevent_initial_call=True,
        )(toggle_grid)
        self.app.callback(
            [
                Output("color-button", "style"),
                Output("live-graph", "figure", allow_duplicate=True),
            ],
            [Input("color-button", "n_clicks")],
            prevent_initial_call=True,
        )(toggle_color)
        self.app.callback(
            [
                Output("internal-edge-button", "style"),
                Output("live-graph", "figure", allow_duplicate=True),
            ],
            [Input("internal-edge-button", "n_clicks")],
            prevent_initial_call=True,
        )(toggle_internal_edges)
        self.app.callback(
            [
                Output("external-edge-button", "style"),
                Output("live-graph", "figure", allow_duplicate=True),
            ],
            [Input("external-edge-button", "n_clicks")],
            prevent_initial_call=True,
        )(toggle_external_edges)
        self.app.callback(
            Output("live-graph", "figure", allow_duplicate=True),
            [Input("percentage-slider", "value")],
            prevent_initial_call=True,
        )(change_node_percent)

        self.app.callback(
            Output({"index": MATCH, "type": "group-button"}, "style"),
            Input({"index": MATCH, "type": "group-button"}, "n_clicks"),
            prevent_initial_call=True,
        )(toggle_group_button)

        self.app.callback(
            Output("live-graph", "figure"),
            Input({"index": ALL, "type": "group-button"}, "n_clicks"),
            prevent_initial_call=True,
        )(toggle_group)

        self.app.server.route("/update", methods=["POST"])

        def update(object):
            # run two python services, one for QT one for Dash
            # QT service hosts network object on url
            # QT service sends request to localhost:8050/update
            # r = requests.get(f'http://XXX') host the network object somewhere so this service can get it
            return
