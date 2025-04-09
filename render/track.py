import os
from PIL import Image
import pygame

from utils import calculate_track_length

from constants import (
    TRACK_CANVAS_WIDTH,
    TRACK_CANVAS_HEIGHT,
    TRACKS_FOLDER,
    MAPS_FOLDER,
)

from data_models import Color


class Track:
    IS_MAP = False
    BORDER_THICKNESS = 2
    TRACK_LENGTH = 0
    FINAL_LINE_POSITION: tuple[float, float, float] = (0, 0, 0)

    def __init__(self, track_name: str, is_map: bool = False) -> None:
        self.IS_MAP = is_map
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

    # Only used for map
    def set_foreground(self):  # TODO: Implement This
        pass

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
