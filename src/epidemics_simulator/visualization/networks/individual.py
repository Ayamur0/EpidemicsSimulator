import itertools
import math
import random
import time
from dash import Dash, html, dcc, callback_context
import plotly.express as px
from dash.dependencies import Input, Output
from src.epidemics_simulator.storage import Network, NodeGroup
import matplotlib.pyplot as plt
from src.epidemics_simulator.algorithms import CircleGrid
import threading
import dash_bootstrap_components as dbc
import os


# https://stackoverflow.com/questions/69498713/how-to-update-a-networkx-drawing
# https://pygraphviz.github.io/documentation/stable/install.html
# https://community.plotly.com/t/set-specific-color-to-scatter-3d-points/67443
# https://community.plotly.com/t/updating-colours-on-an-animation-using-html-and-then-refreshing-the-animation-slider/70911


class Individual:
    HEALTHY = "rgb(0.043, 0.388, 0.082)"
    CURED = "rgb(0.192, 0.961, 0.573)"
    INFECTED = "rgb(0.659, 0, 0)"
    VACCINATED = "rgb(0.067, 0, 0.941)"
    DECEASED = "rgb(0.012, 0.012, 0.012)"

    PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"

    def __init__(self) -> None:
        self.X = []
        self.Y = []
        self.Z = []
        self.color_seq = []
        self.nodes = []
        self.stylesheet = []
        self.next_node_id = 0

    def flask(self):
        from flask import Flask, render_template
        import time
        import json

        x = []
        y = []
        z = []
        pts = CircleGrid.get_points_3D(100)
        x, y, z = zip(*pts)

        app = Flask(__name__)

        @app.route("/")
        def index():
            # Create the initial scatter plot
            fig3 = px.scatter_3d(x=x, y=y, z=z, color_discrete_sequence=["red"] * 100)

            # Convert Plotly figure to JSON
            initial_plot = fig3.to_json()

            return render_template("index.html", initial_plot=initial_plot)

        app.run(debug=True)

    def plot(self):
        x = []
        y = []
        z = []
        pts = CircleGrid.get_points_3D(100)
        x, y, z = zip(*pts)
        fig3 = px.scatter_3d(
            x=x,
            y=y,
            z=z,
            color_discrete_sequence=["red"] * 100
            # color=elem,
            # color_discrete_sequence=[
            #     "rgb(1.0,0.2663545845364998,0.0)",
            #     "rgb(0.6694260712462251,0.7779863207340414,1.0)",
            #     "rgb(1.0,0.9652869470673199,0.9287833665638421)",
            # ],
        )
        # plot_widget = widgets.Output()
        # display(plot_widget)
        # with plot_widget:
        #     fig3.show()
        fig3["layout"]["uirevision"] = "0"
        print(os.listdir(os.getcwd() + "/src/epidemics_simulator/visualization/networks/assets"))
        app = Dash(
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            assets_folder=os.getcwd() + "/assets",
        )

        sidebar = html.Div(
            [
                html.Div(
                    [
                        # width: 3rem ensures the logo is the exact width of the
                        # collapsed sidebar (accounting for padding)
                        html.Img(src=self.PLOTLY_LOGO, style={"width": "3rem"}),
                        html.H2("Sidebar"),
                    ],
                    className="sidebar-header",
                ),
                html.Hr(),
                dbc.Nav(
                    [
                        dbc.NavLink(
                            [html.I(className="fas fa-home me-2"), html.Span("All")],
                            href="/",
                            active="exact",
                        ),
                        dbc.NavLink(
                            [
                                html.I(className="fas fa-calendar-alt me-2"),
                                html.Span("Group1"),
                            ],
                            href="/calendar",
                            active="exact",
                        ),
                        dbc.NavLink(
                            [
                                html.I(className="fas fa-envelope-open-text me-2"),
                                html.Span("Group2"),
                            ],
                            href="/messages",
                            active="exact",
                        ),
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
            className="sidebar",
        )

        content = html.Div(
            [
                dcc.Graph(
                    figure=fig3,
                    id="live-graph",
                    style={"height": "80vh"},
                ),
                dcc.Interval(id="update-color", interval=10 * 1000, n_intervals=0),
                html.Button("Update Graph", id="update-button", n_clicks=0),
            ],
            style={"height": "80vh"},
        )

        # app.layout = html.Div(
        #     [
        #         dcc.Graph(
        #             figure=fig3,
        #             id="live-graph",
        #             style={"height": "80vh"},
        #         ),
        #         dcc.Interval(id="update-color", interval=10 * 1000, n_intervals=0),
        #         html.Button("Update Graph", id="update-button", n_clicks=0),
        #     ],
        #     style={"height": "80vh"},
        # )
        app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

        @app.callback(
            Output("live-graph", "figure"),
            [Input("update-color", "n_intervals"), Input("update-button", "n_clicks")],
            prevent_initial_call=True,
        )
        def update_graph_scatter(n_intervals, x):
            print(n_intervals)
            print(x)
            trigger_id = callback_context.triggered_id
            if trigger_id and "update-button" in trigger_id:
                new_color_sequence = random.choices(["purple", "blue"], k=100)
            elif trigger_id and "update-color" in trigger_id:
                new_color_sequence = random.choices(
                    [self.CURED, self.HEALTHY, self.VACCINATED, self.INFECTED, self.DECEASED], k=100
                )
                # new_color_sequence = self.color_seq
            else:
                new_color_sequence = random.choices(["pink"], k=100)
            fig3.update_traces(marker=dict(color=new_color_sequence))
            fig3["layout"]["uirevision"] = "0"
            return fig3

        # def test():
        #     time.sleep(10)
        #     self.color_seq = random.choices(["purple", "blue"], k=100)

        # t = threading.Thread(target=test)
        # t.run()

        # @app.callback(
        #     Output("live-graph", "figure", allow_duplicate=True),
        #     [Input("update-button", "n_clicks")],
        # )
        # def update_graph_button(n_clicks):
        #     # Similar to update_graph_scatter but triggered by a button click
        #     new_color_sequence = random.choices(["green", "yellow", "blue", "red", "purple"], k=100)
        #     fig3.update_traces(marker=dict(color=new_color_sequence))

        #     return fig3

        app.run_server(debug=True, use_reloader=True)

        plt.pause(1)

    def add_network_points(self, network: Network):
        max_group_size = 0
        group_num = 0
        for group in network.groups:
            if group.active:
                group_num += 1
            if group.size > max_group_size:
                max_group_size = group.size

        offsets, block_len = self.generate_offsets(group_num, max_group_size, 5)
        print(offsets)
        print(block_len)

        for group, offset in zip(network.groups, offsets):
            if group.active:
                self.add_group_points(group, offset, block_len)

    def host(self):
        # G = nx.Graph(len(self.nodes))  # An example graph
        center_node = 5  # Or any other node to be in the center
        # edge_nodes = set(G) - {center_node}
        # Ensures the nodes around the circle are evenly distributed
        # pos = nx.circular_layout(G.subgraph(edge_nodes))
        # pos[center_node] = np.array([0, 0])  # manually specify node position
        # nx.draw(G, self.nodes, with_labels=True)
        # G = nx.Graph()
        options = {
            # "font_size": 36,
            "node_size": 300,
            # "node_color": "white",
            "edgecolors": "black",
            "linewidths": 1,
            # "width": 20,
        }
        # nx.draw_networkx(G, self.nodes, **options)
        colors = ["blue", "green"] * 50
        # pos = nx.nx_agraph.graphviz_layout(G, prog="neato")
        pos = {}
        for i in range(100):
            # G.add_node(i)
            pos[i] = self.nodes[i]
        del colors[50]
        del pos[50]
        # G.remove_node(50)
        # nx.draw(G, pos, node_color=colors, **options)
        plt.ion()
        plt.draw()
        plt.pause(5)
        colors[50] = "red"
        # nx.draw(G, pos, node_color=colors, **options)
        plt.draw()
        # print(G)
        # fig.canvas.draw()
        # fig.canvas.flush_events()
        plt.pause(10)
        # plt.show()
        # app = Dash(__name__)
        # app.layout = html.Div(
        #     [
        #         cyto.Cytoscape(
        #             id="live-graph",
        #             layout={"name": "preset"},
        #             style={"width": "100%", "height": "800px"},
        #             elements=self.nodes,
        #             stylesheet=self.stylesheet,
        #         )
        #     ]
        # )

        # @app.callback(Output("live-graph", "figure"), [Input("interval-component", "n_intervals")])
        # def update_graph_scatter(n):
        #     X.append(np.random.rand() * 10)
        #     Y.append(np.random.rand() * 10)
        #     Z.append(np.random.rand() * 10)

        #     fig = go.Figure()
        #     fig.add_scatter3d(x=X, y=Y, z=Z, mode="markers")

        #     return fig

        # app.run_server(debug=True, use_reloader=False)

    def add_network_points(self, network: Network):
        max_group_size = 0
        group_num = 0
        for group in network.groups:
            if group.active:
                group_num += 1
            if group.size > max_group_size:
                max_group_size = group.size

        offsets, block_len = self.generate_offsets(group_num, max_group_size, 5)
        print(offsets)
        print(block_len)

        for group, offset in zip(network.groups, offsets):
            if group.active:
                self.add_group_points(group, offset, block_len)

    def add_group_points(self, group: NodeGroup, offset: (int, int), block_len: int):
        points = self.generate_cube_points(block_len, 1, offset)
        points = points[: group.size]
        # https://dash.plotly.com/cytoscape/styling
        # add edges {'data': {'source': 'one', 'target': 'two'}, 'classes': 'red'},
        # app.layout = html.Div([
        #     cyto.Cytoscape(
        #         id='cytoscape-styling-1',
        #         layout={'name': 'preset'},
        #         style={'width': '100%', 'height': '400px'},
        #         elements=simple_elements,
        #         stylesheet=[
        #             # Group selectors
        #             {
        #                 'selector': 'node',
        #                 'style': {
        #                     'content': 'data(label)'
        #                 }
        #             },

        #             # Class selectors
        #             {
        #                 'selector': '.red',
        #                 'style': {
        #                     'background-color': 'red',
        #                     'line-color': 'red'
        #                 }
        #             },
        #             {
        #                 'selector': '.triangle',
        #                 'style': {
        #                     'shape': 'triangle'
        #                 }
        #             }
        #         ]
        #     )
        # ])
        for point in points:
            # self.nodes.append(
            #     {
            #         "data": {"id": str(self.next_node_id), "label": ""},
            #         "position": {"x": point[0] * 10, "y": point[1] * 10, "z": point[2] * 10},
            #         "classes": group.id,
            #     }
            # )
            # self.nodes.append(np.array([point[0], point[1]]))
            self.nodes.append(([point[0], point[1]]))
            # self.nodes[self.next_node_id] = (point[0], point[1])
            self.next_node_id += 1

        self.stylesheet.append(
            {
                "selector": f".{group.id}",
                "style": {"background-color": group.color, "width": 20, "height": 20},
            }
        )

    # def generate_cube_points(self, n: int, side_length: int, offset: (int, int, int)):
    #     points = []
    #     for z, y, x in itertools.product(range(n), repeat=3):
    #         point = (
    #             x * side_length + offset[0],
    #             y * side_length + offset[1],
    #             z * side_length + offset[2],
    #         )
    #         points.append(point)
    #     return points

    def generate_cube_points(self, n: int, side_length: int, offset: (int, int)):
        points = []
        for y, x in itertools.product(range(n), repeat=2):
            point = (
                x * side_length + offset[0],
                y * side_length + offset[1],
            )
            points.append(point)
        return points

    def generate_offsets(self, num_groups, max_group_size, spacer):
        # Determine the side length of the cube
        side_length = math.ceil(num_groups ** (1 / 2))
        offset_length = math.ceil(max_group_size ** (1 / 2)) + spacer

        return self.generate_cube_points(side_length, offset_length, (0, 0)), offset_length

    # def generate_offsets(self, num_groups, max_group_size, spacer):
    #     # Determine the side length of the cube
    #     side_length = math.ceil(num_groups ** (1 / 3))
    #     offset_length = math.ceil(max_group_size ** (1 / 3)) + spacer

    #     return self.generate_cube_points(side_length, offset_length, (0, 0, 0)), side_length
