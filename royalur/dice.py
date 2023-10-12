import random
from enum import Enum
from abc import ABC, abstractmethod
from overrides import overrides


class Roll:
    """
    A roll of the dice.
    """

    value: int
    """
    The value of the dice that was rolled.
    """

    def __init__(self, value: int):
        self.value = value


class Dice(ABC):
    """
    A generator of dice rolls.
    """

    name: str
    """
    The name of this dice.
    """

    def __init__(self, name: str):
        self.name = name

    def has_state() -> bool:
        """
        Returns whether this dice holds any state that affects its dice rolls.
        If this is overriden, then copy_from should also be overriden.
        """
        return False

    def copy_from(self, other: 'Dice') -> bool:
        """
        Copies the state of the other dice into this dice. If the dice does
        not have state, this is a no-op.
        """
        pass

    @abstractmethod
    def get_max_roll_value(self) -> int:
        """
        Gets the maximum value that could be rolled by this dice.
        """
        pass

    @abstractmethod
    def get_roll_probabilities(self) -> list[float]:
        """
        Gets the probability of rolling each value of the dice, where the
        index into the returned array represents the value of the roll.
        """
        pass

    @abstractmethod
    def roll_value(self) -> int:
        """
        Generates a random roll using this dice, and returns just the value.
        If this dice has state, this should call record_roll.
        """
        pass

    def record_roll(self, value: int):
        """
        Updates the state of this dice after having rolled value.
        """
        pass

    @abstractmethod
    def generate_roll(self, value: int) -> Roll:
        """
        Generates a roll with the given value using this dice.
        """
        pass

    def roll(self) -> Roll:
        """
        Generates a random roll using this dice.
        """
        return self.generate_roll(self.roll_value())


class BinaryDice(Dice):
    """
    Rolls a number of binary die and counts the result.
    """

    num_die: int
    """
    The number of binary dice to roll.
    """

    roll_probabilities: list[float]
    """
    The probability of rolling each value with these dice.
    """

    def __init__(self, name: str, num_die: int):
        super().__init__(name)
        self.num_die = num_die
        self.roll_probabilities = []

        # Binomial Distribution
        baseProb = 0.5 ** num_die
        nChooseK = 1
        for roll in range(0, num_die + 1):
            self.roll_probabilities.append(baseProb * nChooseK)
            nChooseK = nChooseK * (num_die - roll) // (roll + 1)

    @overrides
    def get_max_roll_value(self) -> int:
        return self.num_die

    @overrides
    def get_roll_probabilities(self) -> list[float]:
        return self.roll_probabilities

    @overrides
    def roll_value(self) -> int:
        value = 0
        for _ in range(self.num_die):
            # Simulate rolling a single D2 dice.
            if random.random() >= 0.5:
                value += 1

        return value

    @overrides
    def generate_roll(self, value: int) -> Roll:
        if value < 0 or value > self.num_die:
            raise ValueError(f"This dice cannot roll {value}");

        return Roll(value)


class BinaryDice0AsMax(BinaryDice):
    """
    A set of binary dice where a roll of zero actually represents
    the highest roll possible, rather than the lowest.
    """

    max_roll_value: int

    def __init__(self, name: str, num_die: int):
        super().__init__(name, num_die)
        self.max_roll_value = num_die + 1
        self.roll_probabilities = [
            0,
            *self.roll_probabilities[1:],
            self.roll_probabilities[0]
        ]

    @overrides
    def get_max_roll_value(self) -> int:
        return self.max_roll_value

    @overrides
    def roll_value(self) -> int:
        value = super().roll_value()
        return self.max_roll_value if value == 0 else value

    @overrides
    def generate_roll(self, value: int) -> Roll:
        if value <= 0 or value > self.max_roll_value:
            raise ValueError(f"This dice cannot roll {value}");

        return Roll(value)


class DiceType(Enum):
    """
    The type of dice to use in a game.
    """

    FOUR_BINARY = (1, "FourBinary", lambda: BinaryDice("FourBinary", 4))
    """
    The standard board shape.
    """

    THREE_BINARY_0MAX = (2, "ThreeBinary0Max", lambda: BinaryDice0AsMax("ThreeBinary0Max", 3))
    """
    The Aseb board shape.
    """

    def __init__(self, value: int, name: str, create_dice: callable[[], Dice]):
        self._value_ = value
        self.name = name
        self.create_dice = create_dice
