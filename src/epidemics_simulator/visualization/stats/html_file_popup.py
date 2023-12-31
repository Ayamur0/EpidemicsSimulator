import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, callback_context, MATCH, ALL, callback
from dash.dependencies import Input, Output, State


class HTMLFilePopup(dbc.Modal):
    def __init__(self, files, stats_view, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.id = "file-popup"
        self.files = files
        self.stats_view = stats_view
        self.centered = True
        self.keyboard = False
        self.backdrop = "static"
        self.is_open = True
        self.children = [
            dbc.ModalHeader(
                dbc.ModalTitle("Pick a stat file to display"),
                close_button=False,
                style={"background-color": "#353535", "color": "azure", "border-color": "#6b6b6b"},
            ),
            self._create_modal_body(),
            dbc.ModalFooter(
                style={"background-color": "#353535", "color": "azure", "border-color": "#353535"},
            ),
        ]

    def _create_modal_body(self):
        if not self.files:
            return dbc.ModalBody(
                html.Div(
                    "You do not have any stat files. Run a simulation and save the results to create one.",
                    className="file-list",
                    style={"display": "flex", "justify-content": "center", "align-items": "center"},
                ),
                style={"background-color": "#353535", "color": "azure"},
            )
        items = []
        for index, file in enumerate(self.files):
            items.append(
                html.Div(
                    [
                        html.I(className="fas fa-file file-icon"),
                        html.Span(file, className="file-text"),
                    ],
                    className="file-item",
                    id=f"file-{index}",
                )
            )

            @callback(
                Output(f"file-popup", "is_open"),
                Input(f"file-{index}", "n_clicks"),
                prevent_initial_call=True,
            )
            def load_file(_, file=file):
                self.stats_view.load_stats(file)
                return False

        return dbc.ModalBody(
            html.Div(items, className="file-list"),
            style={"background-color": "#353535", "color": "azure"},
        )

    def show_popup(self, app):
        app.layout = html.Div([self.modal_body, self])
        self.open()

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
