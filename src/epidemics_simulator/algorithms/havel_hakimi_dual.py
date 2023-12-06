import random
from typing import List
from numpy.random import multinomial
import numpy as np


class HavelHakimiDual:
    def __init__(self, size1: int, size2: int, min_deg: int, max_deg: int) -> None:
        self.size1 = size1
        self.size2 = size2
        self.min_deg = min_deg
        self.max_deg = max_deg
        self.deg_seq1 = []
        self.deg_seq2 = []
        self.node_id_seq1 = []
        self.node_id_seq2 = []
        self.edges = {}

    # resulting edges have node ids of smaller group as keys and values of node ids in bigger group they connect to as values
    # if both groups have the same size ids of group1 are the keys
    def run(self):
        self.edges = {}
        self._create_sequence()
        self._sort_sequence()
        print(self.deg_seq1)
        print(self.deg_seq2)
        self.node_id_seq1 = list(range(0, self.size1))
        self.node_id_seq2 = list(range(0, self.size2))
        random.shuffle(self.node_id_seq1)
        random.shuffle(self.node_id_seq2)
        if not self._erdos_gallai():
            raise ArithmeticError
        while sum(self.deg_seq1) + sum(self.deg_seq2) != 0:
            self._connect_highest_deg_node()
        return self.edges

    # https://en.wikipedia.org/wiki/Erd%C5%91s%E2%80%93Gallai_theorem
    # This should always return true, as the second degree sequence is constructed so the resulting sequences are always graphic
    def _erdos_gallai(self) -> bool:
        for n, seq in zip([self.size1, self.size2], [self.deg_seq2, self.deg_seq1]):
            for k in range(1, n + 1):
                if sum(seq[:k]) > k * (k - 1) + sum([x if x >= k else k for x in seq[k + 1 :]]):
                    return False
        return True

    # always connect from smaller group
    def _connect_highest_deg_node(self):
        if self.size1 <= self.size2:
            node = self.node_id_seq1[0]
            deg = self.deg_seq1[0]
            self.node_id_seq1.pop(0)
            self.deg_seq1.pop(0)
            targets = self._get_highest_n_nodes(deg, self.deg_seq2, self.node_id_seq2)
            for target in targets:
                self.deg_seq2[self.node_id_seq2.index(target)] -= 1
        else:
            node = self.node_id_seq2[0]
            deg = self.deg_seq2[0]
            self.node_id_seq2.pop(0)
            self.deg_seq2.pop(0)
            targets = self._get_highest_n_nodes(deg, self.deg_seq1, self.node_id_seq1)
            for target in targets:
                self.deg_seq1[self.node_id_seq1.index(target)] -= 1
        self.edges[node] = targets
        self._sort_sequence()

    def _create_sequence(self):
        seq = []
        for _ in range(0, min(self.size1, self.size2)):
            seq.append(random.randint(self.min_deg, self.max_deg))
        if self.size1 < self.size2:
            self.deg_seq1 = seq
            self.deg_seq2 = self._create_sequence_with_sum(self.size2, sum(seq))
        else:
            self.deg_seq2 = seq
            self.deg_seq1 = self._create_sequence_with_sum(self.size1, sum(seq))

    def _create_sequence_with_sum(self, size: int, _sum: int):
        seq: List[int] = np.random.randint(self.min_deg, self.max_deg + 1, size=(size)).tolist()
        while sum(seq) != _sum:
            if sum(seq) > _sum:
                # > 0 instead of > min_deg if all nodes have min_deg
                # because the bigger group will have some nodes with less than min_deg connections
                choices = [x for x in seq if x > self.min_deg]
                if len(choices) == 0:
                    choices = [x for x in seq if x > 0]
                seq[seq.index(random.choice(choices))] -= 1
            else:
                seq[seq.index(random.choice([x for x in seq if x < self.max_deg]))] += 1
        return seq

    def _sort_sequence(self):
        self.node_id_seq1 = [
            x for _, x in sorted(zip(self.deg_seq1, self.node_id_seq1), reverse=True)
        ]
        self.deg_seq1.sort(reverse=True)
        self.node_id_seq2 = [
            x for _, x in sorted(zip(self.deg_seq2, self.node_id_seq2), reverse=True)
        ]
        self.deg_seq2.sort(reverse=True)

    def _get_highest_n_nodes(self, n: int, deg_seq: List[int], node_id_seq: List[int]) -> List[int]:
        if n >= len(deg_seq):
            raise ArithmeticError
        max = deg_seq[0]
        cur = max
        viable_nodes = []
        selected_nodes = []
        i = 0
        while i < n:
            # add all viable nodes, if next viable nodes have lower deg
            selected_nodes.extend(viable_nodes)
            viable_nodes.clear()
            while cur == max:
                viable_nodes.append(node_id_seq[i])
                i += 1
                try:
                    cur = deg_seq[i]
                except IndexError:
                    cur = -1
            if cur == -1:
                break
            max = deg_seq[i]
            cur = max
        selected_nodes.extend(random.sample(viable_nodes, n - len(selected_nodes)))
        return selected_nodes


if __name__ == "__main__":
    h = HavelHakimiDual(9, 4, 2, 2)
    h2 = HavelHakimiDual(100, 51, 11, 20)
    h2.run()
    print(h2.edges)
    total = 0
    for x in h2.edges.values():
        total += len(x)
    print(total)
    print(51 * 15.5)
    # print(h2.create_sequence_with_sum(100, 750))
    # h.run()
    # ids = h.get_highest_n_nodes(20)
    # x = []
    # for id in ids:
    #     y = h.node_id_seq.index(id)
    #     x.append(h.deg_seq[y])
    # print(h.deg_seq)
    h.deg_seq1 = [5, 5, 4, 4, 3, 2, 1, 1, 1]
    h.deg_seq2 = [9, 6, 5, 4, 2, 0, 0, 0, 0]
    # total = 0
    # for conns in h.edges.values():
    #     if len(conns) > 20:
    #         print("ERROR2")
    #     total += 2 * len(conns)
