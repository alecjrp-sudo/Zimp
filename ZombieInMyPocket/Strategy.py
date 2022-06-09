from abc import ABCMeta, abstractmethod


class Context:
    def __init__(self):
        self._strategies = {5: GasolineCandleStrategy(), 10: ChainsawStrategy(), 7: OilCandleStrategy()}
        self._strategy = None

    def set_strategy(self, value):
        self._strategy = self._strategies.get(value)

    def execute_attack_strategy(self):
        self._strategy.execute()


class AttackStrategy(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self.__item_values = {"Gasoline": 1, "Chainsaw": 9, "Oil": 3, "Candle": 4, "OilCandle": 7,
                              "GasolineCandle": 5, "GasolineChainsaw": 10, "Machete": 30, "Golf Club": 30,
                              "Grisly Femur": 30, "Board With Nails": 30}

    @abstractmethod
    def calculate(self, *items):
        pass

    @abstractmethod
    def execute(self):
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

    def calculate(self, item1, item2):
        a = self.__item_values.get(item1)
        b = self.__item_values.get(item2)
        return a + b

    def execute(self):
        pass


class OneItemAttackStrategy(AttackStrategy):
    def __init__(self):
        super().__init__()

    def calculate(self, item1):
        return self.__item_values.get(item1)

    def execute(self):
        pass


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
        return self.damage_buff


class OtherWeapon(ItemStrategy):
    def __init__(self):
        self.damage_buff = 2

    def execute(self):
        print("You used a weapon, gain 1 attack")
        return self.damage_buff


class CanOfSoda(ItemStrategy):
    def __init__(self):
        self.damage_buff = 2

    def execute(self):
        print("Used Can of Soda, gained 2 health")
        return self.damage_buff
