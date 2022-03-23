import pickle
import random
from directions import Direction as d
import pandas as pd
import cmd
import sys
import sqlite3
from player import Player
from tile import OutdoorTile, IndoorTile
from dev_card import DevCard
import matplotlib.pyplot as p


class Game:
    def __init__(self, player, time=9, game_map=None,
                 indoor_tiles=None, outdoor_tiles=None, chosen_tile=None,
                 dev_cards=None, state="Starting",
                 current_move_direction=None, can_cower=True, connection=None):
        if indoor_tiles is None:
            indoor_tiles = []
        if outdoor_tiles is None:
            outdoor_tiles = []
        if dev_cards is None:
            dev_cards = []
        if game_map is None:
            game_map = {}
        self.player = player
        self.time = time
        self.indoor_tiles = indoor_tiles
        self.outdoor_tiles = outdoor_tiles
        self.dev_cards = dev_cards
        self.tiles = game_map
        self.chosen_tile = chosen_tile
        self.state = state
        self.current_move_direction = current_move_direction
        self.current_zombies = 0
        self.can_cower = can_cower
        self.room_item = None
        self.connection = connection

    def plot_data(self):
        cursor = self.connection.cursor()
        query = "SELECT COUNT(session_id), SUM(zombies_killed)," \
                " SUM(health_lost)," \
                " SUM(move_count) FROM" \
                " playerStats"
        cursor.execute(query)
        data = list(cursor)
        cursor.close()
        session_count, zombies_killed, health_lost, move_count = data[0]
        data = {"Statistic": ["Games Played", "Zombies Killed",
                              "health Lost", "Moves made"],
                "Number": [session_count, zombies_killed,
                           health_lost, move_count]
                }
        data_frame = pd.DataFrame(data=data)

        data_frame.plot.barh(x="Statistic",
                             y="Number",
                             rot=70,
                             title="Total player statistics")
        p.tight_layout()
        p.show(block=True)

    def get_data(self):
        if self.connection is None:
            self.connect_db()
            if self.check_table_exists() is True:
                self.create_tables()
        cursor = self.connection.cursor()
        query = "SELECT zombies_killed," \
                " health_lost," \
                " move_count FROM" \
                " playerStats"
        cursor.execute(query)
        data = list(cursor)
        cursor.close()
        return data

    def extract_data(self):
        if self.connection is None:
            self.connect_db()
            if self.check_table_exists() is True:
                self.create_tables()
        cursor = self.connection.cursor()
        query = "SELECT COUNT(session_id), SUM(zombies_killed)," \
                " SUM(health_lost)," \
                " SUM(move_count) FROM" \
                " playerStats"
        cursor.execute(query)
        data = list(cursor)
        cursor.close()
        session_count, zombies_killed, health_lost, move_count = data[0]
        data = {"Statistic": ["Games Played", "Zombies Killed",
                              "health Lost", "Moves made"],
                "Number": [session_count, zombies_killed,
                           health_lost, move_count]
                }
        df = pd.DataFrame(data)
        df.to_excel(r'additional_files\player_stats.xlsx')

    def delete_data(self):
        if self.connection is None:
            self.connect_db()
            if self.check_table_exists() is True:
                self.create_tables()
        cursor = self.connection.cursor()
        query = "DELETE FROM playerStats"
        cursor.execute(query)
        cursor.close()

    def connect_db(self):
        try:
            self.connection = sqlite3.connect("database/player_stats.db")
        except Exception as e:
            print(e)
        else:
            print("Opened database successfully")
            return True

    def check_table_exists(self):
        check = """SELECT count(name) FROM sqlite_master
         WHERE type='table' AND name='{playerStats}'"""
        cursor = self.connection.cursor()
        cursor.execute(check)
        if cursor.fetchone()[0] == 1:
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def create_tables(self):
        cursor = self.connection.cursor()
        table_command = """
        CREATE TABLE playerStats (
        session_id INTEGER PRIMARY KEY,
        zombies_killed INTEGER,
        health_lost INTEGER,
        move_count INTEGER)"""
        try:
            cursor.execute(table_command)
            cursor.close()
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])

    def input_data(self):
        cursor = self.connection.cursor()
        v = (self.player.zombies_killed,
             self.player.health_lost,
             self.player.move_count)
        input_command = ''' INSERT INTO
         playerStats(zombies_killed,health_lost,move_count)
              VALUES(?,?,?) '''
        try:
            cursor.execute(input_command, v)
            self.connection.commit()
            cursor.close()
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])

    def start_game(self):  # Run to initialise the game
        self.load_tiles()
        self.load_dev_cards()
        for tile in self.indoor_tiles:
            if tile.name == 'Foyer':
                self.chosen_tile = tile
                self.state = "Rotating"
                break

    def get_game(self):
        s = ''
        f = ''
        if self.state == "Moving":
            s = "In this state you are able to move the" \
                " player using the movement commands of n, e, s, w"
        if self.state == "Rotating":
            s = "Use the rotate command to rotate tiles and align doors," \
                " Once you are happy with the door" \
                " position you can place the tile with the place command"
        if self.state == "Choosing Door":
            s = "Choose where to place a new door" \
                " with the choose command + n, e, s, w"
        if self.state == "Drawing Dev Card":
            s = "Use the draw command to draw a random development card"
        for door in self.chosen_tile.doors:
            f += door.name + ', '
        return print(f' The chosen tile is {self.chosen_tile.name},'
                     f' the available doors in this room are {f}\n '
                     f'The state is {self.state}.'
                     f' {s} \n Special Entrances :'
                     f' {self.chosen_tile.entrance}')

    def get_player_status(self):
        return print(f'It is {self.get_time()} pm \n'
                     f'The player currently has'
                     f' {self.player.get_health()} health \n'
                     f'The player currently has'
                     f' {self.player.get_attack()} attack \n'
                     f'The players items are'
                     f' {self.player.get_items()}\n'
                     f'The game state is {self.state}')

    def get_time(self):
        return self.time

    # Loads tiles from excel file
    def load_tiles(self):
        excel_data = pd.read_excel(r'additional_files\Tiles.xlsx')
        tiles = []
        for name in excel_data.iterrows():
            tiles.append(name[1].tolist())
        for tile in tiles:
            doors = self.resolve_doors(tile[3], tile[4], tile[5], tile[6])
            if tile[2] == "Outdoor":
                new_tile = OutdoorTile(tile[0], tile[1], doors)
                if tile[0] == "Patio":
                    new_tile.set_entrance(d.NORTH)
                self.outdoor_tiles.append(new_tile)
            if tile[2] == "Indoor":
                new_tile = IndoorTile(tile[0], tile[1], doors)
                if tile[0] == "Dining Room":
                    new_tile.set_entrance(d.NORTH)
                self.indoor_tiles.append(new_tile)

    def draw_tile(self, x, y):
        if self.get_current_tile().type == "Indoor":
            if len(self.indoor_tiles) == 0:
                return print("No more indoor tiles")
            if self.get_current_tile().name == "Dining Room" \
                    and self.current_move_direction == \
                    self.get_current_tile().entrance:
                t = [t for t in self.outdoor_tiles if t.name == "Patio"]
                tile = t[0]
                tile.set_x(x)
                tile.set_y(y)
                self.chosen_tile = tile
            else:
                tile = random.choice(self.indoor_tiles)
                tile.set_x(x)
                tile.set_y(y)
                self.chosen_tile = tile
        elif self.get_current_tile().type == "Outdoor":
            if len(self.outdoor_tiles) == 0:
                return print("No more outdoor tiles")
            tile = random.choice(self.outdoor_tiles)
            tile.set_x(x)
            tile.set_y(y)
            self.chosen_tile = tile

    # Loads development cards from excel file
    def load_dev_cards(self):
        card_data = pd.read_excel(r'additional_files\DevCards.xlsx')
        for card in card_data.iterrows():
            item = card[1][0]
            event_one = (card[1][1], card[1][2])
            event_two = (card[1][3], card[1][4])
            event_three = (card[1][5], card[1][6])
            charges = card[1][7]
            dev_card = DevCard(item,
                               charges,
                               event_one,
                               event_two,
                               event_three)
            self.dev_cards.append(dev_card)
        random.shuffle(self.dev_cards)
        self.dev_cards.pop(0)
        self.dev_cards.pop(0)

    def move_player(self, x, y):
        self.player.set_y(y)
        self.player.set_x(x)
        self.player.add_move_count()
        if self.state == "Running":
            self.state = "Moving"
        else:
            self.state = "Drawing Dev Card"

    def get_tile_at(self, x, y):  # Returns the tile given x and y coordinates
        return self.tiles[(x, y)]

    def select_move(self, direction):
        x, y = self.get_destination_coords(direction)
        if self.check_for_door(direction):
            self.current_move_direction = direction
            if self.check_for_room(x, y) is False:
                if self.state == "Running":
                    return print("Can only run into a discovered room")
                else:
                    self.draw_tile(x, y)
                    self.state = "Rotating"
            if self.check_for_room(x, y):
                if self.check_indoor_outdoor_move(
                        self.get_current_tile().type,
                        self.get_tile_at(x, y).type):
                    return print("Cannot Move this way")
                else:
                    self.move_player(x, y)

    def check_indoor_outdoor_move(self, current_type, move_type):
        if current_type != move_type\
                and self.get_current_tile().name\
                != "Patio" or "Dining Room":
            return False

    def get_destination_coords(self, direction):
        if direction == d.NORTH:
            return self.player.get_x(), self.player.get_y() - 1
        if direction == d.SOUTH:
            return self.player.get_x(), self.player.get_y() + 1
        if direction == d.EAST:
            return self.player.get_x() + 1, self.player.get_y()
        if direction == d.WEST:
            return self.player.get_x() - 1, self.player.get_y()

    def check_for_door(self, direction):
        if direction in self.get_current_tile().doors:
            return True
        else:
            return False

    def check_for_room(self, x, y):
        if (x, y) not in self.tiles:
            return False
        else:
            self.chosen_tile = self.tiles[(x, y)]
            return True

    def check_doors_align(self, direction):
        if self.chosen_tile.name == "Foyer":
            return True
        if direction == d.NORTH:
            if d.SOUTH not in self.chosen_tile.doors:
                return False
        if direction == d.SOUTH:
            if d.NORTH not in self.chosen_tile.doors:
                return False
        if direction == d.WEST:
            if d.EAST not in self.chosen_tile.doors:
                return False
        elif direction == d.EAST:
            if d.WEST not in self.chosen_tile.doors:
                return False
        return True

    def check_entrances_align(self):
        if self.get_current_tile().entrance == d.NORTH:
            if self.chosen_tile.entrance == d.SOUTH:
                return True
        if self.get_current_tile().entrance == d.SOUTH:
            if self.chosen_tile.entrance == d.NORTH:
                return True
        if self.get_current_tile().entrance == d.WEST:
            if self.chosen_tile.entrance == d.EAST:
                return True
        if self.get_current_tile().entrance == d.EAST:
            if self.chosen_tile.entrance == d.WEST:
                return True
        return print(" Dining room and Patio entrances dont align")

    def check_dining_room_has_exit(self):
        tile = self.chosen_tile
        if tile.name == "Dining Room":
            if self.current_move_direction == d.NORTH\
                    and tile.entrance == d.SOUTH:
                return False
            if self.current_move_direction == d.SOUTH\
                    and tile.entrance == d.NORTH:
                return False
            if self.current_move_direction == d.EAST\
                    and tile.entrance == d.WEST:
                return False
            if self.current_move_direction == d.WEST\
                    and tile.entrance == d.EAST:
                return False
        else:
            return True

    def place_tile(self, x, y):
        tile = self.chosen_tile
        self.tiles[(x, y)] = tile
        self.state = "Moving"
        if tile.type == "Outdoor":
            self.outdoor_tiles.pop(self.outdoor_tiles.index(tile))
        elif tile.type == "Indoor":
            self.indoor_tiles.pop(self.indoor_tiles.index(tile))

    def get_current_tile(self):
        return self.tiles[self.player.get_x(), self.player.get_y()]

    def rotate(self):
        tile = self.chosen_tile
        tile.rotate_tile()
        if tile.name == "Foyer":
            return
        if self.get_current_tile().name == "Dining Room" or "Patio":
            tile.rotate_entrance()

    # Call when player enters a room and draws a dev card
    def trigger_dev_card(self, time):
        if len(self.dev_cards) == 0:
            if self.get_time == 11:
                print("You have run out of time")
                self.lose_game()
                return
            else:
                print("Reshuffling The Deck")
                self.load_dev_cards()
                self.time += 1

        dev_card = self.dev_cards[0]
        self.dev_cards.pop(0)
        event = dev_card.get_event_at_time(time)
        if event[0] == "Nothing":
            print("There is nothing in this room")
            if len(self.chosen_tile.doors) == 1 \
                    and self.chosen_tile.name != "Foyer":
                self.state = "Choosing Door"
                self.get_game()
                return
            else:
                self.state = "Moving"
                self.get_game()
            return
        elif event[0] == "Health":  # Change health of player
            print("There might be something in this room")
            self.player.add_health(event[1])

            if event[1] > 0:
                print(f"You gained {event[1]} health")
                self.state = "Moving"
            elif event[1] < 0:
                print(f"You lost {event[1]} health")
                self.state = "Moving"
                if self.player.get_health() <= 0:
                    self.lose_game()
                    return
            elif event[1] == 0:
                print("You didn't gain or lose any health")
            if len(self.chosen_tile.doors) == 1 \
                    and self.chosen_tile.name != "Foyer":
                self.state = "Choosing Door"
            if self.get_current_tile().name == "Garden" or "Kitchen":
                self.trigger_room_effect(self.get_current_tile().name)
            else:
                self.state = "Moving"
                self.get_game()
        elif event[0] == "Item":
            if len(self.dev_cards) == 0:
                if self.get_time == 11:
                    print("You have run out of time")
                    self.lose_game()
                    return
                else:
                    print("Reshuffling The Deck")
                    self.load_dev_cards()
                    self.time += 1
            next_card = self.dev_cards[0]
            print(f"There is an item in this room: {next_card.get_item()}")
            if len(self.player.get_items()) < 2:
                self.dev_cards.pop(0)
                self.player.add_item(next_card.get_item(), next_card.charges)
                print(f"You picked up the {next_card.get_item()}")
                if len(self.chosen_tile.doors) == 1 \
                        and self.chosen_tile.name != "Foyer":
                    self.state = "Choosing Door"
                    self.get_game()
                else:
                    self.state = "Moving"
                    self.get_game()
            else:
                self.room_item = [next_card.get_item(), next_card.charges]
                response = input("You already have two items, do"
                                 " you want to drop one of them? (Y/N) ")
                if response == "Y" or response == "y":
                    self.state = "Swapping Item"
                else:  # If player doesn't want to drop item, just move on
                    self.state = "Moving"
                    self.room_item = None
                    self.get_game()
            if self.get_current_tile().name == "Garden" or "Kitchen":
                self.trigger_room_effect(self.get_current_tile().name)
        elif event[0] == "Zombies":  # Add zombies to the game, begin combat
            print(f"There are {event[1]} zombies"
                  f" in this room, prepare to fight!")
            self.current_zombies = int(event[1])
            self.state = "Attacking"  # Create CMD for attacking zombies

    def trigger_attack(self, *item):
        if self.state != "Attacking":
            return False
        player_attack = self.player.get_attack()
        zombies = self.current_zombies
        if len(item) == 2:  # If the player is using two items
            if "Oil" in item and "Candle" in item:
                print("You used the oil and the candle"
                      " to attack the zombies,"
                      " it kills all of them")
                self.drop_item("Oil")
                self.state = "Moving"
                return
            elif "Gasoline" in item and "Candle" in item:
                print("You used the gasoline and the "
                      "candle to attack the zombies,"
                      " it kills all of them")
                self.drop_item("Gasoline")
                self.state = "Moving"
                return
            elif "Gasoline" in item and "Chainsaw" in item:
                chainsaw_charge = self.player.get_item_charges("Chainsaw")
                self.player.set_item_charges("Chainsaw", chainsaw_charge + 2)
                player_attack += 3
                self.drop_item("Gasoline")
                self.player.use_item_charge("Chainsaw")
            else:
                print("These items cannot be used together, try again")
                return
        elif len(item) == 1:
            if "Machete" in item:
                player_attack += 2
            elif "Chainsaw" in item:
                if self.player.get_item_charges("Chainsaw") > 0:
                    player_attack += 3
                    self.player.use_item_charge("Chainsaw")
                else:
                    print("This item has no charges left")
            elif "Golf Club" in item or "Grisly Femur" in\
                    item or "Board With Nails" in item:
                player_attack += 1
            elif "Can of Soda" in item:
                self.player.add_health(2)
                self.drop_item("Can of Soda")
                print("Used Can of Soda, gained 2 health")
                return
            elif "Oil" in item:
                self.trigger_run(0)
                return
            else:
                print("You cannot use this item right now, try again")
                return

        # Calculate damage on the player
        damage = zombies - player_attack
        if damage < 0:
            damage = 0
        print(f"You attacked the zombies, you lost {damage} health")
        self.can_cower = True
        self.player.add_health_lost(damage)
        self.player.add_zombies_killed(zombies)
        self.player.add_health(-damage)
        if self.player.get_health() <= 0:
            self.lose_game()
            return
        else:
            self.current_zombies = 0
            if self.get_current_tile().name == "Garden" or "Kitchen":
                self.trigger_room_effect(self.get_current_tile().name)
            self.state = "Moving"

    def trigger_run(self, direction, health_lost=-1):
        self.state = "Running"
        self.select_move(direction)
        if self.state == "Moving":
            self.player.add_health(health_lost)
            print(f"You run away from the zombies,"
                  f" and lose {health_lost} health")
            self.can_cower = True
            if self.get_current_tile().name == "Garden" or "Kitchen":
                self.trigger_room_effect(self.get_current_tile().name)
        else:
            self.state = "Attacking"

    def trigger_room_effect(self, room_name):
        if room_name == "Garden":
            self.player.add_health(1)
            print(f"After ending your turn in the"
                  f" {room_name} you have gained one health")
            self.state = "Moving"
        if room_name == "Kitchen":
            self.player.add_health(1)
            print(f"After ending your turn in the"
                  f" {room_name} you have gained one health")
            self.state = "Moving"

    # If player chooses to cower instead of move to a new room
    def trigger_cower(self):
        if self.can_cower:
            if self.state == "Moving":
                self.player.add_health(3)
                self.dev_cards.pop(0)
                self.state = "Moving"
                print("You cower in fear, gaining 3 health,"
                      " but lose time with the dev card")
        else:
            return print("Cannot cower during a zombie door attack")

    # Call when player wants to drop an item, and state is dropping item
    def drop_item(self, old_item):
        for item in self.player.get_items():
            if item[0] == old_item:
                self.player.remove_item(item)
                print(f"You dropped the {old_item}")
                self.state = "Moving"
                return
        print("That item is not in your inventory")

    def use_item(self, *item):
        if "Can of Soda" in item:
            self.player.add_health(2)
            self.drop_item("Can of Soda")
            print("Used Can of Soda, gained 2 health")
        elif "Gasoline" in item and "Chainsaw" in item:
            chainsaw_charge = self.player.get_item_charges("Chainsaw")
            self.player.set_item_charges("Chainsaw", chainsaw_charge + 2)
            self.drop_item("Gasoline")
        else:
            print("These items cannot be used right now")
            return

    def choose_door(self, direction):
        if direction in self.chosen_tile.doors:
            print("Choose a NEW door not an existing one")
            return False
        else:
            self.chosen_tile.doors.append(direction)
            self.current_zombies = 3
            print(f"{self.current_zombies} Zombies have appeared,"
                  f" prepare for battle. Use the attack command to"
                  f" fight or the run command to flee")
            self.state = "Attacking"

    def search_for_totem(self):
        if self.get_current_tile().name == "Evil Temple":
            if self.player.has_totem:
                print("player already has the totem")
                return
            else:
                print("Searching for totem, Resolving dev card")
                self.trigger_dev_card(self.time)
                self.player.found_totem()
        else:
            print("You cannot search for a totem in this room")

    def bury_totem(self):  #
        if self.get_current_tile().name == "Graveyard":
            if self.player.has_totem:
                print("Burying totem, Resolving dev card")
                self.trigger_dev_card(self.time)
                if self.player.health != 0:
                    print("You Won")
                    self.state = "Game Over"
        else:
            print("Cannot bury totem here")

    def check_for_dead_player(self):
        if self.player.health <= 0:
            return True
        else:
            return False

    @staticmethod
    def resolve_doors(n, e, s, w):
        doors = []
        if n == 1:
            doors.append(d.NORTH)
        if e == 1:
            doors.append(d.EAST)
        if s == 1:
            doors.append(d.SOUTH)
        if w == 1:
            doors.append(d.WEST)
        return doors

    def lose_game(self):
        self.state = "Game Over"


class Commands(cmd.Cmd):
    intro = 'Welcome, type help or ? to list the' \
            ' commands or start to start the game'

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "> "
        self.player = Player()
        self.game = Game(self.player)

    def do_start(self, line):
        """Starts a new game"""
        if self.game.state == "Starting":
            self.game.start_game()
            self.game.get_game()
        else:
            print("Game has already Started")

    def do_rotate(self, line):
        """Rotates the current map piece 1 rotation clockwise"""
        if self.game.state == "Rotating":
            self.game.rotate()
            self.game.get_game()
        else:
            print("Tile not chosen to rotate")

    def do_place(self, line):
        """Places the current map tile"""
        if self.game.state == "Rotating":
            if self.game.chosen_tile.name == "Foyer":
                self.game.place_tile(16, 16)
            elif self.game.check_dining_room_has_exit() is False:
                return print("Dining room entrance must face an empty tile")
            else:
                if self.game.get_current_tile().name == "Dining Room" \
                        and self.game.current_move_direction ==\
                        self.game.get_current_tile().entrance:
                    if self.game.check_entrances_align():
                        self.game.place_tile(self.game.chosen_tile.x,
                                             self.game.chosen_tile.y)
                        self.game.move_player(self.game.chosen_tile.x,
                                              self.game.chosen_tile.y)
                elif self.game.check_doors_align(
                        self.game.current_move_direction):
                    self.game.place_tile(self.game.chosen_tile.x,
                                         self.game.chosen_tile.y)
                    self.game.move_player(self.game.chosen_tile.x,
                                          self.game.chosen_tile.y)
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
        if self.game.state == "Choosing Door":
            self.game.can_cower = False
            self.game.choose_door(direction)
        else:
            print("Cannot choose a door right now")

    def do_n(self, line):
        """Moves the player North"""
        if self.game.state == "Moving":
            self.game.select_move(d.NORTH)
            self.game.get_game()
        else:
            return print("Player not ready to move")

    def do_s(self, line):
        """Moves the player South"""
        if self.game.state == "Moving":
            self.game.select_move(d.SOUTH)
            self.game.get_game()
        else:
            return print("Player not ready to move")

    def do_e(self, line):
        """Moves the player East"""
        if self.game.state == "Moving":
            self.game.select_move(d.EAST)
            self.game.get_game()
        else:
            return print("Player not ready to move")

    def do_w(self, line):
        """Moves the player West"""
        if self.game.state == "Moving":
            self.game.select_move(d.WEST)
            self.game.get_game()
        else:
            return print("Player not ready to move")

    def do_save(self, line):
        """Takes a filepath and saves the game to a file"""
        if not line:
            return print("Must enter a valid file name")
        else:
            if len(self.game.tiles) == 0:
                return print("Cannot save game with empty map")
            file_name = line + '.pickle'
            with open(file_name, 'wb') as f:
                pickle.dump(self.game, f)

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
            except FileNotFoundError:
                print("No File with this name exists")

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

        if self.game.state == "Attacking":
            if arg1 == '':
                self.game.trigger_attack()
            elif arg2 == 0:
                self.game.trigger_attack(arg1)
            elif arg1 != '' and arg2 != 0:
                self.game.trigger_attack(arg1, arg2)

            if len(self.game.chosen_tile.doors) == 1 and\
                    self.game.chosen_tile.name != "Foyer":
                self.game.state = "Choosing Door"
                self.game.get_game()
            if self.game.state == "Game Over":
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

        if self.game.state == "Moving":
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
        if self.game.state != "Game Over":
            self.game.drop_item(item)
            self.game.get_game()

    def do_swap(self, line):
        """Swaps an item in you hand with the one in the room"""
        if self.game.state == "Swapping Item":
            self.game.drop_item(line)
            self.game.player.add_item(self.game.room_item[0],
                                      self.game.room_item[1])
            self.game.room_item = None
            self.game.get_game()

    def do_draw(self, line):
        """Draws a new development card (Must be done after evey move)"""
        if self.game.state == "Drawing Dev Card":
            self.game.trigger_dev_card(self.game.time)
        else:
            print("Cannot currently draw a card")

    def do_run(self, direction):
        """Given a direction will flee attacking
         zombies at a price of one health"""
        if self.game.state == "Attacking":
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
            if len(self.game.get_current_tile().doors) == 1 \
                    and self.game.chosen_tile.name != "Foyer":
                self.game.state = "Choosing Door"
                self.game.get_game()
        else:
            print("Cannot run when not being attacked")

    def do_cower(self, line):
        """When attacked use this command to cower.
        You will take no damage but will advance the time"""
        if self.game.state == "Moving":
            self.game.trigger_cower()
        else:
            print("Cannot cower while right now")

    def do_search(self, line):
        """Searches for the zombie totem.
         (Player must be in the evil temple and
          will have to resolve a dev card)"""
        if self.game.state == "Moving":
            self.game.search_for_totem()
        else:
            print("Cannot search currently")

    def do_bury(self, line):
        """Buries the totem. (Player must be in the
         graveyard and will have to resolve a dev card)"""
        if self.game.state == "Moving":
            self.game.bury_totem()
        else:
            print("Cannot currently bury the totem")

    def do_prompt(self, line):
        """Change the interactive prompt"""
        self.prompt = line + ': '

    def do_exit(self, line):
        """Exits the game without saving"""
        if self.game.connection is None:
            self.game.connect_db()
            if self.game.check_table_exists() is False:
                self.game.create_tables()
        self.game.input_data()
        self.game.plot_data()
        return True

    def do_extract(self, line):
        self.game.extract_data()

    def do_status(self, line):
        """Shows the status of the player"""
        if self.game.state != "Game Over":
            self.game.get_player_status()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        Commands().onecmd(' '.join(sys.argv[1:]))
    else:
        Commands().cmdloop()
