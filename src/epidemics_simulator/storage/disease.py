class Disease:
    def __init__(self, name) -> None:
        self.name = name
        self.id = name
        self.color = "rgb(0.659, 0, 0)"
        self.fatality_rate = 0.5
        self.vaccinated_fatality_rate = 0.2
        self.infection_rate = 0.2
        self.reinfection_rate = 0.05
        self.vaccinated_infection_rate = 0.001
        self.duration = 5
        self.initial_infection_count = 10
