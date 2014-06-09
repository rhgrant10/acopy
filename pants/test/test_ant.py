from ..ant import Ant
from ..world import World, Edge, Node
import unittest
import unittest.mock

class AntTest(unittest.TestCase):

    @unittest.mock.patch('__main__.World')
    def test_ant_uid_increases_by_one(self, MockWorld):
        # Arrange
        n = 10
        w = World()
        
        # Act
        uids = [Ant(w).uid for _ in range(n)]
        
        # Assert
        for i in range(n - 1):
            self.assertTrue(uids[i] + 1 == uids[i + 1])
    
    # TODO: Mock Node, Edge, and World
    def test_ant_no_distance_on_first_move_without_start(self):
        # Arrange
        a = Node(name='a')
        b = Node(name='b')
        w = World()
        e = Edge(a, b)
        
        w.add_edge(e)
        ant = Ant(w)
        
        # Act
        # This calls:
        #   ant.get_possible_moves
        #   ant.choose_move
        #   ant.make_move        
        ant.move()
        
        # Assert
        self.assertEqual(ant.distance, 0)
        
    # TODO: Mock Node, Edge, and World
    def test_ant_chooses_correct_possible_moves(self):
        # Arrange
        a = Node(name='a')
        b = Node(name='b')
        w = World()
        e = Edge(a, b)
        w.add_edge(e)
        ant = Ant(w)

        moves = ant.get_possible_moves()        
        nodes = w.nodes
        
        # Assert
        self.assertTrue(all(n in moves for n in nodes))
        

if __name__ == '__main__':
    unittest.main()