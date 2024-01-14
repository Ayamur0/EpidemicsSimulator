import math
import itertools
import random
from src.epidemics_simulator.storage import Network
from src.epidemics_simulator.algorithms import CircleGrid


class PlotlyWrapper:
    def calculate_edge_coords(
        network: Network,
        internal_edges: bool,
        external_edges: bool,
        hidden_groups,
        node_id_map,
        node_coords_x,
        node_coords_y,
        node_coords_z,
    ):
        aXe, aYe, aZe = [], [], []
        for group in network.active_groups:
            if group.id in hidden_groups:
                continue
            if internal_edges:
                edges = list(group.internal_edges)
            else:
                edges = []
            if external_edges:
                for target in group.external_edges:
                    if target not in hidden_groups:
                        edges.extend(group.external_edges[target])
            for edge in edges:
                _from, to = edge.split("/")
                if not (_from in node_id_map and to in node_id_map):
                    continue
                from_ind = node_id_map[_from]
                to_ind = node_id_map[to]
                aXe.extend([node_coords_x[from_ind], node_coords_x[to_ind], None])
                aYe.extend([node_coords_y[from_ind], node_coords_y[to_ind], None])
                aZe.extend([node_coords_z[from_ind], node_coords_z[to_ind], None])
        return aXe, aYe, aZe

    def get_cube_coords(network: Network, visible_node_percent):
        max_group_size = 0
        group_num = 0
        for group in network.active_groups:
            if group.active:
                group_num += 1
            if group.size > max_group_size:
                max_group_size = group.size
        max_group_size = math.ceil(max_group_size * visible_node_percent)

        max_sphere_radius = CircleGrid.calculate_radius_3D(max_group_size)
        side_length = math.ceil(max_sphere_radius * 2 * 1.25)
        offset = math.ceil(max_sphere_radius * 2 * 0.125)

        points = []
        for z, y, x in itertools.product(range(math.ceil(group_num ** (1 / 3))), repeat=3):
            point = (x * side_length + offset, y * side_length + offset, z * side_length + offset)
            points.append(point)
        return points

    def adjust_node_coords(cube_coords, node_coords):
        offset = cube_coords.pop(random.randrange(len(cube_coords)))
        return [
            [coord[0] + offset[0], coord[1] + offset[1], coord[2] + offset[2]]
            for coord in node_coords
        ]

    def calculate_network_coords(network: Network, visible_node_percent):
        group_coords = {}
        node_id_map = {}
        Xn = []
        Yn = []
        Zn = []
        cube_coords = PlotlyWrapper.get_cube_coords(network, visible_node_percent)
        for group in network.active_groups:
            node_coords = CircleGrid.get_points_3D(math.ceil(visible_node_percent * group.size))
            node_coords = PlotlyWrapper.adjust_node_coords(cube_coords, node_coords)
            group_coords[group.id] = node_coords
            for i, node in zip(range(len(Xn), len(Xn) + len(node_coords)), group.members):
                node_id_map[node.id] = i
            x, y, z = zip(*node_coords)
            Xn.extend(x)
            Yn.extend(y)
            Zn.extend(z)
        return group_coords, node_id_map, Xn, Yn, Zn
