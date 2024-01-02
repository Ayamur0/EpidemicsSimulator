from src.epidemics_simulator.storage import Network
import plotly.graph_objs as go


class Legend:
    def __init__(self, network: Network) -> None:
        status_colors = [
            network.healthy_color,
            network.cured_color,
            network.vaccinated_color,
            network.deceased_color,
        ]
        status_labels = ["Healthy", "Cured", "Vaccinated", "Deceased"]
        for disease in network.diseases:
            status_colors.append(disease.color)
            status_labels.append(disease.name)
        group_colors = []
        group_labels = []
        for group in network.groups:
            group_colors.append(group.color)
            group_labels.append(group.name)
        self.group_legend = self._create_trace(group_colors, group_labels)
        self.status_legend = self._create_trace(status_colors, status_labels)

    def _create_trace(self, colors, labels):
        trace = []
        for color, label in zip(
            colors,
            labels,
        ):
            trace.append(
                go.Scatter3d(
                    x=[None],
                    y=[None],
                    z=[None],
                    uirevision="0",
                    mode="markers",
                    name=label,
                    marker=dict(size=7, color=color),
                )
            )
        return trace
