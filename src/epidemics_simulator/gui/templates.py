
from src.epidemics_simulator.storage import Network, NodeGroup, Disease
# TODO
r0 = Network()
r0.name = "r0 < 1 experiment"

r01 = Network()
r01.name = "r0 > 1 experiment"

r0_half = Network()
r0_half.name = "r0 network changed"

mul = Network()
mul.name = "Multiple Diseases"

small = Network()
small.name = "Small-World Phenomenon"




templates = [r0, r01, r0_half, mul, small]