import pygame
from constants import DEFAULT_FONT
from data_models import Color


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font_size: int,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont(DEFAULT_FONT, font_size)
        self.is_hovered = False

    def draw(self, screen: pygame.Surface) -> None:
        if self.color is not None:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
            pygame.draw.rect(screen, (100, 100, 100), self.rect, 2, border_radius=5)

        text_surface = self.font.render(self.text, True, Color.BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False
