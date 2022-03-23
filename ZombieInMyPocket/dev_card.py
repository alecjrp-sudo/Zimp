# Development cards for the game. Played when the player moves into the room.
class DevCard:
    def __init__(self, item, charges, event_one, event_two, event_three):
        self.item = item
        self.charges = charges
        self.event_one = event_one
        self.event_two = event_two
        self.event_three = event_three

        if self.charges != "Unlimited":
            int(self.charges)

    def get_event_at_time(self, time):
        if time == 9:
            return self.event_one
        elif time == 10:
            return self.event_two
        elif time == 11:
            return self.event_three

    def get_item(self):
        return self.item

    def get_charges(self):
        return self.charges

    def __str__(self):
        return "Item: {}, Event 1: {}, Event 2: {}, Event 3: {}" \
            .format(self.item, self.event_one,
                    self.event_two, self.event_three)
