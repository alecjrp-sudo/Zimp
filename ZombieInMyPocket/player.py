class Player:
    def __init__(self, attack=1, health=6, x=16, y=16, has_totem=False,
                 zombies_killed=0, health_lost=0, move_count=0):
        self.__attack = attack
        self.__health = health
        self.__x = x
        self.__y = y
        self.__items = []
        self.__has_totem = has_totem
        self.__zombies_killed = zombies_killed
        self.__health_lost = health_lost
        self.__move_count = move_count

    def add_zombies_killed(self, zombies):
        self.__zombies_killed += zombies

    def get_zombies_killed(self):
        return self.__zombies_killed

    def get_health_lost(self):
        return self.__health_lost

    def get_move_count(self):
        return self.__move_count

    def get_has_totem(self):
        return self.__has_totem

    def set_has_totem(self, f):
        self.__has_totem = f

    def add_health_lost(self, health):
        self.__health_lost += health

    def add_move_count(self):
        self.__move_count += 1

    def get_health(self):
        return self.__health

    def found_totem(self):
        self.__has_totem = True

    def get_attack(self):
        return self.__attack

    def set_attack(self, attack):
        self.__attack = attack

    def set_health(self, health):
        self.__health = health

    def add_health(self, health):
        self.__health += health

    def add_attack(self, attack):
        self.__attack += attack

    def get_items(self):
        return self.__items

    def get_item_charges(self, item):
        for check_item in self.get_items():
            if check_item[0] == item:
                return check_item[1]

    def set_item_charges(self, item, charge):
        for check_item in self.get_items():
            if check_item[0] == item:
                check_item[1] = charge

    def use_item_charge(self, item):
        for check_item in self.get_items():
            if check_item[0] == item:
                check_item[1] -= 1

    def add_item(self, item, charges):
        if len(self.__items) < 2:
            self.__items.append([item, charges])

    def remove_item(self, item):
        self.__items.pop(self.__items.index(item))

    def set_x(self, x):
        self.__x = x

    def set_y(self, y):
        self.__y = y

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y
