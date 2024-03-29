from io import StringIO
import json
from dash import html
import pandas as pd
import os
from pathlib import Path
import re


class SimStats:
    def __init__(self, network) -> None:
        self.group_stats = {}
        self.log_text_cache = []
        self.group_ids = []
        self.group_names = []
        self.group_sizes = []
        self.disease_ids = []
        self.disease_names = []
        if network:
            for disease in network.diseases:
                self.disease_ids.append(disease.id)
                self.disease_names.append(disease.name)
            for group in network.active_groups:
                self.group_ids.append(group.id)
                self.group_names.append(group.name)
                self.group_sizes.append(group.size)
                self.group_stats[group.id] = GroupSimStats(group.size, group.name, self.disease_ids)

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
        if not self.group_stats:
            return
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
            group: GroupSimStats.from_dict(stats_data) for group, stats_data in data.items()
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

    def to_csv(self, path, name):
        df = self.to_dataframe()
        df.to_pickle(Path(os.path.join(path, name + ".pkl")))

    @classmethod
    def from_csv(cls, filepath):
        df = pd.read_pickle(Path(filepath))
        return SimStats.from_dataframe(df)

    def to_dataframe(self):
        data = {
            "Group": [],
            "Disease": [],
            "Infections": [],
            "Reinfections": [],
            "VaccInfections": [],
            "UnvaccInfections": [],
            "Cures": [],
            "Vaccinations": [],
            "Deaths": [],
            "VaccDeaths": [],
            "UnvaccDeaths": [],
        }

        group_data = {
            "GroupIds": self.group_ids,
            "GroupNames": self.group_names,
            "GroupSizes": self.group_sizes,
        }
        disease_data = {
            "DiseaseIds": self.disease_ids,
            "DiseaseNames": self.disease_names,
        }

        for group_id, group_stat in self.group_stats.items():
            data["Vaccinations"].append(group_stat.vaccinations)
            data["Deaths"].append(group_stat.deaths)
            data["VaccDeaths"].append(group_stat.vacc_deaths)
            data["UnvaccDeaths"].append(group_stat.unvacc_deaths)
            first = True
            for disease_id, disease_stat in group_stat.infections.items():
                if not first:
                    data["Vaccinations"].append(None)
                    data["Deaths"].append(None)
                    data["VaccDeaths"].append(None)
                    data["UnvaccDeaths"].append(None)
                data["Group"].append(group_id)
                data["Disease"].append(disease_id)
                data["Infections"].append(disease_stat)
                data["Reinfections"].append(group_stat.reinfections[disease_id])
                data["VaccInfections"].append(group_stat.vacc_infections[disease_id])
                data["UnvaccInfections"].append(group_stat.unvacc_infections[disease_id])
                data["Cures"].append(group_stat.cures[disease_id])
                first = False
            if not group_stat.infections.items():
                data["Group"].append(group_id)
                data["Disease"].append(-1)
                data["Infections"].append([])
                data["Reinfections"].append([])
                data["VaccInfections"].append([])
                data["UnvaccInfections"].append([])
                data["Cures"].append([])

        df1 = pd.DataFrame(group_data)
        df1["Source"] = "groups"
        df2 = pd.DataFrame(disease_data)
        df2["Source"] = "diseases"
        df3 = pd.DataFrame(data)
        df3["Source"] = "data"
        return pd.concat([df1, df2, df3])

    @classmethod
    def from_dataframe(cls, df):
        df1 = df[df["Source"] == "groups"].drop(columns="Source")
        df2 = df[df["Source"] == "diseases"].drop(columns="Source")
        df3 = df[df["Source"] == "data"].drop(columns="Source")
        sim_stats = cls(None)

        sim_stats.group_names = df1["GroupNames"].tolist()
        sim_stats.group_ids = df1["GroupIds"].tolist()
        sim_stats.group_sizes = df1["GroupSizes"].tolist()
        sim_stats.disease_ids = df2["DiseaseIds"].tolist()
        sim_stats.disease_names = df2["DiseaseNames"].tolist()

        for id, name, size in zip(
            sim_stats.group_ids, sim_stats.group_names, sim_stats.group_sizes
        ):
            sim_stats.group_stats[id] = GroupSimStats(size, name, sim_stats.disease_ids)

        for _, row in df3.iterrows():
            group_id = row["Group"]
            disease_id = row["Disease"]
            group_stat = sim_stats.group_stats[group_id]

            if disease_id != -1:
                group_stat.infections[disease_id] = row["Infections"]
                group_stat.reinfections[disease_id] = row["Reinfections"]
                group_stat.vacc_infections[disease_id] = row["VaccInfections"]
                group_stat.unvacc_infections[disease_id] = row["UnvaccInfections"]
                group_stat.cures[disease_id] = row["Cures"]
            else:  # no diseases exist, fill all related data with zeroes
                dummy_data = [0] * len(row["Vaccinations"])
                group_stat.infections[disease_id] = dummy_data
                group_stat.reinfections[disease_id] = dummy_data
                group_stat.vacc_infections[disease_id] = dummy_data
                group_stat.unvacc_infections[disease_id] = dummy_data
                group_stat.cures[disease_id] = dummy_data

            if row["Vaccinations"]:
                group_stat.vaccinations = row["Vaccinations"]
                group_stat.deaths = row["Deaths"]
                group_stat.vacc_deaths = row["VaccDeaths"]
                group_stat.unvacc_deaths = row["UnvaccDeaths"]
        return sim_stats

    def is_valid_file_name(name: str):
        # Define a regular expression pattern to match forbidden characters
        ILLEGAL_NTFS_CHARS = r"[<>:/\\|?*\"]|[\0-\31]"
        # Define a list of forbidden names
        FORBIDDEN_NAMES = [
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        ]
        # Check for forbidden characters
        match = re.search(ILLEGAL_NTFS_CHARS, name)
        if match:
            return False, f"Invalid character {match[0]} for filename {name}"
        # Check for forbidden names
        if name.upper() in FORBIDDEN_NAMES:
            return False, f"{name} is a reserved folder name in windows"
        # Check for empty name (disallowed in Windows)
        if name.strip() == "":
            return False, "Empty file name not allowed in Windows"
        # Check for names starting or ending with dot or space
        match = re.match(r"^[. ]|.*[. ]$", name)
        if match:
            return False, f"Invalid start or end character ({match[0]})" f" in folder name {name}"
        return True, ""


class GroupSimStats:
    def __init__(self, group_size, group_name, diseases_ids) -> None:
        self.name = group_name
        self.size = group_size
        self.unvacc_infections = {}
        self.vacc_infections = {}
        self.reinfections = {}
        self.infections = {}
        self.cures = {}
        for id in diseases_ids:
            self.infections[id] = [0]
            self.unvacc_infections[id] = [0]
            self.vacc_infections[id] = [0]
            self.reinfections[id] = [0]
            self.cures[id] = [0]
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
