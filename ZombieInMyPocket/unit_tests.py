import unittest
import main as m
import player as p
from directions import Direction as d


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.player = p.Player()
        self.game = m.Game(self.player)
        self.game.start_game()

    def tearDown(self):
        del self.game
        del self.player

    def placeFoyer(self):
        self.game.place_tile(16, 16)

    def test_game_starts_with_foyer(self):
        tile = self.game.chosen_tile

        assert tile.name == "Foyer"

    def test_foyer_starts_at_right_coords(self):
        tile = self.game.chosen_tile

        coordinates = (tile.x, tile.y)

        assert coordinates == (16, 16)

    def test_starting_state(self):  # game should start rotating the foyer
        state = self.game.state

        assert state == "Rotating"

    def test_tile_can_rotate(self):
        tile = self.game.chosen_tile

        tile.rotate_tile()

        assert tile.doors[0] == d.NORTH

    def test_placing_tile(self):
        result = False
        self.placeFoyer()

        if (16, 16) in self.game.tiles:
            result = True

        assert result is True

    def test_placing_tile_changes_state_to_moving(self):
        self.placeFoyer()

        state = self.game.state

        assert state == "Moving"

    def test_player_starts_in_foyer(self):
        self.placeFoyer()

        player_position = (self.player.get_x(), self.player.get_y())

        assert player_position == (16, 16)

    def test_drawing_new_tile(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        new_tile = self.game.chosen_tile

        assert new_tile.name != "Foyer"

    def test_drawing_tile_state_is_rotating(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        state = self.game.state

        assert state == "Rotating"

    def test_placing_tile_when_doors_align(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.chosen_tile
        tile.doors.clear()
        tile.doors.append(d.EAST)
        result = self.game.check_doors_align(d.WEST)

        assert result is True

    def test_cant_place_tile_when_doors_dont_align(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.chosen_tile
        tile.doors.clear()
        tile.doors.append(d.NORTH)
        result = self.game.check_doors_align(d.WEST)

        assert result is False

    def test_moving_player_changes_coordinates(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.chosen_tile
        tile.doors.clear()
        tile.doors.append(d.EAST)
        x, y = self.game.get_destination_coords(d.WEST)
        self.game.move_player(x, y)
        player_x, player_y = self.player.get_x(), self.player.get_y()

        assert player_x, player_y == (15, 16)

    def test_moving_player_changes_state_to_drawing(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.chosen_tile
        tile.doors.clear()
        tile.doors.append(d.EAST)
        x, y = self.game.get_destination_coords(d.WEST)
        self.game.place_tile(x, y)
        self.game.move_player(x, y)
        state = self.game.state

        assert state == "Drawing Dev Card"

    def test_player_can_move_to_a_discovered_room(self):
        self.placeFoyer()

        self.game.select_move(d.WEST)
        tile = self.game.chosen_tile
        tile.doors.clear()
        tile.doors.append(d.EAST)
        x, y = self.game.get_destination_coords(d.WEST)
        self.game.move_player(x, y)
        self.game.state = "Moving"
        x, y = self.game.get_destination_coords(d.EAST)
        self.game.move_player(x, y)
        tile = self.game.get_current_tile()

        assert tile.name == "Foyer"

    def test_game_can_hold_multiple_tiles(self):
        self.placeFoyer()
        result = False

        self.game.select_move(d.WEST)
        tile = self.game.chosen_tile
        tile.doors.clear()
        tile.doors.append(d.EAST)
        x, y = self.game.get_destination_coords(d.WEST)
        self.game.place_tile(x, y)
        if (16, 16) and (15, 16) in self.game.tiles:
            result = True

        assert result is True


if __name__ == '__main__':
    unittest.main()
