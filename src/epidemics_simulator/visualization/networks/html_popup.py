import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, callback_context, MATCH, ALL, callback
from dash.dependencies import Input, Output, State


class HTMLPopup(dbc.Modal):
    def __init__(self, title, content=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.centered = True
        if content:
            body = dbc.ModalBody(content)
        else:
            body = None
        self.children = [
            dbc.ModalHeader(
                dbc.ModalTitle(title),
                close_button=True,
            ),
            body,
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Confirm",
                        id=f"{self.id}-confirm",
                        className="btn btn-primary",
                        n_clicks=0,
                        style={
                            "margin-left": "auto",
                            "background-color": "rgb(238, 105, 11)",
                            "border-color": "rgb(238, 105, 11)",
                        },
                    ),
                    dbc.Button(
                        "Cancel",
                        id=f"{self.id}-close",
                        className="btn btn-secondary",
                        n_clicks=0,
                    ),
                ],
                # style={
                #     "display": "flex",
                #     "align-items": "flex-end",
                #     "justify-content": "flex-end",
                # },
            ),
        ]

        @callback(
            Output(self.id, "is_open", allow_duplicate=True),
            Input(f"{self.id}-close", "n_clicks"),
            prevent_initial_call=True,
        )
        def confirm(_):
            return False

    def register_confirm_callback(self, output, cb, state=[]):
        @callback(
            output=[output, Output(self.id, "is_open", allow_duplicate=True)],
            inputs=[Input(f"{self.id}-confirm", "n_clicks")],
            state=state,
            prevent_initial_call=True,
        )
        def func(_):
            return cb(), False

    def register_confirm_callback_with_state(self, output, cb, state):
        @callback(
            output=[output, Output(self.id, "is_open", allow_duplicate=True)],
            inputs=[Input(f"{self.id}-confirm", "n_clicks")],
            state=state,
            prevent_initial_call=True,
        )
        def func(*args):
            return cb(*args), False
