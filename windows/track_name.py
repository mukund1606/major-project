import math
import os
import pygame

from constants import WIDTH, HEIGHT, FPS, DEFAULT_FONT, TRACKS_FOLDER
from data_models import AvailableSteps, Color
from utils import quit_event

from render.game_state import GameState

from windows.train_ai import TrainAIWindow


class TrackNameWindow:
    EXIT_LOOP = False
    TITLE = "Enter Track Name"
    INPUT_TEXT = ""
    INPUT_TEXT_ERROR = ""
    RECTANGLE_WIDTH = math.floor(WIDTH * 0.4)
    RECTANGLE_HEIGHT = math.floor(HEIGHT * 0.4)

    def __init__(self, game_state: GameState, train_ai_window: TrainAIWindow) -> None:
        self.GAME_STATE = game_state
        self.train_ai_window = train_ai_window

        # Create semi-transparent overlay
        self.OVERLAY = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.OVERLAY.fill((0, 0, 0, 128))

        self.HEADING_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.05))
        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

    def draw(self, screen: pygame.Surface) -> None:
        # Draw the train AI window as background
        self.train_ai_window.draw(screen)

        # Draw our semi-transparent overlay
        screen.blit(self.OVERLAY, (0, 0))

        # Draw White Rectangle With Black Border in center of screen width and height of 50 px
        pygame.draw.rect(
            screen,
            Color.WHITE,
            (
                WIDTH // 2 - self.RECTANGLE_WIDTH // 2,
                HEIGHT // 2 - self.RECTANGLE_HEIGHT // 2,
                self.RECTANGLE_WIDTH,
                self.RECTANGLE_HEIGHT,
            ),
            border_radius=10,
        )

        # Draw Title inside the rectangle
        title_surface = self.HEADING_FONT.render(self.TITLE, True, Color.BLACK)
        TITLE_X = WIDTH // 2
        TITLE_Y = HEIGHT // 2 - self.RECTANGLE_HEIGHT // 2 + (HEIGHT * 0.05)
        title_rect = title_surface.get_rect(center=(TITLE_X, TITLE_Y))
        screen.blit(title_surface, title_rect)

        # Track Name Input
        track_name_input_surface = self.HEADING_FONT.render(
            self.INPUT_TEXT + "█", True, Color.BLACK
        )
        TRACK_NAME_INPUT_X = WIDTH // 2
        TRACK_NAME_INPUT_Y = HEIGHT // 2 - self.RECTANGLE_HEIGHT // 2 + (HEIGHT * 0.15)
        track_name_input_rect = track_name_input_surface.get_rect(
            center=(TRACK_NAME_INPUT_X, TRACK_NAME_INPUT_Y)
        )
        screen.blit(track_name_input_surface, track_name_input_rect)

        if self.INPUT_TEXT_ERROR != "":
            error_surface = self.HEADING_FONT.render(
                self.INPUT_TEXT_ERROR, True, Color.RED
            )
            error_rect = error_surface.get_rect(
                center=(
                    WIDTH // 2,
                    HEIGHT // 2 - self.RECTANGLE_HEIGHT // 2 + (HEIGHT * 0.225),
                )
            )
            screen.blit(error_surface, error_rect)

        # Draw instructions as separate lines
        instructions = [
            "Press Enter to continue, ESC to go back",
            "and Backspace to delete",
        ]
        line_spacing = self.FONT.get_linesize()
        start_y = HEIGHT // 2 - self.RECTANGLE_HEIGHT // 2 + (HEIGHT * 0.3)

        for i, instruction in enumerate(instructions):
            instruction_surface = self.FONT.render(instruction, True, Color.BLACK)
            instruction_rect = instruction_surface.get_rect(
                center=(WIDTH // 2, start_y + (i * line_spacing))
            )
            screen.blit(instruction_surface, instruction_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.INPUT_TEXT) > 0:
                    self.INPUT_TEXT = self.INPUT_TEXT[:-1]
                    self.INPUT_TEXT_ERROR = ""
                else:
                    self.INPUT_TEXT_ERROR = "Track name cannot be empty"
            elif event.key == pygame.K_RETURN:
                if self.check_track_name():
                    self.GAME_STATE.INPUT_TEXT = self.INPUT_TEXT
                    self.GAME_STATE.set_state(AvailableSteps.DRAW_TRACK)
                    self.EXIT_LOOP = True
            elif event.key == pygame.K_ESCAPE:
                self.GAME_STATE.set_previous_state()
                self.EXIT_LOOP = True
            elif len(self.INPUT_TEXT) < 25:
                if event.unicode.isalnum() or event.unicode in ["_", "-", " "]:
                    self.INPUT_TEXT += event.unicode
                    self.INPUT_TEXT_ERROR = ""
                else:
                    self.INPUT_TEXT_ERROR = f"Invalid character: {event.unicode}"

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
