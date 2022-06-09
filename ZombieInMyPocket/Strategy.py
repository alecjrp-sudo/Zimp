from abc import ABCMeta, abstractmethod


class Context:
    def __init__(self):
        self._strategy = None

    def set_strategy(self, strategy):
        self._strategy = strategy

    def execute_attack_strategy(self):
        self._strategy.execute()


class AttackStrategy(metaclass=ABCMeta):
    @abstractmethod
    def execute(self):
        pass


class OilCandleStrategy(AttackStrategy):
    def execute(self):
        print("You used the oil and the candle"
              " to attack the zombies,"
              " it kills all of them")
        return 0


class GasolineCandleStrategy(AttackStrategy):
    def execute(self):
        print("You used the gasoline and the "
              "candle to attack the zombies,"
              " it kills all of them")
        return 0


class ChainsawStrategy(AttackStrategy):
    def execute(self):
        print("You used the chainsaw, gain 3 attack")
        return 3


class MacheteStrategy(AttackStrategy):
    def execute(self):
        print("You used the Machete, gain 2 attack")
        return 2


class OtherWeapon(AttackStrategy):
    def execute(self):
        print("You used a weapon, gain 1 attack")
        return 1


class CanOfSoda(AttackStrategy):
    def execute(self):
        print("Used Can of Soda, gained 2 health")
        return 2
