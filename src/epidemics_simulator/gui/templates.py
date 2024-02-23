
from src.epidemics_simulator.storage import Network, NodeGroup, Disease

group_size: int = 5000
group_age: int = 20
group_vac_rate: float = 0.0
group_max_vac_rate: float = 0.0
r0s1 = Network()
r0s1.name = "R0 < 1 Experiment"
g1 = NodeGroup(r0s1, "Group 1", group_size, group_age, group_vac_rate, group_max_vac_rate, 5, 0, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(r0s1, "Group 2", group_size, group_age, group_vac_rate, group_max_vac_rate, 4, 0, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(r0s1, "Group 3", group_size, group_age, group_vac_rate, group_max_vac_rate, 3, 0, "rgb(0.439, 0.999, 0.878)")
r0s1.add_group(g1)
r0s1.add_group(g2)
r0s1.add_group(g3)
g1.add_external_connection(g2.id, 2, 0)
g1.add_external_connection(g3.id, 2, 0)
g2.add_external_connection(g3.id, 2, 0)
d1 = Disease("Disease 1", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=0.024, reinfection_rate=0.024, vaccinated_infection_rate=0.024, duration=5, cure_chance=1.0, immunity_period=0, infectiousness_factor=1.0, initial_infection_count=5)
r0s1.add_disease(d1)

r0g1 = Network()
r0g1.name = "R0 > 1 Experiment"
g1 = NodeGroup(r0g1, "Group 1", group_size, group_age, group_vac_rate, group_max_vac_rate, 5, 0, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(r0g1, "Group 2", group_size, group_age, group_vac_rate, group_max_vac_rate, 4, 0, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(r0g1, "Group 3", group_size, group_age, group_vac_rate, group_max_vac_rate, 3, 0, "rgb(0.439, 0.999, 0.878)")
r0g1.add_group(g1)
r0g1.add_group(g2)
r0g1.add_group(g3)
g1.add_external_connection(g2.id, 2, 0)
g1.add_external_connection(g3.id, 2, 0)
g2.add_external_connection(g3.id, 2, 0)
d1 = Disease("Disease 1", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=0.036, reinfection_rate=0.036, vaccinated_infection_rate=0.036, duration=5, cure_chance=1.0, immunity_period=0, infectiousness_factor=1.0, initial_infection_count=150)
r0g1.add_disease(d1)

r0_die = Network()
r0_die.name = "R0 Network Changed: Dieing"
g1 = NodeGroup(r0_die, "Group 1", int(group_size/2), group_age, group_vac_rate, group_max_vac_rate, 2, 0, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(r0_die, "Group 2", int(group_size/2), group_age, group_vac_rate, group_max_vac_rate, 2, 0, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(r0_die, "Group 3", int(group_size/2), group_age, group_vac_rate, group_max_vac_rate, 2, 0, "rgb(0.439, 0.999, 0.878)")

r0_die.add_group(g1)
r0_die.add_group(g2)
r0_die.add_group(g3)
g1.add_external_connection(g2.id, 1, 0)
g1.add_external_connection(g3.id, 1, 0)
g2.add_external_connection(g3.id, 1, 0)

g1_1 = NodeGroup(r0_die, "Group 1", group_size, group_age, group_vac_rate, group_max_vac_rate, 8, 0, "rgb(0.992, 0.106, 0.416)")
g1_2 = NodeGroup(r0_die, "Group 2", group_size, group_age, group_vac_rate, group_max_vac_rate, 1, 0, "rgb(0.999, 0.761, 0.906)")
g1_2 = NodeGroup(r0_die, "Group 3", group_size, group_age, group_vac_rate, group_max_vac_rate, 1, 0, "rgb(0.439, 0.999, 0.878)")



d1 = Disease("Disease 1", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=0.036, reinfection_rate=0.036, vaccinated_infection_rate=0.036, duration=5, cure_chance=1.0, immunity_period=0, infectiousness_factor=1.0, initial_infection_count=150)
r0_die.add_disease(d1)

r0_surv = Network()
r0_surv.name = "R0 Network Changed: Surviving"
g1 = NodeGroup(r0_surv, "Group 1", group_size, group_age, group_vac_rate, group_max_vac_rate, 8, 0, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(r0_surv, "Group 2", group_size, group_age, group_vac_rate, group_max_vac_rate, 1, 0, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(r0_surv, "Group 3", group_size, group_age, group_vac_rate, group_max_vac_rate, 1, 0, "rgb(0.439, 0.999, 0.878)")
r0_surv.add_group(g1)
r0_surv.add_group(g2)
r0_surv.add_group(g3)
g1.add_external_connection(g2.id, 1, 0)
g1.add_external_connection(g3.id, 1, 0)
g2.add_external_connection(g3.id, 1, 0)
d1 = Disease("Disease 1", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=0.036, reinfection_rate=0.036, vaccinated_infection_rate=0.036, duration=5, cure_chance=1.0, immunity_period=0, infectiousness_factor=1.0, initial_infection_count=150)
r0_surv.add_disease(d1)

mul = Network()
mul.name = "Multiple Diseases"
g1 = NodeGroup(mul, "Group 1", group_size, group_age, group_vac_rate, group_max_vac_rate, 5, 0, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(mul, "Group 2", group_size, group_age, group_vac_rate, group_max_vac_rate, 4, 0, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(mul, "Group 3", group_size, group_age, group_vac_rate, group_max_vac_rate, 3, 0, "rgb(0.439, 0.999, 0.878)")
mul.add_group(g1)
mul.add_group(g2)
mul.add_group(g3)
g1.add_external_connection(g2.id, 2, 0)
g1.add_external_connection(g3.id, 2, 0)
g2.add_external_connection(g3.id, 2, 0)
d1 = Disease("Disease 1", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=0.06, reinfection_rate=0.06, vaccinated_infection_rate=0.06, duration=5, cure_chance=1.0, immunity_period=0, infectiousness_factor=1.0, initial_infection_count=50)
d2 = Disease("Disease 2", color="rgb(0.118, 0.000, 0.999)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=0.04, reinfection_rate=0.04, vaccinated_infection_rate=0.04, duration=5, cure_chance=1.0, immunity_period=0, infectiousness_factor=1.0, initial_infection_count=50)
mul.add_disease(d1)
mul.add_disease(d2)

small = Network()
small.name = "Small-World Phenomenon"
g1 = NodeGroup(small, "Group 1", 10000, group_age, group_vac_rate, group_max_vac_rate, 6, 0, "rgb(0.992, 0.106, 0.416)")
small.add_group(g1)
d1 = Disease("Disease 1", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=1.0, reinfection_rate=0.0, vaccinated_infection_rate=0.0, duration=1000, cure_chance=0.0, immunity_period=0, infectiousness_factor=1.0, initial_infection_count=1)
small.add_disease(d1)


corona = Network() # TODO
corona.name = "Corona"
g1 = NodeGroup(corona, "Group 1", group_size, group_age, group_vac_rate, group_max_vac_rate, 5, 0, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(corona, "Group 2", group_size, group_age, group_vac_rate, group_max_vac_rate, 4, 0, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(corona, "Group 3", group_size, group_age, group_vac_rate, group_max_vac_rate, 3, 0, "rgb(0.439, 0.999, 0.878)")
corona.add_group(g1)
corona.add_group(g2)
corona.add_group(g3)
g1.add_external_connection(g2.id, 2, 0)
g1.add_external_connection(g3.id, 2, 0)
g2.add_external_connection(g3.id, 2, 0)
d1 = Disease("Corona", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=0.024, reinfection_rate=0.024, vaccinated_infection_rate=0.024, duration=5, cure_chance=1.0, immunity_period=0, infectiousness_factor=1.0, initial_infection_count=5)
corona.add_disease(d1)



influenza = Network() # TODO
influenza.name = "Influenza"
g1 = NodeGroup(influenza, "Group 1", group_size, group_age, group_vac_rate, group_max_vac_rate, 5, 0, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(influenza, "Group 2", group_size, group_age, group_vac_rate, group_max_vac_rate, 4, 0, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(influenza, "Group 3", group_size, group_age, group_vac_rate, group_max_vac_rate, 3, 0, "rgb(0.439, 0.999, 0.878)")
influenza.add_group(g1)
influenza.add_group(g2)
influenza.add_group(g3)
g1.add_external_connection(g2.id, 2, 0)
g1.add_external_connection(g3.id, 2, 0)
g2.add_external_connection(g3.id, 2, 0)
d1 = Disease("Influenza", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=0.024, reinfection_rate=0.024, vaccinated_infection_rate=0.024, duration=5, cure_chance=1.0, immunity_period=0, infectiousness_factor=1.0, initial_infection_count=5)
influenza.add_disease(d1)


templates = [r0s1, r0g1, r0_die, r0_surv, mul, small, corona, influenza]