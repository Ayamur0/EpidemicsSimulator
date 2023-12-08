import random
from typing import List


class HavelHakimi:
    def __init__(self, size: int, min_deg: int, max_deg: int) -> None:
        self.size = size
        self.min_deg = min_deg
        self.max_deg = max_deg
        self.deg_seq = []
        self.node_id_seq = []
        self.edges = {}

    def run(self):
        self.edges = {}
        self._create_sequence()
        self._sort_sequence()
        self.node_id_seq = list(range(0, self.size))
        random.shuffle(self.node_id_seq)
        self._make_graphic()
        while sum(self.deg_seq) != 0:
            self._connect_highest_deg_node()
        return self.edges

    def _make_graphic(self):
        while not self._erdos_gallai():
            self.deg_seq[0] -= 1
            self._sort_sequence()

    # https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93Gallai_theorem
    def _erdos_gallai(self) -> bool:
        if sum(self.deg_seq) % 2 != 0:
            return False
        n = self.size
        for k in range(1, n + 1):
            if sum(self.deg_seq[:k]) > k * (k - 1) + sum(min(k, d) for d in self.deg_seq[k + 1 :]):
                return False
        return True

    def _connect_highest_deg_node(self):
        node = self.node_id_seq[0]
        deg = self.deg_seq[0]
        self.node_id_seq.pop(0)
        self.deg_seq.pop(0)
        targets = self._get_highest_n_nodes(deg)
        for target in targets:
            self.deg_seq[self.node_id_seq.index(target)] -= 1
        self.edges[node] = targets
        self._sort_sequence()

    def _create_sequence(self):
        seq = []
        for _ in range(0, self.size):
            seq.append(random.randint(self.min_deg, self.max_deg))
        self.deg_seq = seq

    def _sort_sequence(self):
        self.node_id_seq = [x for _, x in sorted(zip(self.deg_seq, self.node_id_seq), reverse=True)]
        self.deg_seq.sort(reverse=True)

    def _get_highest_n_nodes(self, n: int) -> List[int]:
        if n >= len(self.deg_seq):
            raise ArithmeticError
        max = self.deg_seq[0]
        cur = max
        viable_nodes = []
        selected_nodes = []
        i = 0
        while i < n:
            # add all viable nodes, if next viable nodes have lower deg
            selected_nodes.extend(viable_nodes)
            viable_nodes.clear()
            while cur == max:
                viable_nodes.append(self.node_id_seq[i])
                i += 1
                try:
                    cur = self.deg_seq[i]
                except IndexError:
                    cur = -1
            if cur == -1:
                break
            max = self.deg_seq[i]
            cur = max
        selected_nodes.extend(random.sample(viable_nodes, n - len(selected_nodes)))
        return selected_nodes
