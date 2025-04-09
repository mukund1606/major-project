import pygame
import math
import os


from data_models import Color
from constants import WIDTH, CARS_FOLDER

from render.game_state import GameState


class Action:
    TURN_LEFT = 0
    TURN_RIGHT = 1
    ACCELERATE = 2
    BRAKE = 3


class Car:
    CAR_SPRITE_PATH = os.path.join(CARS_FOLDER, "car.png")
    DEAD_CAR_SPRITE_PATH = os.path.join(CARS_FOLDER, "dead_car.png")
    FINISH_LINE_CAR_SPRITE_PATH = os.path.join(CARS_FOLDER, "finish_line_car.png")

    CAR_SIZE_X: float = 40
    CAR_SIZE_Y: float = 40

    MINIMUM_SPEED: float = 3
    MAXIMUM_SPEED: float = 20
    ANGLE_INCREMENT: float = 10
    SPEED_INCREMENT: float = 1

    DEFAULT_SPEED: float = 5
    DEFAULT_ANGLE: float = 0

    COLLISION_SURFACE_COLOR = Color.WHITE

    DRAW_SENSORS: bool = True
    SENSORS_DRAW_DISTANCE: float = WIDTH

    @classmethod
    def toggle_sensors(cls):
        """Toggle the visibility of sensors for all cars"""
        cls.DRAW_SENSORS = not cls.DRAW_SENSORS

    def __init__(self, game_state: GameState) -> None:
        self.GAME_STATE = game_state
        self._original_sprite = pygame.image.load(self.CAR_SPRITE_PATH).convert_alpha()
        self._finish_line_sprite = pygame.image.load(
            self.FINISH_LINE_CAR_SPRITE_PATH
        ).convert_alpha()
        self._dead_sprite = pygame.image.load(self.DEAD_CAR_SPRITE_PATH).convert_alpha()

        self.track_canvas_offset = self.GAME_STATE.TRACK_CANVAS_RECT.topleft

        CAR_PREVIEW_DATA = game_state.CAR_PREVIEW_DATA
        size = CAR_PREVIEW_DATA.size
        rotation = CAR_PREVIEW_DATA.rotation
        abs_center_pos = CAR_PREVIEW_DATA.position  # Absolute screen center

        # Modify size based on preview data
        self.CAR_SIZE_X = size
        self.CAR_SIZE_Y = size

        # Modify angle based on preview data
        self.DEFAULT_ANGLE = rotation

        # Scale sprites based on preview data
        scaled_original = pygame.transform.scale(
            self._original_sprite, (self.CAR_SIZE_X, self.CAR_SIZE_Y)
        )
        scaled_finish_line = pygame.transform.scale(
            self._finish_line_sprite, (self.CAR_SIZE_X, self.CAR_SIZE_Y)
        )
        scaled_dead = pygame.transform.scale(
            self._dead_sprite, (self.CAR_SIZE_X, self.CAR_SIZE_Y)
        )

        # Store scaled versions before rotation for later use
        self._scaled_original_sprite = scaled_original
        self._scaled_finish_line_sprite = scaled_finish_line
        self._scaled_dead_sprite = scaled_dead

        self.angle = self.DEFAULT_ANGLE
        self.speed = self.DEFAULT_SPEED
        self.current_size = [self.CAR_SIZE_X, self.CAR_SIZE_Y]

        # --- Initialization with relative coordinates ---
        # Start with the unrotated scaled sprite
        temp_sprite = self._scaled_original_sprite
        # Rotate it according to the initial angle
        rotated_sprite = pygame.transform.rotate(temp_sprite, self.angle)

        # Calculate the RELATIVE center position
        rel_center_x = abs_center_pos[0] - self.track_canvas_offset[0]
        rel_center_y = abs_center_pos[1] - self.track_canvas_offset[1]

        # Get the rectangle of the rotated sprite, centered at the RELATIVE position
        new_rect = rotated_sprite.get_rect(center=(rel_center_x, rel_center_y))

        # Set the final sprite and RELATIVE top-left position
        self.sprite = rotated_sprite
        self.position = (new_rect.left, new_rect.top)  # Relative top-left

        # Update RELATIVE center based on the final relative top-left position and size
        self.center = list(new_rect.center)  # Relative center
        # --- End Initialization with relative coordinates ---

        self.sensors = []  # Stores relative end points and distance

        self.alive = True
        self.has_been_rendered_as_dead = False
        self.reached_finish_line = False

        self._final_reward = 0.0

        self.driven_distance = 0
        self.speed_penalty = 0

        self.track = game_state.TRACK

        self.DISTANCE_NORMALIZER = (
            self.track.TRACK_LENGTH / 2
        )  # Expect to cover at least half the track
        self.MAX_EXPECTED_SPEED = (
            self.track.TRACK_LENGTH / 100
        )  # Reasonable speed expectation
        self.penalty_factor = self.track.TRACK_LENGTH / 1000

        self.path_history = []  # Stores relative center positions

    def accelerate(self) -> None:
        """Accelerate the car"""
        if not self.reached_finish_line:
            if (self.speed + Car.SPEED_INCREMENT) <= Car.MAXIMUM_SPEED:
                self.speed += Car.SPEED_INCREMENT
            else:
                self.speed = Car.MAXIMUM_SPEED
                self.speed_penalty += 0.01

    def brake(self) -> None:
        """Brake the car"""
        if not self.reached_finish_line:
            if (
                self.speed - Car.SPEED_INCREMENT >= Car.MINIMUM_SPEED
            ):  # We don't want to go backwards nor going too slow
                self.speed -= Car.SPEED_INCREMENT
            else:
                self.speed = Car.MINIMUM_SPEED
                # Minimal penalty accumulation
                self.speed_penalty += 0.01  # Further reduced from 0.05 to 0.01

    def turn_left(self) -> None:
        """Turn the car to the left"""
        if not self.reached_finish_line:
            self.angle += Car.ANGLE_INCREMENT

    def turn_right(self) -> None:
        """Turn the car to the right"""
        if not self.reached_finish_line:
            self.angle -= Car.ANGLE_INCREMENT

    def check_collision(self, track: pygame.Surface) -> bool:
        """Check if the car is colliding with the track (using relative coordinates)

        Args:
            track (pygame.Surface): The track surface (assumed at 0,0 relative)
        """
        track_x = track.get_width()
        track_y = track.get_height()
        for point in self.corners:  # corners are already relative
            if (
                point[0] < 0
                or point[0] >= track_x
                or point[1] < 0
                or point[1] >= track_y
            ):
                self.alive = False
                return True

            elif (
                track.get_at((int(point[0]), int(point[1])))  # Use relative point
                == Car.COLLISION_SURFACE_COLOR
            ):
                self.alive = False
                return True

        return False

    def refresh_corners_positions(self) -> None:
        """Refresh the corners' current RELATIVE positions of the car"""
        length_x = 0.5 * self.current_size[0]
        length_y = 0.5 * self.current_size[1]

        corner1 = math.radians(360 - (self.angle + 30))
        corner2 = math.radians(360 - (self.angle + 150))
        corner3 = math.radians(360 - (self.angle + 210))
        corner4 = math.radians(360 - (self.angle + 330))

        # Calculate corners relative to the relative self.center
        left_top = [
            self.center[0] + math.cos(corner1) * length_x,
            self.center[1] + math.sin(corner1) * length_y,
        ]
        right_top = [
            self.center[0] + math.cos(corner2) * length_x,
            self.center[1] + math.sin(corner2) * length_y,
        ]
        left_bottom = [
            self.center[0] + math.cos(corner3) * length_x,
            self.center[1] + math.sin(corner3) * length_y,
        ]
        right_bottom = [
            self.center[0] + math.cos(corner4) * length_x,
            self.center[1] + math.sin(corner4) * length_y,
        ]

        self.corners = [
            left_top,
            right_top,
            left_bottom,
            right_bottom,
        ]  # Stored as relative

    def get_reward(self) -> float:
        """
        Get the reward of the car based on multiple factors.
        (Calculations use relative positions where relevant, e.g., distance to finish)
        """

        if self.reached_finish_line:
            return self._final_reward

        # Calculate distance to finish_line (using relative coordinates)
        finish_line_distance_factor = 0.0
        if (
            hasattr(self, "track")
            and hasattr(self.track, "finish_line_pos")
            and self.track.FINAL_LINE_POSITION
        ):
            # Convert finish line screen pos to relative pos for distance calculation
            abs_fx, abs_fy, _ = self.track.FINAL_LINE_POSITION
            rel_fx = abs_fx - self.track_canvas_offset[0]
            rel_fy = abs_fy - self.track_canvas_offset[1]

            finish_line_distance = math.sqrt(
                (self.center[0] - rel_fx) ** 2 + (self.center[1] - rel_fy) ** 2
            )
            finish_line_distance_factor = 1.0 - (
                finish_line_distance / self.track.TRACK_LENGTH
            )
            finish_line_distance_factor = (
                max(0, finish_line_distance_factor) * 20
            )  # Scale to 0-20

        # Scale distance reward to 0-100
        distance_reward = min(
            100, self.driven_distance / self.DISTANCE_NORMALIZER * 100
        )

        # Scale speed reward to 0-20
        speed_reward = min(20, (self.speed / self.MAX_EXPECTED_SPEED) * 20)

        # Scale malus to 0-10
        malus = min(10, self.speed_penalty / self.penalty_factor)

        # Scale progress factor to give 1-1.2x multiplier based on track length
        progress_factor = 1.0 + (
            min(1.0, self.driven_distance / (self.track.TRACK_LENGTH * 0.75)) * 0.2
        )

        # TODO: Implement improvement rate penalty
        # Calculate improvement rate penalty
        improvement_penalty = 0
        # if hasattr(self, "previous_fitness") and hasattr(Car, "best_improvement"):
        #     current_fitness = (
        #         distance_reward + speed_reward + finish_line_distance_factor
        #     )
        #     improvement = current_fitness - self.previous_fitness

        #     # If this car's improvement is less than 15% of the best improvement
        #     # Apply a penalty proportional to how far behind it is
        #     if Car.best_improvement > 0 and improvement < (Car.best_improvement * 0.15):
        #         improvement_penalty = min(
        #             10, (Car.best_improvement - improvement) / Car.best_improvement * 10
        #         )

        # Store current fitness for next generation's comparison

        self.previous_fitness = (
            distance_reward + speed_reward + finish_line_distance_factor
        )

        # Combine all factors with stricter scaling
        raw_reward = (
            distance_reward  # 0-100
            + speed_reward  # 0-20
            + finish_line_distance_factor  # 0-20
            - malus  # 0-10
            - improvement_penalty  # 0-10
        )

        # Apply progress factor and cap
        final_reward = raw_reward * progress_factor

        if self.reached_finish_line:
            final_reward += 150  # Add finish line bonus after capping normal reward

        return final_reward

    def check_finish_line_collision(self):
        """Check if the car has collided with the finish_line (using relative coordinates)."""
        if not self.reached_finish_line:
            final_marker = self.GAME_STATE.FINAL_MARKER_PREVIEW_DATA
            abs_x, abs_y = final_marker.position
            size = final_marker.size

            # Store absolute position for drawing later
            self.track.FINAL_LINE_POSITION = (abs_x, abs_y, size)

            # Convert absolute finish line center to relative rect for collision check
            rel_fx = abs_x - self.track_canvas_offset[0]
            rel_fy = abs_y - self.track_canvas_offset[1]
            finish_line_rect = pygame.Rect(0, 0, size, size)
            finish_line_rect.center = (rel_fx, rel_fy)

            # Create a relative rect for the car
            car_rect = pygame.Rect(
                self.position[0],  # Relative top-left
                self.position[1],
                self.current_size[0],
                self.current_size[1],
            )

            # Check for collision using relative rects
            if finish_line_rect.colliderect(car_rect):
                self._final_reward = (
                    self.get_reward() + 150
                )  # Bonus for reaching finish line
                self.reached_finish_line = True
                return True
        return False

    def check_sensor(self, degree: int, track: pygame.Surface) -> None:
        """Check distance using relative coordinates and store relative end point.

        Args:
            degree (int): Angle relative to car's forward direction.
            track (pygame.Surface): Track surface.
        """
        radians = math.radians(360 - (self.angle + degree))
        cos = math.cos(radians)
        sin = math.sin(radians)
        length = 1

        # Start from relative center
        cx, cy = int(self.center[0]), int(self.center[1])
        track_x = track.get_width()
        track_y = track.get_height()

        # Calculate end point relative to track
        rel_x, rel_y = cx, cy
        while (
            rel_x < track_x
            and rel_y < track_y
            and rel_x > 0
            and rel_y > 0
            and track.get_at((rel_x, rel_y)) != Car.COLLISION_SURFACE_COLOR
        ):
            rel_x = int(cx + cos * length)
            rel_y = int(cy + sin * length)

            if length > Car.SENSORS_DRAW_DISTANCE:
                break

            length += 1

        distance = int(math.hypot(rel_x - cx, rel_y - cy))
        self.sensors.append([(rel_x, rel_y), distance])  # Store relative end point

    def update_sprite(self, track: pygame.Surface | None = None):
        """Update car state (position, sensors, collision) using relative coordinates."""

        # Store initial state for physics calculation
        was_alive = self.alive
        was_not_finished = not self.reached_finish_line

        new_center_x = self.center[0]
        new_center_y = self.center[1]

        # If simulating, update position, check collisions/sensors (relative coords)
        if track is not None and was_alive and was_not_finished:
            radians = math.radians(360 - self.angle)
            cos = math.cos(radians)
            sin = math.sin(radians)

            # Calculate new *center* position based on speed and angle
            new_center_x = self.center[0] + cos * self.speed
            new_center_y = self.center[1] + sin * self.speed
            self.center = [new_center_x, new_center_y]  # Update center immediately

            # Calculate driven distance *before* potential collision sets alive=False
            self.driven_distance += self.speed

            # Record relative path history (based on updated center)
            self.path_history.append(list(self.center))

            # Calculate relative corners based on the *new* center
            self.refresh_corners_positions()  # Uses self.center

            # Check collisions relative to track surface
            self.check_collision(track)  # May set self.alive = False

            # Update sensors only if still alive after potential collision
            if self.alive:
                self.sensors.clear()
                for sensor_angle in range(-90, 90 + 1, 45):
                    self.check_sensor(sensor_angle, track)  # Uses self.center

        # --- Choose base sprite *after* potential state change in physics block ---
        if self.reached_finish_line:
            base_sprite = self._scaled_finish_line_sprite
        elif not self.alive:  # Check the *current* alive status
            base_sprite = self._scaled_dead_sprite
        else:  # Must be alive and not finished
            base_sprite = self._scaled_original_sprite

        # --- Rotate the correct sprite for drawing ---
        rotated_sprite = None
        if not self.alive:
            # Use the stored sprite if already rendered dead, otherwise rotate the (now correctly selected) dead base_sprite
            if self.has_been_rendered_as_dead:
                rotated_sprite = self.sprite
            else:
                rotated_sprite = pygame.transform.rotate(base_sprite, self.angle)
                self.has_been_rendered_as_dead = True
                self.sprite = rotated_sprite  # Store the newly rotated dead sprite
        else:  # Alive or finished
            rotated_sprite = pygame.transform.rotate(base_sprite, self.angle)
            self.sprite = rotated_sprite  # Update sprite if alive/finished

        # --- Update sprite rect for drawing ---
        # Set the final sprite's rect center to the calculated new center position
        # (or the last known center if the car just died)
        final_rect = rotated_sprite.get_rect(center=(new_center_x, new_center_y))
        # Update relative top-left position based on the final rect
        self.position = (final_rect.left, final_rect.top)
        # Center should already be correct, but update for consistency
        self.center = list(final_rect.center)

    def get_data(self) -> list[int]:
        """Get the data of the car's sensors (distances)

        Returns:
            list[int]: The list of the sensors' distances
        """
        distances = [int(sensor[1]) for sensor in self.sensors]
        distances += [0] * (5 - len(distances))
        return distances

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the car and sensors, converting relative coords to screen coords.

        Args:
            screen (pygame.Surface): The main display screen.
        """
        # Calculate absolute screen position for blitting
        screen_pos_x = self.position[0] + self.track_canvas_offset[0]
        screen_pos_y = self.position[1] + self.track_canvas_offset[1]
        screen_position = (screen_pos_x, screen_pos_y)

        screen.blit(self.sprite, screen_position)

        # Draw sensors if enabled and car is alive
        if Car.DRAW_SENSORS and self.alive:
            # Calculate absolute screen center
            screen_center_x = self.center[0] + self.track_canvas_offset[0]
            screen_center_y = self.center[1] + self.track_canvas_offset[1]
            screen_center = (screen_center_x, screen_center_y)

            for sensor in self.sensors:
                # Calculate absolute screen position for sensor end point
                rel_end_pos = sensor[0]
                screen_end_pos_x = rel_end_pos[0] + self.track_canvas_offset[0]
                screen_end_pos_y = rel_end_pos[1] + self.track_canvas_offset[1]
                screen_end_position = (screen_end_pos_x, screen_end_pos_y)

                pygame.draw.line(
                    screen, Color.GREEN, screen_center, screen_end_position, 2
                )
                pygame.draw.circle(screen, Color.RED, screen_end_position, 4)
