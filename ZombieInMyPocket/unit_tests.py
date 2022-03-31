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

    def placeFoyer(self):
        self.game.place_tile(16, 16)

    def test_game_starts_with_foyer(self):
        tile = self.game.get_chosen_tile()

        assert tile.get_name() == "Foyer"

    def test_foyer_starts_at_right_coords(self):
        tile = self.game.get_chosen_tile()

        coordinates = (tile.get_x(), tile.get_y())

        assert coordinates == (16, 16)

    def test_starting_state(self):  # game should start rotating the foyer
        state = self.game.get_state()

        assert state == "Rotating"

    def test_game_has_player(self):
        player = self.game.get_player()

        assert player is not None

    def test_player_starting_position(self):
        expected = (16, 16)

        actual = self.game.get_player().get_x(), self.game.get_player().get_y()

        assert expected == actual

    def test_player_starting_items(self):  # Should start with no items
        expected = []

        actual = self.game.get_player().get_items()

        assert expected == actual

    def test_player_starting_health(self):  # Should start with no items
        expected = 6

        actual = self.game.get_player().get_health()

        assert expected == actual

    def test_player_starting_attack(self):  # Should start with no items
        expected = 1

        actual = self.game.get_player().get_attack()

        assert expected == actual

    def test_cant_find_totem_if_not_in_evil_temple(self):
        expected = False

        self.game.place_tile(16, 16)
        self.game.search_for_totem()
        actual = self.game.get_player().get_has_totem()

        assert expected == actual

    def test_cant_bury_totem_if_not_in_evil_temple(self):
        expected = True

        self.game.place_tile(16, 16)
        self.game.get_player().set_has_totem(True)
        self.game.bury_totem()
        actual = self.game.get_player().get_has_totem()

        assert expected == actual

    def test_tile_can_rotate(self):
        tile = self.game.get_chosen_tile()

        tile.rotate_tile()

        assert tile.get_doors()[0] == d.NORTH

    def test_db_connection(self):
        expected = True

        actual = self.game.connect_db()

        assert expected == actual

    def test_db_table_exists(self):
        expected = False

        self.game.connect_db()
        actual = self.game.check_table_exists()

        assert expected == actual

    def test_delete_data(self):
        expected = []

        self.game.delete_data()
        actual = self.game.get_data()

        assert expected == actual

    def test_db_data_input(self):
        expected = (5, 10, 1)

        self.game.delete_data()
        self.game.place_tile(16, 16)
        self.game.get_player().add_zombies_killed(5)
        self.game.get_player().add_health_lost(10)
        self.game.get_player().add_move_count()
        self.game.input_data()
        actual = self.game.get_data()

        assert expected == actual[0]

    def test_extract_data(self):
        expected = True

        if exists(r'additional_files\player_stats.xlsx'):
            os.remove(r'additional_files\player_stats.xlsx')
        self.game.extract_data('player_stats')
        actual = exists(r'additional_files\player_stats.xlsx')

        assert expected == actual

    def test_player_cant_cower_when_not_moving(self):
        expected = self.game.get_player().get_health()

        self.game.trigger_cower()
        actual = self.game.get_player().get_health()

        assert expected == actual

    def test_resolving_door_to_input(self):
        expected = [d.NORTH, d.WEST]

        actual = self.game.resolve_doors(1, 0, 0, 1)

        assert expected == actual

    def test_player_cant_attack_when_in_wrong_state(self):
        expected = False

        actual = self.game.trigger_attack()

        assert expected == actual

    def test_placing_tile(self):
        result = False
        self.placeFoyer()

        if (16, 16) in self.game.get_tiles():
            result = True

        assert result is True

    def test_placing_tile_changes_state_to_moving(self):
        self.placeFoyer()

        state = self.game.get_state()

        assert state == "Moving"

    def test_player_starts_in_foyer(self):
        self.placeFoyer()

        player_position = (self.player.get_x(), self.player.get_y())

        assert player_position == (16, 16)

    def test_drawing_new_tile(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        new_tile = self.game.get_chosen_tile()

        assert new_tile.get_name() != "Foyer"

    def test_drawing_tile_state_is_rotating(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        state = self.game.get_state()

        assert state == "Rotating"

    def test_placing_tile_when_doors_align(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.get_chosen_tile()
        tile.get_doors().clear()
        tile.get_doors().append(d.EAST)
        result = self.game.check_doors_align(d.WEST)

        assert result is True

    def test_cant_place_tile_when_doors_dont_align(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.get_chosen_tile()
        tile.get_doors().clear()
        tile.get_doors().append(d.NORTH)
        result = self.game.check_doors_align(d.WEST)

        assert result is False

    def test_moving_player_changes_coordinates(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.get_chosen_tile()
        tile.get_doors().clear()
        tile.get_doors().append(d.EAST)
        x, y = self.game.get_destination_coords(d.WEST)
        self.game.move_player(x, y)
        player_x, player_y = self.player.get_x(), self.player.get_y()

        assert player_x, player_y == (15, 16)

    def test_moving_player_changes_state_to_drawing(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.get_chosen_tile()
        tile.get_doors().clear()
        tile.get_doors().append(d.EAST)
        x, y = self.game.get_destination_coords(d.WEST)
        self.game.place_tile(x, y)
        self.game.move_player(x, y)
        state = self.game.get_state()

        assert state == "Drawing Dev Card"

    def test_player_can_move_to_a_discovered_room(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.get_chosen_tile()
        tile.get_doors().clear()
        tile.get_doors().append(d.EAST)
        x, y = self.game.get_destination_coords(d.WEST)
        self.game.move_player(x, y)
        self.game.set_state("Moving")
        x, y = self.game.get_destination_coords(d.EAST)
        self.game.move_player(x, y)
        tile = self.game.get_current_tile()

        assert tile.get_name() == "Foyer"

    def test_game_can_hold_multiple_tiles(self):
        self.placeFoyer()
        result = False

        self.game.select_move(d.WEST)
        tile = self.game.get_chosen_tile()
        tile.get_doors().clear()
        tile.get_doors().append(d.EAST)
        x, y = self.game.get_destination_coords(d.WEST)
        self.game.place_tile(x, y)
        if (16, 16) and (15, 16) in self.game.get_tiles():
            result = True

        assert result is True


if __name__ == '__main__':
    unittest.main()
