class Disease:
    id_counter = 0

    def __init__(
        self,
        name: str,
        color: str = "rgb(0.659, 0, 0)",
        fatality_rate: float = 0.2,
        vaccinated_fatality_rate: float = 0.05,
        infection_rate: float = 0.2,
        reinfection_rate: float = 0.05,
        vaccinated_infection_rate: float = 0.001,
        duration: int = 5,
        cure_chance: float = 0.2,
        immunity_period: int = 8,
        infectiousness_factor: float = 1,
        initial_infection_count: int = 10,
    ) -> None:
        self.name = name
        self.id = str(Disease.id_counter)
        Disease.id_counter += 1
        self.color = color
        self.fatality_rate = fatality_rate
        self.vaccinated_fatality_rate = vaccinated_fatality_rate
        self.infection_rate = infection_rate
        self.reinfection_rate = reinfection_rate
        self.vaccinated_infection_rate = vaccinated_infection_rate
        self.duration = duration
        self.cure_chance = cure_chance
        self.immunity_period = immunity_period
        self.infectiousness_factor = infectiousness_factor
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
            "cure_chance": self.cure_chance,
            "immunity_period": self.immunity_period,
            "infectiousness_factor": self.infectiousness_factor,
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
            cure_chance=data["cure_chance"],
            immunity_period=data["immunity_period"],
            infectiousness_factor=data["infectiousness_factor"],
        )
        instance.id = data["id"]
        if int(instance.id) >= Disease.id_counter:
            Disease.id_counter = int(instance.id) + 1
        return instance

    def get_properties_dict(self):
        original_dict = self.to_dict()
        del original_dict["id"]
        return {key.replace("_", " "): value for key, value in original_dict.items()}

    def get_values_from_dict(value_dict: dict):
        name = str(value_dict.get("name"))
        color = str(value_dict.get("color"))
        fatality_rate = float(value_dict.get("fatality rate"))
        vaccinated_fatality_rate = float(value_dict.get("vaccinated fatality rate"))
        infection_rate = float(value_dict.get("infection rate"))
        reinfection_rate = float(value_dict.get("reinfection rate"))
        vaccinated_infection_rate = float(value_dict.get("vaccinated infection rate"))
        duration = int(value_dict.get("duration"))
        initial_infection_count = int(value_dict.get("initial infection count"))
        cure_chance = float(value_dict.get("cure chance"))
        immunity_period = int(value_dict.get("immunity period"))
        infectiousness_factor = float(value_dict.get("infectiousness factor"))

        return (
            name,
            color,
            fatality_rate,
            vaccinated_fatality_rate,
            infection_rate,
            reinfection_rate,
            vaccinated_infection_rate,
            duration,
            initial_infection_count,
            cure_chance,
            immunity_period,
            infectiousness_factor,
        )

    def set_from_dict(self, value_dict: dict):
        (
            name,
            color,
            fatality_rate,
            vaccinated_fatality_rate,
            infection_rate,
            reinfection_rate,
            vaccinated_infection_rate,
            duration,
            initial_infection_count,
            cure_chance,
            immunity_period,
            infectiousness_factor,
        ) = Disease.get_values_from_dict(value_dict)
        self.name = name
        self.color = color
        self.fatality_rate = fatality_rate
        self.vaccinated_fatality_rate = vaccinated_fatality_rate
        self.infection_rate = infection_rate
        self.reinfection_rate = reinfection_rate
        self.vaccinated_infection_rate = vaccinated_infection_rate
        self.duration = duration
        self.initial_infection_count = initial_infection_count
        self.cure_chance = cure_chance
        self.immunity_period = immunity_period
        self.infectiousness_factor = infectiousness_factor

    def init_from_dict(value_dict):
        (
            name,
            color,
            fatality_rate,
            vaccinated_fatality_rate,
            infection_rate,
            reinfection_rate,
            vaccinated_infection_rate,
            duration,
            initial_infection_count,
            cure_chance,
            immunity_period,
            infectiousness_factor,
        ) = Disease.get_values_from_dict(value_dict)
        return Disease(
            name=name,
            color=color,
            fatality_rate=fatality_rate,
            vaccinated_fatality_rate=vaccinated_fatality_rate,
            infection_rate=infection_rate,
            reinfection_rate=reinfection_rate,
            vaccinated_infection_rate=vaccinated_infection_rate,
            duration=duration,
            initial_infection_count=initial_infection_count,
            cure_chance=cure_chance,
            immunity_period=immunity_period,
            infectiousness_factor=infectiousness_factor,
        )
