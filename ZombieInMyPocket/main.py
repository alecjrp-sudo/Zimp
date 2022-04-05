import os
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
    """
    >>> test_g = Game(Player())
    >>> test_g.get_time()
    9
    >>> test_g.get_player().get_health()
    6
    >>> test_g.get_player().get_attack()
    1
    """

    def __init__(self, player, time=9, __game_map=None,
                 __indoor_tiles=None, __outdoor_tiles=None, chosen_tile=None,
                 __dev_cards=None, state="Starting",
                 current_move_direction=None, can_cower=True, connection=None):
        if __indoor_tiles is None:
            __indoor_tiles = []
        if __outdoor_tiles is None:
            __outdoor_tiles = []
        if __dev_cards is None:
            __dev_cards = []
        if __game_map is None:
            __game_map = {}
        self.__player = player
        self.__time = time
        self.__indoor_tiles = __indoor_tiles
        self.__outdoor_tiles = __outdoor_tiles
        self.__dev_cards = __dev_cards
        self.__tiles = __game_map
        self.__chosen_tile = chosen_tile
        self.__state = state
        self.__current_move_direction = current_move_direction
        self.__current_zombies = 0
        self.__can_cower = can_cower
        self.__room_item = None
        self.__connection = connection

    def get_state(self):
        return self.__state

    def set_state(self, state):
        self.__state = state

    def set_time(self, time):
        self.__time = time

    def get_tiles(self):
        return self.__tiles

    def get_room_item(self, index):
        return self.__room_item[index]

    def set_room_item(self, item):
        self.__room_item = item

    def get_chosen_tile(self):
        return self.__chosen_tile

    def get_player(self):
        return self.__player

    def get_con(self):
        return self.__connection

    def get_current_move_direction(self):
        return self.__current_move_direction

    def set_can_cower(self, b):
        self.__can_cower = b

    def plot_data(self):
        if self.__connection is None:
            self.connect_db()
        cursor = self.__connection.cursor()
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
        if self.__connection is None:
            self.connect_db()
        if self.check_table_exists() is False:
            self.create_tables()
        cursor = self.__connection.cursor()
        query = "SELECT zombies_killed," \
                " health_lost," \
                " move_count FROM" \
                " playerStats"
        cursor.execute(query)
        data = list(cursor)
        cursor.close()
        return data

    def extract_data(self, filename):
        if self.__connection is None:
            self.connect_db()
        if self.check_table_exists() is False:
            self.create_tables()
        cursor = self.__connection.cursor()
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
        df.to_excel(rf'additional_files\{filename}.xlsx')

    def delete_data(self):
        if self.__connection is None:
            self.connect_db()
        if self.check_table_exists() is False:
            self.create_tables()
        cursor = self.__connection.cursor()
        query = "DELETE FROM playerStats"
        cursor.execute(query)
        cursor.close()

    def connect_db(self):
        """
        >>> test_g = Game(Player())
        >>> test_g.connect_db()
        Opened database successfully
        True
        """
        if not os.path.exists('database'):
            os.mkdir('database')
        try:
            self.__connection = sqlite3.connect("database/player_stats.db")
        except Exception as e:
            print(e)
        else:
            print("Opened database successfully")
            return True

    def check_table_exists(self):
        if self.__connection is None:
            self.connect_db()
        check = """SELECT count(name) FROM sqlite_master
         WHERE type='table' AND name='playerStats'"""
        cursor = self.__connection.cursor()
        cursor.execute(check)
        if cursor.fetchone()[0] == 1:
            cursor.close()
            return True
        else:
            cursor.close()
            return False

    def create_tables(self):
        if self.__connection is None:
            self.connect_db()
        cursor = self.__connection.cursor()
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
        cursor = self.__connection.cursor()
        v = (self.__player.get_zombies_killed(),
             self.__player.get_health_lost(),
             self.__player.get_move_count())
        input_command = ''' INSERT INTO
         playerStats(zombies_killed,health_lost,move_count)
              VALUES(?,?,?) '''
        try:
            cursor.execute(input_command, v)
            self.__connection.commit()
            cursor.close()
        except sqlite3.Error as e:
            print("An error occurred:", e.args[0])

    def start_game(self):  # Run to initialise the game
        """
        >>> test_g = Game(Player())
        >>> test_g.start_game()
        >>> test_g.get_state()
        'Rotating'
        >>> test_g.get_chosen_tile().get_name()
        'Foyer'
        >>> test_g.get_chosen_tile().get_x()
        16
        >>> test_g.get_chosen_tile().get_y()
        16
        """
        self.load_tiles()
        self.load_dev_cards()
        for tile in self.__indoor_tiles:
            if tile.get_name() == 'Foyer':
                self.__chosen_tile = tile
                self.__state = "Rotating"
                break

    def get_game(self):
        s = ''
        f = ''
        if self.__state == "Moving":
            s = "In this state you are able to move the" \
                " player using the movement commands of n, e, s, w"
        if self.__state == "Rotating":
            s = "Use the rotate command to rotate tiles and align doors," \
                " Once you are happy with the door" \
                " position you can place the tile with the place command"
        if self.__state == "Choosing Door":
            s = "Choose where to place a new door" \
                " with the choose command + n, e, s, w"
        if self.__state == "Drawing Dev Card":
            s = "Use the draw command to draw a random development card"
        for door in self.__chosen_tile.get_doors():
            f += door.name + ', '
        return print(f' The chosen tile is {self.__chosen_tile.get_name()},'
                     f' the available doors in this room are {f}\n '
                     f'The state is {self.__state}.'
                     f' {s} \n'
                     f' Special Entrances :'
                     f' {self.__chosen_tile.get_entrance()}')

    def get_player_status(self):
        return print(f'It is {self.get_time()} pm \n'
                     f'The player currently has'
                     f' {self.__player.get_health()} health \n'
                     f'The player currently has'
                     f' {self.__player.get_attack()} attack \n'
                     f'The players items are'
                     f' {self.__player.get_items()}\n'
                     f'The game state is {self.__state}')

    def get_time(self):
        """
        >>> test_g = Game(Player())
        >>> test_g.get_time()
        9
        >>> test_g.set_time(10)
        >>> test_g.get_time()
        10
        """
        return self.__time

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
                self.__outdoor_tiles.append(new_tile)
            if tile[2] == "Indoor":
                new_tile = IndoorTile(tile[0], tile[1], doors)
                if tile[0] == "Dining Room":
                    new_tile.set_entrance(d.NORTH)
                self.__indoor_tiles.append(new_tile)

    def draw_tile(self, x, y):
        if self.get_current_tile().get_type() == "Indoor":
            if len(self.__indoor_tiles) == 0:
                return print("No more indoor tiles")
            elif self.get_current_tile().get_name() == "Dining Room" \
                    and self.__current_move_direction == \
                    self.get_current_tile().get_entrance():
                t = [t for t in self.__outdoor_tiles if t.__name == "Patio"]
                tile = t[0]
                tile.set_x(x)
                tile.set_y(y)
                self.__chosen_tile = tile
            else:
                tile = random.choice(self.__indoor_tiles)
                tile.set_x(x)
                tile.set_y(y)
                self.__chosen_tile = tile
        elif self.get_current_tile().__type == "Outdoor":
            if len(self.__outdoor_tiles) == 0:
                return print("No more outdoor tiles")
            tile = random.choice(self.__outdoor_tiles)
            tile.set_x(x)
            tile.set_y(y)
            self.__chosen_tile = tile

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
            self.__dev_cards.append(dev_card)
        random.shuffle(self.__dev_cards)
        self.__dev_cards.pop(0)
        self.__dev_cards.pop(0)

    def move_player(self, x, y):
        """
        >>> test_g = Game(Player())
        >>> test_g.move_player(15,16)
        >>> test_g.get_player().get_x()
        15
        >>> test_g.get_player().get_y()
        16
        >>> test_g.move_player(15,15)
        >>> test_g.get_player().get_x()
        15
        >>> test_g.get_player().get_y()
        15
        """
        self.__player.set_y(y)
        self.__player.set_x(x)
        self.__player.add_move_count()
        if self.__state == "Running":
            self.__state = "Moving"
        else:
            self.__state = "Drawing Dev Card"

    def get_tile_at(self, x, y):  # Returns the tile given x and y coordinates
        return self.__tiles[(x, y)]

    def select_move(self, direction):
        x, y = self.get_destination_coords(direction)
        if self.check_for_door(direction):
            self.__current_move_direction = direction
            if self.check_for_room(x, y) is False:
                if self.__state == "Running":
                    return print("Can only run into a discovered room")
                else:
                    self.draw_tile(x, y)
                    self.__state = "Rotating"
            if self.check_for_room(x, y):
                if self.check_indoor_outdoor_move(
                        self.get_current_tile().get_type(),
                        self.get_tile_at(x, y).get_type()):
                    return print("Cannot Move this way")
                else:
                    self.move_player(x, y)

    def check_indoor_outdoor_move(self, current_type, move_type):
        if current_type != move_type \
                and self.get_current_tile().get_name() \
                != "Patio" or "Dining Room":
            return False

    def get_destination_coords(self, direction):
        """
        >>> test_g = Game(Player())
        >>> test_g.get_destination_coords(d.NORTH)
        (16, 15)
        >>> test_g.get_destination_coords(d.SOUTH)
        (16, 17)
        >>> test_g.get_destination_coords(d.WEST)
        (15, 16)
        >>> test_g.get_destination_coords(d.EAST)
        (17, 16)
        """
        if direction == d.NORTH:
            return self.__player.get_x(), self.__player.get_y() - 1
        if direction == d.SOUTH:
            return self.__player.get_x(), self.__player.get_y() + 1
        if direction == d.EAST:
            return self.__player.get_x() + 1, self.__player.get_y()
        if direction == d.WEST:
            return self.__player.get_x() - 1, self.__player.get_y()

    def check_for_door(self, direction):
        if direction in self.get_current_tile().get_doors():
            return True
        else:
            return False

    def check_for_room(self, x, y):
        """
        >>> test_g = Game(Player())
        >>> test_g.check_for_room(16,16)
        False
        """
        if (x, y) not in self.__tiles:
            return False
        else:
            self.__chosen_tile = self.__tiles[(x, y)]
            return True

    def check_doors_align(self, direction):
        if self.__chosen_tile.get_name() == "Foyer":
            return True
        if direction == d.NORTH:
            if d.SOUTH not in self.__chosen_tile.get_doors():
                return False
        if direction == d.SOUTH:
            if d.NORTH not in self.__chosen_tile.get_doors():
                return False
        if direction == d.WEST:
            if d.EAST not in self.__chosen_tile.get_doors():
                return False
        elif direction == d.EAST:
            if d.WEST not in self.__chosen_tile.get_doors():
                return False
        return True

    def check_entrances_align(self):
        if self.get_current_tile().get_entrance() == d.NORTH:
            if self.__chosen_tile.get_entrance() == d.SOUTH:
                return True
        if self.get_current_tile().get_entrance() == d.SOUTH:
            if self.__chosen_tile.get_entrance() == d.NORTH:
                return True
        if self.get_current_tile().get_entrance() == d.WEST:
            if self.__chosen_tile.get_entrance() == d.EAST:
                return True
        if self.get_current_tile().get_entrance() == d.EAST:
            if self.__chosen_tile.get_entrance() == d.WEST:
                return True
        return print(" Dining room and Patio entrances dont align")

    def check_dining_room_has_exit(self):
        tile = self.__chosen_tile
        if tile.get_name() == "Dining Room":
            if self.__current_move_direction == d.NORTH \
                    and tile.get_entrance() == d.SOUTH:
                return False
            if self.__current_move_direction == d.SOUTH \
                    and tile.get_entrance() == d.NORTH:
                return False
            if self.__current_move_direction == d.EAST \
                    and tile.get_entrance() == d.WEST:
                return False
            if self.__current_move_direction == d.WEST \
                    and tile.get_entrance() == d.EAST:
                return False
        else:
            return True

    def place_tile(self, x, y):
        tile = self.__chosen_tile
        self.__tiles[(x, y)] = tile
        self.__state = "Moving"
        if tile.get_type() == "Outdoor":
            self.__outdoor_tiles.pop(self.__outdoor_tiles.index(tile))
        elif tile.get_type() == "Indoor":
            self.__indoor_tiles.pop(self.__indoor_tiles.index(tile))

    def get_current_tile(self):
        return self.__tiles[self.__player.get_x(), self.__player.get_y()]

    def rotate(self):
        tile = self.__chosen_tile
        tile.rotate_tile()
        if tile.get_name() == "Foyer":
            return
        if self.get_current_tile().get_name() \
                == "Dining Room" or "Patio":
            tile.rotate_entrance()

    # Call when player enters a room and draws a dev card
    def trigger_dev_card(self, time):
        if len(self.__dev_cards) == 0:
            if self.get_time == 11:
                print("You have run out of time")
                self.lose_game()
                return
            else:
                print("Reshuffling The Deck")
                self.load_dev_cards()
                self.__time += 1

        dev_card = self.__dev_cards[0]
        self.__dev_cards.pop(0)
        event = dev_card.get_event_at_time(time)
        if event[0] == "Nothing":
            print("There is nothing in this room")
            if len(self.__chosen_tile.__doors) == 1 \
                    and self.__chosen_tile.get_name() != "Foyer":
                self.__state = "Choosing Door"
                self.get_game()
                return
            else:
                self.__state = "Moving"
                self.get_game()
            return
        elif event[0] == "Health":  # Change health of player
            print("There might be something in this room")
            self.__player.add_health(event[1])

            if event[1] > 0:
                print(f"You gained {event[1]} health")
                self.__state = "Moving"
            elif event[1] < 0:
                print(f"You lost {event[1]} health")
                self.__state = "Moving"
                if self.__player.get_health() <= 0:
                    self.lose_game()
                    return
            elif event[1] == 0:
                print("You didn't gain or lose any health")
            if len(self.__chosen_tile.__doors) == 1 \
                    and self.__chosen_tile.get_name() != "Foyer":
                self.__state = "Choosing Door"
            if self.get_current_tile().get_name() == "Garden" or "Kitchen":
                self.trigger_room_effect(self.get_current_tile().get_name())
            else:
                self.__state = "Moving"
                self.get_game()
        elif event[0] == "Item":
            if len(self.__dev_cards) == 0:
                if self.get_time == 11:
                    print("You have run out of time")
                    self.lose_game()
                    return
                else:
                    print("Reshuffling The Deck")
                    self.load_dev_cards()
                    self.__time += 1
            next_card = self.__dev_cards[0]
            print(f"There is an item in this room: {next_card.get_item()}")
            if len(self.__player.get_items()) < 2:
                self.__dev_cards.pop(0)
                self.__player.add_item(next_card.get_item(), next_card.get_charges())
                print(f"You picked up the {next_card.get_item()}")
                if len(self.__chosen_tile.get_doors()) == 1 \
                        and self.__chosen_tile.get_name() != "Foyer":
                    self.__state = "Choosing Door"
                    self.get_game()
                else:
                    self.__state = "Moving"
                    self.get_game()
            else:
                self.__room_item = [next_card.get_item(), next_card.__charges]
                response = input("You already have two items, do"
                                 " you want to drop one of them? (Y/N) ")
                if response == "Y" or response == "y":
                    self.__state = "Swapping Item"
                else:  # If player doesn't want to drop item, just move on
                    self.__state = "Moving"
                    self.__room_item = None
                    self.get_game()
            if self.get_current_tile().get_name() == "Garden" or "Kitchen":
                self.trigger_room_effect(self.get_current_tile().get_name())
        elif event[0] == "Zombies":  # Add zombies to the game, begin combat
            print(f"There are {event[1]} zombies"
                  f" in this room, prepare to fight!")
            self.__current_zombies = int(event[1])
            self.__state = "Attacking"  # Create CMD for attacking zombies

    def trigger_attack(self, *item):
        if self.__state != "Attacking":
            return False
        player_attack = self.__player.get_attack()
        zombies = self.__current_zombies
        if len(item) == 2:  # If the player is using two items
            if "Oil" in item and "Candle" in item:
                print("You used the oil and the candle"
                      " to attack the zombies,"
                      " it kills all of them")
                self.drop_item("Oil")
                self.__state = "Moving"
                return
            elif "Gasoline" in item and "Candle" in item:
                print("You used the gasoline and the "
                      "candle to attack the zombies,"
                      " it kills all of them")
                self.drop_item("Gasoline")
                self.__state = "Moving"
                return
            elif "Gasoline" in item and "Chainsaw" in item:
                chainsaw_charge = self.__player.get_item_charges("Chainsaw")
                self.__player.set_item_charges("Chainsaw", chainsaw_charge + 2)
                player_attack += 3
                self.drop_item("Gasoline")
                self.__player.use_item_charge("Chainsaw")
            else:
                print("These items cannot be used together, try again")
                return
        elif len(item) == 1:
            if "Machete" in item:
                player_attack += 2
            elif "Chainsaw" in item:
                if self.__player.get_item_charges("Chainsaw") > 0:
                    player_attack += 3
                    self.__player.use_item_charge("Chainsaw")
                else:
                    print("This item has no charges left")
            elif "Golf Club" in item or "Grisly Femur" in \
                    item or "Board With Nails" in item:
                player_attack += 1
            elif "Can of Soda" in item:
                self.__player.add_health(2)
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
        self.__can_cower = True
        self.__player.add_health_lost(damage)
        self.__player.add_zombies_killed(zombies)
        self.__player.add_health(-damage)
        if self.__player.get_health() <= 0:
            self.lose_game()
            return
        else:
            self.__current_zombies = 0
            if self.get_current_tile().get_name() == "Garden" or "Kitchen":
                self.trigger_room_effect(self.get_current_tile().get_name())
            self.__state = "Moving"

    def trigger_run(self, direction, health_lost=-1):
        self.__state = "Running"
        self.select_move(direction)
        if self.__state == "Moving":
            self.__player.add_health(health_lost)
            print(f"You run away from the zombies,"
                  f" and lose {health_lost} health")
            self.__can_cower = True
            if self.get_current_tile().__name == "Garden" or "Kitchen":
                self.trigger_room_effect(self.get_current_tile().__name)
        else:
            self.__state = "Attacking"

    def trigger_room_effect(self, room_name):
        if room_name == "Garden":
            self.__player.add_health(1)
            print(f"After ending your turn in the"
                  f" {room_name} you have gained one health")
            self.__state = "Moving"
        if room_name == "Kitchen":
            self.__player.add_health(1)
            print(f"After ending your turn in the"
                  f" {room_name} you have gained one health")
            self.__state = "Moving"

    # If player chooses to cower instead of move to a new room
    def trigger_cower(self):
        """
        >>> test_g = Game(Player())
        >>> test_g.start_game()
        >>> test_g.place_tile(16, 16)
        >>> test_g.trigger_cower()
        You cower in fear, gaining 3 health, but lose time with the dev card
        >>> test_g.select_move(d.WEST)
        >>> test_g.trigger_cower()
        Cannot cower
        """
        if self.__can_cower:
            if self.__state == "Moving":
                self.__player.add_health(3)
                self.__dev_cards.pop(0)
                self.__state = "Moving"
                print("You cower in fear, gaining 3 health,"
                      " but lose time with the dev card")
            else:
                return print("Cannot cower")
        else:
            return print("Cannot cower during a zombie door attack")

    # Call when player wants to drop an item, and state is dropping item
    def drop_item(self, old_item):
        """
        >>> test_g = Game(Player())
        >>> test_g.start_game()
        >>> test_g.place_tile(16, 16)
        >>> test_g.drop_item("Chainsaw")
        That item is not in your inventory
        """
        for item in self.__player.get_items():
            if item[0] == old_item:
                self.__player.remove_item(item)
                print(f"You dropped the {old_item}")
                self.__state = "Moving"
                return
        print("That item is not in your inventory")

    def use_item(self, *item):
        if "Can of Soda" in item:
            self.__player.add_health(2)
            self.drop_item("Can of Soda")
            print("Used Can of Soda, gained 2 health")
        elif "Gasoline" in item and "Chainsaw" in item:
            chainsaw_charge = self.__player.get_item_charges("Chainsaw")
            self.__player.set_item_charges("Chainsaw", chainsaw_charge + 2)
            self.drop_item("Gasoline")
        else:
            print("These items cannot be used right now")
            return

    def choose_door(self, direction):
        if direction in self.__chosen_tile.get_doors():
            print("Choose a NEW door not an existing one")
            return False
        else:
            self.__chosen_tile.get_doors.append(direction)
            self.__current_zombies = 3
            print(f"{self.__current_zombies} Zombies have appeared,"
                  f" prepare for battle. Use the attack command to"
                  f" fight or the run command to flee")
            self.set_state("Attacking")

    def search_for_totem(self):
        """
        >>> test_g = Game(Player())
        >>> test_g.start_game()
        >>> test_g.place_tile(16, 16)
        >>> test_g.search_for_totem()
        You cannot search for a totem in this room
        """
        if self.get_current_tile().get_name() == "Evil Temple":
            if self.get_player().get_has_totem():
                print("player already has the totem")
                return
            else:
                print("Searching for totem, Resolving dev card")
                self.trigger_dev_card(self.get_time())
                self.get_player().found_totem()
        else:
            return print("You cannot search for a totem in this room")

    def bury_totem(self):
        """
        >>> test_g = Game(Player())
        >>> test_g.start_game()
        >>> test_g.place_tile(16, 16)
        >>> test_g.bury_totem()
        Cannot bury totem here
        """
        if self.get_current_tile().get_name() == "Graveyard":
            if self.get_player().get_has_totem():
                print("Burying totem, Resolving dev card")
                self.trigger_dev_card(self.get_time())
                if self.get_player().get_health() != 0:
                    print("You Won")
                    self.set_state("Game Over")
        else:
            return print("Cannot bury totem here")

    def check_for_dead_player(self):
        """Checks if the player is dead
        >>> test_g = Game(Player())
        >>> test_g.check_for_dead_player()
        False
        >>> test_g.get_player().set_health(0)
        >>> test_g.check_for_dead_player()
        True
        """
        if self.__player.get_health() <= 0:
            return True
        else:
            return False

    @staticmethod
    def resolve_doors(n, e, s, w):
        """Takes in a vale of 0 or 1 indicating if
         a door exists or not in a direction.
        >>> test_g = Game(Player())
        >>> test_g.resolve_doors(1,0,0,0)
        [<Direction.NORTH: (1,)>]
        >>> test_g.resolve_doors(0,1,0,0)
        [<Direction.EAST: (3,)>]
        >>> test_g.resolve_doors(0,0,1,0)
        [<Direction.SOUTH: (2,)>]
        >>> test_g.resolve_doors(0,0,0,1)
        [<Direction.WEST: 4>]

        """
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
        self.set_state("Game Over")


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
