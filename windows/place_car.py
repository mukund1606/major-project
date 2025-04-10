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
    CARS_FOLDER,
)
from data_models import AvailableSteps, Color
from render.button import Button
from utils import quit_event

from render.game_state import GameState


class PlaceCarWindow:
    EXIT_LOOP = False
    TITLE = "Place Car"
    MAX_CAR_SIZE_LIMIT = 80
    MIN_CAR_SIZE_LIMIT = 5
    ROTATION_SPEED = 2.5  # Degrees per frame

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state
        # Create white background
        BACKGROUND = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        BACKGROUND.fill(Color.WHITE)
        self.BACKGROUND = BACKGROUND

        self.HEADING_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.05))
        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

        self.BORDER_THICKNESS = 2

        # Load and setup car image
        self.CAR_IMG = pygame.image.load(
            os.path.join(CARS_FOLDER, "car.png")
        ).convert_alpha()

        self.update_car_size()

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

    def update_car_size(self) -> None:
        car_size = self.GAME_STATE.CAR_PREVIEW_DATA.size
        # Scale the original car image to current size with 0.6 aspect ratio
        scaled_car = pygame.transform.scale(
            self.CAR_IMG, (car_size, int(car_size * 0.6))
        )
        # Create rotated version
        self.car_preview = pygame.transform.rotate(
            scaled_car, self.GAME_STATE.CAR_PREVIEW_DATA.rotation
        )
        # Get the rect for positioning
        self.car_preview_rect = self.car_preview.get_rect()

    def place_car(self, mouse_pos: tuple[int, int]) -> None:
        self.GAME_STATE.CAR_PREVIEW_DATA.position = mouse_pos
        self.placed_car = self.car_preview.copy()
        self.placed_car_rect = self.placed_car.get_rect()

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.BACKGROUND, (0, 0))
        title_surface = self.HEADING_FONT.render(self.TITLE, True, Color.BLACK)
        TITLE_X = WIDTH // 2
        TITLE_Y = HEIGHT * 0.05
        title_rect = title_surface.get_rect(center=(TITLE_X, TITLE_Y))
        screen.blit(title_surface, title_rect)

        instructions = [
            "Left Click to Place Car. Press Enter for Next Step",
            f"Arrow Keys to Rotate Car ({self.GAME_STATE.CAR_PREVIEW_DATA.rotation}°), Mouse Wheel to Change Size ({self.GAME_STATE.CAR_PREVIEW_DATA.size})",
            f"Overlay: {'On' if self.GAME_STATE.TRACK.SHOW_OVERLAY else 'Off'}, Grid: {'On' if self.GAME_STATE.TRACK.SHOW_GRID else 'Off'}",
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

        # Draw car preview at current mouse position if within canvas
        mouse_pos = pygame.mouse.get_pos()
        if self.GAME_STATE.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
            self.car_preview_rect.center = mouse_pos
            screen.blit(self.car_preview, self.car_preview_rect)

        if self.GAME_STATE.CAR_PREVIEW_DATA.position != (0, 0):
            self.placed_car_rect.center = self.GAME_STATE.CAR_PREVIEW_DATA.position
            screen.blit(self.placed_car, self.placed_car_rect)

    def handle_rotation(self) -> None:
        """Handle continuous rotation based on key state"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.GAME_STATE.CAR_PREVIEW_DATA.rotation = (
                self.GAME_STATE.CAR_PREVIEW_DATA.rotation + self.ROTATION_SPEED
            ) % 360
            self.update_car_size()
        elif keys[pygame.K_RIGHT]:
            self.GAME_STATE.CAR_PREVIEW_DATA.rotation = (
                self.GAME_STATE.CAR_PREVIEW_DATA.rotation - self.ROTATION_SPEED
            ) % 360
            self.update_car_size()

    def handle_event(self, event: pygame.event.Event) -> None:
        MOUSE_PRESSED = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if MOUSE_PRESSED[0]:
            # Ensure track canvas rect exists before checking collision
            if self.GAME_STATE.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
                self.place_car(mouse_pos)  # Store absolute screen position

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.GAME_STATE.set_state(AvailableSteps.PLACE_DESTINATION_MARKER)
                self.EXIT_LOOP = True
            if event.key == pygame.K_g:
                self.GAME_STATE.TRACK.toggle_grid()
            if event.key == pygame.K_o:
                self.GAME_STATE.TRACK.toggle_overlay()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Scroll to change car size
            if event.button == 4:  # Scroll up
                if self.GAME_STATE.CAR_PREVIEW_DATA.size < self.MAX_CAR_SIZE_LIMIT:
                    self.GAME_STATE.CAR_PREVIEW_DATA.size += 1
                    self.update_car_size()
            elif event.button == 5:  # Scroll down
                if self.GAME_STATE.CAR_PREVIEW_DATA.size > self.MIN_CAR_SIZE_LIMIT:
                    self.GAME_STATE.CAR_PREVIEW_DATA.size -= 1
                    self.update_car_size()

        for button in self.buttons:
            if button.handle_event(event):
                if button.text == "Back":
                    self.GAME_STATE.set_previous_state()
                    self.EXIT_LOOP = True

    def run(self) -> None:
        self.EXIT_LOOP = False

        self.GAME_STATE.CAR_PREVIEW_DATA.rotation = 0
        self.GAME_STATE.CAR_PREVIEW_DATA.position = (0, 0)
        if self.GAME_STATE.TRACK.IS_MAP:
            self.GAME_STATE.CAR_PREVIEW_DATA.size = 20
        else:
            self.GAME_STATE.CAR_PREVIEW_DATA.size = 40

        self.update_car_size()

        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                # Handle events
                quit_event(event)
                self.handle_event(event)

            # Handle continuous rotation
            self.handle_rotation()

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
