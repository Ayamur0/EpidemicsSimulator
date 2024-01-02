class Disease:
    id_counter = 0

    def __init__(self, name) -> None:
        self.name = name
        self.id = Disease.id_counter
        Disease.id_counter += 1
        self.color = "rgb(0.659, 0, 0)"
        self.fatality_rate = 0.2
        self.vaccinated_fatality_rate = 0.05
        self.infection_rate = 0.2
        self.reinfection_rate = 0.05
        self.vaccinated_infection_rate = 0.001
        self.duration = 5
        self.initial_infection_count = 10
