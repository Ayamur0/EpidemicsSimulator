import os
from dash import Dash, html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


class HTMLNetworkView:
    PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    BACKGROUND_COLOR = "#272727"
    ENABLED_COLOR = "#545454"

    SPACER = html.Hr(className="spacer")

    def __init__(
        self,
        figure,
        groups,
        hidden_groups,
        on_reload,
    ) -> None:
        self.app = Dash(
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            assets_folder=os.getcwd() + "/assets",
        )
        self.show_grid = True
        self.show_internal_edges = False
        self.show_external_edges = True
        self.show_status_colors = True
        self.shown_groups = {}
        self.group_divs = []
        self.on_grid_changed = None
        self.on_show_status_colors_changed = None
        self.on_show_internal_edge_changed = None
        self.on_show_external_edge_changed = None
        self.on_node_percent_changed = None
        self.on_show_group_changed = {}
        self.on_reload = on_reload

        self.update_groups(groups, hidden_groups)
        self.set_callbacks()

        self.app.layout = lambda: self.get_layout(figure)

    def get_layout(self, figure):
        if not self.on_reload:
            raise ValueError
        groups, hidden_groups = self.on_reload()
        self.show_grid = True
        self.show_internal_edges = False
        self.show_external_edges = True
        self.show_group_colors = True
        sidebar = self._build_sidebar()
        self.update_groups(groups, hidden_groups)

        content = html.Div(
            [
                dcc.Graph(
                    figure=figure,
                    id="live-graph",
                    style={"height": "100vh"},
                ),
                dcc.Interval(id="update-color", interval=10 * 1000, n_intervals=0),
                html.Button("Update Graph", id="update-button", n_clicks=0),
            ],
            style={"height": "80vh"},
        )
        return html.Div([dcc.Location(id="url"), sidebar, content])

    def set_callbacks(self):
        # this function is used to toggle the is_open property of each Collapse
        def toggle_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        # this function applies the "open" class to rotate the chevron
        def set_navitem_class(is_open):
            if is_open:
                return "open"
            return ""

        def toggle_grid(_):
            self.show_grid = not self.show_grid
            if self.on_grid_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if self.show_grid
                    else self.BACKGROUND_COLOR
                }, self.on_grid_changed(self.show_grid)

        def toggle_color(_):
            self.show_status_colors = not self.show_status_colors
            if self.on_show_status_colors_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if self.show_status_colors
                    else self.BACKGROUND_COLOR
                }, self.on_show_status_colors_changed(self.show_status_colors)

        def toggle_internal_edges(_):
            self.show_internal_edges = not self.show_internal_edges
            if self.on_show_internal_edge_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if self.show_internal_edges
                    else self.BACKGROUND_COLOR
                }, self.on_show_internal_edge_changed(self.show_internal_edges)

        def toggle_external_edges(_):
            self.show_external_edges = not self.show_external_edges
            if self.on_show_external_edge_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if self.show_external_edges
                    else self.BACKGROUND_COLOR
                }, self.on_show_external_edge_changed(self.show_external_edges)

        def change_node_percent(percent):
            if self.on_node_percent_changed:
                return self.on_node_percent_changed(percent)

        def toggle_group(_):
            id = callback_context.triggered_id.split("_")[0]
            self.shown_groups[id] = not self.shown_groups[id]
            if id in self.on_show_group_changed:
                return {
                    "background-color": self.ENABLED_COLOR
                    if self.shown_groups[id]
                    else self.BACKGROUND_COLOR
                }, self.on_show_group_changed[id](id, self.shown_groups[id])

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

        for group in self.shown_groups:
            self.app.callback(
                [
                    Output(f"{group}_button", "style"),
                    Output("live-graph", "figure", allow_duplicate=True),
                ],
                [Input(f"{group}_button", "n_clicks")],
                prevent_initial_call=True,
            )(toggle_group)

    def update_groups(self, groups, hidden_groups):
        self.shown_groups.clear()
        self.group_divs.clear()
        for group in groups:
            self.shown_groups[group.id] = group.id not in hidden_groups
            self.group_divs.append(
                html.Div(
                    [
                        html.I(className="fas fa-object-ungroup me-2"),
                        html.Span(f" Show {group.name}"),
                    ],
                    id=f"{group.id}_button",
                    className="toggle",
                    style={
                        "background-color": self.ENABLED_COLOR
                        if self.shown_groups[group.id]
                        else self.BACKGROUND_COLOR
                    },
                )
            )

    def _build_sidebar(self):
        submenu = [
            html.Li(
                dbc.Row(
                    [
                        dbc.Col(
                            html.I(className="fas fa-object-ungroup me-3"),
                            width="auto",
                        ),
                        dbc.Col("Groups", className="hidden"),
                        dbc.Col(
                            html.I(className="fas fa-chevron-right me-3"),
                            width="auto",
                            className="hidden",
                        ),
                    ],
                    className="submenu-label",
                ),
                style={"cursor": "pointer", "color": "azure"},
                id="submenu",
            ),
            dbc.Collapse(
                self.group_divs,
                id="submenu-collapse",
            ),
        ]

        return html.Div(
            [
                html.Div(
                    [
                        # width: 3rem ensures the logo is the exact width of the
                        # collapsed sidebar (accounting for padding)
                        html.Img(src=self.PLOTLY_LOGO, style={"width": "3rem"}),
                        html.H2("Config"),
                    ],
                    className="sidebar-header",
                ),
                html.Hr(),
                dbc.Nav(
                    [
                        html.Div(
                            [
                                html.I(className="fas fa-border-all me-2"),
                                html.Span("Show Grid"),
                            ],
                            id="grid-button",
                            className="toggle",
                            style={
                                "background-color": self.ENABLED_COLOR
                                if self.show_grid
                                else self.BACKGROUND_COLOR
                            },
                        ),
                        html.Div(
                            [
                                html.I(className="fas fa-circle-nodes me-2"),
                                html.Span("Show inner Edges"),
                            ],
                            id="internal-edge-button",
                            className="toggle",
                            style={
                                "background-color": self.ENABLED_COLOR
                                if self.show_internal_edges
                                else self.BACKGROUND_COLOR
                            },
                        ),
                        html.Div(
                            [
                                html.I(className="fas fa-circle-nodes me-2"),
                                html.Span("Show inter group edges"),
                            ],
                            id="external-edge-button",
                            className="toggle",
                            style={
                                "background-color": self.ENABLED_COLOR
                                if self.show_external_edges
                                else self.BACKGROUND_COLOR
                            },
                        ),
                        html.Div(
                            [
                                html.I(className="fas fa-palette me-2"),
                                html.Span("Show status colors"),
                            ],
                            id="color-button",
                            className="toggle",
                            style={
                                "background-color": self.ENABLED_COLOR
                                if self.show_status_colors
                                else self.BACKGROUND_COLOR
                            },
                        ),
                        self.SPACER,
                        dbc.Nav(submenu, vertical=True),
                        self.SPACER,
                        html.Li(
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                html.I(className="fas fa-circle-dot me-3"),
                                                width="auto",
                                            ),
                                            dbc.Col("Node percentage", className="hidden"),
                                        ]
                                    ),
                                    dcc.Slider(
                                        id="percentage-slider",
                                        className="hidden",
                                        min=1,
                                        max=100,
                                        step=1,
                                        marks={i: f"{i}%" for i in range(0, 101, 25)},
                                        value=100,
                                        tooltip={"placement": "bottom", "always_visible": False},
                                        updatemode="drag",
                                    ),
                                ],
                            ),
                            className="toggle",
                        ),
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
            className="sidebar",
        )
