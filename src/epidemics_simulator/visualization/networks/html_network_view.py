import os
from dash import Dash, html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


class HTMLNetworkView:
    PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    BACKGROUND_COLOR = "#272727"
    ENABLED_COLOR = "#545454"

    SPACER = html.Hr(className="spacer")

    def __init__(self, figure, groups) -> None:
        self.app = Dash(
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            assets_folder=os.getcwd() + "/assets",
        )
        self.show_grid = True
        self.show_internal_edges = True
        self.show_external_edges = True
        self.show_group_colors = True
        self.shown_groups = {}

        group_divs = []
        for group in groups:
            self.shown_groups[group.id] = True
            group_divs.append(
                html.Div(
                    [
                        html.I(className="fas fa-object-ungroup me-2"),
                        html.Span(
                            f" Hide {group.name}"
                            if self.shown_groups[group.id]
                            else f" Show {group.name}"
                        ),
                    ],
                    className="toggle",
                    style={
                        "background-color": self.ENABLED_COLOR
                        if self.shown_groups[group.id]
                        else self.BACKGROUND_COLOR
                    },
                ),
            )

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
                group_divs,
                id="submenu-collapse",
            ),
        ]

        sidebar = html.Div(
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
                                html.Span("Hide Grid" if self.show_grid else "Show Grid"),
                            ],
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
                                html.Span(
                                    "Hide inner Edges"
                                    if self.show_internal_edges
                                    else "Show inner Edges"
                                ),
                            ],
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
                                html.Span(
                                    "Hide inter group edges"
                                    if self.show_external_edges
                                    else "Show inter group edges"
                                ),
                            ],
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
                                html.Span(
                                    "Show status colors"
                                    if self.show_group_colors
                                    else "Show group colors"
                                ),
                            ],
                            className="toggle",
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
                                        min=0,
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

        content = html.Div(
            [
                dcc.Graph(
                    figure=figure,
                    id="live-graph",
                    style={"height": "80vh"},
                ),
                dcc.Interval(id="update-color", interval=10 * 1000, n_intervals=0),
                html.Button("Update Graph", id="update-button", n_clicks=0),
            ],
            style={"height": "80vh"},
        )

        self.app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

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

        self.app.callback(
            Output(f"submenu-collapse", "is_open"),
            [Input(f"submenu", "n_clicks")],
            [State(f"submenu-collapse", "is_open")],
        )(toggle_collapse)

        self.app.callback(
            Output(f"submenu", "className"),
            [Input(f"submenu-collapse", "is_open")],
        )(set_navitem_class)
