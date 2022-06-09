import os
import pickle
from directions import Direction as d
import cmd
import sys
from player import Player
from Game import Game


class Commands(cmd.Cmd):
    intro = 'Welcome, type help or ? to list the' \
            ' commands or start to start the game'

    game_path = os.getcwd()

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "> "
        self.player = Player()
        self.game = Game(self.player)

    def do_start(self, line):
        """Starts a new game"""
        os.chdir(self.game_path)
        if self.game.get_state() == "Starting":
            self.game.start_game()
            self.game.get_game()
        else:
            print("Game has already Started")

    def do_rotate(self, line):
        """Rotates the current map piece 1 rotation clockwise"""
        if self.game.get_state() == "Rotating":
            self.game.rotate()
            self.game.get_game()
        else:
            print("Tile not chosen to rotate")

    def do_place(self, line):
        """Places the current map tile"""
        if self.game.get_state() == "Rotating":
            if self.game.get_chosen_tile().get_name() == "Foyer":
                self.game.place_tile(16, 16)
            elif self.game.check_dining_room_has_exit() is False:
                return print("Dining room entrance must face an empty tile")
            else:
                if self.game.get_current_tile().get_name == "Dining Room" \
                        and self.game.get_current_move_direction() == \
                        self.game.get_current_tile().get_entrance():
                    if self.game.check_entrances_align():
                        self.game.place_tile(self.game.get_chosen_tile()
                                             .get_x(),
                                             self.game.get_chosen_tile().
                                             get_y())
                        self.game.move_player(self.game.get_chosen_tile()
                                              .get_x(),
                                              self.game.get_chosen_tile()
                                              .get_y())
                elif self.game.check_doors_align(
                        self.game.get_current_move_direction()):
                    self.game.place_tile(self.game.get_chosen_tile()
                                         .get_x(),
                                         self.game.get_chosen_tile()
                                         .get_y())
                    self.game.move_player(self.game.get_chosen_tile()
                                          .get_x(),
                                          self.game.get_chosen_tile()
                                          .get_y())
                else:
                    print(" Must have at least one door"
                          " facing the way you came from")
            self.game.get_game()
        else:
            print("Tile not chosen to place")

    def do_choose(self, direction):
        """When a zombie door attack is completed. Use this
         command to select an exit door with a valid direction"""
        valid_inputs = ["n", "e", "s", "w"]
        if direction not in valid_inputs:
            return print("Input a valid direction."
                         " (Check choose help for more information)")
        if direction == 'n':
            direction = d.NORTH
        if direction == "e":
            direction = d.EAST
        if direction == "s":
            direction = d.SOUTH
        if direction == "w":
            direction = d.WEST
        if self.game.get_state() == "Choosing Door":
            self.game.set_can_cower(False)
            self.game.choose_door(direction)
        else:
            print("Cannot choose a door right now")

    def do_n(self, line):
        """Moves the player North"""
        if self.game.get_state() == "Moving":
            self.game.select_move(d.NORTH)
            self.game.get_game()
        else:
            return print("Player not ready to move")

    def do_s(self, line):
        """Moves the player South"""
        if self.game.get_state() == "Moving":
            self.game.select_move(d.SOUTH)
            self.game.get_game()
        else:
            return print("Player not ready to move")

    def do_e(self, line):
        """Moves the player East"""
        if self.game.get_state() == "Moving":
            self.game.select_move(d.EAST)
            self.game.get_game()
        else:
            return print("Player not ready to move")

    def do_w(self, line):
        """Moves the player West"""
        if self.game.get_state() == "Moving":
            self.game.select_move(d.WEST)
            self.game.get_game()
        else:
            return print("Player not ready to move")

    def do_save(self, line):
        """Takes a filepath and saves the game to a file"""
        if not line:
            return print("Must enter a valid file name")
        else:
            if len(self.game.get_tiles()) == 0:
                return print("Cannot save game with empty map")
            try:
                file_name = line + '.pickle'
                with open(file_name, 'wb') as f:
                    pickle.dump(self.game, f)
            except OSError as o:
                print(f"Oh no an error {o}")

    def do_load(self, name):
        """Takes a filepath and loads the game from a file"""
        if not name:
            return print("Must enter a valid file name")
        else:
            file_name = name + '.pickle'
            try:
                with open(file_name, 'rb') as f:
                    self.game = pickle.load(f)
                    self.game.get_game()
            except (FileNotFoundError, OSError) as o:
                print(f"Oh no an error {o}")

    def do_restart(self, line):
        """Deletes your progress and ends the game"""
        del self.game
        del self.player
        self.player = Player()
        self.game = Game(self.player)

    def do_attack(self, line):
        """Player attacks the zombies"""
        arg1 = ''
        arg2 = 0
        if "," in line:
            arg1, arg2 = [item for item in line.split(", ")]
        else:
            arg1 = line

        if self.game.get_state() == "Attacking":
            if arg1 == '':
                self.game.trigger_attack()
            elif arg2 == 0:
                self.game.trigger_attack(arg1)
            elif arg1 != '' and arg2 != 0:
                self.game.trigger_attack(arg1, arg2)

            if len(self.game.get_chosen_tile().get_doors()) == 1 and \
                    self.game.get_chosen_tile().get_name() != "Foyer":
                self.game.set_state("Choosing Door")
                self.game.get_game()
            if self.game.get_state() == "Game Over":
                print("You lose, game over, you have"
                      " succumbed to the zombie horde")
                print("To play again, type 'restart'")
            else:
                self.game.get_game()
        else:
            print("You cannot attack right now")

    def do_use(self, line):
        """Player uses item"""
        arg1 = ''
        arg2 = 0
        if "," in line:
            arg1, arg2 = [item for item in line.split(", ")]
        else:
            arg1 = line

        if self.game.get_state() == "Moving":
            if arg1 == '':
                return
            if arg2 == 0:
                self.game.use_item(arg1)
            elif arg1 != '' and arg2 != 0:
                self.game.use_item(arg1, arg2)
        else:
            print("You cannot do that right now")

    # Not finished yet, needs testing for spelling
    def do_drop(self, item):
        """Drops an item from your hand"""
        if self.game.get_state() != "Game Over":
            self.game.drop_item(item)
            self.game.get_game()

    def do_swap(self, line):
        """Swaps an item in you hand with the one in the room"""
        if self.game.get_state() == "Swapping Item":
            self.game.drop_item(line)
            self.game.get_player().add_item(self.game.get_room_item(0),
                                            self.game.get_room_item(1))
            self.game.set_room_item(None)
            self.game.get_game()

    def do_draw(self, line):
        """Draws a new development card (Must be done after evey move)"""
        if self.game.get_state() == "Drawing Dev Card":
            self.game.trigger_dev_card(self.game.get_time())
        else:
            print("Cannot currently draw a card")

    def do_run(self, direction):
        """Given a direction will flee attacking
         zombies at a price of one health"""
        if self.game.get_state() == "Attacking":
            if direction == 'n':
                self.game.trigger_run(d.NORTH)
            elif direction == 'e':
                self.game.trigger_run(d.EAST)
            elif direction == 's':
                self.game.trigger_run(d.SOUTH)
            elif direction == 'w':
                self.game.trigger_run(d.WEST)
            else:
                print("Cannot run that direction")
            if len(self.game.get_current_tile().get_doors()) == 1 \
                    and self.game.get_chosen_tile().get_name() != "Foyer":
                self.game.set_state("Choosing Door")
                self.game.get_game()
        else:
            print("Cannot run when not being attacked")

    def do_cower(self, line):
        """When attacked use this command to cower.
        You will take no damage but will advance the time"""
        if self.game.get_state() == "Moving":
            self.game.trigger_cower()
        else:
            print("Cannot cower while right now")

    def do_search(self, line):
        """Searches for the zombie totem.
         (Player must be in the evil temple and
          will have to resolve a dev card)"""
        if self.game.get_state() == "Moving":
            self.game.search_for_totem()
        else:
            print("Cannot search currently")

    def do_bury(self, line):
        """Buries the totem. (Player must be in the
         graveyard and will have to resolve a dev card)
         """
        if self.game.get_state() == "Moving":
            self.game.bury_totem()
        else:
            print("Cannot currently bury the totem")

    def do_prompt(self, line):
        """Change the interactive prompt"""
        self.prompt = line + ': '

    def do_exit(self, line):
        """Exits the game without saving"""
        os.chdir(self.game_path)
        if self.game.get_con() is None:
            self.game.connect_db()
        if self.game.check_table_exists() is False:
            self.game.create_tables()
        self.game.input_data()
        self.game.plot_data()
        return True

    def do_extract(self, filename):
        """Extracts data from the database to an Excel file"""
        os.chdir(self.game_path)
        if not filename:
            return print("Must enter a valid file name")
        else:
            try:
                self.game.extract_data(filename)
            except OSError as o:
                print(f"Oh no an error {o}")

    def do_status(self, line):
        """Shows the status of the player"""
        if self.game.get_state() != "Game Over":
            self.game.get_player_status()

    @staticmethod
    def do_dir(line):
        """Gets the current working directory"""
        return print(os.getcwd())

    @staticmethod
    def do_cd(directory):
        """Changes the current directory"""
        if not directory:
            return print("Must enter a valid file name")
        else:
            try:
                os.chdir(directory)
            except (OSError, FileNotFoundError) as o:
                print(f"Oh no an error {o}")
        return print(os.getcwd())

    def do_back(self, line):
        """Goes back to the root game directory"""
        os.chdir(self.game_path)

    @staticmethod
    def do_mkdir(name):
        """Creates a new directory"""
        if not name:
            return print("Must enter a valid file name")
        else:
            try:
                os.mkdir(name)
            except (OSError, FileNotFoundError) as o:
                print(f"Oh no an error {o}")
        return print(os.listdir())

    def do_stats(self, line):
        """Displays the stat graph on request"""
        os.chdir(self.game_path)
        if self.game.get_con() is None:
            self.game.connect_db()
        if self.game.check_table_exists() is False:
            self.game.create_tables()
        self.game.plot_data()


if __name__ == '__main__':
    #  import doctest
    #  doctest.testmod(verbose=True)
    if len(sys.argv) > 1:
        Commands().onecmd(' '.join(sys.argv[1:]))
    else:
        Commands().cmdloop()
