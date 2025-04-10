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
from windows.place_car import PlaceCarWindow
from windows.place_destination_marker import PlaceDestinationMarkerWindow
from windows.running_simulation import RunningSimulationWindow
from windows.select_generation import SelectGenerationWindow
from windows.map_window import MapWindow


class GameEngine:

    def __init__(
        self, neat_config_path: str, debug: bool, max_simulations: int
    ) -> None:
        self.GAME_STATE = GameState(neat_config_path, debug, max_simulations)
        self.MAIN_WINDOW = MainMenuWindow(self.GAME_STATE)
        self.TRAIN_AI_WINDOW = TrainAIWindow(self.GAME_STATE)
        self.TRACK_NAME_WINDOW = TrackNameWindow(self.GAME_STATE, self.TRAIN_AI_WINDOW)
        self.DRAW_TRACK_WINDOW = DrawTrackWindow(self.GAME_STATE)
        self.SELECT_TRACK_WINDOW = SelectTrackWindow(self.GAME_STATE)
        self.SIMULATE_AI_WINDOW = SimulateAIWindow(self.GAME_STATE)
        self.SELECT_GENERATION_WINDOW = SelectGenerationWindow(self.GAME_STATE)
        self.PLACE_CAR_WINDOW = PlaceCarWindow(self.GAME_STATE)
        self.PLACE_DESTINATION_MARKER_WINDOW = PlaceDestinationMarkerWindow(
            self.GAME_STATE
        )
        self.RUNNING_SIMULATION_WINDOW = RunningSimulationWindow(self.GAME_STATE)
        self.MAP_WINDOW = MapWindow(self.GAME_STATE)

    def run(self) -> None:
        while True:
            if self.GAME_STATE.CURRENT_STATE == AvailableSteps.EXIT:
                pygame.quit()
                sys.exit(0)
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.MAIN_MENU:
                pygame.display.set_caption("AI Car Simulation - Main Menu")
                self.MAIN_WINDOW.run()
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.TRAIN_AI:
                pygame.display.set_caption("AI Car Simulation - Train AI")
                self.GAME_STATE.IS_TRAINING_MODE = True
                self.TRAIN_AI_WINDOW.run()
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.SIMULATE_AI:
                pygame.display.set_caption("AI Car Simulation - Simulate AI")
                self.GAME_STATE.IS_TRAINING_MODE = False
                self.SIMULATE_AI_WINDOW.run()
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.ENTER_TRACK_NAME:
                pygame.display.set_caption("AI Car Simulation - Enter Track Name")
                self.TRACK_NAME_WINDOW.run()
                pygame.display.set_caption("AI Car Simulation - Draw Track")
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.DRAW_TRACK:
                self.DRAW_TRACK_WINDOW.run()
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.SELECT_TRACK:
                pygame.display.set_caption("AI Car Simulation - Select Track")
                self.SELECT_TRACK_WINDOW.run()
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.MAP:
                pygame.display.set_caption("AI Car Simulation - Map")
                self.GAME_STATE.TRACK.IS_MAP = True
                self.MAP_WINDOW.run()
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.SELECT_GENERATION:
                pygame.display.set_caption("AI Car Simulation - Select Generation")
                self.SELECT_GENERATION_WINDOW.run()
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.PLACE_CAR:
                pygame.display.set_caption("AI Car Simulation - Place Car")
                self.PLACE_CAR_WINDOW.run()
            elif (
                self.GAME_STATE.CURRENT_STATE == AvailableSteps.PLACE_DESTINATION_MARKER
            ):
                pygame.display.set_caption(
                    "AI Car Simulation - Place Destination Marker"
                )
                self.PLACE_DESTINATION_MARKER_WINDOW.run()
            elif self.GAME_STATE.CURRENT_STATE == AvailableSteps.START_SIMULATION:
                pygame.display.set_caption("AI Car Simulation - Running Simulation")
                self.RUNNING_SIMULATION_WINDOW.run()
