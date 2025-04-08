import os
import pygame

from constants import (
    TRACK_CANVAS_WIDTH,
    TRACK_CANVAS_HEIGHT,
    TRACKS_FOLDER,
)
from data_models import Color


class Track:
    def __init__(self, track_name: str, border_thickness: int = 2) -> None:
        self.track_name = track_name
        self.border_thickness = border_thickness

        # Create the track canvas
        self.surface = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.surface.fill(Color.WHITE)

        # Load track if name is provided
        if track_name:
            self.load_track()

        # Draw border
        self.draw_border()

    def load_track(self) -> None:
        """Load and scale the track image."""
        track_path = os.path.join(TRACKS_FOLDER, f"{self.track_name}.png")
        track_image = pygame.image.load(track_path).convert_alpha()
        self.surface = pygame.transform.scale(
            track_image, (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT)
        )
        self.draw_border()

    def draw_border(self) -> None:
        """Draw border around the track."""
        pygame.draw.rect(
            self.surface,
            Color.BLACK,
            self.surface.get_rect(),
            self.border_thickness,
        )

    def get_rect(self, **kwargs) -> pygame.Rect:
        """Get the track's rect with optional positioning arguments."""
        return self.surface.get_rect(**kwargs)

    def draw(
        self, screen: pygame.Surface, position: tuple[int, int] | pygame.Rect
    ) -> None:
        """Draw the track on the screen at the specified position."""
        if isinstance(position, tuple):
            screen.blit(self.surface, position)
        else:
            screen.blit(self.surface, position)
