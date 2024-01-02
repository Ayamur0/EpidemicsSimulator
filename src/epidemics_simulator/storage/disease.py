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

    def to_dict(self):
        return {
            "name": self.name,
            "id": self.id,
            "color": self.color,
            "fatality_rate": self.fatality_rate,
            "vaccinated_fatality_rate": self.vaccinated_fatality_rate,
            "infection_rate": self.infection_rate,
            "reinfection_rate": self.reinfection_rate,
            "vaccinated_infection_rate": self.vaccinated_infection_rate,
            "duration": self.duration,
            "initial_infection_count": self.initial_infection_count,
        }

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            name=data["name"],
            color=data["color"],
            fatality_rate=data["fatality_rate"],
            vaccinated_fatality_rate=data["vaccinated_fatality_rate"],
            infection_rate=data["infection_rate"],
            reinfection_rate=data["reinfection_rate"],
            vaccinated_infection_rate=data["vaccinated_infection_rate"],
            duration=data["duration"],
            initial_infection_count=data["initial_infection_count"],
        )
        instance.id = data["id"]
        if instance.id >= Disease.id_counter:
            Disease.id_counter = instance.id + 1
        return instance
