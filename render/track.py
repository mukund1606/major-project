import os
from PIL import Image
import pygame

from utils import calculate_track_length, load_csv

from constants import (
    TRACK_CANVAS_WIDTH,
    TRACK_CANVAS_HEIGHT,
    TRACKS_FOLDER,
    TILEMAP_RATIO,
    TILEMAP_CANVAS_WIDTH,
    TILEMAP_CANVAS_HEIGHT,
)

from data_models import Color


class Track:
    IS_MAP: bool = False
    BORDER_THICKNESS = 2
    TRACK_LENGTH = 0
    FINAL_LINE_POSITION: tuple[float, float, float] = (0, 0, 0)

    def __init__(self, track_name: str) -> None:
        self.track_name = track_name

        # Create the track canvas (WHITE)
        self.AI_SURFACE = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.AI_SURFACE.fill(Color.WHITE)

        # Foreground for map (TODO)
        self.FOREGROUND = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.FOREGROUND.fill(Color.WHITE)

        # Load track if name is provided
        if track_name and track_name != "":
            self.load_track()
        else:
            # Load Empty Track
            self.AI_SURFACE.fill(Color.WHITE)
            self.FOREGROUND.fill(Color.WHITE)

        # Draw border
        self.draw_border()

        self.MAP_TILESET_PATH = "assets/map/tileset.png"
        self.MAP_PATH = "assets/map/map.csv"
        self.ROADS_PATH = "assets/map/roads.csv"

        self.MAP_DATA = load_csv(self.MAP_PATH)
        self.ROADS_DATA = load_csv(self.ROADS_PATH)

    def load_track(self) -> None:
        self.TRACK_LENGTH = 0
        if not self.IS_MAP:
            # Create white background surface
            self.AI_SURFACE = pygame.Surface(
                (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
            )
            self.AI_SURFACE.fill(Color.WHITE)

            # Load the track image
            track_path = os.path.join(TRACKS_FOLDER, f"{self.track_name}.png")
            img = Image.open(track_path)
            rgb_img = img.convert("RGB")
            track_image = pygame.image.fromstring(
                rgb_img.tobytes(), rgb_img.size, "RGB"
            )

            # Calculate the size to match either width or height while maintaining aspect ratio
            track_width, track_height = track_image.get_size()
            width_ratio = TRACK_CANVAS_WIDTH / track_width
            height_ratio = TRACK_CANVAS_HEIGHT / track_height

            # Use the smaller ratio to ensure track fits in canvas
            scale_factor = min(width_ratio, height_ratio)
            new_width = int(track_width * scale_factor)
            new_height = int(track_height * scale_factor)

            # Scale the track image
            scaled_track = pygame.transform.scale(track_image, (new_width, new_height))

            # Calculate center position
            x = (TRACK_CANVAS_WIDTH - new_width) // 2
            y = (TRACK_CANVAS_HEIGHT - new_height) // 2

            # Blit the scaled track onto the white surface
            self.AI_SURFACE.blit(scaled_track, (x, y))

            self.TRACK_LENGTH = calculate_track_length(img)
            self.draw_border()
        else:
            self.set_foreground()
            self.draw_border()

    def draw_border(self) -> None:
        pygame.draw.rect(
            self.AI_SURFACE,
            Color.BLACK,
            self.AI_SURFACE.get_rect(),
            self.BORDER_THICKNESS,
        )
        pygame.draw.rect(
            self.FOREGROUND,
            Color.BLACK,
            self.FOREGROUND.get_rect(),
            self.BORDER_THICKNESS,
        )

    # Only used for map
    def set_foreground(self) -> None:
        # First load the tilemap with decorative tiles
        tileset = self.load_tileset(self.MAP_TILESET_PATH)
        self.load_tilemap(tileset)

        # Then load the roads for AI navigation
        self.load_roads()

    def load_tileset(self, path: str) -> pygame.Surface:
        tileset = pygame.image.load(path).convert_alpha()
        tileset = pygame.transform.scale_by(tileset, TILEMAP_RATIO)
        return tileset

    def load_tilemap(self, tileset: pygame.Surface) -> None:
        # Get tileset dimensions
        tile_width = tileset.get_width() // 11  # 11 columns in tileset
        tile_height = tileset.get_height() // 20  # 20 rows in tileset

        # Clear the foreground surface
        self.FOREGROUND.fill(Color.WHITE)

        # Draw each tile according to the MAP_DATA
        for y, row in enumerate(self.MAP_DATA):
            for x, tile_id in enumerate(row):
                if tile_id == "":  # Skip empty cells
                    continue
                    print(f"Error with tile at {x},{y}: {tile_id_str} - {e}")
                # Convert to integer and subtract 1 (CSV data starts from 1)
                tile_id = int(tile_id) - 1

                # Calculate position in tileset
                # For an 11x20 tileset, we need to convert the linear index to x,y coordinates
                tile_x = tile_id % 11  # 11 tiles per row
                tile_y = tile_id // 11

                # Create a rect for the source tile
                tile_rect = pygame.Rect(
                    tile_x * tile_width, tile_y * tile_height, tile_width, tile_height
                )

                # Calculate destination position
                dest_x = x * tile_width
                dest_y = y * tile_height

                # Draw the tile on the foreground
                self.FOREGROUND.blit(tileset, (dest_x, dest_y), tile_rect)

    def load_roads(self) -> None:
        # Roads data is in self.ROADS_DATA 0 for white 1 for black
        BOX_SIZE = 80 * TILEMAP_RATIO

        # Create a new surface for AI track with transparent background
        self.AI_SURFACE = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.AI_SURFACE.fill(Color.WHITE)  # Fill with white background

        # Process road data and draw on AI_SURFACE
        for y, row in enumerate(self.ROADS_DATA):
            for x, road in enumerate(row):
                if road == "":  # Skip empty cells
                    continue

                # Calculate position
                dest_x = x * BOX_SIZE
                dest_y = y * BOX_SIZE

                # Convert road value to int (0 for white, 1 for black)
                try:
                    road_value = int(road)
                    # Create road rectangle
                    road_rect = pygame.Rect(dest_x, dest_y, BOX_SIZE, BOX_SIZE)

                    # Draw appropriate color based on road value
                    if road_value == 1:
                        # Black for actual roads
                        pygame.draw.rect(self.AI_SURFACE, Color.BLACK, road_rect)
                    else:
                        # White or transparent for non-road areas
                        pygame.draw.rect(self.AI_SURFACE, Color.WHITE, road_rect)
                except ValueError:
                    print(f"Invalid road data at {x},{y}: {road}")

        # Convert AI_SURFACE to PIL Image to get the TRACK_LENGTH
        surface_string = pygame.image.tostring(self.AI_SURFACE, "RGB")
        surface_size = self.AI_SURFACE.get_size()
        pil_image = Image.frombytes("RGB", surface_size, surface_string)

        # Calculate the track length using the same function used for regular tracks
        self.TRACK_LENGTH = calculate_track_length(pil_image)
        print(f"Track length calculated: {self.TRACK_LENGTH}")

        # Redraw the border after filling in road data
        self.draw_border()

    # AI Ke liye
    def get_ai_track(self) -> pygame.Surface:
        return self.AI_SURFACE

    # Screen Pe draw kar diya
    def draw(
        self, screen: pygame.Surface, position: tuple[int, int] | pygame.Rect
    ) -> None:
        if not self.IS_MAP:
            screen.blit(self.AI_SURFACE, position)
        else:
            screen.blit(self.FOREGROUND, position)
            # # TODO: Remove this after testing
            # screen.blit(self.AI_SURFACE, position)
