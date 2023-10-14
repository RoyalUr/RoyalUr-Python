from abc import ABC


class PieceProvider(ABC):
    """
    An interface that provides instances of pieces. This may be used
    to store custom information with each piece, for situations such
    as adding stacking or unique piece behavior.
    """
    pass


class PlayerStateProvider(ABC):
    """
    An interface that provides the manipulation of PlayerStates as a game progresses.
    """
    pass


class RuleSet(ABC):
    """
    A set of rules that govern the play of a game of the Royal Game of Ur.
    """
    pass


class RuleSetProvider(ABC):
    """
    Creates rule sets to match game settings.
    """
    pass
