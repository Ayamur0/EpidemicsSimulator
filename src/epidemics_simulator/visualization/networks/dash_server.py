from src.epidemics_simulator.storage import Network, Project
from .html_network_view import HTMLNetworkView
from .html_simulation_view import HTMLSimulationView
from .graph_3d import Graph3D
from flask import Flask
from dash.dependencies import Input, Output, State
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
import os

current_page = "/"


class DashServer:
    def run_network_view(self, project: Project):
        graph = Graph3D(project.network)
        html_view = HTMLNetworkView(graph.fig, graph.on_reload)
        app = Dash(
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            assets_folder=os.getcwd() + "/assets",
            suppress_callback_exceptions=True,
        )
        # app.layout = html_view.layout
        app.layout = html.Div([dcc.Location(id="url", refresh=False), html.Div(id="page-content")])
        html_view.on_grid_changed = graph.toggle_grid
        html_view.on_show_status_colors_changed = graph.toggle_color
        html_view.on_show_internal_edge_changed = graph.toggle_internal_edges
        html_view.on_show_external_edge_changed = graph.toggle_external_edges
        html_view.on_node_percent_changed = graph.change_visible_node_percent
        html_view.on_show_group_changed = graph.hide_group
        graph.sim_test(app)

        sim_view = HTMLSimulationView(
            project, graph.update_status_colors, graph.fig, graph.on_reload
        )
        sim_view.on_grid_changed = graph.toggle_grid
        sim_view.on_show_status_colors_changed = graph.toggle_color
        sim_view.on_show_internal_edge_changed = graph.toggle_internal_edges
        sim_view.on_show_external_edge_changed = graph.toggle_external_edges
        sim_view.on_node_percent_changed = graph.change_visible_node_percent
        sim_view.on_show_group_changed = graph.hide_group

        @app.callback(Output("page-content", "children"), [Input("url", "pathname")])
        def display_page(pathname):
            global current_page
            print(pathname)
            if pathname == "/view":
                html_view.reset()
                current_page = pathname
                return html_view.layout
            elif pathname == "/sim":
                sim_view.reset()
                return sim_view.layout
            else:  # if redirected to unknown link
                return "404"

        app.run(debug=True, use_reloader=True)
