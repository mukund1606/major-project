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
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)

    def draw(self, screen: pygame.Surface) -> None:
        self.surface.fill((0, 0, 0, 0))

        if self.color is not None:
            color_with_alpha = (
                self.color if isinstance(self.color, tuple) else tuple(self.color)
            )
            if len(color_with_alpha) == 3:
                draw_color = color_with_alpha
            else:
                draw_color = color_with_alpha[:3]  # Take only RGB components

            alpha = 255 if not self.is_hovered else 191

            pygame.draw.rect(
                self.surface,
                draw_color,
                self.surface.get_rect(),
                border_radius=5,
            )

            self.surface.set_alpha(alpha)

            pygame.draw.rect(
                self.surface,
                (100, 100, 100),
                self.surface.get_rect(),
                2,
                border_radius=5,
            )

            screen.blit(self.surface, self.rect)

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
