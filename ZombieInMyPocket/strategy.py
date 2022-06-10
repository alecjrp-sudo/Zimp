from abc import ABCMeta, abstractmethod


class Context:
    def __init__(self):
        self._strategies = {5: GasolineCandleStrategy(),
                            51: ChainsawStrategy(),
                            52: ChainsawStrategy(),
                            53: ChainsawStrategy(),
                            7: OilCandleStrategy(),
                            30: MacheteStrategy(),
                            31: OtherWeaponStrategy(),
                            50: EmptyChainsawStrategy()}
        self._strategy = None

    def set_strategy(self, value):
        if value not in self._strategies:
            return False
        else:
            self._strategy = self._strategies.get(value)
            return True

    def execute_attack_strategy(self):
        return self._strategy.execute()


class AttackStrategy(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self._item_values = {"Gasoline": 1, "Chainsaw": 50,
                             "Oil": 3, "Candle": 4, "OilCandle": 7,
                             "GasolineCandle": 5, "GasolineChainsaw": 53,
                             "Machete": 29, "Golf Club": 30,
                             "Grisly Femur": 30, "Board With Nails": 30}

    @abstractmethod
    def calculate(self, *items):
        pass  # pragma: no cover


class ItemStrategy(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self._damage_buff = 10

    @abstractmethod
    def execute(self):
        pass  # pragma: no cover


class TwoItemAttackStrategy(AttackStrategy):
    def __init__(self):
        super().__init__()

    def calculate(self, item):
        a = self._item_values.get(item[0][0])
        b = self._item_values.get(item[1][0])
        return a + b


class OneItemAttackStrategy(AttackStrategy):
    def __init__(self, charges):
        super().__init__()
        self._charges = charges

    def calculate(self, item):
        value = self._item_values.get(item[0][0][0]) \
                + self._charges
        return value


class OilCandleStrategy(ItemStrategy):
    def __init__(self):
        super().__init__()

    def execute(self):
        print("You used the oil and the candle"
              " to attack the zombies,"
              " it kills all of them")
        return self._damage_buff


class GasolineCandleStrategy(ItemStrategy):
    def __init__(self):
        super().__init__()

    def execute(self):
        print("You used the gasoline"
              " and the candle to attack"
              " the zombies,"
              " it kills all of them")
        return self._damage_buff


class ChainsawStrategy(ItemStrategy):
    def __init__(self):
        self._damage_buff = 3

    def execute(self):
        return self._damage_buff


class EmptyChainsawStrategy(ItemStrategy):
    def __init__(self):
        self._damage_buff = 0

    def execute(self):
        print("Chainsaw is empty")
        return self._damage_buff


class MacheteStrategy(ItemStrategy):
    def __init__(self):
        self._damage_buff = 2

    def execute(self):
        print("You used the Machete, gain 2 attack")
        return int(self._damage_buff)


class OtherWeaponStrategy(ItemStrategy):
    def __init__(self):
        super().__init__()
        self._damage_buff = 1

    def execute(self):
        print("You used a weapon, gain 1 attack")
        return self._damage_buff
