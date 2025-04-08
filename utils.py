import pygame
import sys


def quit_event(event: pygame.event.Event) -> None:
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit(0)
