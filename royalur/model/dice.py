import random
from enum import Enum
from abc import ABC, abstractmethod
from overrides import overrides
from typing import Callable


class Roll:
    """
    A roll of the dice.
    """

    __slots__ = ("_value",)

    _value: int

    def __init__(self, value: int):
        self._value = value

    @property
    def value(self) -> int:
        """
        The value of the dice that was rolled.
        """
        return self._value


class Dice(ABC):
    """
    A generator of dice rolls.
    """
    __slots__ = ("_name",)

    _name: str

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        """
        The name of this dice.
        """
        return self._name

    def has_state() -> bool:
        """
        Returns whether this dice holds any state that
        affects its dice rolls. If this is overriden,
        then copy_from should also be overriden.
        """
        return False

    def copy_from(self, other: 'Dice') -> bool:
        """
        Copies the state of the other dice into this dice.
        If the dice does not have state, this is a no-op.
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
        Gets the probability of rolling each value of
        the dice, where the index into the returned
        array represents the value of the roll.
        """
        pass

    @abstractmethod
    def roll_value(self) -> int:
        """
        Generates a random roll using this dice, and
        returns just the value. If this dice has state,
        this should call record_roll.
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

    def roll(self, value: int | None = None) -> Roll:
        """
        Generates a roll using this dice. If no value is
        provided, then the value of the roll will be random.
        """
        if value is None:
            value = self.roll_value()
        else:
            self.record_roll(value)

        return self.generate_roll(value)


class BinaryDice(Dice):
    """
    Rolls a number of binary die and counts the result.
    """
    __slots__ = ("_num_die", "_roll_probabilities")

    _num_die: int
    _roll_probabilities: list[float]

    def __init__(self, name: str, num_die: int):
        super().__init__(name)
        self._num_die = num_die
        self._roll_probabilities = []

        # Binomial Distribution
        baseProb = 0.5 ** num_die
        nChooseK = 1
        for roll in range(0, num_die + 1):
            self._roll_probabilities.append(baseProb * nChooseK)
            nChooseK = nChooseK * (num_die - roll) // (roll + 1)

    @property
    def num_die(self) -> int:
        """
        The number of binary dice to roll.
        """
        return self._num_die

    @overrides
    def get_max_roll_value(self) -> int:
        return self._num_die

    @overrides
    def get_roll_probabilities(self) -> list[float]:
        return self._roll_probabilities

    @overrides
    def roll_value(self) -> int:
        value = 0
        for _ in range(self._num_die):
            # Simulate rolling a single D2 dice.
            if random.random() >= 0.5:
                value += 1

        return value

    @overrides
    def generate_roll(self, value: int) -> Roll:
        if value < 0 or value > self._num_die:
            raise ValueError(f"This dice cannot roll {value}")

        return Roll(value)


class BinaryDice0AsMax(BinaryDice):
    """
    A set of binary dice where a roll of zero actually represents
    the highest roll possible, rather than the lowest.
    """
    __slots__ = ("_max_roll_value",)

    _max_roll_value: int

    def __init__(self, name: str, num_die: int):
        super().__init__(name, num_die)
        self._max_roll_value = num_die + 1
        self._roll_probabilities = [
            0,
            *self._roll_probabilities[1:],
            self._roll_probabilities[0]
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
            raise ValueError(f"This dice cannot roll {value}")

        return Roll(value)


class DiceType(Enum):
    """
    The type of dice to use in a game.
    """

    FOUR_BINARY = (
        1, "FourBinary",
        lambda: BinaryDice("FourBinary", 4)
    )
    """
    The standard board shape.
    """

    THREE_BINARY_0MAX = (
        2, "ThreeBinary0Max",
        lambda: BinaryDice0AsMax("ThreeBinary0Max", 3)
    )
    """
    The Aseb board shape.
    """

    def __init__(
            self,
            value: int,
            text_name: str,
            create_dice: Callable[[], Dice]
    ):
        self._value_ = value
        self._text_name = text_name
        self._create_dice = create_dice

    @property
    def text_name(self) -> str:
        """
        The name of this dice.
        """
        return self._text_name

    @property
    def dice_factory(self) -> Callable[[], Dice]:
        """
        The factory that is used to produce this type of dice.
        """
        return self._create_dice

    def create_dice(self) -> Dice:
        """
        Creates a set of these dice.
        """
        return self._create_dice()
