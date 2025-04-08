import pygame
import sys

from data_models import AvailableSteps

from render.game_state import GameState

from windows.main_menu import MainMenuWindow
from windows.train_ai import TrainAIWindow
from windows.simulate_ai import SimulateAIWindow
from windows.track_name import TrackNameWindow
from windows.select_track import SelectTrackWindow
from windows.draw_track import DrawTrackWindow


class GameEngine:

    def __init__(
        self, neat_config_path: str, debug: bool, max_simulations: int
    ) -> None:
        self.game_state = GameState(neat_config_path, debug, max_simulations)
        self.MAIN_WINDOW = MainMenuWindow(self.game_state)
        self.TRAIN_AI_WINDOW = TrainAIWindow(self.game_state)
        self.TRACK_NAME_WINDOW = TrackNameWindow(self.game_state, self.TRAIN_AI_WINDOW)
        self.DRAW_TRACK_WINDOW = DrawTrackWindow(self.game_state)
        self.SELECT_TRACK_WINDOW = SelectTrackWindow(self.game_state)
        self.SIMULATE_AI_WINDOW = SimulateAIWindow(self.game_state)

    def run(self) -> None:
        while True:
            if self.game_state.CURRENT_STATE == AvailableSteps.EXIT:
                pygame.quit()
                sys.exit(0)
            elif self.game_state.CURRENT_STATE == AvailableSteps.MAIN_MENU:
                pygame.display.set_caption("AI Car Simulation - Main Menu")
                self.MAIN_WINDOW.run()
            elif self.game_state.CURRENT_STATE == AvailableSteps.TRAIN_AI:
                pygame.display.set_caption("AI Car Simulation - Train AI")
                self.game_state.IS_TRAINING_MODE = True
                self.TRAIN_AI_WINDOW.run()
            elif self.game_state.CURRENT_STATE == AvailableSteps.ENTER_TRACK_NAME:
                pygame.display.set_caption("AI Car Simulation - Enter Track Name")
                self.TRACK_NAME_WINDOW.run()
                pygame.display.set_caption("AI Car Simulation - Draw Track")
            elif self.game_state.CURRENT_STATE == AvailableSteps.DRAW_TRACK:
                self.DRAW_TRACK_WINDOW.run()
            elif self.game_state.CURRENT_STATE == AvailableSteps.SELECT_TRACK:
                pygame.display.set_caption("AI Car Simulation - Select Track")
                self.SELECT_TRACK_WINDOW.run()
            elif self.game_state.CURRENT_STATE == AvailableSteps.SIMULATE_AI:
                pygame.display.set_caption("AI Car Simulation - Simulate AI")
                self.game_state.IS_TRAINING_MODE = False
                self.SIMULATE_AI_WINDOW.run()
