import os
import sys
import pygame

from data_models import AvailableSteps
from render.game_state import GameState
from windows.main_menu import MainMenuWindow
from windows.train_ai import TrainAIWindow


class GameEngine:

    def __init__(
        self, neat_config_path: str, debug: bool, max_simulations: int
    ) -> None:
        self.game_state = GameState(neat_config_path, debug, max_simulations)
        self.MAIN_WINDOW = MainMenuWindow(self.game_state)
        self.TRAIN_AI_WINDOW = TrainAIWindow(self.game_state)

    def run(self) -> None:
        while True:
            print(self.game_state.CURRENT_STATE)
            if self.game_state.CURRENT_STATE == AvailableSteps.EXIT:
                pygame.quit()
                sys.exit(0)
            elif self.game_state.CURRENT_STATE == AvailableSteps.MAIN_MENU:
                self.MAIN_WINDOW.run()
            elif self.game_state.CURRENT_STATE == AvailableSteps.TRAIN_AI:
                self.TRAIN_AI_WINDOW.run()
