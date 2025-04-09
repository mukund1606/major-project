import math
import os
import pygame

from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    DEFAULT_FONT,
    TRACK_CANVAS_WIDTH,
    TRACK_CANVAS_HEIGHT,
)

from data_models import Color
from utils import quit_event

from render.game_state import GameState


class RunningSimulationWindow:
    EXIT_LOOP = False
    TITLE = "Running Simulation"

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state
        # Create white background
        BACKGROUND = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        BACKGROUND.fill(Color.WHITE)
        self.BACKGROUND = BACKGROUND

        self.HEADING_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.05))
        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

        self.BORDER_THICKNESS = 2

        # Setup track canvas position
        CANVAS_CENTER_X = int(WIDTH // 2)
        CANVAS_CENTER_Y = int(TRACK_CANVAS_HEIGHT // 2 + HEIGHT * 0.2)
        self.TRACK_CANVAS_RECT = pygame.Rect(
            0, 0, TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT
        )
        self.TRACK_CANVAS_RECT.center = (CANVAS_CENTER_X, CANVAS_CENTER_Y)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.BACKGROUND, (0, 0))
        title_surface = self.HEADING_FONT.render(self.TITLE, True, Color.BLACK)
        TITLE_X = WIDTH // 2
        TITLE_Y = HEIGHT * 0.05
        title_rect = title_surface.get_rect(center=(TITLE_X, TITLE_Y))
        screen.blit(title_surface, title_rect)

        instructions = [
            "Simulation is running...",
            f"Generation: {self.GAME_STATE.CURRENT_GENERATION}, Alive: {self.GAME_STATE.ALIVE_CARS}, Best Fitness: {self.GAME_STATE.BEST_FITNESS}",
        ]
        line_spacing = self.FONT.get_linesize()
        start_y = HEIGHT * 0.1

        for i, instruction in enumerate(instructions):
            instruction_surface = self.FONT.render(instruction, True, Color.BLACK)
            instruction_rect = instruction_surface.get_rect(
                center=(WIDTH // 2, start_y + (i * line_spacing))
            )
            screen.blit(instruction_surface, instruction_rect)

        # Draw Track Canvas
        if self.GAME_STATE.TRACK:
            self.GAME_STATE.TRACK.draw(screen, self.TRACK_CANVAS_RECT)

    def handle_event(self, event: pygame.event.Event) -> None:
        # TODO: Implement this
        pass

    def run(self) -> None:
        self.EXIT_LOOP = False
        self.GAME_STATE.load_track()

        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                # Handle events
                quit_event(event)
                self.handle_event(event)

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
