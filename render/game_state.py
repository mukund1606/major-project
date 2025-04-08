import os
import pygame

from constants import WIDTH, HEIGHT, CHECKPOINT_DIR
from data_models import AvailableSteps, History, CarPreviewData


class GameState:
    HISTORY: list[History] = []
    PREVIOUS_STATES: list[AvailableSteps] = []
    CURRENT_STATE: AvailableSteps = AvailableSteps.MAIN_MENU
    CAR_PREVIEW_DATA = CarPreviewData(
        car_scale=1.0,
        car_rotation=0.0,
        car_scale_speed=0.1,
        car_rotation_speed=5,
        car_final_scale=1.0,
        car_final_rotation=0.0,
    )
    PREVIEW_SURFACE = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    def __init__(
        self, neat_config_path: str, debug: bool, max_simulations: int
    ) -> None:
        self.neat_config_path = neat_config_path
        self.debug = debug
        self.max_simulations = max_simulations
        self.title = "AI Car Simulation"
        self.MOUSE_UP = False

        if not os.path.exists(CHECKPOINT_DIR):
            os.makedirs(CHECKPOINT_DIR)

        pygame.init()
        pygame.display.set_caption(self.title)
        self.SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
        self.CLOCK = pygame.time.Clock()

    def set_state(self, state: AvailableSteps) -> None:
        self.PREVIOUS_STATES.append(self.CURRENT_STATE)
        self.CURRENT_STATE = state

    def set_previous_state(self) -> None:
        if len(self.PREVIOUS_STATES) > 0:
            prev = self.PREVIOUS_STATES.pop()
            print(prev)
            self.CURRENT_STATE = prev
