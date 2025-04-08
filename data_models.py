from enum import Enum
from pydantic import BaseModel


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


class Color:
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
    DRAW_TRACK = "draw_track"  # TODO

    SELECT_TRACK = "select_track"  # Done
    SELECT_MAP = "select_map"  # TODO

    SIMULATE_AI = "simulate_ai"  # Done

    PLACE_CAR = "place_car"
    PLACE_CHECKPOINTS = "place_checkpoints"
    PLACE_DESTINATION_POINT = "place_destination_point"

    SELECT_GENERATION = "select_generation"

    START_SIMULATION = "start_simulation"

    EXIT = "exit"


class CarPreviewData(BaseModel):
    car_scale: float
    car_rotation: float
    car_scale_speed: float
    car_rotation_speed: float
    car_final_scale: float
    car_final_rotation: float
