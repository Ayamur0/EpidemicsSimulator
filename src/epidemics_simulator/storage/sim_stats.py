import json
from dash import html


class SimStats:
    def __init__(self, network) -> None:
        self.group_stats = {}
        self.log_text_cache = []
        for group in network.groups:
            self.group_stats[group.id] = GroupSimStats(group.size, group.name, network.diseases)

    def new_step(self):
        for group in self.group_stats:
            self.group_stats[group].new_step()

    def finish_step(self):
        self._add_log_text()

    def add_death(self, node):
        self.group_stats[node.group.id].add_death()
        if node.vaccinated:
            self.group_stats[node.group.id].add_vacc_death()
        else:
            self.group_stats[node.group.id].add_unvacc_death()

    def add_vaccination(self, node):
        self.group_stats[node.group.id].add_vaccination()

    def add_infection(self, node):
        self.group_stats[node.group.id].add_infection(node.infected.id)
        if node.vaccinated:
            self.group_stats[node.group.id].add_vacc_infection(node.infected.id)
        else:
            self.group_stats[node.group.id].add_unvacc_infection(node.infected.id)
        if node.num_of_infections > 1:
            self.group_stats[node.group.id].add_reinfection(node.infected.id)

    def add_cure(self, node):
        self.group_stats[node.group.id].add_cure(node.infected.id)

    def get_log_text(self):
        return "".join(reversed(self.log_text_cache))

    def get_log_text_html(self):
        html_el = []
        for text in reversed(self.log_text_cache):
            html_el.append(
                html.Span(
                    text,
                    className="mb-0",
                    style={"white-space": "pre-wrap"},
                ),
            )
            html_el.append(html.Hr())
        return html_el

    def _add_log_text(self):
        step = len(next(iter(self.group_stats.values())).deaths)
        s = f"Step {step}\n"
        for group in self.group_stats:
            s += self.group_stats[group].get_log_text()
            s += "\n"
        self.log_text_cache.append(s)

    def _add_full_log_text(self):
        self.log_text_cache.clear()
        steps = len(next(iter(self.group_stats.values())).deaths)
        for step in range(0, steps):
            s = f"Step {step}\n"
            for group in self.group_stats:
                s += self.group_stats[group].get_log_text_for_step(step)
                s += "\n"
            self.log_text_cache.append(s)

    def to_dict(self):
        return {group: stats.to_dict() for group, stats in self.group_stats.items()}

    @classmethod
    def from_dict(cls, data):
        instance = cls.__new__(cls)
        instance.group_stats = {
            group: GroupSimStats.from_dict(stats_data)
            for group, stats_data in data["group_stats"].items()
        }
        instance.log_text_cache = []
        instance._add_full_log_text()
        return instance

    def to_json(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "group_stats": {
                        group: stats.to_dict() for group, stats in self.group_stats.items()
                    }
                },
                f,
                ensure_ascii=False,
                indent=4,
            )
        return

    @classmethod
    def from_json(cls, filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        instance = cls.__new__(cls)
        instance.group_stats = {
            group: GroupSimStats.from_dict(stats_data)
            for group, stats_data in data["group_stats"].items()
        }
        instance.log_text_cache = []
        instance._add_full_log_text()
        return instance


class GroupSimStats:
    def __init__(self, group_size, group_name, diseases) -> None:
        self.name = group_name
        self.size = group_size
        self.unvacc_infections = {}
        self.vacc_infections = {}
        self.reinfections = {}
        self.infections = {}
        self.cures = {}
        for disease in diseases:
            self.infections[disease.id] = [0]
            self.unvacc_infections[disease.id] = [0]
            self.vacc_infections[disease.id] = [0]
            self.reinfections[disease.id] = [0]
            self.cures[disease.id] = [0]
        self.vaccinations = [0]
        self.deaths = [0]
        self.vacc_deaths = [0]
        self.unvacc_deaths = [0]

    def get_log_text(self):
        new_infections = 0
        total_infections = 0
        for disease in self.infections:
            new_infections += self.infections[disease][-1]
            total_infections += sum(self.infections[disease])
        new_cures = 0
        total_cures = 0
        for disease in self.cures:
            new_cures += self.cures[disease][-1]
            total_cures += sum(self.cures[disease])

        return f"""Group: {self.name}
            New Infections: {new_infections}
            Total Infections: {total_infections}
            Cured Infections: {new_cures}
            Total Cured Infections: {total_cures}
            New deaths: {self.deaths[-1]}
            Total deaths: {sum(self.deaths)}
            New Vaccinations: {self.vaccinations[-1]}
            Total Vaccinations: {sum(self.vaccinations)}
            """

    def get_log_text_for_step(self, step):
        new_infections = 0
        total_infections = 0
        for disease in self.infections:
            new_infections += self.infections[disease][step]
            total_infections += sum(self.infections[disease][:step])
        new_cures = 0
        total_cures = 0
        for disease in self.cures:
            new_cures += self.cures[disease][step]
            total_cures += sum(self.cures[disease][:step])

        return f"""Group: {self.name}
            New Infections: {new_infections}
            Total Infections: {total_infections}
            Cured Infections: {new_cures}
            Total Cured Infections: {total_cures}
            New deaths: {self.deaths[step]}
            Total deaths: {sum(self.deaths[:step])}
            New Vaccinations: {self.vaccinations[step]}
            Total Vaccinations: {sum(self.vaccinations[:step])}
            """

    def new_step(self):
        for disease in self.infections:
            self.infections[disease].append(0)
            self.reinfections[disease].append(0)
            self.vacc_infections[disease].append(0)
            self.unvacc_infections[disease].append(0)
            self.cures[disease].append(0)
        self.vaccinations.append(0)
        self.deaths.append(0)
        self.vacc_deaths.append(0)
        self.unvacc_deaths.append(0)

    def add_death(self):
        self.deaths[-1] += 1

    def add_vacc_death(self):
        self.vacc_deaths[-1] += 1

    def add_unvacc_death(self):
        self.unvacc_deaths[-1] += 1

    def add_vaccination(self):
        self.vaccinations[-1] += 1

    def add_infection(self, disease_id):
        self.infections[disease_id][-1] += 1

    def add_vacc_infection(self, disease_id):
        self.vacc_infections[disease_id][-1] += 1

    def add_unvacc_infection(self, disease_id):
        self.unvacc_infections[disease_id][-1] += 1

    def add_reinfection(self, disease_id):
        self.reinfections[disease_id][-1] += 1

    def add_cure(self, disease_id):
        self.cures[disease_id][-1] += 1

    def to_dict(self):
        return {
            "name": self.name,
            "size": self.size,
            "unvacc_infections": self.unvacc_infections,
            "vacc_infections": self.vacc_infections,
            "re_infections": self.reinfections,
            "total_infections": self.infections,
            "cures": self.cures,
            "vaccinations": self.vaccinations,
            "total_deaths": self.deaths,
            "vacc_deaths": self.vacc_deaths,
            "unvacc_deaths": self.unvacc_deaths,
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls.__new__(cls)
        instance.name = data["name"]
        instance.size = data["size"]
        instance.unvacc_infections = data["unvacc_infections"]
        instance.vacc_infections = data["vacc_infections"]
        instance.reinfections = data["re_infections"]
        instance.infections = data["total_infections"]
        instance.cures = data["cures"]
        instance.vaccinations = data["vaccinations"]
        instance.deaths = data["total_deaths"]
        instance.vacc_deaths = data["vacc_deaths"]
        instance.unvacc_deaths = data["unvacc_deaths"]
        return instance
