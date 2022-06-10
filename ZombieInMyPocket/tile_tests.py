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

    def tearDown(self):
        del self.game
        del self.player

    def test_indoor_tiles_load(self):
        expected = 8
        t = self.game.get_indoor_tiles()

        actual = len(t)

        assert expected == actual

    def test_outdoor_tiles_load(self):
        expected = 8
        t = self.game.get_outdoor_tiles()

        actual = len(t)

        assert expected == actual

    def test_indoor_tile_name(self):
        expected = "Bathroom"

        actual = self.game.get_indoor_tiles()[0]
        name = actual.get_name()

        assert expected == name

    def test_outdoor_tile_name(self):
        expected = "Graveyard"

        actual = self.game.get_outdoor_tiles()[0]
        name = actual.get_name()

        assert expected == name

    def test_getting_tile_x(self):
        expected = 16

        actual = self.game.get_outdoor_tiles()[0].get_x()

        assert expected == actual

    def test_getting_tile_y(self):
        expected = 16

        actual = self.game.get_outdoor_tiles()[0].get_y()

        assert expected == actual

    def test_getting_tile_effect(self):
        expected = "Bury Totem"

        actual = self.game.get_outdoor_tiles()[0].get_effect()

        assert expected == actual

    def test_getting_outdoor_tile_type(self):
        expected = "Outdoor"

        actual = self.game.get_outdoor_tiles()[0].get_type()

        assert expected == actual

    def test_getting_indoor_tile_type(self):
        expected = "Indoor"

        actual = self.game.get_indoor_tiles()[0].get_type()

        assert expected == actual

    def test_getting_tile_doors(self):
        expected = [d.WEST]

        actual = self.game.get_indoor_tiles()[0].get_doors()

        assert expected == actual

    def test_getting_tile_entrance(self):
        expected = d.NORTH

        actual = self.game.get_indoor_tiles()[3].get_entrance()

        assert expected == actual

    def test_setting_tile_x(self):
        expected = 15

        self.game.get_outdoor_tiles()[0].set_x(15)
        actual = self.game.get_outdoor_tiles()[0].get_x()

        assert expected == actual

    def test_setting_tile_y(self):
        expected = 15

        self.game.get_outdoor_tiles()[0].set_y(15)
        actual = self.game.get_outdoor_tiles()[0].get_y()

        assert expected == actual

    def test_changing_tile_doors(self):
        expected = [d.NORTH]

        self.game.get_indoor_tiles()[0].change_door_position(0, d.NORTH)
        actual = self.game.get_indoor_tiles()[0].get_doors()

        assert expected == actual

    def test_rotating_tile_doors_north(self):
        expected = [d.NORTH]

        self.game.get_indoor_tiles()[0].rotate_tile()
        actual = self.game.get_indoor_tiles()[0].get_doors()

        assert expected == actual

    def test_rotating_tile_doors_east(self):
        expected = [d.EAST]

        self.game.get_indoor_tiles()[0].rotate_tile()
        self.game.get_indoor_tiles()[0].rotate_tile()
        actual = self.game.get_indoor_tiles()[0].get_doors()

        assert expected == actual

    def test_rotating_tile_doors_south(self):
        expected = [d.SOUTH]

        self.game.get_indoor_tiles()[0].rotate_tile()
        self.game.get_indoor_tiles()[0].rotate_tile()
        self.game.get_indoor_tiles()[0].rotate_tile()
        actual = self.game.get_indoor_tiles()[0].get_doors()

        assert expected == actual

    def test_rotating_tile_doors_west(self):
        expected = [d.WEST]

        self.game.get_indoor_tiles()[0].rotate_tile()
        self.game.get_indoor_tiles()[0].rotate_tile()
        self.game.get_indoor_tiles()[0].rotate_tile()
        self.game.get_indoor_tiles()[0].rotate_tile()
        actual = self.game.get_indoor_tiles()[0].get_doors()

        assert expected == actual

    def test_rotating_tile_entrance_east(self):
        expected = d.EAST

        self.game.get_indoor_tiles()[3].rotate_entrance()
        actual = self.game.get_indoor_tiles()[3].get_entrance()

        assert expected == actual

    def test_rotating_tile_entrance_south(self):
        expected = d.SOUTH

        self.game.get_indoor_tiles()[3].rotate_entrance()
        self.game.get_indoor_tiles()[3].rotate_entrance()
        actual = self.game.get_indoor_tiles()[3].get_entrance()

        assert expected == actual

    def test_rotating_tile_entrance_west(self):
        expected = d.WEST

        self.game.get_indoor_tiles()[3].rotate_entrance()
        self.game.get_indoor_tiles()[3].rotate_entrance()
        self.game.get_indoor_tiles()[3].rotate_entrance()
        actual = self.game.get_indoor_tiles()[3].get_entrance()

        assert expected == actual

    def test_rotating_tile_entrance_north(self):
        expected = d.NORTH

        self.game.get_indoor_tiles()[3].rotate_entrance()
        self.game.get_indoor_tiles()[3].rotate_entrance()
        self.game.get_indoor_tiles()[3].rotate_entrance()
        self.game.get_indoor_tiles()[3].rotate_entrance()
        actual = self.game.get_indoor_tiles()[3].get_entrance()

        assert expected == actual


if __name__ == '__main__':
    unittest.main()
