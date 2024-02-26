
from src.epidemics_simulator.storage import Network, NodeGroup, Disease
group_size: int = 5000
group_age: int = 20
group_vac_rate: float = 0.0
group_max_vac_rate: float = 0.0


oscillating = Network()
oscillating.name = "Oscillating disease"
g1 = NodeGroup(oscillating, "Group 1", 2000, group_age, 0, 0, 5, 0, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(oscillating, "Group 2", 2000, group_age, 0, 0, 5, 0, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(oscillating, "Group 3", 2000, group_age, 0, 0, 5, 0, "rgb(0.439, 0.999, 0.878)")
g4 = NodeGroup(oscillating, "Group 4", 2000, group_age, 0, 0, 5, 0, "rgb(0.008, 0.424, 0.647)")
g5 = NodeGroup(oscillating, "Group 5", 2000, group_age, 0, 0, 5, 0, "rgb(0.847, 0.153, 0.659)")
oscillating.add_group(g1)
oscillating.add_group(g2)
oscillating.add_group(g3)
oscillating.add_group(g4)
oscillating.add_group(g5)

g1.add_external_connection(g2.id, 1, 0)

g2.add_external_connection(g3.id, 1, 0)

g3.add_external_connection(g4.id, 1, 0)

g4.add_external_connection(g5.id, 1, 0)

g5.add_external_connection(g1.id, 1, 0)

d1 = Disease("Disease 1", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.0, vaccinated_fatality_rate=0.0, infection_rate=0.3, reinfection_rate=0.3, vaccinated_infection_rate=0.3, duration=5, cure_chance=1.0, immunity_period=3, infectiousness_factor=1.0, initial_infection_count=2)
oscillating.add_disease(d1)



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


corona = Network()
corona.name = "Corona"
g1 = NodeGroup(corona, "Students", 3000, 16, 0.012, 0.2, 5, 2, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(corona, "Worker", 6000, 45, 0.007, 0.15, 3, 1, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(corona, "Retirees", 1000, 80, 0.005, 0.1, 2, 2, "rgb(0.439, 0.999, 0.878)")
corona.add_group(g1)
corona.add_group(g2)
corona.add_group(g3)
g1.add_external_connection(g2.id, 3, 2)
g1.add_external_connection(g3.id, 1, 1)
g2.add_external_connection(g3.id, 1, 1)
d1 = Disease("Corona", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.024, vaccinated_fatality_rate=0.01, infection_rate=0.081, reinfection_rate=0.027, vaccinated_infection_rate=0.0272, duration=7, cure_chance=0.4, immunity_period=128, infectiousness_factor=0.8, initial_infection_count=50)
corona.add_disease(d1)



influenza = Network()
influenza.name = "Influenza"
g1 = NodeGroup(influenza, "Students", 3000, 16, 0.02, 0.32, 5, 2, "rgb(0.992, 0.106, 0.416)")
g2 = NodeGroup(influenza, "Worker", 6000, 45, 0.03, 0.45, 3, 1, "rgb(0.999, 0.761, 0.906)")
g3 = NodeGroup(influenza, "Retirees", 1000, 80, 0.04, 0.7, 2, 2, "rgb(0.439, 0.999, 0.878)")
influenza.add_group(g1)
influenza.add_group(g2)
influenza.add_group(g3)
g1.add_external_connection(g2.id, 3, 2)
g1.add_external_connection(g3.id, 1, 1)
g2.add_external_connection(g3.id, 1, 1)
d1 = Disease("Influenza", color="rgb(0.996, 0.000, 0.016)", fatality_rate=0.006, vaccinated_fatality_rate=0.0005, infection_rate=0.09, reinfection_rate=0.02, vaccinated_infection_rate=0.04, duration=5, cure_chance=0.5, immunity_period=128, infectiousness_factor=0.7, initial_infection_count=50)
influenza.add_disease(d1)


templates = [oscillating, r0s1, r0g1, r0_die, r0_surv, mul, small, corona, influenza]