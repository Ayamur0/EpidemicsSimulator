import itertools
import math
from dash import Dash, html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import numpy as np
from src.epidemics_simulator.storage import Network, NodeGroup
import dash_cytoscape as cyto


class Individual:
    def __init__(self) -> None:
        self.X = []
        self.Y = []
        self.Z = []
        self.nodes = []
        self.stylesheet = []
        self.next_node_id = 0

    def host(self):
        app = Dash(__name__)

        X, Y, Z = [], [], []

        # app.layout = html.Div(
        #     [
        #         dcc.Graph(id="live-graph"),
        #         dcc.Interval(
        #             id="interval-component",
        #             interval=1000,  # in milliseconds
        #             n_intervals=1,  # start
        #             max_intervals=100,  # end , You should specify how many points you will receive
        #         ),
        #     ]
        # )
        app.layout = html.Div(
            [
                cyto.Cytoscape(
                    id="cytoscape-styling-1",
                    layout={"name": "preset"},
                    style={"width": "100%", "height": "400px"},
                    elements=self.nodes,
                    stylesheet=self.stylesheet,
                )
            ]
        )

        @app.callback(Output("live-graph", "figure"), [Input("interval-component", "n_intervals")])
        def update_graph_scatter(n):
            X.append(np.random.rand() * 10)
            Y.append(np.random.rand() * 10)
            Z.append(np.random.rand() * 10)

            fig = go.Figure()
            fig.add_scatter3d(x=X, y=Y, z=Z, mode="markers")

            return fig

        app.run_server(debug=True, use_reloader=False)

    def add_network_points(self, network: Network):
        max_group_size = 0
        group_num = 0
        for group in network.groups:
            if group.active:
                group_num += 1
            if group.size > max_group_size:
                max_group_size = group.size

        offsets, block_len = self.generate_offsets(group_num, max_group_size, 5)

        for group, offset in zip(network.groups, offsets):
            if group.active:
                self.add_group_points(group, offset, block_len)

    def add_group_points(self, group: NodeGroup, offset: (int, int, int), block_len: int):
        points = self.generate_cube_points(block_len, block_len, offset)
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
            self.nodes.append(
                {
                    "data": {"id": str(self.next_node_id), "label": ""},
                    "position": {"x": point[0], "y": point[1], "z": point[2]},
                    "classes": group.id,
                }
            )
            self.next_node_id += 1

        self.stylesheet.append(
            {
                "selector": f".{group.id}",
                "style": {"baclground-color": group.color},
            }
        )

    def generate_cube_points(self, n: int, side_length: int, offset: (int, int, int)):
        points = []
        for z, y, x in itertools.product(range(n), repeat=3):
            point = (
                x * side_length + offset[0],
                y * side_length + offset[1],
                z * side_length + offset[2],
            )
            points.append(point)
        return points

    def generate_offsets(self, num_groups, max_group_size, spacer):
        # Determine the side length of the cube
        side_length = math.ceil(num_groups ** (1 / 3))
        offset_length = math.ceil(max_group_size ** (1 / 3)) + spacer

        return self.generate_cube_points(side_length, offset_length, (0, 0, 0)), side_length
