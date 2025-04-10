import math
import os
import pygame

from data_models import AvailableSteps, Color
from constants import WIDTH, HEIGHT, FPS, DEFAULT_FONT, BACKGROUND_FOLDER
from utils import quit_event

from render.game_state import GameState
from render.button import Button


class TrainAIWindow:
    EXIT_LOOP = False

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state
        BACKGROUND = pygame.image.load(
            os.path.join(BACKGROUND_FOLDER, "train_ai.png")
        ).convert_alpha()
        self.BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT))
        self.BUTTON_WIDTH = math.floor(WIDTH * 0.25)
        self.BUTTON_HEIGHT = math.floor(HEIGHT * 0.1)
        self.X_START = math.floor(WIDTH * 0.65)
        self.Y_START = math.floor(HEIGHT * 0.28)
        self.X_BUTTON_SPACE = math.floor(-1 * WIDTH * 0.052)
        self.Y_BUTTON_SPACE = math.floor(HEIGHT * 0.14)
        self.TITLE_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.08))

        BUTTON_TEXT = ["Create New Track", "Select Track", "Map"]
        self.buttons = [
            Button(
                self.X_START + i * self.X_BUTTON_SPACE,
                self.Y_START + i * self.Y_BUTTON_SPACE,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT,
                text,
                math.floor(self.BUTTON_HEIGHT * 0.4),
            )
            for i, text in enumerate(BUTTON_TEXT)
        ]

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

        self.buttons.append(BACK_BUTTON)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.BACKGROUND, (0, 0))
        title_surface = self.TITLE_FONT.render(self.GAME_STATE.title, True, Color.WHITE)
        title_rect = title_surface.get_rect(
            center=(math.floor(WIDTH * 0.275), math.floor(HEIGHT * 0.125))
        )
        screen.blit(title_surface, title_rect)
        for button in self.buttons:
            button.draw(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        for button in self.buttons:
            if button.handle_event(event):
                if button.text == "Create New Track":
                    self.GAME_STATE.set_state(AvailableSteps.ENTER_TRACK_NAME)
                    self.EXIT_LOOP = True
                elif button.text == "Select Track":
                    self.GAME_STATE.set_state(AvailableSteps.SELECT_TRACK)
                    self.EXIT_LOOP = True
                elif button.text == "Map":
                    self.GAME_STATE.set_state(AvailableSteps.MAP)
                    self.EXIT_LOOP = True
                elif button.text == "Back":
                    self.GAME_STATE.set_previous_state()
                    self.EXIT_LOOP = True

    def run(self) -> None:
        self.EXIT_LOOP = False
        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                # Handle events
                quit_event(event)
                self.handle_event(event)

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
