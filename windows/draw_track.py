import math
import os
import pygame
from PIL import Image

from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    DEFAULT_FONT,
    TRACKS_FOLDER,
    TRACK_CANVAS_WIDTH,
    TRACK_CANVAS_HEIGHT,
)
from data_models import AvailableSteps, Color
from render.button import Button
from utils import quit_event

from render.game_state import GameState


class DrawTrackWindow:
    EXIT_LOOP = False
    TITLE = "Draw Track"

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state
        # Create white background
        self.BACKGROUND = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.BACKGROUND.fill(Color.WHITE)

        self.HEADING_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.05))
        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

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

        # Empty Rectangle with black border to give space to draw track
        self.TRACK_CANVAS = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.TRACK_CANVAS.fill(Color.WHITE)
        CANVAS_CENTER_X = WIDTH // 2
        CANVAS_CENTER_Y = TRACK_CANVAS_HEIGHT // 2 + HEIGHT * 0.16
        self.TRACK_CANVAS_RECT = self.TRACK_CANVAS.get_rect(
            center=(CANVAS_CENTER_X, CANVAS_CENTER_Y)
        )
        pygame.draw.rect(
            self.TRACK_CANVAS,
            Color.BLACK,
            self.TRACK_CANVAS.get_rect(),
            2,
        )

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.BACKGROUND, (0, 0))

        title_surface = self.HEADING_FONT.render(self.TITLE, True, Color.BLACK)
        TITLE_X = WIDTH // 2
        TITLE_Y = HEIGHT * 0.05
        title_rect = title_surface.get_rect(center=(TITLE_X, TITLE_Y))
        screen.blit(title_surface, title_rect)

        instructions = [
            "Left Click to Draw, Right Click to Erase",
            "Press Enter to Save",
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

        for button in self.buttons:
            button.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Save Track Canvas
                data = pygame.image.tostring(self.TRACK_CANVAS, "RGB")
                img = Image.frombytes("RGB", self.TRACK_CANVAS.get_size(), data)
                path = os.path.join(TRACKS_FOLDER, f"{self.GAME_STATE.TRACK_NAME}.png")
                print(path)
                img.save(path)
                self.GAME_STATE.set_state(AvailableSteps.SELECT_TRACK)
                self.EXIT_LOOP = True

        for button in self.buttons:
            if button.handle_event(event):
                if button.text == "Back":
                    self.GAME_STATE.set_previous_state()
                    self.EXIT_LOOP = True

    def check_track_name(self) -> bool:
        if len(self.INPUT_TEXT) == 0:
            self.INPUT_TEXT_ERROR = "Track name cannot be empty"
            return False
        available_file_types = ["png", "jpg", "jpeg"]
        for file_type in available_file_types:
            if os.path.exists(
                os.path.join(TRACKS_FOLDER, f"{self.INPUT_TEXT}.{file_type}")
            ):
                self.INPUT_TEXT_ERROR = "Track name already exists"
                return False
        return True

    def run(self) -> None:
        self.EXIT_LOOP = False
        self.INPUT_TEXT_ERROR = ""
        self.INPUT_TEXT = ""
        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                # Handle events
                quit_event(event)
                self.handle_event(event)

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
