from directions import Direction as d


class Tile:
    def __init__(self, name, x=16, y=16, effect=None,
                 doors=None, entrance=None):
        if doors is None:
            doors = []
        self.name = name
        self.x = x  # x will represent the tiles position horizontally
        self.y = y  # y will represent the tiles position vertically
        self.effect = effect
        self.doors = doors
        self.entrance = entrance

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def change_door_position(self, idx, direction):
        self.doors[idx] = direction

    def set_entrance(self, direction):
        self.entrance = direction

    def rotate_entrance(self):
        if self.entrance == d.NORTH:
            self.set_entrance(d.EAST)
            return
        if self.entrance == d.SOUTH:
            self.set_entrance(d.WEST)
            return
        if self.entrance == d.EAST:
            self.set_entrance(d.SOUTH)
            return
        if self.entrance == d.WEST:
            self.set_entrance(d.NORTH)
            return

    def rotate_tile(self):  # Will rotate the tile 1 position clockwise
        for door in self.doors:
            if door == d.NORTH:
                self.change_door_position(self.doors.index(door), d.EAST)
            if door == d.EAST:
                self.change_door_position(self.doors.index(door), d.SOUTH)
            if door == d.SOUTH:
                self.change_door_position(self.doors.index(door), d.WEST)
            if door == d.WEST:
                self.change_door_position(self.doors.index(door), d.NORTH)


class IndoorTile(Tile):
    def __init__(self, name, effect=None,
                 doors=None, x=16, y=16, entrance=None):
        if doors is None:
            doors = []
        self.type = "Indoor"
        super().__init__(name, x, y, effect, doors, entrance)

    def __repr__(self):
        return f'{self.name}, {self.doors}, {self.type},' \
               f' {self.x}, {self.y}, {self.effect} \n'


class OutdoorTile(Tile):
    def __init__(self, name, effect=None,
                 doors=None, x=16, y=16, entrance=None):
        if doors is None:
            doors = []
        self.type = "Outdoor"
        super().__init__(name, x, y, effect, doors, entrance)

    def __repr__(self):
        return f'{self.name}, {self.doors}, {self.type},' \
               f' {self.x}, {self.y}, {self.effect} \n'
