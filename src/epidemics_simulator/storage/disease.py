class Disease:
    id_counter = 0

    def __init__(
        self,
        name,
        color: str = "rgb(0.659, 0, 0)",
        fatality_rate: float = 0.2,
        vaccinated_fatality_rate: float = 0.05,
        infection_rate: float = 0.2,
        reinfection_rate: float = 0.05,
        vaccinated_infection_rate: float = 0.001,
        duration: int = 5,
        initial_infection_count: int = 10,
    ) -> None:
        self.name = name
        self.id = Disease.id_counter
        Disease.id_counter += 1
        self.color = color
        self.fatality_rate = fatality_rate
        self.vaccinated_fatality_rate = vaccinated_fatality_rate
        self.infection_rate = infection_rate
        self.reinfection_rate = reinfection_rate
        self.vaccinated_infection_rate = vaccinated_infection_rate
        self.duration = duration
        self.initial_infection_count = initial_infection_count
