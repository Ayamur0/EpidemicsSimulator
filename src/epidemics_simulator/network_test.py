import time

from storage import NodeGroup, Network, Node
import gravis as gv
from tkinterhtml import HtmlFrame
import tkinter as tk


def main():
    n = Network()
    g1 = NodeGroup(n, "Test1", 100, 10, 0.1, 5, 2)
    g2 = NodeGroup(n, "Test2", 100, 10, 0.1, 5, 2)
    g3 = NodeGroup(n, "Test3", 100, 10, 0.1, 5, 2)
    g4 = NodeGroup(n, "Test4", 100, 10, 0.1, 5, 2)
    n.add_group(g1)
    n.add_group(g2)
    n.add_group(g3)
    n.add_group(g4)
    g1.create_internal_connections()
    g2.create_internal_connections()
    g3.create_internal_connections()
    g4.create_internal_connections()

    g1.add_external_connection(g2.id, -1, 2)
    g2.add_external_connection(g3.id, -2, 3)
    g3.add_external_connection(g4.id, -1, 2)

    graph1 = {
        "graph": {
            "directed": False,
            "metadata": {
                "arrow_size": 5,
                "background_color": "white",
                "edge_size": 3,
                "edge_label_size": 14,
                "edge_label_color": "black",
                "node_size": 15,
            },
            "nodes": Node.graph_nodes,
            "edges": Node.graph_edges,
        }
    }

    t1 = time.time()
    fig = gv.three(graph1, show_node_label=True, show_edge_label=False, show_edge=True).display()
    print(time.time() - t1)
    # for n in Node.graph_nodes.keys():
    #     t1 = time.time()
    #     Node.graph_nodes[n]["metadata"]["color"] = "#00ff00"
    #     graph1["nodes"] = Node.graph_nodes
    #
    #     fig = gv.three(graph1, show_node_label=True, show_edge_label=False).to_html()
    #     print(fig.to_html())
    #     print(time.time() - t1)


if __name__ == "__main__":
    main()
