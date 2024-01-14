import os
from dash import Dash, html, dcc, callback_context, callback
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from .html_submenu import HTMLSubmenu
from src.epidemics_simulator.visualization.id_factory import id_factory


class HTMLSidebar(html.Div):
    PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    BACKGROUND_COLOR = "#272727"
    ENABLED_COLOR = "#545454"

    SPACER = html.Hr(className="spacer")

    def __init__(self, network, stats_view) -> None:
        super().__init__()
        self.network = network
        self.stats_view = stats_view
        self.show_total_deaths = False
        self.show_vacc_deaths = False
        self.show_unvacc_deaths = False
        self.show_vaccinations = False
        self.show_cures = {}
        self.show_total_infections = False
        self.show_vacc_infections = False
        self.show_unvacc_infections = False
        self.show_disease_infections = {}
        self.show_group = {}
        self.show_per_step = False

        self.id_factory = id_factory("stats")
        self.children = self._build_sidebar()

    def rebuild(self):
        self.children = self._build_sidebar()

    def death_submenu(self):
        submenu = HTMLSubmenu("Deaths", "skull", "deaths", self.stats_view)
        submenu.add_default_entries("deaths", "skull")
        return submenu

    def cumulative_button(self):
        @callback(
            Output(self.id_factory("cumulative-button"), "style"),
            Output("stats-graph", "figure", allow_duplicate=True),
            Input(self.id_factory("cumulative-button"), "n_clicks"),
            State(self.id_factory(f"cumulative-button"), "style"),
            prevent_initial_call=True,
        )
        def toggle(_, style):
            if style["background-color"] == self.BACKGROUND_COLOR:
                new_color = self.ENABLED_COLOR
                self.stats_view.use_cumulative_data = True
            else:
                new_color = self.BACKGROUND_COLOR
                self.stats_view.use_cumulative_data = False
            # data add {prefix}-{name} (except if prefix = total then prefix = "")
            return {"background-color": new_color}, self.stats_view.build_graph()

        return html.Div(
            [
                html.I(className=f"fas fa-calculator me-3"),
                html.Span("Cumulate Data"),
            ],
            className="toggle",
            style={
                "background-color": self.BACKGROUND_COLOR,
                "color": "azure",
                "cursor": "pointer",
            },
            id=self.id_factory("cumulative-button"),
        )

    def cures_button(self):
        @callback(
            Output(self.id_factory("cures-button"), "style"),
            Output("stats-graph", "figure", allow_duplicate=True),
            Input(self.id_factory("cures-button"), "n_clicks"),
            State(self.id_factory(f"cures-button"), "style"),
            prevent_initial_call=True,
        )
        def toggle(_, style):
            if style["background-color"] == self.BACKGROUND_COLOR:
                new_color = self.ENABLED_COLOR
                self.stats_view.add_data(f"cures")
            else:
                new_color = self.BACKGROUND_COLOR
                self.stats_view.remove_data(f"cures")
            # data add {prefix}-{name} (except if prefix = total then prefix = "")
            return {"background-color": new_color}, self.stats_view.build_graph()

        return html.Div(
            [
                html.I(className=f"fas fa-heart me-3"),
                html.Span("Cures"),
            ],
            className="toggle",
            style={
                "background-color": self.BACKGROUND_COLOR,
                "color": "azure",
                "cursor": "pointer",
            },
            id=self.id_factory("cures-button"),
        )

    def change_file_button(self):
        @callback(
            Output("file-popup", "is_open", allow_duplicate=True),
            Input(self.id_factory("change-file-button"), "n_clicks"),
            prevent_initial_call=True,
        )
        def open(_):
            return True

        return html.Div(
            [
                html.I(className=f"fas fa-folder me-3"),
                html.Span("Open other file"),
            ],
            className="toggle",
            style={
                "background-color": self.BACKGROUND_COLOR,
                "color": "azure",
                "cursor": "pointer",
            },
            id=self.id_factory("change-file-button"),
        )

    def infections_submenu(self):
        submenu = HTMLSubmenu("Infections", "bed", "infections", self.stats_view)
        submenu.add_default_entries(
            "infections",
            "bed",
            prefixes=["total", "vacc", "unvacc", "re"],
            labels=["Total", "Vaccinated", "Unvaccinated", "Re"],
        )
        return submenu

    def groups_submenu(self):
        submenu = HTMLSubmenu("Groups", "people-group", "groups", self.stats_view)
        submenu.add_group_entries(self.network.active_groups)
        return submenu

    def disease_submenu(self):
        submenu = HTMLSubmenu("Diseases", "viruses", "diseases", self.stats_view)
        submenu.add_disease_entries(self.network.diseases)
        return submenu

    def vaccinations_button(self):
        @callback(
            Output(self.id_factory("vaccinations-button"), "style"),
            Output("stats-graph", "figure", allow_duplicate=True),
            Input(self.id_factory("vaccinations-button"), "n_clicks"),
            State(self.id_factory(f"vaccinations-button"), "style"),
            prevent_initial_call=True,
        )
        def toggle(_, style):
            if style["background-color"] == self.BACKGROUND_COLOR:
                new_color = self.ENABLED_COLOR
                self.stats_view.add_data(f"vaccinations")
            else:
                new_color = self.BACKGROUND_COLOR
                self.stats_view.remove_data(f"vaccinations")
            # data add {prefix}-{name} (except if prefix = total then prefix = "")
            return {"background-color": new_color}, self.stats_view.build_graph()

        return html.Div(
            [
                html.I(className=f"fas fa-syringe me-3"),
                html.Span("Vaccinations"),
            ],
            className="toggle",
            style={
                "background-color": self.BACKGROUND_COLOR,
                "color": "azure",
                "cursor": "pointer",
            },
            id=self.id_factory("vaccinations-button"),
        )

    def _build_sidebar(self):
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
                        self.change_file_button(),
                        html.Hr(className="spacer"),
                        self.cumulative_button(),
                        html.Hr(className="spacer"),
                        self.vaccinations_button(),
                        html.Hr(className="spacer"),
                        self.cures_button(),
                        html.Hr(className="spacer"),
                        self.death_submenu(),
                        html.Hr(className="spacer"),
                        self.infections_submenu(),
                        html.Hr(className="spacer"),
                        self.disease_submenu(),
                        html.Hr(className="spacer"),
                        self.groups_submenu(),
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
            className="sidebar",
        )
