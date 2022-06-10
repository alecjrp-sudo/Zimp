from abc import ABCMeta, abstractmethod


class Context:
    def __init__(self):
        self._strategies = {5: GasolineCandleStrategy(), 10: ChainsawStrategy(),
                            7: OilCandleStrategy(), 29: MacheteStrategy(), 30: OtherWeapon()}
        self._strategy = None

    def set_strategy(self, value):
        self._strategy = self._strategies.get(value)

    def execute_attack_strategy(self):
        return self._strategy.execute()

    def get_strategy(self):
        return self._strategy


class AttackStrategy(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self._item_values = {"Gasoline": 1, "Chainsaw": 9, "Oil": 3, "Candle": 4, "OilCandle": 7,
                             "GasolineCandle": 5, "GasolineChainsaw": 10, "Machete": 29, "Golf Club": 30,
                             "Grisly Femur": 30, "Board With Nails": 30}

    @abstractmethod
    def calculate(self, *items):
        pass


class ItemStrategy(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self.damage_buff = 0

    @abstractmethod
    def execute(self):
        pass


class TwoItemAttackStrategy(AttackStrategy):
    def __init__(self):
        super().__init__()

    def calculate(self, item):
        a = self._item_values.get(item[0][0])
        b = self._item_values.get(item[1][0])
        return a + b


class OneItemAttackStrategy(AttackStrategy):
    def __init__(self):
        super().__init__()

    def calculate(self, item1):
        return self._item_values.get(item1[0][0][0])


class OilCandleStrategy(ItemStrategy):
    def __init__(self):
        super().__init__()

    def execute(self):
        print("You used the oil and the candle"
              " to attack the zombies,"
              " it kills all of them")
        return self.damage_buff


class GasolineCandleStrategy(ItemStrategy):
    def __init__(self):
        super().__init__()

    def execute(self):
        print("You used the gasoline and the "
              "candle to attack the zombies,"
              " it kills all of them")
        return self.damage_buff


class ChainsawStrategy(ItemStrategy):
    def __init__(self):
        self.damage_buff = 3

    def execute(self):
        print("You used the chainsaw, gain 3 attack")
        return self.damage_buff


class MacheteStrategy(ItemStrategy):
    def __init__(self):
        self.damage_buff = 2

    def execute(self):
        print("You used the Machete, gain 2 attack")
        return int(self.damage_buff)


class OtherWeapon(ItemStrategy):
    def __init__(self):
        super().__init__()
        self.damage_buff = 2

    def execute(self):
        print("You used a weapon, gain 1 attack")
        return self.damage_buff
