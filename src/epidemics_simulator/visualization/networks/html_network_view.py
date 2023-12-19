import os
from dash import Dash, html, dcc, callback_context
import dash_bootstrap_components as dbc


class HTMLNetworkView:
    PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    def __init__(self, figure) -> None:
        self.app = Dash(
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            assets_folder=os.getcwd() + "/assets",
        )

        sidebar = html.Div(
            [
                html.Div(
                    [
                        # width: 3rem ensures the logo is the exact width of the
                        # collapsed sidebar (accounting for padding)
                        html.Img(src=self.PLOTLY_LOGO, style={"width": "3rem"}),
                        html.H2("Sidebar"),
                    ],
                    className="sidebar-header",
                ),
                html.Hr(),
                dbc.Nav(
                    [
                        dbc.NavLink(
                            [html.I(className="fas fa-home me-2"), html.Span("All")],
                            href="/",
                            active="exact",
                        ),
                        dbc.NavLink(
                            [
                                html.I(className="fas fa-calendar-alt me-2"),
                                html.Span("Group1"),
                            ],
                            href="/calendar",
                            active="exact",
                        ),
                        dbc.NavLink(
                            [
                                html.I(className="fas fa-envelope-open-text me-2"),
                                html.Span("Group2"),
                            ],
                            href="/messages",
                            active="exact",
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
