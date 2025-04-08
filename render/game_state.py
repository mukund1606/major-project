import os
import pygame

from constants import WIDTH, HEIGHT, CHECKPOINT_FOLDER
from data_models import (
    AvailableSteps,
    History,
    CarPreviewData,
    CheckpointPreviewData,
    FinalMarkerPreviewData,
)


class GameState:
    PREVIOUS_STATES: list[AvailableSteps] = []
    CURRENT_STATE: AvailableSteps = AvailableSteps.MAIN_MENU
    HISTORY: list[History] = []
    CAR_PREVIEW_DATA = CarPreviewData(
        size=40,
        rotation=0,
        position=(0, 0),
    )
    CHECKPOINTS_PREVIEW_DATA: list[CheckpointPreviewData] = []
    FINAL_MARKER_PREVIEW_DATA = FinalMarkerPreviewData(
        size=40,
        position=(0, 0),
    )
    SELECTED_TRACK_PATH: str | None = None
    IS_TRAINING_MODE: bool = True
    TRACK_NAME: str = ""
    CURRENT_GENERATION: int = 0
    BEST_FITNESS: float = 0.0
    ALIVE_CARS: int = 0

    def __init__(
        self, neat_config_path: str, debug: bool, max_simulations: int
    ) -> None:
        self.neat_config_path = neat_config_path
        self.debug = debug
        self.max_simulations = max_simulations
        self.title = "AI Car Simulation"
        self.MOUSE_UP = False

        if not os.path.exists(CHECKPOINT_FOLDER):
            os.makedirs(CHECKPOINT_FOLDER)

        pygame.init()
        pygame.display.set_caption(self.title)
        self.SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
        self.CLOCK = pygame.time.Clock()

    def set_state(self, state: AvailableSteps) -> None:
        self.PREVIOUS_STATES.append(self.CURRENT_STATE)
        self.CURRENT_STATE = state

    def set_previous_state(self, steps: int = 1) -> None:
        if len(self.PREVIOUS_STATES) > steps - 1:
            for _ in range(steps):
                prev = self.PREVIOUS_STATES.pop()
            self.CURRENT_STATE = prev
        else:
            self.CURRENT_STATE = AvailableSteps.MAIN_MENU

    def get_previous_state(self) -> AvailableSteps:
        if len(self.PREVIOUS_STATES) > 0:
            return self.PREVIOUS_STATES[-1]
        else:
            return AvailableSteps.MAIN_MENU
