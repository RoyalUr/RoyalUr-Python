from .settings import GameSettings


class GameMetadata:
    # TODO

    @staticmethod
    def create_for_new_game(settings: GameSettings) -> 'GameMetadata':
        return GameMetadata()
