import os
from dash import Dash, html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State


class HTMLSidebar(html.Div):
    PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    BACKGROUND_COLOR = "#272727"
    ENABLED_COLOR = "#545454"

    SPACER = html.Hr(className="spacer")

    def __init__(
        self, show_grid, show_internal_edges, show_external_edges, show_status_colors, id_factory
    ) -> None:
        super().__init__()
        self.shown_groups = {}
        self.group_divs = []
        self.show_grid = show_grid
        self.show_internal_edges = show_internal_edges
        self.show_external_edges = show_external_edges
        self.show_status_colors = show_status_colors
        self.id_factory = id_factory
        self.children = self._build_sidebar()

    def rebuild(self):
        self.children = self._build_sidebar()

    def is_visible(self, group_id):
        return self.shown_groups[group_id]

    def toggle_group(self, group_id):
        self.shown_groups[group_id] = not self.shown_groups[group_id]

    def update_group_divs(self, groups, hidden_groups):
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
                    id={"index": group.id, "type": self.id_factory("group-button")},
                    className="toggle",
                    style={
                        "background-color": HTMLSidebar.ENABLED_COLOR
                        if self.shown_groups[group.id]
                        else HTMLSidebar.BACKGROUND_COLOR
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
                id=self.id_factory("submenu"),
            ),
            dbc.Collapse(
                self.group_divs,
                id=self.id_factory("submenu-collapse"),
                class_name="submenu-collapse",
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
                            id=self.id_factory("grid-button"),
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
                            id=self.id_factory("internal-edge-button"),
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
                            id=self.id_factory("external-edge-button"),
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
                            id=self.id_factory("color-button"),
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
                                        id=self.id_factory("percentage-slider"),
                                        className="hidden percentage-slider",
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
