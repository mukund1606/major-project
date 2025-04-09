import sys
import time
import math
import os
import pygame
import neat


from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    DEFAULT_FONT,
    TRACK_CANVAS_WIDTH,
    TRACK_CANVAS_HEIGHT,
    MARKERS_FOLDER,
    NEAT_CONFIG_PATH,
    DEBUG,
    CHECKPOINT_FOLDER,
    CHECKPOINT_INTERVAL,
    MAX_SIMULATIONS,
)

from data_models import Color
from utils import quit_event
from ai.car_ai import CarAI
from render.car import Car
from render.button import Button

from render.game_state import GameState


class RunningSimulationWindow:
    EXIT_LOOP = False
    TITLE = "Simulation"
    IS_RUNNING = False

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state
        # Create white background
        BACKGROUND = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        BACKGROUND.fill(Color.WHITE)
        self.BACKGROUND = BACKGROUND

        self.HEADING_FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.05))
        self.FONT = pygame.font.SysFont(DEFAULT_FONT, math.floor(HEIGHT * 0.025))

        self.BORDER_THICKNESS = 2

        self.MARKER_IMG = pygame.image.load(
            os.path.join(MARKERS_FOLDER, "finish_marker.png")
        ).convert_alpha()

        # Setup track canvas position and store in GameState if not already set
        CANVAS_CENTER_X = int(WIDTH // 2)
        CANVAS_CENTER_Y = int(TRACK_CANVAS_HEIGHT // 2 + HEIGHT * 0.2)
        track_canvas_rect = pygame.Rect(0, 0, TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT)
        track_canvas_rect.center = (CANVAS_CENTER_X, CANVAS_CENTER_Y)
        self.GAME_STATE.TRACK_CANVAS_RECT = track_canvas_rect

        # --- Create Buttons ---
        button_width = math.floor(WIDTH * 0.1)
        button_height = math.floor(HEIGHT * 0.075)
        button_font_size = math.floor(button_height * 0.4)

        radar_button_text = "Hide Radars" if Car.DRAW_SENSORS else "Show Radars"
        self.radar_button = Button(
            WIDTH - button_width - 2,
            2,  # y
            button_width,
            button_height,
            radar_button_text,
            button_font_size,
            Color.WHITE,  # Text color
        )

        self.back_button = Button(
            WIDTH - (button_width + 2) * 2,
            2,  # y
            button_width,
            button_height,
            "Back",
            button_font_size,
            Color.WHITE,  # Text color
        )

        self.buttons = [self.back_button, self.radar_button]
        # ---------------------

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.BACKGROUND, (0, 0))
        title_surface = self.HEADING_FONT.render(self.TITLE, True, Color.BLACK)
        TITLE_X = WIDTH // 2
        TITLE_Y = HEIGHT * 0.05
        title_rect = title_surface.get_rect(center=(TITLE_X, TITLE_Y))
        screen.blit(title_surface, title_rect)

        # Update instructions based on simulation state
        if self.IS_RUNNING:
            self.instructions = [
                f"Generation: {self.GAME_STATE.CURRENT_GENERATION}, Alive: {self.GAME_STATE.ALIVE_CARS}, Best Fitness: {self.GAME_STATE.BEST_FITNESS:.2f}",
                f"Time Left: {CarAI.TIME_LIMIT - (time.time() - self.simulation_start_time):.2f} seconds. Running Simulation...",
            ]
        else:
            self.instructions = [
                "Press Enter to Start Simulation",
                "Use Back button to return to previous step.",
            ]

        line_spacing = self.FONT.get_linesize()
        start_y = HEIGHT * 0.1

        for i, instruction in enumerate(self.instructions):
            instruction_surface = self.FONT.render(instruction, True, Color.BLACK)
            instruction_rect = instruction_surface.get_rect(
                center=(WIDTH // 2, start_y + (i * line_spacing))
            )
            screen.blit(instruction_surface, instruction_rect)

        # Draw Track Canvas using the rect from GameState
        self.GAME_STATE.TRACK.draw(screen, self.GAME_STATE.TRACK_CANVAS_RECT)

        if self.IS_RUNNING:
            for car in self.car_ai.cars:
                car.draw(screen)
        else:
            self.test_car.draw(screen)

        # Draw placed marker
        if self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position != (0, 0):
            self.placed_marker_rect.center = (
                self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position
            )
            screen.blit(self.placed_marker, self.placed_marker_rect)

        for button in self.buttons:
            if self.IS_RUNNING and button.text == "Back":
                continue
            button.draw(screen)

        if self.GAME_STATE.BEST_VISUAL_NN is not None:
            self.GAME_STATE.BEST_VISUAL_NN.draw(screen)

    def start_ai_simulation(self) -> None:
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            NEAT_CONFIG_PATH,
        )

        if not self.GAME_STATE.IS_TRAINING_MODE:
            if self.GAME_STATE.CHECKPOINT_POPULATION is None:
                print("No checkpoint population available for replay mode")
                return

            # Get the top 5 genomes from the checkpoint population
            all_genomes = []
            for (
                genome_id,
                genome,
            ) in self.GAME_STATE.CHECKPOINT_POPULATION.population.items():
                if genome.fitness is not None:
                    all_genomes.append((genome_id, genome))

            # Sort genomes by fitness in descending order
            all_genomes.sort(
                key=lambda x: (
                    x[1].fitness if x[1].fitness is not None else -float("inf")
                ),
                reverse=True,
            )

            # Take top 5 genomes
            top_genomes = all_genomes[:5]

            if not top_genomes:
                print("No valid genomes found in checkpoint population")
                return

            # Run the top genomes in a loop
            while not self.EXIT_LOOP:
                self.run_simulation(top_genomes, config)
            return

        # Training mode logic
        population = neat.Population(config)

        if self.GAME_STATE.CHECKPOINT_POPULATION is not None:
            population = self.GAME_STATE.CHECKPOINT_POPULATION

        if DEBUG:
            population.add_reporter(neat.StdOutReporter(True))
            population.add_reporter(neat.StatisticsReporter())

            checkpoint_dir = os.path.join(
                CHECKPOINT_FOLDER, self.GAME_STATE.TRACK.track_name
            )
            if not os.path.exists(checkpoint_dir):
                os.makedirs(checkpoint_dir)
            checkpointer = neat.Checkpointer(
                generation_interval=CHECKPOINT_INTERVAL,
                time_interval_seconds=None,  # type: ignore
                filename_prefix=os.path.join(checkpoint_dir, "checkpoint-"),
            )
            population.add_reporter(checkpointer)

        population.run(self.run_simulation, MAX_SIMULATIONS)
        self.IS_RUNNING = (
            False  # Set running to false after NEAT finishes or is interrupted
        )

    def run_simulation(
        self, genomes: list[tuple[int, neat.DefaultGenome]], config: neat.Config
    ) -> None:
        # Create car_ai with current rotation and scale
        self.car_ai = CarAI(config, genomes, self.GAME_STATE)

        self.simulation_start_time = time.time()
        self.IS_RUNNING = True

        # Simulation Loop
        while self.IS_RUNNING:
            # Handle events
            for event in pygame.event.get():
                quit_event(event)  # Use utility function for quitting

                # Pass mouse events to radar button for hover effects and clicks
                # Only handle radar button clicks during simulation
                if self.radar_button.handle_event(event):
                    Car.toggle_sensors()
                    self.radar_button.text = (
                        "Hide Radars" if Car.DRAW_SENSORS else "Show Radars"
                    )
                # Back button is handled in the main run loop

            # ---- Simulation Logic ----
            self.car_ai.compute()
            self.car_ai.compute_reward(self.GAME_STATE.TRACK.get_ai_track())
            self.GAME_STATE.BEST_FITNESS = self.car_ai.BEST_FITNESS

            # Check for finish_line collisions
            for car in self.car_ai.cars:
                if car.alive and not car.reached_finish_line:
                    car.check_finish_line_collision()

            # Update alive car count for display and end condition
            active_cars = sum(1 for car in self.car_ai.cars if car.alive)
            finish_line_cars = sum(
                1 for car in self.car_ai.cars if car.reached_finish_line
            )
            self.car_ai.remaining_cars = active_cars
            self.GAME_STATE.ALIVE_CARS = active_cars

            # End conditions for the current generation
            if (
                (
                    active_cars == finish_line_cars and finish_line_cars > 0
                )  # All active cars finished
                or active_cars == 0  # All cars crashed
                or time.time() - self.simulation_start_time
                > CarAI.TIME_LIMIT  # Time limit reached
            ):
                self.IS_RUNNING = False  # Stop this generation's simulation loop
                break  # Exit while loop
            # ---------------------------

            # ---- Drawing ----
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
            # ----------------

        # Compute final rewards for the generation after the loop ends
        self.car_ai.compute_reward(self.GAME_STATE.TRACK.get_ai_track())
        self.GAME_STATE.BEST_FITNESS = self.car_ai.BEST_FITNESS

        # Reset relevant states for the next generation or exit
        self.IS_RUNNING = False

    def handle_event(self, event: pygame.event.Event) -> None:
        # Handle events *before* simulation starts (Enter key)
        # Or button clicks when not simulating
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not self.IS_RUNNING:
                self.start_ai_simulation()  # Start the NEAT process

        self.radar_button.handle_event(event)  # Allow toggle even before start
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.radar_button.is_hovered:
                Car.toggle_sensors()
                self.radar_button.text = (
                    "Hide Radars" if Car.DRAW_SENSORS else "Show Radars"
                )

        if not self.IS_RUNNING:
            # Update hover state for both buttons
            self.back_button.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button.is_hovered:
                    self.GAME_STATE.set_previous_state()
                    self.EXIT_LOOP = True

    def run(self) -> None:
        self.EXIT_LOOP = False
        self.IS_RUNNING = False  # Ensure simulation is not running initially

        self.test_car = Car(self.GAME_STATE)  # Create test car for preview
        self.GAME_STATE.ALIVE_CARS = 0
        self.GAME_STATE.BEST_FITNESS = 0.0

        # Initialize placed marker image if data exists
        if self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position != (0, 0):
            marker_size = self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size
            self.placed_marker = pygame.transform.scale(
                self.MARKER_IMG, (marker_size, marker_size)
            )
            self.placed_marker_rect = self.placed_marker.get_rect()
            self.placed_marker_rect.center = (
                self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position
            )

        # Main Window Loop
        while not self.EXIT_LOOP:
            for event in pygame.event.get():
                quit_event(event)
                self.handle_event(event)

            # Update the screen
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
