from render.game_engine import GameEngine


class TrackNameWindow:
    TRACK_NAME = ""
    TRACK_NAME_ERROR = ""

    def __init__(self, game_engine: GameEngine) -> None:
        self.game_engine = game_engine

    def run(self) -> None:
        pass
