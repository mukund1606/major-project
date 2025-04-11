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
    MAX_HISTORY_SIZE,
    IS_LIVE_DATA,
    MAX_LIVE_HISTORY_SIZE,
)

from data_models import Color
from utils import quit_event
from ai.car_ai import CarAI
from render.car import Car
from render.button import Button

from render.game_state import GameState

from utils import write_data_to_file

LIVE_DATA_FITNESS_HISTORY = []
LIVE_DATA_AVG_FITNESS_HISTORY = []
LIVE_DATA_CRASH_HISTORY = []
LIVE_DATA_FINISH_LINE_HISTORY = []


class RunningSimulationWindow:
    EXIT_LOOP = False
    TITLE = "Simulation"
    IS_RUNNING = False
    IS_LIVE = IS_LIVE_DATA

    @classmethod
    def toggle_live_data(cls):
        cls.IS_LIVE = not cls.IS_LIVE

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
        button_font_size = math.floor(button_height * 0.35)

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

        toggle_live_button_text = "Disable Live" if self.IS_LIVE else "Enable Live"
        self.toggle_live_button = Button(
            WIDTH - (button_width + 2) * 2,
            2,  # y
            button_width,
            button_height,
            toggle_live_button_text,
            button_font_size,
            Color.WHITE,  # Text color
        )

        grid_button_text = (
            "Show Grid" if self.GAME_STATE.TRACK.SHOW_GRID else "Hide Grid"
        )
        self.grid_button = Button(
            WIDTH - button_width - 2,
            button_height + 4,  # y
            button_width,
            button_height,
            grid_button_text,
            button_font_size,
            Color.WHITE,  # Text color
        )

        overlay_button_text = (
            "Show Overlay" if self.GAME_STATE.TRACK.SHOW_OVERLAY else "Hide Overlay"
        )
        self.overlay_button = Button(
            WIDTH - (button_width + 2) * 2,
            button_height + 4,  # y
            button_width,
            button_height,
            overlay_button_text,
            button_font_size,
            Color.WHITE,  # Text color
        )

        # Add zoom reset button
        self.zoom_reset_button = Button(
            WIDTH - button_width - 2,
            (button_height + 4) * 2,  # y
            button_width,
            button_height,
            "Reset Zoom",
            button_font_size,
            Color.WHITE,  # Text color
        )

        self.buttons = [
            self.back_button,
            self.radar_button,
            self.grid_button,
            self.overlay_button,
            self.zoom_reset_button,
            self.toggle_live_button,
        ]
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
                f"Generation: {self.GAME_STATE.CURRENT_GENERATION}, Alive: {self.GAME_STATE.ALIVE_CARS}, Best Fitness: {self.GAME_STATE.BEST_FITNESS:.2f}, Time Left: {CarAI.TIME_LIMIT - (time.time() - self.simulation_start_time):.2f}s.",
                f"Zoom: {self.GAME_STATE.TRACK.zoom_level:.1f}x (CTRL+Wheel to zoom, CTRL+Drag to pan, CTRL+R to reset view)",
                f"R: Toggle Radars, G: Toggle Grid, O: Toggle Overlay",
            ]
        else:
            self.instructions = [
                "Press Enter to Start Simulation, Use Back button to return to previous step.",
                f"Zoom: {self.GAME_STATE.TRACK.zoom_level:.1f}x (CTRL+Wheel to zoom, CTRL+Drag to pan, CTRL+R to reset view)",
                f"R: Toggle Radars, G: Toggle Grid, O: Toggle Overlay",
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
        if self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position != (0, 0) and hasattr(
            self, "marker_track_position"
        ):
            # Handle marker drawing with zoom
            marker_size = self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.size

            # Get track's zoom level and viewport
            zoom_level = self.GAME_STATE.TRACK.zoom_level
            viewport_x = getattr(self.GAME_STATE.TRACK, "viewport_x", 0)
            viewport_y = getattr(self.GAME_STATE.TRACK, "viewport_y", 0)
            canvas_rect = self.GAME_STATE.TRACK_CANVAS_RECT

            # Get marker track position (relative to track canvas)
            rel_track_x = self.marker_track_position[0]
            rel_track_y = self.marker_track_position[1]

            # Apply viewport transformation (similar to how Track.draw does it)
            screen_x = (rel_track_x - viewport_x) * zoom_level + canvas_rect.x
            screen_y = (rel_track_y - viewport_y) * zoom_level + canvas_rect.y

            # Scale marker based on zoom level
            zoomed_size = int(marker_size * zoom_level)
            zoomed_marker = pygame.transform.scale(
                self.MARKER_IMG, (zoomed_size, zoomed_size)
            )
            zoomed_marker_rect = zoomed_marker.get_rect(center=(screen_x, screen_y))

            # Draw the marker
            screen.blit(zoomed_marker, zoomed_marker_rect)

        for button in self.buttons:
            if self.IS_RUNNING and button.text == "Back":
                continue
            if not self.IS_RUNNING and (
                button.text == "Disable Live" or button.text == "Enable Live"
            ):
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

            # Get the best genome from the checkpoint population
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

            # Take only the best genome
            best_genome = all_genomes[:1]

            if not best_genome:
                print("No valid genomes found in checkpoint population")
                return

            self.run_simulation(best_genome, config)
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
        LIVE_DATA_FITNESS_HISTORY = []
        LIVE_DATA_AVG_FITNESS_HISTORY = []
        LIVE_DATA_CRASH_HISTORY = []
        LIVE_DATA_FINISH_LINE_HISTORY = []

        CURRENT_FRAME = 0

        # Simulation Loop
        while self.IS_RUNNING:
            CURRENT_FRAME += 1
            # Handle events
            for event in pygame.event.get():
                quit_event(event)  # Use utility function for quitting

                # Handle zoom and pan during simulation
                keys = pygame.key.get_pressed()
                mouse_pos = pygame.mouse.get_pos()
                zoom_mode = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]

                # Zoom with mouse wheel
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if zoom_mode and (event.button == 4 or event.button == 5):
                        if self.GAME_STATE.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
                            zoom_in = event.button == 4
                            self.GAME_STATE.TRACK.handle_zoom(
                                zoom_in, mouse_pos, self.GAME_STATE.TRACK_CANVAS_RECT
                            )

                # Pan with mouse drag
                if (
                    zoom_mode
                    and event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    if self.GAME_STATE.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
                        self.GAME_STATE.TRACK.start_panning(mouse_pos)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.GAME_STATE.TRACK.stop_panning()

                if (
                    event.type == pygame.MOUSEMOTION
                    and self.GAME_STATE.TRACK.is_panning
                ):
                    self.GAME_STATE.TRACK.update_panning(
                        mouse_pos, self.GAME_STATE.TRACK_CANVAS_RECT
                    )

                # Reset zoom with CTRL+R key
                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_r
                    and zoom_mode
                ):
                    self.GAME_STATE.TRACK.zoom_level = 1.0
                    self.GAME_STATE.TRACK.viewport_x = 0
                    self.GAME_STATE.TRACK.viewport_y = 0

                # Toggle radar with R key (without CTRL)
                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_r
                    and not zoom_mode
                ):
                    Car.toggle_sensors()
                    self.radar_button.text = (
                        "Hide Radars" if Car.DRAW_SENSORS else "Show Radars"
                    )

                # Toggle grid with G key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                    self.GAME_STATE.TRACK.toggle_grid()
                    self.grid_button.text = (
                        "Show Grid"
                        if not self.GAME_STATE.TRACK.SHOW_GRID
                        else "Hide Grid"
                    )

                # Toggle overlay with O key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
                    self.GAME_STATE.TRACK.toggle_overlay()
                    self.overlay_button.text = (
                        "Show Overlay"
                        if not self.GAME_STATE.TRACK.SHOW_OVERLAY
                        else "Hide Overlay"
                    )

                if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    self.toggle_live_data()
                    self.toggle_live_button.text = (
                        "Disable Live" if self.IS_LIVE else "Enable Live"
                    )

                # Pass mouse events to buttons for hover effects and clicks
                if self.radar_button.handle_event(event):
                    Car.toggle_sensors()
                    self.radar_button.text = (
                        "Hide Radars" if Car.DRAW_SENSORS else "Show Radars"
                    )

                if self.grid_button.handle_event(event):
                    self.GAME_STATE.TRACK.toggle_grid()
                    self.grid_button.text = (
                        "Show Grid" if self.GAME_STATE.TRACK.SHOW_GRID else "Hide Grid"
                    )

                if self.overlay_button.handle_event(event):
                    self.GAME_STATE.TRACK.toggle_overlay()
                    self.overlay_button.text = (
                        "Show Overlay"
                        if self.GAME_STATE.TRACK.SHOW_OVERLAY
                        else "Hide Overlay"
                    )

                if self.toggle_live_button.handle_event(event):
                    self.toggle_live_data()
                    self.toggle_live_button.text = (
                        "Disable Live" if self.IS_LIVE else "Enable Live"
                    )

                if self.zoom_reset_button.handle_event(event):
                    self.GAME_STATE.TRACK.zoom_level = 1.0
                    self.GAME_STATE.TRACK.viewport_x = 0
                    self.GAME_STATE.TRACK.viewport_y = 0

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

            # Update live data every 1 second
            if self.IS_LIVE and CURRENT_FRAME % FPS == 0:
                GENERATION_FITNESS: list[float] = [genome[1].fitness for genome in genomes]  # type: ignore
                GENERATION_MAX = max(GENERATION_FITNESS) if GENERATION_FITNESS else 0
                GENERATION_AVG = (
                    sum(GENERATION_FITNESS) / len(GENERATION_FITNESS)
                    if GENERATION_FITNESS
                    else 0
                )

                DEAD_CARS_COUNT = sum(
                    1
                    for car in self.car_ai.cars
                    if not car.alive and not car.reached_finish_line
                )
                FINISH_LINE_CARS_COUNT = sum(
                    1 for car in self.car_ai.cars if car.reached_finish_line
                )

                LIVE_DATA_FITNESS_HISTORY.append(GENERATION_MAX)
                LIVE_DATA_AVG_FITNESS_HISTORY.append(GENERATION_AVG)
                LIVE_DATA_CRASH_HISTORY.append(DEAD_CARS_COUNT)
                LIVE_DATA_FINISH_LINE_HISTORY.append(FINISH_LINE_CARS_COUNT)

                for history in [
                    LIVE_DATA_FITNESS_HISTORY,
                    LIVE_DATA_AVG_FITNESS_HISTORY,
                    LIVE_DATA_CRASH_HISTORY,
                    LIVE_DATA_FINISH_LINE_HISTORY,
                ]:
                    if len(history) > MAX_LIVE_HISTORY_SIZE:
                        del history[0]

                data = {
                    "generation": self.GAME_STATE.CURRENT_GENERATION,
                    "fitness_history": LIVE_DATA_FITNESS_HISTORY,
                    "avg_fitness_history": LIVE_DATA_AVG_FITNESS_HISTORY,
                    "crash_history": LIVE_DATA_CRASH_HISTORY,
                    "finish_line_history": LIVE_DATA_FINISH_LINE_HISTORY,
                    "detailed_path_data": [
                        {"path": car.path_history, "fitness": genomes[i][1].fitness}
                        for i, car in enumerate(self.car_ai.cars)
                    ],
                    "sensor_data": [car.get_data() for car in self.car_ai.cars],
                    "velocities": [car.speed for car in self.car_ai.cars],
                    "headings": [car.angle for car in self.car_ai.cars],
                }

                write_data_to_file(data, True)

            # ---- Drawing ----
            self.draw(self.GAME_STATE.SCREEN)
            pygame.display.update()
            self.GAME_STATE.CLOCK.tick(FPS)
            # ----------------

        # Compute final rewards for the generation after the loop ends
        self.car_ai.compute_reward(self.GAME_STATE.TRACK.get_ai_track())
        self.GAME_STATE.BEST_FITNESS = self.car_ai.BEST_FITNESS

        GENERATION_FITNESS: list[float] = [genome[1].fitness for genome in genomes]  # type: ignore
        GENERATION_MAX = max(GENERATION_FITNESS) if GENERATION_FITNESS else 0
        GENERATION_AVG = (
            sum(GENERATION_FITNESS) / len(GENERATION_FITNESS)
            if GENERATION_FITNESS
            else 0
        )

        DEAD_CARS_COUNT = sum(
            1
            for car in self.car_ai.cars
            if not car.alive and not car.reached_finish_line
        )
        FINISH_LINE_CARS_COUNT = sum(
            1 for car in self.car_ai.cars if car.reached_finish_line
        )

        self.FITNESS_HISTORY.append(GENERATION_MAX)
        self.AVG_FITNESS_HISTORY.append(GENERATION_AVG)
        self.CRASH_HISTORY.append(DEAD_CARS_COUNT)
        self.FINISH_LINE_HISTORY.append(FINISH_LINE_CARS_COUNT)

        for history in [
            self.FITNESS_HISTORY,
            self.AVG_FITNESS_HISTORY,
            self.CRASH_HISTORY,
            self.FINISH_LINE_HISTORY,
        ]:
            if len(history) > MAX_HISTORY_SIZE:
                del history[0]

        data = {
            "generation": self.GAME_STATE.CURRENT_GENERATION,
            "fitness_history": self.FITNESS_HISTORY,
            "avg_fitness_history": self.AVG_FITNESS_HISTORY,
            "crash_history": self.CRASH_HISTORY,
            "finish_line_history": self.FINISH_LINE_HISTORY,
            "detailed_path_data": [
                {"path": car.path_history, "fitness": genomes[i][1].fitness}
                for i, car in enumerate(self.car_ai.cars)
            ],
            "sensor_data": [car.get_data() for car in self.car_ai.cars],
            "velocities": [car.speed for car in self.car_ai.cars],
            "headings": [car.angle for car in self.car_ai.cars],
        }

        write_data_to_file(data, False)

        # Reset relevant states for the next generation or exit
        self.IS_RUNNING = False

    def handle_event(self, event: pygame.event.Event) -> None:
        # Get mouse position and key state
        mouse_pos = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        # Determine if we're in zoom/pan mode (CTRL key held)
        zoom_mode = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]

        # Handle zooming with mouse wheel when CTRL is held - always allowed
        if event.type == pygame.MOUSEBUTTONDOWN:
            if zoom_mode and (
                event.button == 4 or event.button == 5
            ):  # Mouse wheel + CTRL
                if self.GAME_STATE.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
                    zoom_in = event.button == 4  # Wheel up = zoom in
                    self.GAME_STATE.TRACK.handle_zoom(
                        zoom_in, mouse_pos, self.GAME_STATE.TRACK_CANVAS_RECT
                    )

        # Handle panning with mouse drag when CTRL is held - always allowed
        if zoom_mode and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.GAME_STATE.TRACK_CANVAS_RECT.collidepoint(mouse_pos):
                self.GAME_STATE.TRACK.start_panning(mouse_pos)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.GAME_STATE.TRACK.stop_panning()

        if event.type == pygame.MOUSEMOTION and self.GAME_STATE.TRACK.is_panning:
            self.GAME_STATE.TRACK.update_panning(
                mouse_pos, self.GAME_STATE.TRACK_CANVAS_RECT
            )

        # Reset zoom with CTRL+R key - always allowed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r and zoom_mode:
            self.GAME_STATE.TRACK.zoom_level = 1.0
            self.GAME_STATE.TRACK.viewport_x = 0
            self.GAME_STATE.TRACK.viewport_y = 0

        # Toggle radar with R key (without CTRL)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and not zoom_mode:
            Car.toggle_sensors()
            self.radar_button.text = (
                "Hide Radars" if Car.DRAW_SENSORS else "Show Radars"
            )

        # Toggle grid with G key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
            self.GAME_STATE.TRACK.toggle_grid()
            self.grid_button.text = (
                "Show Grid" if not self.GAME_STATE.TRACK.SHOW_GRID else "Hide Grid"
            )

        # Toggle overlay with O key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
            self.GAME_STATE.TRACK.toggle_overlay()
            self.overlay_button.text = (
                "Show Overlay"
                if not self.GAME_STATE.TRACK.SHOW_OVERLAY
                else "Hide Overlay"
            )

        if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            self.toggle_live_data()
            self.toggle_live_button.text = (
                "Disable Live" if self.IS_LIVE else "Enable Live"
            )

        # Handle events *before* simulation starts (Enter key)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and not self.IS_RUNNING:
                self.start_ai_simulation()  # Start the NEAT process

        # Handle button clicks
        self.radar_button.handle_event(event)
        self.grid_button.handle_event(event)
        self.overlay_button.handle_event(event)
        self.zoom_reset_button.handle_event(event)
        self.toggle_live_button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.radar_button.is_hovered:
                Car.toggle_sensors()
                self.radar_button.text = (
                    "Hide Radars" if Car.DRAW_SENSORS else "Show Radars"
                )

            elif self.grid_button.is_hovered:
                self.GAME_STATE.TRACK.toggle_grid()
                self.grid_button.text = (
                    "Show Grid" if self.GAME_STATE.TRACK.SHOW_GRID else "Hide Grid"
                )

            elif self.overlay_button.is_hovered:
                self.GAME_STATE.TRACK.toggle_overlay()
                self.overlay_button.text = (
                    "Show Overlay"
                    if self.GAME_STATE.TRACK.SHOW_OVERLAY
                    else "Hide Overlay"
                )

            elif self.toggle_live_button.is_hovered:
                self.toggle_live_data()
                self.toggle_live_button.text = (
                    "Disable Live" if self.IS_LIVE else "Enable Live"
                )

            elif self.zoom_reset_button.is_hovered:
                # Reset zoom and viewport
                self.GAME_STATE.TRACK.zoom_level = 1.0
                self.GAME_STATE.TRACK.viewport_x = 0
                self.GAME_STATE.TRACK.viewport_y = 0

        if not self.IS_RUNNING:
            # Update hover state for back button
            self.back_button.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.back_button.is_hovered:
                    self.GAME_STATE.set_previous_state()
                    self.EXIT_LOOP = True

    def run(self) -> None:
        self.FITNESS_HISTORY = []
        self.AVG_FITNESS_HISTORY = []
        self.CRASH_HISTORY = []
        self.FINISH_LINE_HISTORY = []

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

            # Store marker position relative to the track canvas for proper zooming
            canvas_rect = self.GAME_STATE.TRACK_CANVAS_RECT
            marker_pos = self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA.position
            self.marker_track_position = (
                marker_pos[0] - canvas_rect.x,
                marker_pos[1] - canvas_rect.y,
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
