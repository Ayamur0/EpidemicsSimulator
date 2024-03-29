import itertools
from src.epidemics_simulator.visualization.stats.html_sidebar import HTMLSidebar
from dash import Dash, html, dcc, exceptions, callback
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from src.epidemics_simulator.storage import SimStats
from .html_file_popup import HTMLFilePopup


class HTMLStatsView:
    def __init__(self, project) -> None:
        self.stats: SimStats = None
        self.project = project
        self.sidebar = HTMLSidebar(self)
        self.visible_data = []
        self.visible_groups = [None]
        self.visible_diseases = [None]
        self.data_dict = {}
        self.use_cumulative_data = False
        self.needs_build = False
        # self.data_dict = self.stats.group_stats["0"].infections
        self.file_popup = HTMLFilePopup(list(self.project.stat_file_names), self)
        self.content = html.Div(
            [
                dcc.Graph(
                    figure=self.build_graph(),
                    style={
                        "width": "60%",
                        "height": "70%",
                    },
                    id="stats-graph",
                ),
                self.file_popup,
                dcc.Interval(
                    id="stats-build-request",
                    interval=0.5 * 1000,
                    n_intervals=0,
                    disabled=False,
                ),
            ],
            style={
                "width": "100vw",
                "height": "100vh",
                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "background-color": "#353535",
            },
        )
        self.layout = html.Div([self.sidebar, self.content], id="stats-main")
        self.displayed_data = {}

        @callback(
            Output("file-popup", "is_open", allow_duplicate=True),
            Output("file-popup", "children", allow_duplicate=True),
            Input("stats-build-request", "n_intervals"),
            prevent_initial_call=True,
        )
        def check_for_update(_):
            if self.needs_build:
                self.needs_build = False
                return True, self.file_popup.update_files()
            else:
                raise exceptions.PreventUpdate()

        # print(self.get_data("cures", None, None))

    def print(self):
        print(self.visible_data)
        print(self.visible_groups)
        print(self.visible_diseases)

    def reset(self):
        self.visible_data = []
        self.visible_groups = [None]
        self.visible_diseases = [None]
        self.data_dict = {}
        self.use_cumulative_data = False
        self.sidebar.rebuild()
        self.file_popup.update_files()

    def rebuild_sidebar(self):
        self.sidebar = HTMLSidebar(self)

    def load_stats(self, name):
        self.stats = self.project.load_stats(name)

    def build_graph(self):
        self.update_data()
        if not self.data_dict:
            # Handle the case when data_dict is empty
            df = pd.DataFrame(columns=["Step", "DefaultColumn"])
            fig = px.line(df, x="Step", y=df.columns[1:], labels={"index": "Step"})
        else:
            df = pd.DataFrame(self.data_dict)
            if self.use_cumulative_data:
                df = df.cumsum(axis=0)
            fig = px.line(df, x=df.index, y=df.columns, labels={"index": "Step"})
        fig.update_layout(
            legend_title_text="Plots", paper_bgcolor="#353535", font={"color": "azure"}
        )
        fig.update_yaxes(title_text="People")
        return fig

    def update_data(self):
        self.data_dict.clear()
        for data, group, disease in itertools.product(
            self.visible_data, self.visible_groups, self.visible_diseases
        ):
            name = data
            if group:
                name += f" {self.project.network.get_group_by_id(group).name}"
            if disease:
                name += f" {self.project.network.get_disease_by_id(disease).name}"
            name = name.replace("_", " ")
            self.data_dict[name] = self.get_data(data, group, disease)

    def get_data(self, data, group=None, disease=None):
        if group:
            if disease and ("infections" in data or "cures" in data):
                return self.stats.group_stats[group].to_dict()[data][disease]
            elif not disease and ("infections" in data or "cures" in data):
                return [
                    sum(x) for x in zip(*self.stats.group_stats[group].to_dict()[data].values())
                ]
            else:
                return self.stats.group_stats[group].to_dict()[data]
        else:
            if disease and ("infections" in data or "cures" in data):
                arrs = [y.to_dict()[data][disease] for y in self.stats.group_stats.values()]
                return [sum(x) for x in zip(*arrs)]
            elif not disease and ("infections" in data or "cures" in data):
                arrs = []
                for x in (y.to_dict()[data].values() for y in self.stats.group_stats.values()):
                    arrs.extend([*x])
                return [sum(x) for x in zip(*arrs)]
            else:
                arrs = [y.to_dict()[data] for y in self.stats.group_stats.values()]
                return [sum(x) for x in zip(*arrs)]

    def add_data(self, data):
        if data not in self.visible_data:
            self.visible_data.append(data)

    def remove_data(self, data):
        if data in self.visible_data:
            self.visible_data.remove(data)

    def add_group(self, group):
        if self.visible_groups and self.visible_groups[0] is None:
            self.visible_groups.clear()
        if group not in self.visible_groups:
            self.visible_groups.append(group)

    def remove_group(self, group):
        if group in self.visible_groups:
            self.visible_groups.remove(group)

    def set_all_groups(self):
        self.visible_groups.clear()
        self.visible_groups.append(None)

    def add_disease(self, disease):
        if self.visible_diseases and self.visible_diseases[0] is None:
            self.visible_diseases.clear()
        if disease not in self.visible_diseases:
            self.visible_diseases.append(disease)

    def remove_disease(self, disease):
        if disease in self.visible_diseases:
            self.visible_diseases.remove(disease)

    def set_all_diseases(self):
        self.visible_diseases.clear()
        self.visible_diseases.append(None)
