from .html_network_view import HTMLNetworkView
from dash import Dash, html, dcc, callback_context, MATCH, ALL, callback
from dash.dependencies import Input, Output, State
from src.epidemics_simulator.simulation import Simulation
from .html_popup import HTMLPopup
from .html_log_console import HTMLLogConsole
from threading import Lock
import dash_bootstrap_components as dbc
from datetime import datetime


class HTMLSimulationView(HTMLNetworkView):
    def __init__(self, project, graph) -> None:
        self.confirm_reset_popup = HTMLPopup(
            title="Are you sure you want to reset the simulation?",
            id="sim-confirm-reset-modal",
            is_open=False,
        )
        self.save_popup = HTMLPopup(
            title="Choose a name to save this simulation data",
            content=[
                dcc.Input(
                    id="sim-save-input",
                    type="text",
                    placeholder=datetime.now(),
                    className="form-control save-input",
                    style={
                        "margin": "0 1rem 0 1rem",
                        "width": "calc(100% - 2rem)",
                    },
                )
            ],
            id="sim-save-modal",
            is_open=False,
        )
        super().__init__(graph, "sim")
        self.project = project
        self.network = project.network
        self.build_layout()
        self.sim = Simulation(self.network)
        self.sim.init_simulation()
        color_map, _ = self.sim.create_color_seq()
        self.graph.update_status_colors(color_map)
        self.sim_mutex = Lock()
        self.sim_timer = False
        self.show_logs = False

    def build_layout(self):
        content = html.Div(
            [
                dcc.Graph(
                    figure=self.graph.fig,
                    id=self.id_factory("live-graph"),
                    style={"height": "100vh"},
                ),
                dcc.Interval(
                    id=self.id_factory("update-color"),
                    interval=2 * 1000,
                    n_intervals=0,
                    disabled=True,
                ),
                html.Div(
                    [
                        self._round_button("fa-trash", self.id_factory("reset"), False),
                        self._round_button("fa-terminal", self.id_factory("show-log"), False),
                        self._round_button("fa-forward-step", self.id_factory("step"), True),
                        self._round_button("fa-stopwatch", self.id_factory("timer"), False),
                        self._round_button("fa-floppy-disk", self.id_factory("save"), False),
                    ],
                    className="floating-controls",
                ),
                dbc.Toast(
                    [
                        html.P(
                            "Your simulation data has been saved successfully",
                            className="mb-0",
                        )
                    ],
                    id=self.id_factory("save-toast"),
                    header="Saving successful",
                    icon="success",
                    className="toast",
                    duration=4000,
                    is_open=False,
                ),
                html.Div(id=self.id_factory("dummy")),
                self.confirm_reset_popup,
                self.save_popup,
            ],
            style={"height": "80vh"},
            id=self.id_factory("page-content"),
        )
        self.layout = html.Div([self.sidebar, content, HTMLLogConsole()])

    def reset(self):
        self.sim.init_simulation()
        color_map, _ = self.sim.create_color_seq()
        self.graph.update_status_colors(color_map)
        super().reset()

    def _round_button(self, icon, id, big):
        return html.Button(
            [
                html.I(
                    className=f"fas {icon} round-button-icon",
                    style={"fontSize": "3.5rem"} if big else {},
                    id=f"{id}-icon",
                ),
            ],
            className="round-button big-button" if big else "round-button",
            id=id,
        )

    def set_callbacks(self):
        super().set_callbacks()

        @callback(
            Output(self.id_factory("live-graph"), "figure", allow_duplicate=True),
            Output("log-console-content", "children", allow_duplicate=True),
            Input(self.id_factory("step"), "n_clicks"),
            prevent_initial_call=True,
        )
        def step(_):
            with self.sim_mutex:
                self.sim.simulate_step()
                color_map, _ = self.sim.create_color_seq()
                if self.show_logs:
                    return (
                        self.graph.update_status_colors(color_map),
                        self.sim.stats.get_log_text_html(),
                    )
                else:
                    return self.graph.update_status_colors(color_map), ""

        @callback(
            Output(self.id_factory("confirm-reset-modal"), "is_open"),
            Input(self.id_factory("reset"), "n_clicks"),
            prevent_initial_call=True,
        )
        def open_modal(_):
            return True

        @callback(
            Output(self.id_factory("save-modal"), "is_open"),
            Input(self.id_factory("save"), "n_clicks"),
            prevent_initial_call=True,
        )
        def open_modal(_):
            return True

        @callback(
            Output(self.id_factory("timer-icon"), "className"),
            Output(self.id_factory("update-color"), "disabled"),
            Output(self.id_factory("reset"), "disabled"),
            Output(self.id_factory("show-log"), "disabled"),
            Output(self.id_factory("step"), "disabled"),
            Output(self.id_factory("save"), "disabled"),
            Input(self.id_factory("timer"), "n_clicks"),
            prevent_initial_call=True,
        )
        def toggle_timer(_):
            self.sim_timer = not self.sim_timer
            if self.sim_timer:
                return "fas fa-stop round-button-icon", False, True, True, True, True
            else:
                return "fas fa-stopwatch round-button-icon", True, False, False, False, False

        @callback(
            Output(self.id_factory("live-graph"), "figure", allow_duplicate=True),
            Output("log-console-content", "children", allow_duplicate=True),
            Input(self.id_factory("update-color"), "n_intervals"),
            prevent_initial_call=True,
        )
        def step(_):
            with self.sim_mutex:
                self.sim.simulate_step()
                color_map, _ = self.sim.create_color_seq()
                if self.show_logs:
                    return (
                        self.graph.update_status_colors(color_map),
                        self.sim.stats.get_log_text_html(),
                    )
                else:
                    return self.graph.update_status_colors(color_map), ""

        @callback(
            Output("log-console", "style"),
            Output("log-console-content", "children", allow_duplicate=True),
            Input(self.id_factory("show-log"), "n_clicks"),
            prevent_initial_call=True,
        )
        def show_logs(_):
            self.show_logs = not self.show_logs
            return {"opacity": "1" if self.show_logs else "0"}, self.sim.stats.get_log_text_html()

        def reset_sim():
            self.sim.init_simulation()
            color_map, _ = self.sim.create_color_seq()
            return self.graph.update_status_colors(color_map), self.sim.stats.get_log_text_html()

        self.confirm_reset_popup.register_confirm_callback(
            [
                Output(self.id_factory("live-graph"), "figure", allow_duplicate=True),
                Output("log-console-content", "children", allow_duplicate=True),
            ],
            reset_sim,
        )

        def save_data(_, name):
            if not name:
                name = datetime.now()
            print(name)
            self.project.stats[name] = self.sim.stats
            self.sim.stats.to_json()

        self.save_popup.register_confirm_callback_with_state(
            Output(self.id_factory("save-toast"), "is_open"),
            save_data,
            [
                State(self.id_factory("save-input"), "value"),
            ],
        )
