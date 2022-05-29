from directions import Direction as d
from abc import ABCMeta, abstractmethod


# Abstract Product
class Tile(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, name, x=16, y=16, effect=None,
                 __doors=None, entrance=None, tile_type=None):
        self.__type = tile_type
        self.__name = name
        self.__x = x  # x will represent the tiles position horizontally
        self.__y = y  # y will represent the tiles position vertically
        self.__effect = effect
        self.__doors = __doors
        self.__entrance = entrance

    def get_x(self):
        return self.__x

    def get_type(self):
        return self.__type

    def get_name(self):
        return self.__name

    def get_y(self):
        return self.__y

    def get_effect(self):
        return self.__effect

    def get_doors(self):
        return self.__doors

    def get_entrance(self):
        return self.__entrance

    def set_x(self, x):
        self.__x = x

    def set_y(self, y):
        self.__y = y

    def change_door_position(self, idx, direction):
        self.__doors[idx] = direction

    def set_entrance(self, direction):
        self.__entrance = direction

    def rotate_entrance(self):
        if self.__entrance == d.SOUTH:
            self.set_entrance(d.WEST)
            return
        if self.__entrance == d.EAST:
            self.set_entrance(d.SOUTH)
            return
        if self.__entrance == d.WEST:
            self.set_entrance(d.NORTH)
            return
        else:
            self.set_entrance(d.EAST)
            return

    def rotate_tile(self):  # Will rotate the tile 1 position clockwise
        for door in self.__doors:
            if door == d.NORTH:
                self.change_door_position(self.__doors.index(door), d.EAST)
            if door == d.EAST:
                self.change_door_position(self.__doors.index(door), d.SOUTH)
            if door == d.SOUTH:
                self.change_door_position(self.__doors.index(door), d.WEST)
            if door == d.WEST:
                self.change_door_position(self.__doors.index(door), d.NORTH)


# Abstract Factory
class TileFactory(metaclass=ABCMeta):
    @abstractmethod
    def create_tile(self, *args, **kwargs):
        pass  # pragma: no cover


# Concrete Factory
class IndoorTileFactory(TileFactory):
    def create_tile(self, *args, **kwargs):
        return IndoorTile(*args, **kwargs)


# Concrete Factory
class OutdoorTileFactory(TileFactory):
    def create_tile(self, *args, **kwargs):
        return OutdoorTile(*args, **kwargs)


# Concrete Product A
class IndoorTile(Tile):
    def __init__(self, name, effect=None,
                 __doors=None, x=16, y=16, entrance=None, tile_type="Indoor"):
        super().__init__(name, x, y, effect, __doors, entrance, tile_type)


# Concrete Product B
class OutdoorTile(Tile):
    def __init__(self, name, effect=None,
                 __doors=None, x=16, y=16, entrance=None, tile_type="Outdoor"):
        super().__init__(name, x, y, effect, __doors, entrance, tile_type)
