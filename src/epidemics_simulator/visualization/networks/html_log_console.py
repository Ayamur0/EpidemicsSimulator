from dash import Dash, html, dcc, callback_context, MATCH, ALL, callback
import dash_bootstrap_components as dbc


class HTMLLogConsole(html.Div):
    def __init__(self):
        super().__init__()
        self.children = (
            html.Div(
                [
                    html.Div(
                        [
                            # width: 3rem ensures the logo is the exact width of the
                            # collapsed sidebar (accounting for padding)
                            html.I(
                                className="fas fa-terminal me-2",
                                style={"width": "3rem", "font-size": "2rem"},
                            ),
                            html.H2("Log Output"),
                        ],
                        className="logbar-header",
                    ),
                    html.Hr(),
                    dbc.Nav(
                        [
                            html.Div(
                                html.Span(
                                    "Some log text",
                                    className="mb-0",
                                    id="log-console-content",
                                ),
                            )
                        ],
                        vertical=True,
                        pills=True,
                    ),
                ],
                className="logbar",
                id="log-console",
            ),
        )
