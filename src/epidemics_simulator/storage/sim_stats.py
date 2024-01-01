class SimStats:
    def __init__(self, network) -> None:
        self.group_stats = {}
        for group in network.groups:
            self.group_stats[group.id] = GroupSimStats(group.size, group.name, network.diseases)

    def new_step(self):
        for group in self.group_stats:
            self.group_stats[group].new_step()

    def add_death(self, group_id):
        self.group_stats[group_id].add_death()

    def add_vaccination(self, group_id):
        self.group_stats[group_id].add_vaccination()

    def add_infection(self, group_id, disease_id):
        self.group_stats[group_id].add_infection(disease_id)

    def add_cure(self, group_id, disease_id):
        self.group_stats[group_id].add_cure(disease_id)

    def get_log_text(self):
        steps = len(next(iter(self.group_stats.values())).deaths)
        s = ""
        for step in range(steps - 1, -1, -1):
            s += f"Step {step}\n"
            for group in self.group_stats:
                s += self.group_stats[group].get_log_text(step)
                s += "\n"
        return s

    def print(self):
        for group in self.group_stats:
            print(f"Stats of group {group}")
            self.group_stats[group].print()


class GroupSimStats:
    def __init__(self, group_size, group_name, diseases) -> None:
        self.name = group_name
        self.size = group_size
        self.infections = {}
        self.cures = {}
        for disease in diseases:
            self.infections[disease.id] = [0]
            self.cures[disease.id] = [0]
        self.vaccinations = [0]
        self.deaths = [0]

    def add_step_results(self, new_infections, new_vaccinations, new_deaths):
        for inf in new_infections:
            if inf not in self.infected:
                self.infections[inf] = []
            self.infected[inf].append(new_infections[inf])
        self.vaccinations.append(new_vaccinations)
        self.deaths.append(new_deaths)

    def get_log_text(self, step):
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
            self.cures[disease].append(0)
        self.vaccinations.append(0)
        self.deaths.append(0)

    def add_death(self):
        self.deaths[-1] += 1

    def add_vaccination(self):
        self.vaccinations[-1] += 1

    def add_infection(self, disease_id):
        self.infections[disease_id][-1] += 1

    def add_cure(self, disease_id):
        self.cures[disease_id][-1] += 1

    def print(self):
        print("infections")
        print(self.infections)
        print("vaccinations")
        print(self.vaccinations)
        print("deaths")
        print(self.deaths)
