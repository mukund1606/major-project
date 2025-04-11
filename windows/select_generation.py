import math
import os
import pygame

from data_models import AvailableSteps, Color
from constants import WIDTH, HEIGHT, FPS, DEFAULT_FONT, CHECKPOINT_FOLDER
from utils import quit_event

from render.game_state import GameState
from render.button import Button


class CheckpointPreview:
    def __init__(
        self, x: int, y: int, width: int, height: int, name: str, path: str
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.path = path
        self.y_offset = 0

        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

    def draw(self, screen: pygame.Surface) -> None:
        # Update rect position with scroll offset
        adjusted_y = self.y + self.y_offset
        pygame.draw.rect(
            screen, Color.WHITE, (self.x, adjusted_y, self.width, self.height)
        )
        # Draw the border
        pygame.draw.rect(
            screen, Color.BLACK, (self.x, adjusted_y, self.width, self.height), 2
        )
        text = self.FONT.render(self.name, True, Color.BLACK)
        text_rect = text.get_rect(
            center=(self.x + self.width / 2, adjusted_y + self.height / 2)
        )
        screen.blit(text, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Create a temporary rect with the scrolled position for collision detection
            scrolled_rect = pygame.Rect(
                self.x, self.y + self.y_offset, self.width, self.height
            )
            if scrolled_rect.collidepoint(event.pos):
                return True
        return False


class SelectGenerationWindow:
    EXIT_LOOP = False
    CHECKPOINTS: list[CheckpointPreview] = []
    PREVIEW_WIDTH = math.floor(WIDTH * 0.15)
    PREVIEW_HEIGHT = math.floor(HEIGHT * 0.1)
    GRID_SPACE = math.floor(WIDTH * 0.025)
    GRID_COLUMNS = 4
    # Calculate total width of all previews and spaces
    TOTAL_GRID_WIDTH = (PREVIEW_WIDTH * GRID_COLUMNS) + (
        GRID_SPACE * (GRID_COLUMNS - 1)
    )
    # Center the entire grid horizontally
    START_X = (WIDTH - TOTAL_GRID_WIDTH) // 2
    START_Y = math.floor(HEIGHT * 0.2)
    PREVIEW_SPACING_Y = PREVIEW_HEIGHT + GRID_SPACE
    # Scrolling parameters
    SCROLL_SPEED = 50
    scroll_y = 0
    max_scroll = 0
    VISIBLE_AREA_START = START_Y
    VISIBLE_AREA_HEIGHT = (
        HEIGHT - START_Y - math.floor(HEIGHT * 0.05)
    )  # Slightly reduced bottom margin

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state

        # White background
        BACKGROUND = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        BACKGROUND.fill(Color.WHITE)
        self.BACKGROUND = BACKGROUND

        self.HEADING_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.05))

        BUTTON_WIDTH = math.floor(WIDTH * 0.1)
        BUTTON_HEIGHT = math.floor(HEIGHT * 0.075)
        BUTTON_FONT_SIZE = math.floor(BUTTON_HEIGHT * 0.4)

        # New Simulation button (only in training mode)
        if self.GAME_STATE.IS_TRAINING_MODE:
            NEW_SIM_BUTTON = Button(
                2,  # x position - left aligned
                2,  # y position - top aligned
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
                "New Sim",
                BUTTON_FONT_SIZE,
                Color.WHITE,
            )
            self.buttons = [NEW_SIM_BUTTON]
        else:
            self.buttons = []

        # Back button
        BACK_BUTTON = Button(
            WIDTH - BUTTON_WIDTH - 2,
            2,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Back",
            BUTTON_FONT_SIZE,
            Color.WHITE,
        )
        self.buttons.append(BACK_BUTTON)

        # Refresh button
        REFRESH_BUTTON = Button(
            WIDTH - (BUTTON_WIDTH + 2) * 2,
            2,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Refresh",
            BUTTON_FONT_SIZE,
            Color.WHITE,
        )
        self.buttons.append(REFRESH_BUTTON)

        self.get_checkpoints()

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.BACKGROUND, (0, 0))

        title = self.HEADING_FONT.render("Select Generation", True, Color.BLACK)
        TITLE_X = WIDTH // 2
        TITLE_Y = math.floor(HEIGHT * 0.05)
        title_rect = title.get_rect(center=(TITLE_X, TITLE_Y))
        screen.blit(title, title_rect)

        # Create a clipping rect for the scrollable area
        scroll_area = pygame.Rect(
            0, self.VISIBLE_AREA_START, WIDTH, self.VISIBLE_AREA_HEIGHT
        )
        screen.set_clip(scroll_area)

        if not self.CHECKPOINTS:
            # Display "No generations found" message
            no_gen_text = self.HEADING_FONT.render(
                "No generations found", True, Color.BLACK
            )
            no_gen_rect = no_gen_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(no_gen_text, no_gen_rect)
        else:
            for preview in self.CHECKPOINTS:
                # Adjust preview position by scroll amount
                preview.y_offset = self.scroll_y
                # Only draw if in visible area
                if (
                    preview.y + preview.y_offset
                    >= self.VISIBLE_AREA_START - self.PREVIEW_HEIGHT
                    and preview.y + preview.y_offset
                    <= self.VISIBLE_AREA_START + self.VISIBLE_AREA_HEIGHT
                ):
                    preview.draw(screen)

        # Reset clipping
        screen.set_clip(None)

        for button in self.buttons:
            button.draw(screen)

    def get_checkpoints(self) -> None:
        path = os.path.join(CHECKPOINT_FOLDER, self.GAME_STATE.TRACK.track_name)
        if self.GAME_STATE.TRACK.track_name == "":
            self.CHECKPOINTS = []
            return
        if not os.path.exists(path):
            os.makedirs(path)
            self.CHECKPOINTS = []
            return
        checkpoints = os.listdir(path)
        # Sort checkpoints by generation number instead of alphabetically
        checkpoints.sort(key=lambda x: int(x.split("-")[-1]))
        previews = []
        for i, checkpoint in enumerate(checkpoints):
            row = i // self.GRID_COLUMNS
            col = i % self.GRID_COLUMNS
            x_pos = self.START_X + col * (self.PREVIEW_WIDTH + self.GRID_SPACE)
            # Use PREVIEW_SPACING_Y instead of PREVIEW_HEIGHT for vertical spacing
            y_pos = self.START_Y + row * self.PREVIEW_SPACING_Y

            checkpoint_path = os.path.join(path, checkpoint)
            checkpoint_name = os.path.splitext(checkpoint)[0]

            preview = CheckpointPreview(
                x_pos,
                y_pos,
                self.PREVIEW_WIDTH,
                self.PREVIEW_HEIGHT,
                checkpoint_name,
                checkpoint_path,
            )
            previews.append(preview)
        self.CHECKPOINTS = previews

        # Calculate max scroll based on content height including text space
        if previews:
            last_preview = previews[-1]
            content_height = last_preview.y + self.PREVIEW_HEIGHT - self.START_Y
            self.max_scroll = min(0, self.VISIBLE_AREA_HEIGHT - content_height)

    def handle_event(self, event: pygame.event.Event) -> None:
        for button in self.buttons:
            if button.handle_event(event):
                if button.text == "Back":
                    if self.GAME_STATE.TRACK.IS_MAP:
                        self.GAME_STATE.set_previous_state(steps=3)
                    else:
                        self.GAME_STATE.set_previous_state()
                    self.EXIT_LOOP = True
                elif button.text == "Refresh":
                    self.get_checkpoints()
                    self.scroll_y = 0  # Reset scroll position on refresh
                elif button.text == "New Sim":
                    self.GAME_STATE.CURRENT_GENERATION = 0
                    self.GAME_STATE.set_state(AvailableSteps.PLACE_CAR)
                    self.EXIT_LOOP = True

        # Handle mouse wheel scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * self.SCROLL_SPEED
            # Clamp scroll value
            self.scroll_y = max(min(0, self.scroll_y), self.max_scroll)

        for preview in self.CHECKPOINTS:
            if preview.handle_event(event):
                generation = int(preview.name.split("-")[-1])
                self.GAME_STATE.load_checkpoint(preview.path, generation)
                self.GAME_STATE.set_state(AvailableSteps.PLACE_CAR)
                self.EXIT_LOOP = True

    def run(self) -> None:
        self.EXIT_LOOP = False
        self.get_checkpoints()
        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                # Handle events
                quit_event(event)
                self.handle_event(event)

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
