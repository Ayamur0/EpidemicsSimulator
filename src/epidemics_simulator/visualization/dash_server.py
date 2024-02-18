from src.epidemics_simulator.storage import Network, Project, SimStats
from src.epidemics_simulator.visualization.networks.html_network_view import HTMLNetworkView
from src.epidemics_simulator.visualization.networks.html_simulation_view import HTMLSimulationView
from src.epidemics_simulator.visualization.networks.graph_3d import Graph3D
from src.epidemics_simulator.visualization.stats.html_stats_view import HTMLStatsView
from flask import make_response, jsonify, request
from dash.dependencies import Input, Output, State
from dash import Dash, html, dcc, callback
import dash_bootstrap_components as dbc
import os
import traceback


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
        app.layout = html.Div(
            [
                dcc.Location(id="url", refresh=False),
                html.Div(id="page-content"),
                # html.Button(id="dummy-button", style={"opacity": "0"}),
            ]
        )

        sim_view = HTMLSimulationView(project, graph)

        stats_view = HTMLStatsView(project)

        @callback(
            Output("page-content", "children"),
            # Output("dummy-button", "n_clicks"),
            [Input("url", "pathname")],
            # State("dummy-button", "n_clicks"),
        )
        def display_page(pathname):
            if pathname == "/view":
                html_view.reset()
                return html_view.layout
            elif pathname == "/sim":
                sim_view.reset()
                return sim_view.layout
            elif pathname == "/stats":
                stats_view.reset()
                return stats_view.layout
            else:  # if redirected to unknown link
                return "404"

        @app.server.route("/update-data", methods=["POST"])
        def update():
            try:
                json_data = request.get_json()
                project = Project.from_dict(json_data)
                project.network.build()
                graph.update_network(project.network)
                html_view.reset()
                sim_view.project = project
                sim_view.reset()
                stats_view.project = project
                stats_view.reset()
                graph.build()
                html_view.needs_build = True
                sim_view.needs_build = True
                stats_view.needs_build = True
                return make_response(jsonify({"status": "OK"}), 200)
            except Exception as e:
                return make_response(
                    jsonify({"status": str(e), "stack_trace": traceback.format_exc()}), 400
                )

        @app.server.route("/update-stats", methods=["POST"])
        def update_stats():
            stats_view.reset()
            stats_view.needs_build = True
            return make_response(jsonify({"status": "OK"}), 200)

        app.run(debug=False, use_reloader=True) # Changed from debug=True to be able to start the server from an .exe
