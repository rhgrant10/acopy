from .ant import Ant
from .evilant import EvilAnt


class Colony:
    """Colony of ants.

    Effectively this is a source of :class:`~acopy.ant.Ant` for a
    :class:`~acopy.solvers.Solver`.

    :param float alpha: relative factor for edge pheromone
    :param float beta: relative factor for edge weight
    """

    def __init__(self, alpha=1, beta=3, evil=0.0):
        self.alpha = alpha
        self.beta = beta
        self.evil = evil

    def __repr__(self):
        return (f'{self.__class__.__name__}(alpha={self.alpha}, '
                f'beta={self.beta})')

    def get_ants(self, count):
        """Return the requested number of :class:`~acopy.ant.Ant` s.

        :param int count: number of ants to return
        :rtype: list
        """
        ants = []
        num_of_evil = int(count * self.evil)
        num_of_virtue = count - num_of_evil
        for __ in range(num_of_evil):
            ants.append(EvilAnt(**vars(self)))
        for __ in range(num_of_virtue):
            ants.append(Ant(**vars(self)))
        return ants
