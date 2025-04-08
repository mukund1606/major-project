import pygame
import sys


def quit_event(event: pygame.event.Event) -> None:
    if event.type == pygame.QUIT or (
        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
    ):
        pygame.quit()
        sys.exit(0)
