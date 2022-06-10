import unittest
import main as m
from player import Player


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.player = Player()
        self.game = m.Game(self.player)
        self.game.start_game()
        self.game.place_tile(16, 16)
        self.game.set_current_zombies(5)
        self.game.set_state("Attacking")

    def tearDown(self):
        del self.game
        del self.player

    # def test_machete(self):
    #     self.player.add_item("Machete", 1)
    #     self.game.trigger_attack(self.player.get_items())
    #     expected_health = 4
    #
    #     actual_health = self.player.get_health()
    #
    #     assert expected_health == actual_health

    # def test_grisly_femur(self):
    #     self.player.add_item("Grisly Femur", 1)
    #     self.game.trigger_attack(self.player.get_items())
    #     expected_health = 4
    #
    #     actual_health = self.player.get_health()
    #
    #     assert expected_health == actual_health

    # def test_golf_club(self):
    #     self.player.add_item("Golf Club", 1)
    #     self.game.trigger_attack(self.player.get_items())
    #     expected_health = 4
    #
    #     actual_health = self.player.get_health()
    #
    #     assert expected_health == actual_health

    def test_oil_and_candle(self):
        self.player.add_item("Oil", 1)
        self.player.add_item("Candle", 1)
        self.game.trigger_attack(self.player.get_items())
        expected_health = 4

        actual_health = self.player.get_health()

        assert expected_health == actual_health

    # def test_candle_and_gasoline(self):
    #     self.player.add_item("Machete", 1)
    #     self.game.trigger_attack(self.player.get_items())
    #     expected_health = 4
    #
    #     actual_health = self.player.get_health()
    #
    #     assert expected_health == actual_health

    # def test_chainsaw(self):
    #     self.player.add_item("Machete", 1)
    #     self.game.trigger_attack(self.player.get_items())
    #     expected_health = 4
    #
    #     actual_health = self.player.get_health()
    #
    #     assert expected_health == actual_health

    # def test_no_item(self):
    #     self.game.trigger_attack()
    #     expected_health = 2
    #
    #     actual_health = self.player.get_health()
    #
    #     assert expected_health == actual_health


if __name__ == '__main__':
    unittest.main()
