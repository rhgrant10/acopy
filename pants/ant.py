import itertools
import bisect
import random

from .solvers import Solution


class Ant:
    def __init__(self, alpha=1, beta=3):
        self.alpha = alpha
        self.beta = beta

    def __repr__(self):
        return f'Ant(alpha={self.alpha}, beta={self.beta})'

    def tour(self, graph):
        solution = self.start_new_solution(graph)
        while True:
            moves = self.get_moves(graph, solution)
            if not moves:
                break
            elif len(moves) > 1:
                node = self.choose_move(graph, solution.current, moves)
            else:
                node = moves[0]
            solution.add_node(node)
        solution.close()
        return solution

    def start_new_solution(self, graph):
        start = self.get_starting_node(graph)
        return Solution(graph, start, ant=self)

    def get_starting_node(self, graph):
        return random.choice(list(graph.nodes))

    def get_moves(self, graph, solution):
        moves = []
        for node in graph[solution.current]:
            if node not in solution:
                moves.append(node)
        return moves

    def choose_move(self, graph, current, moves):
        scores = self.score_moves(graph, current, moves)
        return self.choose_scored_move(moves, scores)

    def score_moves(self, graph, current, moves):
        scores = []
        for node in moves:
            data = graph.edges[current, node]
            score = self.score_move(data)
            scores.append(score)
        return scores

    def choose_scored_move(self, moves, scores):
        total = sum(scores)
        cumdist = list(itertools.accumulate(scores)) + [total]
        index = bisect.bisect(cumdist, random.random() * total)
        return moves[min(index, len(moves) - 1)]

    def score_move(self, data):
        pre = 1 / data.get('weight', 1)
        post = data['pheromone']
        return post ** self.alpha * pre ** self.beta


class Colony:
    def __init__(self, alpha=1, beta=3):
        self.alpha = alpha
        self.beta = beta

    def __repr__(self):
        return (f'{self.__class__.__name__}(alpha={self.alpha}, '
                f'beta={self.beta})')

    def get_ants(self, count):
        return [Ant(**vars(self)) for __ in range(count)]
