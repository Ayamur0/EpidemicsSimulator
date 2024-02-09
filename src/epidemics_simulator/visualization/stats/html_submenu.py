from dash import html, callback, ALL, MATCH, callback_context
import dash_bootstrap_components as dbc
from src.epidemics_simulator.visualization.id_factory import id_factory
from dash.dependencies import Input, Output, State


class HTMLSubmenu(dbc.Nav):
    BACKGROUND_COLOR = "#272727"
    ENABLED_COLOR = "#545454"

    def __init__(self, name, icon, view_id, stats_view, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.id_factory = id_factory(view_id)
        self.content = []
        self.vertical = True
        self.stats_view = stats_view
        self.children = [
            html.Li(
                dbc.Row(
                    [
                        dbc.Col(
                            html.I(className=f"fas fa-{icon} me-3"),
                            width=2,
                        ),
                        dbc.Col(name, className="hidden", width=7),
                        dbc.Col(
                            html.I(className="fas fa-chevron-right me-3"),
                            width=2,
                            className="hidden",
                        ),
                    ],
                    className="submenu-label",
                ),
                style={"cursor": "pointer", "color": "azure"},
                id=self.id_factory("submenu"),
            ),
            dbc.Collapse(
                self.content,
                id=self.id_factory("submenu-collapse"),
                class_name="submenu-collapse",
            ),
        ]

        @callback(
            Output(self.id_factory("submenu-collapse"), "is_open"),
            [Input(self.id_factory("submenu"), "n_clicks")],
            [State(self.id_factory("submenu-collapse"), "is_open")],
        )
        def toggle_collapse(n, is_open):
            if n:
                return not is_open
            return is_open

        @callback(
            Output(self.id_factory("submenu"), "className"),
            [Input(self.id_factory("submenu-collapse"), "is_open")],
        )
        def set_navitem_class(is_open):
            if is_open:
                return "open"
            return ""

    def add_entry(self, name, icon):
        self.content.append(
            html.Div(
                [
                    html.I(className=f"fas fa-{icon} me-2"),
                    html.Span(name),
                ],
                id=self.id_factory(f"{name}-button"),
                className="toggle",
                style={"background-color": self.BACKGROUND_COLOR},
            )
        )

    def add_hr_rule(self):
        self.content.append(html.Hr())

    def add_group_entries(self, groups, icon1="people-group", icon2="person", identifier="group"):
        self.content.append(
            html.Div(
                [
                    html.I(className=f"fas fa-{icon1} me-2"),
                    html.Span(f" Show all {identifier}s"),
                ],
                id=self.id_factory(f"all-{identifier}s-button"),
                className="toggle",
                style={"background-color": self.ENABLED_COLOR},
            )
        )
        for id, name in groups:
            self.content.append(
                html.Div(
                    [
                        html.I(className=f"fas fa-{icon2} me-2"),
                        html.Span(f" Show {name}"),
                    ],
                    id={"index": id, "type": self.id_factory(f"{identifier}-button")},
                    className="toggle",
                    style={"background-color": self.BACKGROUND_COLOR},
                )
            )

        @callback(
            Output(
                {"index": MATCH, "type": self.id_factory(f"{identifier}-button")},
                "style",
                allow_duplicate=True,
            ),
            Input({"index": ALL, "type": self.id_factory(f"{identifier}-button")}, "n_clicks"),
            State({"index": MATCH, "type": self.id_factory(f"{identifier}-button")}, "style"),
            prevent_initial_call=True,
        )
        def toggle(_, style):
            if style["background-color"] == self.BACKGROUND_COLOR:
                new_color = self.ENABLED_COLOR
            else:
                new_color = self.BACKGROUND_COLOR
            # add / remove group.id/disease.id from groups/diseases
            return {"background-color": new_color}

        @callback(
            Output(self.id_factory(f"all-{identifier}s-button"), "style", allow_duplicate=True),
            Output("stats-graph", "figure", allow_duplicate=True),
            Input({"index": ALL, "type": self.id_factory(f"{identifier}-button")}, "n_clicks"),
            prevent_initial_call=True,
        )
        def toggle(_, identifier=identifier):
            id = callback_context.triggered_id["index"]
            if identifier == "group":
                if id in self.stats_view.visible_groups:
                    self.stats_view.remove_group(id)
                else:
                    self.stats_view.add_group(id)
            else:
                if id in self.stats_view.visible_diseases:
                    self.stats_view.remove_disease(id)
                else:
                    self.stats_view.add_disease(id)
            return (
                {"background-color": self.BACKGROUND_COLOR},
                self.stats_view.build_graph(),
            )

        @callback(
            Output(
                {"index": ALL, "type": self.id_factory(f"{identifier}-button")},
                "style",
                allow_duplicate=True,
            ),
            Output(self.id_factory(f"all-{identifier}s-button"), "style"),
            Output("stats-graph", "figure", allow_duplicate=True),
            Input(self.id_factory(f"all-{identifier}s-button"), "n_clicks"),
            State(self.id_factory(f"all-{identifier}s-button"), "style"),
            prevent_initial_call=True,
        )
        def toggle(_, style, identifier=identifier):
            if identifier == "group":
                self.stats_view.set_all_groups()
                n_buttons = len(self.stats_view.stats.group_ids)
            else:
                self.stats_view.set_all_diseases()
                n_buttons = len(self.stats_view.stats.disease_ids)
            # set groups/diseases to only "all"
            new_color = (
                self.ENABLED_COLOR
                if style["background-color"] == self.BACKGROUND_COLOR
                else self.BACKGROUND_COLOR
            )
            return (
                [{"background-color": self.BACKGROUND_COLOR}] * n_buttons,
                {"background-color": new_color},
                self.stats_view.build_graph(),
            )

    def add_disease_entries(self, diseases):
        self.add_group_entries(diseases, icon1="viruses", icon2="virus", identifier="disease")

    def add_default_entries(
        self,
        name,
        icon,
        prefixes=["total", "vacc", "unvacc"],
        labels=["Total", "Vaccinated", "Unvaccinated"],
    ):
        for prefix, label in zip(prefixes, labels):
            self.content.append(
                html.Div(
                    [
                        html.I(className=f"fas fa-{icon} me-2"),
                        html.Span(f"{label} {name}"),
                    ],
                    id=self.id_factory(f"{prefix}-{name}-button"),
                    className="toggle",
                    style={"background-color": self.BACKGROUND_COLOR},
                )
            )

            @callback(
                Output(self.id_factory(f"{prefix}-{name}-button"), "style"),
                Output("stats-graph", "figure", allow_duplicate=True),
                Input(self.id_factory(f"{prefix}-{name}-button"), "n_clicks"),
                State(self.id_factory(f"{prefix}-{name}-button"), "style"),
                prevent_initial_call=True,
            )
            def toggle(_, style, prefix=prefix, name=name):
                if style["background-color"] == self.BACKGROUND_COLOR:
                    new_color = self.ENABLED_COLOR
                    self.stats_view.add_data(f"{prefix}_{name}")
                else:
                    new_color = self.BACKGROUND_COLOR
                    self.stats_view.remove_data(f"{prefix}_{name}")
                # data add {prefix}-{name} (except if prefix = total then prefix = "")
                return {"background-color": new_color}, self.stats_view.build_graph()
