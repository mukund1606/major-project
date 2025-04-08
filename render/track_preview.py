import math
import pygame

from constants import DEFAULT_FONT, HEIGHT
from data_models import Color


class TrackPreview:

    def __init__(
        self, x: int, y: int, width: int, height: int, track_name: str, track_path: str
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.track_name = track_name
        self.track_path = track_path
        self.y_offset = 0

        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

        self.preview_image = pygame.image.load(track_path).convert_alpha()
        self.preview_image = pygame.transform.scale(self.preview_image, (width, height))

    def draw(self, screen: pygame.Surface) -> None:
        # Update rect position with scroll offset
        self.rect.y = self.y + self.y_offset

        screen.blit(self.preview_image, self.rect)
        pygame.draw.rect(screen, Color.BLACK, self.rect, 2)

        text_surface = self.FONT.render(self.track_name, True, Color.BLACK)
        text_rect = text_surface.get_rect(
            center=(self.rect.centerx, self.rect.bottom + math.floor(HEIGHT * 0.02))
        )
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Update collision detection to use scrolled position
            mouse_pos = event.pos
            if self.rect.collidepoint(mouse_pos):
                return True
        return False
