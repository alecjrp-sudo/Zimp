import unittest
import main as m
from player import Player
from directions import Direction as d
import os
from os.path import exists


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.player = Player()
        self.game = m.Game(self.player)
        self.game.start_game()
        self.game.place_tile(16, 16)
        self.game.__current_zombies = 10

    def test_something(self):
        zombies = self.__current_zombies


if __name__ == '__main__':
    unittest.main()
