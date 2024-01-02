from src.epidemics_simulator.storage import Network, Project
from src.epidemics_simulator.visualization.networks.html_network_view import HTMLNetworkView
from src.epidemics_simulator.visualization.networks.html_simulation_view import HTMLSimulationView
from src.epidemics_simulator.visualization.networks.graph_3d import Graph3D
from src.epidemics_simulator.visualization.stats.html_stats_view import HTMLStatsView
from flask import Flask
from dash.dependencies import Input, Output, State
from dash import Dash, html, dcc, callback
import dash_bootstrap_components as dbc
import os


class DashServer:
    def run_network_view(self, project: Project):
        graph = Graph3D(project.network)
        html_view = HTMLNetworkView(graph)
        app = Dash(
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            assets_folder=os.getcwd() + "/assets",
            suppress_callback_exceptions=True,
        )
        # app.layout = html_view.layout
        app.layout = html.Div([dcc.Location(id="url", refresh=False), html.Div(id="page-content")])

        sim_view = HTMLSimulationView(project, graph)

        stats_view = HTMLStatsView(project)

        @callback(Output("page-content", "children"), [Input("url", "pathname")])
        def display_page(pathname):
            if pathname == "/view":
                html_view.reset()
                return html_view.layout
            elif pathname == "/sim":
                sim_view.reset()
                return sim_view.layout
            elif pathname == "/stats":
                return stats_view.layout
            else:  # if redirected to unknown link
                return "404"

        app.run(debug=True, use_reloader=True)
