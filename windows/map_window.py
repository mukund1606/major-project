import math
import pygame

from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    DEFAULT_FONT,
    TRACK_CANVAS_WIDTH,
    TRACK_CANVAS_HEIGHT,
    TILEMAP_RATIO,
)
from data_models import AvailableSteps, Color
from render.button import Button
from utils import quit_event

from render.game_state import GameState


class MapWindow:
    EXIT_LOOP = False
    TITLE = "Map"

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state
        # Create white background
        BACKGROUND = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        BACKGROUND.fill(Color.WHITE)
        self.BACKGROUND = BACKGROUND

        self.HEADING_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.05))
        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

        self.BORDER_THICKNESS = 2

        BACK_BUTTON_WIDTH = math.floor(WIDTH * 0.1)
        BACK_BUTTON_HEIGHT = math.floor(HEIGHT * 0.075)
        BACK_BUTTON = Button(
            WIDTH - BACK_BUTTON_WIDTH - 2,
            2,
            BACK_BUTTON_WIDTH,
            BACK_BUTTON_HEIGHT,
            "Back",
            math.floor(BACK_BUTTON_HEIGHT * 0.4),
            Color.WHITE,
        )

        self.buttons = [BACK_BUTTON]

        # Setup track canvas position and store in GameState
        CANVAS_CENTER_X = int(WIDTH // 2)
        CANVAS_CENTER_Y = int(TRACK_CANVAS_HEIGHT // 2 + HEIGHT * 0.2)
        track_canvas_rect = pygame.Rect(0, 0, TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT)
        track_canvas_rect.center = (CANVAS_CENTER_X, CANVAS_CENTER_Y)
        self.GAME_STATE.TRACK_CANVAS_RECT = track_canvas_rect

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.BACKGROUND, (0, 0))
        title_surface = self.HEADING_FONT.render(self.TITLE, True, Color.BLACK)
        TITLE_X = WIDTH // 2
        TITLE_Y = HEIGHT * 0.05
        title_rect = title_surface.get_rect(center=(TITLE_X, TITLE_Y))
        screen.blit(title_surface, title_rect)

        instructions = [
            "Press Enter to Select Generation",
            f"Press G to Toggle Grid (Currently: {'On' if self.GAME_STATE.TRACK.SHOW_GRID else 'Off'})",
            f"Press O to Toggle Overlay (Currently: {'On' if self.GAME_STATE.TRACK.SHOW_OVERLAY else 'Off'})",
        ]
        line_spacing = self.FONT.get_linesize()
        start_y = HEIGHT * 0.1

        for i, instruction in enumerate(instructions):
            instruction_surface = self.FONT.render(instruction, True, Color.BLACK)
            instruction_rect = instruction_surface.get_rect(
                center=(WIDTH // 2, start_y + (i * line_spacing))
            )
            screen.blit(instruction_surface, instruction_rect)

        self.GAME_STATE.TRACK.draw(screen, self.GAME_STATE.TRACK_CANVAS_RECT)

        for button in self.buttons:
            button.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.GAME_STATE.set_state(AvailableSteps.SELECT_GENERATION)
                self.EXIT_LOOP = True
            if event.key == pygame.K_g:
                self.GAME_STATE.TRACK.toggle_grid()
            if event.key == pygame.K_o:
                self.GAME_STATE.TRACK.toggle_overlay()

        for button in self.buttons:
            if button.handle_event(event):
                if button.text == "Back":
                    self.GAME_STATE.set_previous_state()
                    self.EXIT_LOOP = True

    def run(self) -> None:
        self.EXIT_LOOP = False

        self.GAME_STATE.TRACK.load_track()
        self.GAME_STATE.TRACK.track_name = "Map"

        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                # Handle events
                quit_event(event)
                self.handle_event(event)

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
