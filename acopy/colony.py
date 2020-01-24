from .ant import Ant
from .evilant import EvilAnt
from .randomant import RandomAnt
from .sensitiveant import SensitiveAnt
from .localant import LocalAnt


class Colony:
    """Colony of ants.

    Effectively this is a source of :class:`~acopy.ant.Ant` for a
    :class:`~acopy.solvers.Solver`.

    :param float alpha: relative factor for edge pheromone
    :param float beta: relative factor for edge weight
    """

    def __init__(self, alpha=1, beta=3, evil=0.0, random=0.0, sensitive=0.0, local=0.0, q_0=0.2, tau_0=0.01, rho=0.03):
        self.alpha = alpha
        self.beta = beta
        self.evil = evil
        self.random = random
        self.sensitive = sensitive
        self.local = local
        self.q_0 = q_0
        self.tau_0 = tau_0
        self.rho = rho

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
        num_of_random = int(count * self.random)
        num_of_sensitive = int(count * self.sensitive)
        num_of_local = int(count * self.local)
        num_of_virtue = count - num_of_evil
        for __ in range(num_of_evil):
            ants.append(EvilAnt(alpha=self.alpha, beta=self.beta))
        for __ in range(num_of_random):
            ants.append(RandomAnt(alpha=self.alpha, beta=self.beta, q_0=self.q_0))
        for __ in range(num_of_sensitive):
            ants.append(SensitiveAnt(alpha=self.alpha, beta=self.beta, q_0=self.q_0))
        for __ in range(num_of_local):
            ants.append(LocalAnt(alpha=self.alpha, beta=self.beta, tau_0=self.tau_0, rho=self.rho))
        for __ in range(num_of_virtue):
            ants.append(Ant(alpha=self.alpha, beta=self.beta))
        return ants
