import math

WIDTH = 1280
HEIGHT = 720

TRACK_CANVAS_WIDTH = math.floor(WIDTH * 0.98)
TRACK_CANVAS_HEIGHT = math.floor(HEIGHT * 0.84)

FPS = 60

DEFAULT_FONT = "comicsansms"

TRACKS_PER_PAGE = 12
TRACKS_SCROLL_OFFSET = 0
TRACKS_SCROLL_SPEED = 120

CHECKPOINTS_PER_PAGE = 28
CHECKPOINTS_SCROLL_OFFSET = 0
CHECKPOINTS_SCROLL_SPEED = 80

BACKGROUND_FOLDER = "assets/backgrounds"
CARS_FOLDER = "assets/cars"
MAPS_FOLDER = "assets/maps"
MARKERS_FOLDER = "assets/markers"
TRACKS_FOLDER = "assets/tracks"

CHECKPOINT_FOLDER = "checkpoints"
CHECKPOINT_INTERVAL = 1
CHECKPOINT_MAX_HISTORY = 100

DATA_FILE = "simulation_data.json"
