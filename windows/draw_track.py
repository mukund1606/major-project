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
    MAX_BRUSH_SIZE_LIMIT = 30
    MIN_BRUSH_SIZE_LIMIT = 5

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state
        # Create white background
        self.BACKGROUND = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.BACKGROUND.fill(Color.WHITE)

        self.HEADING_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.05))
        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

        self.BRUSH_SIZE = 10
        self.LAST_POSITION: tuple[int, int] | None = None
        self.BORDER_THICKNESS = 2
        self.BORDER_PADDING = 5  # Minimum distance from border that can be drawn/erased

        # Create a surface for the brush preview
        self.BRUSH_PREVIEW_SURFACE = pygame.Surface(
            (self.MAX_BRUSH_SIZE_LIMIT * 2, self.MAX_BRUSH_SIZE_LIMIT * 2),
            pygame.SRCALPHA,
        )
        self.update_brush_preview()

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

    def draw_track(self, position: tuple[int, int], color=Color.BLACK):
        # Convert global mouse position to canvas local position
        canvas_x = position[0] - self.TRACK_CANVAS_RECT.x
        canvas_y = position[1] - self.TRACK_CANVAS_RECT.y
        canvas_pos = (canvas_x, canvas_y)

        # Check if position is within canvas bounds
        if not self.TRACK_CANVAS_RECT.collidepoint(position):
            self.LAST_POSITION = None
            return

        # Check if we're too close to the border when erasing
        if color == Color.WHITE:  # Erasing
            border_zone = self.BORDER_THICKNESS + self.BORDER_PADDING
            if (
                canvas_x < border_zone
                or canvas_x > TRACK_CANVAS_WIDTH - border_zone
                or canvas_y < border_zone
                or canvas_y > TRACK_CANVAS_HEIGHT - border_zone
            ):
                return

        if self.LAST_POSITION:
            self.draw_interpolated(self.LAST_POSITION, canvas_pos, color)
        else:
            pygame.draw.circle(self.TRACK_CANVAS, color, canvas_pos, self.BRUSH_SIZE)
        self.LAST_POSITION = canvas_pos

        # Always ensure border is visible after any drawing operation
        pygame.draw.rect(
            self.TRACK_CANVAS,
            Color.BLACK,
            self.TRACK_CANVAS.get_rect(),
            self.BORDER_THICKNESS,
        )

    def draw_interpolated(
        self, last_position: tuple[int, int], position: tuple[int, int], color: Color
    ):
        x1, y1 = last_position
        x2, y2 = position
        dx = x2 - x1
        dy = y2 - y1
        distance = max(abs(dx), abs(dy))
        if distance == 0:
            # Check if we're too close to the border when erasing
            if color == Color.WHITE:
                border_zone = self.BORDER_THICKNESS + self.BORDER_PADDING
                if (
                    x1 < border_zone
                    or x1 > TRACK_CANVAS_WIDTH - border_zone
                    or y1 < border_zone
                    or y1 > TRACK_CANVAS_HEIGHT - border_zone
                ):
                    return
            pygame.draw.circle(self.TRACK_CANVAS, color, position, self.BRUSH_SIZE)
            return

        for i in range(distance + 1):  # +1 to include the end point
            progress = float(i) / distance
            x = int(x1 + progress * dx)
            y = int(y1 + progress * dy)
            # Check if we're too close to the border when erasing
            if color == Color.WHITE:
                border_zone = self.BORDER_THICKNESS + self.BORDER_PADDING
                if (
                    x < border_zone
                    or x > TRACK_CANVAS_WIDTH - border_zone
                    or y < border_zone
                    or y > TRACK_CANVAS_HEIGHT - border_zone
                ):
                    continue
            pygame.draw.circle(self.TRACK_CANVAS, color, (x, y), self.BRUSH_SIZE)

    def update_brush_preview(self) -> None:
        # Clear the preview surface
        self.BRUSH_PREVIEW_SURFACE.fill((0, 0, 0, 0))

        # Draw the brush preview circle
        center = (
            self.BRUSH_PREVIEW_SURFACE.get_width() // 2,
            self.BRUSH_PREVIEW_SURFACE.get_height() // 2,
        )
        # Draw outer circle (black outline)
        pygame.draw.circle(
            self.BRUSH_PREVIEW_SURFACE, Color.BLACK, center, self.BRUSH_SIZE + 2
        )
        # Draw inner circle (white with some transparency)
        pygame.draw.circle(
            self.BRUSH_PREVIEW_SURFACE, (255, 255, 255, 128), center, self.BRUSH_SIZE
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
            f"Mouse Wheel to Change Brush Size ({self.BRUSH_SIZE})",
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

        # Draw brush preview at current mouse position if within canvas
        mouse_pos = pygame.mouse.get_pos()
        if self.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
            preview_rect = self.brush_preview_surface.get_rect(center=mouse_pos)
            screen.blit(self.brush_preview_surface, preview_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        MOUSE_PRESSED = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        if MOUSE_PRESSED[0] or MOUSE_PRESSED[2]:
            # Only draw if mouse is within canvas bounds
            if self.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
                if MOUSE_PRESSED[0]:
                    self.draw_track(mouse_pos)
                elif MOUSE_PRESSED[2]:
                    self.draw_track(mouse_pos, Color.WHITE)
            else:
                self.LAST_POSITION = None
        else:
            self.LAST_POSITION = None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Save Track Canvas
                data = pygame.image.tostring(self.TRACK_CANVAS, "RGB")
                img = Image.frombytes("RGB", self.TRACK_CANVAS.get_size(), data)
                path = os.path.join(TRACKS_FOLDER, f"{self.GAME_STATE.TRACK_NAME}.png")
                img.save(path)
                self.GAME_STATE.set_state(AvailableSteps.SELECT_TRACK)
                self.EXIT_LOOP = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Scroll to change brush size
            if event.button == 4:  # Scroll up
                if self.BRUSH_SIZE < self.MAX_BRUSH_SIZE_LIMIT:
                    self.BRUSH_SIZE += 1
                    self.update_brush_preview()
            elif event.button == 5:  # Scroll down
                if self.BRUSH_SIZE > self.MIN_BRUSH_SIZE_LIMIT:
                    self.BRUSH_SIZE -= 1
                    self.update_brush_preview()

        for button in self.buttons:
            if button.handle_event(event):
                if button.text == "Back":
                    self.GAME_STATE.set_previous_state(steps=2)
                    self.EXIT_LOOP = True

    def run(self) -> None:
        self.EXIT_LOOP = False
        self.LAST_POSITION = None
        self.BRUSH_SIZE = 10
        self.update_brush_preview()
        self.TRACK_CANVAS.fill(Color.WHITE)
        pygame.draw.rect(
            self.TRACK_CANVAS,
            Color.BLACK,
            self.TRACK_CANVAS.get_rect(),
            self.BORDER_THICKNESS,
        )
        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                # Handle events
                quit_event(event)
                self.handle_event(event)

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
