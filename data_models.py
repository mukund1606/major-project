from enum import Enum
from pydantic import BaseModel
from pygame.color import Color as PygameColor


class CarPathHistory(BaseModel):
    path: list[tuple[float, float]]
    fitness: float


class History(BaseModel):
    generation: int
    num_crashes: int
    max_num_checkpoints: int
    max_fitness: float
    avg_fitness: float
    car_path_history: list[CarPathHistory]


class Color(PygameColor):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    BLUE = (0, 0, 255)
    DARK_RED = (100, 0, 0)
    RED_PALE = (250, 200, 200)
    DARK_RED_PALE = (150, 100, 100)
    GREEN = (0, 200, 0)
    DARK_GREEN = (0, 100, 0)
    GREEN_PALE = (200, 250, 200)
    DARK_GREEN_PALE = (100, 150, 100)
    BLUE = (0, 0, 255)
    BLUE_PALE = (200, 200, 255)
    DARK_BLUE = (100, 100, 150)
    GRAY = (128, 128, 128)


class AvailableSteps(Enum):
    MAIN_MENU = "main_menu"  # Done

    TRAIN_AI = "train_ai"  # Done
    ENTER_TRACK_NAME = "enter_track_name"  # Done
    DRAW_TRACK = "draw_track"  # Done

    SELECT_TRACK = "select_track"  # Done
    MAP = "map"  # Done

    SIMULATE_AI = "simulate_ai"  # Done

    PLACE_CAR = "place_car"  # Done
    # PLACE_CHECKPOINTS = "place_checkpoints"  # TODO (Maybe)
    PLACE_DESTINATION_MARKER = "place_destination_point"  # Done

    SELECT_GENERATION = "select_generation"  # Done

    START_SIMULATION = "start_simulation"  # Done

    EXIT = "exit"  # Done


class CarPreviewData(BaseModel):
    size: float
    rotation: float
    position: tuple[int, int]


class CheckpointPreviewData(BaseModel):
    size: float
    position: tuple[int, int]


class FinalMarkerPreviewData(BaseModel):
    size: float
    position: tuple[int, int]
