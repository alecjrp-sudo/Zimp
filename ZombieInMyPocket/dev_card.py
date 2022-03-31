# Development cards for the game. Played when the player moves into the room.
class DevCard:
    def __init__(self, item, charges, event_one, event_two, event_three):
        self.__item = item
        self.__charges = charges
        self.__event_one = event_one
        self.__event_two = event_two
        self.__event_three = event_three

        if self.__charges != "Unlimited":
            int(self.__charges)

    def get_event_at_time(self, time):
        if time == 9:
            return self.__event_one
        elif time == 10:
            return self.__event_two
        elif time == 11:
            return self.__event_three

    def get_item(self):
        return self.__item

    def get_charges(self):
        return self.__charges

    def __str__(self):
        return "Item: {}, Event 1: {}, Event 2: {}, Event 3: {}" \
            .format(self.__item, self.__event_one,
                    self.__event_two, self.__event_three)
