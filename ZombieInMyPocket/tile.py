from directions import Direction as d


class Tile:
    def __init__(self, name, x=16, y=16, effect=None,
                 __doors=None, entrance=None):
        if __doors is None:
            __doors = []
        self.__name = name
        self.__x = x  # x will represent the tiles position horizontally
        self.__y = y  # y will represent the tiles position vertically
        self.__effect = effect
        self.__doors = __doors
        self.__entrance = entrance

    def get_x(self):
        return self.__x

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
        if self.__entrance == d.NORTH:
            self.set_entrance(d.EAST)
            return
        if self.__entrance == d.SOUTH:
            self.set_entrance(d.WEST)
            return
        if self.__entrance == d.EAST:
            self.set_entrance(d.SOUTH)
            return
        if self.__entrance == d.WEST:
            self.set_entrance(d.NORTH)
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


class IndoorTile(Tile):
    def __init__(self, name, effect=None,
                 __doors=None, x=16, y=16, entrance=None):
        if __doors is None:
            __doors = []
        self.__type = "Indoor"
        super().__init__(name, x, y, effect, __doors, entrance)

    def get_type(self):
        return self.__type

    def __repr__(self):
        return f'{self.__name}, {self.__doors}, {self.__type},' \
               f' {self.__x}, {self.__y}, {self.__effect} \n'


class OutdoorTile(Tile):
    def __init__(self, name, effect=None,
                 __doors=None, x=16, y=16, entrance=None):
        if __doors is None:
            __doors = []
        self.__type = "Outdoor"
        super().__init__(name, x, y, effect, __doors, entrance)

    def get_type(self):
        return self.__type

    def __repr__(self):
        return f'{self.__name}, {self.__doors}, {self.__type},' \
               f' {self.__x}, {self.__y}, {self.__effect} \n'
