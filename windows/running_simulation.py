import math
import os
import pygame

from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    DEFAULT_FONT,
    TRACKS_FOLDER,
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

        self.LAST_POSITION: tuple[int, int] | None = None
        self.BORDER_THICKNESS = 2

        self.TRACK_CANVAS = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.TRACK_CANVAS.fill(Color.WHITE)

        CANVAS_CENTER_X = WIDTH // 2
        CANVAS_CENTER_Y = TRACK_CANVAS_HEIGHT // 2 + HEIGHT * 0.2
        self.TRACK_CANVAS_RECT = self.TRACK_CANVAS.get_rect(
            center=(CANVAS_CENTER_X, CANVAS_CENTER_Y)
        )
        pygame.draw.rect(
            self.TRACK_CANVAS,
            Color.BLACK,
            self.TRACK_CANVAS.get_rect(),
            self.BORDER_THICKNESS,
        )

    def load_track_canvas(self) -> None:
        TRACK_IMAGE_PATH = os.path.join(
            TRACKS_FOLDER, f"{self.GAME_STATE.TRACK_NAME}.png"
        )
        track_image = pygame.image.load(TRACK_IMAGE_PATH).convert_alpha()
        self.TRACK_CANVAS = pygame.transform.scale(
            track_image, (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT)
        )
        pygame.draw.rect(
            self.TRACK_CANVAS,
            Color.BLACK,
            self.TRACK_CANVAS.get_rect(),
            self.BORDER_THICKNESS,
        )

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
        screen.blit(self.TRACK_CANVAS, self.TRACK_CANVAS_RECT)

    def handle_event(self, event: pygame.event.Event) -> None:
        # TODO: Implement this
        pass

    def run(self) -> None:
        self.EXIT_LOOP = False
        self.load_track_canvas()

        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                # Handle events
                quit_event(event)
                self.handle_event(event)

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
