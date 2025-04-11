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
    MARKERS_FOLDER,
    CARS_FOLDER,
    CAR_SIZE_RATIO,
)
from data_models import AvailableSteps, Color
from render.button import Button
from utils import quit_event

from render.game_state import GameState


class PlaceDestinationMarkerWindow:
    EXIT_LOOP = False
    TITLE = "Place Destination Marker"
    MAX_MARKER_SIZE_LIMIT = 120
    MIN_MARKER_SIZE_LIMIT = 10

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state
        # Create white background
        BACKGROUND = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        BACKGROUND.fill(Color.WHITE)
        self.BACKGROUND = BACKGROUND

        self.HEADING_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.05))
        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

        self.BORDER_THICKNESS = 2

        # Load and setup marker image
        self.MARKER_IMG = pygame.image.load(
            os.path.join(MARKERS_FOLDER, "finish_marker.png")
        ).convert_alpha()

        # Load and setup car image
        self.CAR_IMG = pygame.image.load(
            os.path.join(CARS_FOLDER, "car.png")
        ).convert_alpha()

        self.update_marker_size()
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
        # Scale the original car image to current size with aspect ratio
        scaled_car = pygame.transform.scale(
            self.CAR_IMG, (car_size, int(car_size * CAR_SIZE_RATIO))
        )
        # Create rotated version
        self.car_preview = pygame.transform.rotate(
            scaled_car, self.GAME_STATE.CAR_PREVIEW_DATA.rotation
        )
        # Get the rect for positioning
        self.car_preview_rect = self.car_preview.get_rect()

    def update_marker_size(self) -> None:
        marker_size = self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size
        self.marker_preview = pygame.transform.scale(
            self.MARKER_IMG, (marker_size, marker_size)
        )
        self.marker_preview_rect = self.marker_preview.get_rect()

    def place_marker(self, mouse_pos: tuple[int, int]) -> None:
        self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position = mouse_pos
        self.placed_marker = self.marker_preview.copy()
        self.placed_marker_rect = self.placed_marker.get_rect()

        # Get track position from the TRACK_CANVAS_RECT
        track_position = (
            self.GAME_STATE.TRACK_CANVAS_RECT.x,
            self.GAME_STATE.TRACK_CANVAS_RECT.y,
        )

        if self.GAME_STATE.TRACK.IS_MAP:
            # Generate the road with adjusted coordinates
            self.GAME_STATE.TRACK.load_roads_from_points(
                self.GAME_STATE.CAR_PREVIEW_DATA.position,
                self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position,
                track_position,
            )

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.BACKGROUND, (0, 0))
        title_surface = self.HEADING_FONT.render(self.TITLE, True, Color.BLACK)
        TITLE_X = WIDTH // 2
        TITLE_Y = HEIGHT * 0.05
        title_rect = title_surface.get_rect(center=(TITLE_X, TITLE_Y))
        screen.blit(title_surface, title_rect)

        instructions = [
            "Left Click to Place Marker. Press Enter for Next Step",
            f"Mouse Wheel to Change Size ({self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size})",
            f"Overlay: {'On' if self.GAME_STATE.TRACK.SHOW_OVERLAY else 'Off'} (O To Toggle), Grid: {'On' if self.GAME_STATE.TRACK.SHOW_GRID else 'Off'} (G To Toggle)",
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

        # Draw marker preview at current mouse position if within canvas
        mouse_pos = pygame.mouse.get_pos()
        if self.GAME_STATE.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
            self.marker_preview_rect.center = mouse_pos
            screen.blit(self.marker_preview, self.marker_preview_rect)

        if self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position != (0, 0):
            self.placed_marker_rect.center = (
                self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position
            )
            screen.blit(self.placed_marker, self.placed_marker_rect)

        if self.GAME_STATE.CAR_PREVIEW_DATA.position != (0, 0):
            self.car_preview_rect.center = self.GAME_STATE.CAR_PREVIEW_DATA.position
            screen.blit(self.car_preview, self.car_preview_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        MOUSE_PRESSED = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if MOUSE_PRESSED[0]:
            if self.GAME_STATE.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
                self.place_marker(mouse_pos)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position != (0, 0):
                    self.GAME_STATE.set_state(AvailableSteps.START_SIMULATION)
                    self.EXIT_LOOP = True
                else:
                    print("Please place a marker first")
            if event.key == pygame.K_g:
                self.GAME_STATE.TRACK.toggle_grid()
            if event.key == pygame.K_o:
                self.GAME_STATE.TRACK.toggle_overlay()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Scroll to change marker size
            if event.button == 4:  # Scroll up
                if (
                    self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size
                    < self.MAX_MARKER_SIZE_LIMIT
                ):
                    self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size += 1
                    self.update_marker_size()
            elif event.button == 5:  # Scroll down
                if (
                    self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size
                    > self.MIN_MARKER_SIZE_LIMIT
                ):
                    self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size -= 1
                    self.update_marker_size()

        for button in self.buttons:
            if button.handle_event(event):
                if button.text == "Back":
                    self.GAME_STATE.set_previous_state()
                    self.EXIT_LOOP = True

    def run(self) -> None:
        self.EXIT_LOOP = False
        self.update_car_size()

        self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position = (0, 0)
        if self.GAME_STATE.TRACK.IS_MAP:
            self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size = 20
        else:
            self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size = 60

        self.update_marker_size()

        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                # Handle events
                quit_event(event)
                self.handle_event(event)

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
