import os
from PIL import Image
import pygame

from utils import calculate_track_length, load_csv

from constants import (
    TRACK_CANVAS_WIDTH,
    TRACK_CANVAS_HEIGHT,
    TRACKS_FOLDER,
    TILEMAP_RATIO,
    TILEMAP_WIDTH,
    TILEMAP_HEIGHT,
)

from data_models import Color


class Track:
    IS_MAP: bool = False
    BORDER_THICKNESS = 2
    TRACK_LENGTH = 0
    FINAL_LINE_POSITION: tuple[float, float, float] = (0, 0, 0)
    SHOW_GRID = False
    SHOW_OVERLAY = False

    @classmethod
    def toggle_grid(cls):
        """Toggle the visibility of the grid"""
        cls.SHOW_GRID = not cls.SHOW_GRID

    @classmethod
    def toggle_overlay(cls):
        """Toggle the visibility of the overlay"""
        cls.SHOW_OVERLAY = not cls.SHOW_OVERLAY

    def __init__(self, track_name: str) -> None:
        self.track_name = track_name

        # Create the track canvas (WHITE)
        self.AI_SURFACE = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.AI_SURFACE.fill(Color.WHITE)

        # Foreground for map (TODO)
        self.FOREGROUND = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.FOREGROUND.fill(Color.WHITE)

        # Overlay for map
        self.OVERLAY_SURFACE = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )

        # Grid for map - created once
        self.GRID_SURFACE = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.create_grid()

        # Load track if name is provided
        if track_name and track_name != "":
            self.load_track()
        else:
            # Load Empty Track
            self.AI_SURFACE.fill(Color.WHITE)
            self.FOREGROUND.fill(Color.WHITE)

        # Draw border
        self.draw_border()

        self.MAP_TILESET_PATH = "assets/map/tileset.png"
        self.MAP_PATH = "assets/map/map.csv"
        self.ROADS_PATH = "assets/map/roads.csv"

        self.MAP_DATA = load_csv(self.MAP_PATH)
        self.ROADS_DATA = load_csv(self.ROADS_PATH)

    def create_grid(self) -> None:
        """Create the grid surface with transparent boxes and black 1px borders"""
        GRID_SIZE = 80 * TILEMAP_RATIO

        # Clear the grid surface
        self.GRID_SURFACE.fill((0, 0, 0, 0))  # Fully transparent

        # Get map offsets (if available)
        offset_x = getattr(self, "map_offset_x", 0)
        offset_y = getattr(self, "map_offset_y", 0)

        # Calculate the actual map width and height
        actual_map_width = TILEMAP_WIDTH * TILEMAP_RATIO
        actual_map_height = TILEMAP_HEIGHT * TILEMAP_RATIO

        # Calculate number of grid cells based on the actual map size
        grid_cols = int(actual_map_width // GRID_SIZE)
        grid_rows = int(actual_map_height // GRID_SIZE)

        # Draw grid lines with proper offset
        for col in range(grid_cols):
            for row in range(grid_rows):
                # Only draw if within the canvas bounds
                x = col * GRID_SIZE + offset_x
                y = row * GRID_SIZE + offset_y

                # Skip if outside the canvas area
                if (
                    x >= TRACK_CANVAS_WIDTH
                    or y >= TRACK_CANVAS_HEIGHT
                    or x + GRID_SIZE <= 0
                    or y + GRID_SIZE <= 0
                ):
                    continue

                rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
                # Draw transparent rectangles with 1px black border
                pygame.draw.rect(
                    self.GRID_SURFACE, (0, 0, 0, 0), rect
                )  # Transparent fill
                pygame.draw.rect(
                    self.GRID_SURFACE, (0, 0, 0, 128), rect, 1
                )  # 1px black border

    def load_track(self) -> None:
        self.TRACK_LENGTH = 0
        if not self.IS_MAP:
            # Create white background surface
            self.AI_SURFACE = pygame.Surface(
                (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
            )
            self.AI_SURFACE.fill(Color.WHITE)

            # Load the track image
            track_path = os.path.join(TRACKS_FOLDER, f"{self.track_name}.png")
            img = Image.open(track_path)
            rgb_img = img.convert("RGB")
            track_image = pygame.image.fromstring(
                rgb_img.tobytes(), rgb_img.size, "RGB"
            )

            # Calculate the size to match either width or height while maintaining aspect ratio
            track_width, track_height = track_image.get_size()
            width_ratio = TRACK_CANVAS_WIDTH / track_width
            height_ratio = TRACK_CANVAS_HEIGHT / track_height

            # Use the smaller ratio to ensure track fits in canvas
            scale_factor = min(width_ratio, height_ratio)
            new_width = int(track_width * scale_factor)
            new_height = int(track_height * scale_factor)

            # Scale the track image
            scaled_track = pygame.transform.scale(track_image, (new_width, new_height))

            # Calculate center position
            x = (TRACK_CANVAS_WIDTH - new_width) // 2
            y = (TRACK_CANVAS_HEIGHT - new_height) // 2

            # Blit the scaled track onto the white surface
            self.AI_SURFACE.blit(scaled_track, (x, y))

            self.TRACK_LENGTH = calculate_track_length(img)
            self.draw_border()
        else:
            self.set_foreground()
            self.draw_border()

    def draw_border(self) -> None:
        pygame.draw.rect(
            self.AI_SURFACE,
            Color.BLACK,
            self.AI_SURFACE.get_rect(),
            self.BORDER_THICKNESS,
        )
        pygame.draw.rect(
            self.FOREGROUND,
            Color.BLACK,
            self.FOREGROUND.get_rect(),
            self.BORDER_THICKNESS,
        )

    # Only used for map
    def set_foreground(self) -> None:
        # First load the tilemap with decorative tiles
        tileset = self.load_tileset(self.MAP_TILESET_PATH)
        self.load_tilemap(tileset)

        # Then load the roads for AI navigation
        self.load_roads()

    def load_tileset(self, path: str) -> pygame.Surface:
        tileset = pygame.image.load(path).convert_alpha()
        tileset = pygame.transform.scale_by(tileset, TILEMAP_RATIO)
        return tileset

    def load_tilemap(self, tileset: pygame.Surface) -> None:
        # Get tileset dimensions
        tile_width = tileset.get_width() // 11  # 11 columns in tileset
        tile_height = tileset.get_height() // 20  # 20 rows in tileset

        # Clear the foreground surface
        self.FOREGROUND.fill(Color.WHITE)

        # First pass to determine the actual map bounds
        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = 0, 0

        for y, row in enumerate(self.MAP_DATA):
            for x, tile_id in enumerate(row):
                if (
                    tile_id == "" or tile_id == "0"
                ):  # Skip empty cells or tiles with ID 0
                    continue

                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

        # Calculate the actual map dimensions
        map_width = (max_x - min_x + 1) * tile_width
        map_height = (max_y - min_y + 1) * tile_height

        # Calculate the offset to center the map
        offset_x = (TRACK_CANVAS_WIDTH - map_width) // 2
        offset_y = (TRACK_CANVAS_HEIGHT - map_height) // 2

        # Ensure we don't have negative offsets (this would happen if map is larger than canvas)
        offset_x = max(0, offset_x)
        offset_y = max(0, offset_y)

        # Store the offset for later use in road positioning
        self.map_offset_x = offset_x - min_x * tile_width
        self.map_offset_y = offset_y - min_y * tile_height

        # Draw each tile according to the MAP_DATA with centering offset
        for y, row in enumerate(self.MAP_DATA):
            for x, tile_id in enumerate(row):
                if tile_id == "":  # Skip empty cells
                    continue

                # Convert to integer and subtract 1 (CSV data starts from 1)
                tile_id = int(tile_id) - 1

                # Calculate position in tileset
                # For an 11x20 tileset, we need to convert the linear index to x,y coordinates
                tile_x = tile_id % 11  # 11 tiles per row
                tile_y = tile_id // 11

                # Create a rect for the source tile
                tile_rect = pygame.Rect(
                    tile_x * tile_width, tile_y * tile_height, tile_width, tile_height
                )

                # Calculate destination position with centering offset
                dest_x = x * tile_width + self.map_offset_x
                dest_y = y * tile_height + self.map_offset_y

                # Draw the tile on the foreground
                self.FOREGROUND.blit(tileset, (dest_x, dest_y), tile_rect)

    def load_roads(self) -> None:
        # Roads data is in self.ROADS_DATA 0 for white 1 for black
        BOX_SIZE = 80 * TILEMAP_RATIO

        # Create a new surface for AI track with transparent background
        self.AI_SURFACE = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.AI_SURFACE.fill(Color.WHITE)  # Fill with white background

        # Process road data and draw on AI_SURFACE
        for y, row in enumerate(self.ROADS_DATA):
            for x, road in enumerate(row):
                if road == "":  # Skip empty cells
                    continue

                # Calculate position with the same offset used for the map
                dest_x = x * BOX_SIZE + getattr(self, "map_offset_x", 0)
                dest_y = y * BOX_SIZE + getattr(self, "map_offset_y", 0)

                # Convert road value to int (0 for white, 1 for black)
                try:
                    road_value = int(road)
                    # Create road rectangle
                    road_rect = pygame.Rect(dest_x, dest_y, BOX_SIZE, BOX_SIZE)

                    # Draw appropriate color based on road value
                    if road_value == 1:
                        # Black for actual roads
                        pygame.draw.rect(self.AI_SURFACE, Color.BLACK, road_rect)
                    else:
                        # White or transparent for non-road areas
                        pygame.draw.rect(self.AI_SURFACE, Color.WHITE, road_rect)
                except ValueError:
                    print(f"Invalid road data at {x},{y}: {road}")

        # Convert AI_SURFACE to PIL Image to get the TRACK_LENGTH
        surface_string = pygame.image.tostring(self.AI_SURFACE, "RGB")
        surface_size = self.AI_SURFACE.get_size()
        pil_image = Image.frombytes("RGB", surface_size, surface_string)

        # Calculate the track length using the same function used for regular tracks
        self.TRACK_LENGTH = calculate_track_length(pil_image)
        print(f"Track length calculated: {self.TRACK_LENGTH}")

        # Redraw the border after filling in road data
        self.draw_border()

        # Also update the GRID_SURFACE with the same offset
        self.create_grid()

    def load_roads_from_points(
        self,
        start_point: tuple[int, int],
        end_point: tuple[int, int],
        track_position: tuple[int, int] | None = None,
    ) -> None:
        """Generate the shortest path between start and end points using A* algorithm.
        Only creates paths where roads exist according to ROADS_DATA.

        Args:
            start_point: Starting point coordinates (x, y) on the screen
            end_point: Ending point coordinates (x, y) on the screen
            track_position: Position of the track on the screen (if None, uses absolute coordinates)
        """
        # Clear AI surface with white background
        self.AI_SURFACE = pygame.Surface(
            (TRACK_CANVAS_WIDTH, TRACK_CANVAS_HEIGHT), pygame.SRCALPHA
        )
        self.AI_SURFACE.fill(Color.WHITE)

        # Calculate grid size based on TILEMAP_RATIO
        BOX_SIZE = 80 * TILEMAP_RATIO

        # Get map offsets
        offset_x = getattr(self, "map_offset_x", 0)
        offset_y = getattr(self, "map_offset_y", 0)

        # Adjust start and end points based on track position and map offset
        if track_position:
            # Convert screen coordinates to track coordinates
            adjusted_start = (
                start_point[0] - track_position[0],
                start_point[1] - track_position[1],
            )
            adjusted_end = (
                end_point[0] - track_position[0],
                end_point[1] - track_position[1],
            )

            # Ensure the points are within track bounds
            adjusted_start = (
                max(0, min(adjusted_start[0], TRACK_CANVAS_WIDTH - 1)),
                max(0, min(adjusted_start[1], TRACK_CANVAS_HEIGHT - 1)),
            )
            adjusted_end = (
                max(0, min(adjusted_end[0], TRACK_CANVAS_WIDTH - 1)),
                max(0, min(adjusted_end[1], TRACK_CANVAS_HEIGHT - 1)),
            )

            print(f"Original points: {start_point} -> {end_point}")
            print(f"Adjusted points: {adjusted_start} -> {adjusted_end}")
        else:
            # Use absolute coordinates
            adjusted_start = start_point
            adjusted_end = end_point

        # First, let's create a grid representing where roads exist from ROADS_DATA
        # 0 = no road, 1 = road
        grid_width = (
            len(self.ROADS_DATA[0]) if self.ROADS_DATA and self.ROADS_DATA[0] else 0
        )
        grid_height = len(self.ROADS_DATA)

        # Create a grid with roads information
        road_grid = []
        for y in range(grid_height):
            row = []
            for x in range(len(self.ROADS_DATA[y])):
                road_value = 0
                if self.ROADS_DATA[y][x] and self.ROADS_DATA[y][x] != "":
                    try:
                        road_value = int(self.ROADS_DATA[y][x])
                    except ValueError:
                        pass
                row.append(road_value)
            road_grid.append(row)

        # A* pathfinding implementation
        def heuristic(a, b):
            """Manhattan distance heuristic"""
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def get_neighbors(pos, max_width, max_height):
            """Get valid neighbor cells that have roads (4-directional movement)"""
            x, y = pos
            neighbors = []
            # Check all 4 directions (up, right, down, left)
            for nx, ny in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                new_x, new_y = x + nx, y + ny
                # Ensure neighbor is within grid bounds and is a road
                if (
                    0 <= new_x < max_width
                    and 0 <= new_y < max_height
                    and new_y < len(road_grid)
                    and new_x < len(road_grid[new_y])
                    and road_grid[new_y][new_x] == 1
                ):
                    neighbors.append((new_x, new_y))
            return neighbors

        # Convert pixel coordinates to grid coordinates, accounting for the map offset
        start_grid = (
            int((adjusted_start[0] - offset_x) / BOX_SIZE),
            int((adjusted_start[1] - offset_y) / BOX_SIZE),
        )
        end_grid = (
            int((adjusted_end[0] - offset_x) / BOX_SIZE),
            int((adjusted_end[1] - offset_y) / BOX_SIZE),
        )

        # Ensure start and end are within grid bounds
        start_grid = (
            min(max(0, start_grid[0]), grid_width - 1 if grid_width > 0 else 0),
            min(max(0, start_grid[1]), grid_height - 1 if grid_height > 0 else 0),
        )
        end_grid = (
            min(max(0, end_grid[0]), grid_width - 1 if grid_width > 0 else 0),
            min(max(0, end_grid[1]), grid_height - 1 if grid_height > 0 else 0),
        )

        print(f"Grid coordinates: {start_grid} -> {end_grid}")

        # If start or end is not on a road, find the nearest road
        if (
            start_grid[1] < len(road_grid)
            and start_grid[0] < len(road_grid[start_grid[1]])
            and road_grid[start_grid[1]][start_grid[0]] != 1
        ):
            print("Start point is not on a road. Finding nearest road...")
            # Simple search for nearest road
            nearest_road = None
            min_distance = float("inf")
            for y in range(len(road_grid)):
                for x in range(len(road_grid[y])):
                    if road_grid[y][x] == 1:
                        dist = abs(x - start_grid[0]) + abs(y - start_grid[1])
                        if dist < min_distance:
                            min_distance = dist
                            nearest_road = (x, y)
            if nearest_road:
                start_grid = nearest_road
                print(f"Adjusted start to nearest road: {start_grid}")

        if (
            end_grid[1] < len(road_grid)
            and end_grid[0] < len(road_grid[end_grid[1]])
            and road_grid[end_grid[1]][end_grid[0]] != 1
        ):
            print("End point is not on a road. Finding nearest road...")
            # Simple search for nearest road
            nearest_road = None
            min_distance = float("inf")
            for y in range(len(road_grid)):
                for x in range(len(road_grid[y])):
                    if road_grid[y][x] == 1:
                        dist = abs(x - end_grid[0]) + abs(y - end_grid[1])
                        if dist < min_distance:
                            min_distance = dist
                            nearest_road = (x, y)
            if nearest_road:
                end_grid = nearest_road
                print(f"Adjusted end to nearest road: {end_grid}")

        # A* algorithm
        # Priority queue for open nodes
        open_set = {start_grid}
        # Set of already processed nodes
        closed_set = set()
        # Track where each node came from for path reconstruction
        came_from = {}

        # G-score: cost from start to current node (using dictionaries with int values)
        g_score = {}
        g_score[start_grid] = 0
        # F-score: estimated total cost (g_score + heuristic)
        f_score = {}
        f_score[start_grid] = heuristic(start_grid, end_grid)

        # Main A* loop
        while open_set:
            # Get node with lowest f_score
            current = None
            lowest_f = float("inf")
            for pos in open_set:
                if pos in f_score and f_score[pos] < lowest_f:
                    lowest_f = f_score[pos]
                    current = pos

            if current is None:
                break  # No path found

            # If we reached the end, reconstruct and draw the path
            if current == end_grid:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_grid)
                path.reverse()

                # Draw the path on AI_SURFACE with proper map offset
                for grid_pos in path:
                    road_rect = pygame.Rect(
                        grid_pos[0] * BOX_SIZE + offset_x,
                        grid_pos[1] * BOX_SIZE + offset_y,
                        BOX_SIZE,
                        BOX_SIZE,
                    )
                    pygame.draw.rect(self.AI_SURFACE, Color.BLACK, road_rect)

                break

            # Remove current from open set and add to closed set
            open_set.remove(current)
            closed_set.add(current)

            # Check all neighbors
            for neighbor in get_neighbors(current, grid_width, grid_height):
                # Skip if already processed
                if neighbor in closed_set:
                    continue

                # Calculate tentative g_score
                tentative_g_score = g_score.get(current, float("inf")) + 1

                # If neighbor not in open set, add it
                if neighbor not in open_set:
                    open_set.add(neighbor)
                # If this path is not better, skip
                elif tentative_g_score >= g_score.get(neighbor, float("inf")):
                    continue

                # This path is the best so far, record it
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = int(
                    tentative_g_score + heuristic(neighbor, end_grid)
                )

        # Convert AI_SURFACE to PIL Image to calculate track length
        surface_string = pygame.image.tostring(self.AI_SURFACE, "RGB")
        surface_size = self.AI_SURFACE.get_size()
        pil_image = Image.frombytes("RGB", surface_size, surface_string)

        # Calculate track length
        self.TRACK_LENGTH = calculate_track_length(pil_image)
        print(
            f"Generated path from {start_point} to {end_point}. Track length: {self.TRACK_LENGTH}"
        )

        self.OVERLAY_SURFACE = self.AI_SURFACE.copy()
        # Remove white background
        self.OVERLAY_SURFACE.set_colorkey(Color.WHITE)

        for y in range(self.OVERLAY_SURFACE.get_height()):
            for x in range(self.OVERLAY_SURFACE.get_width()):
                color = self.OVERLAY_SURFACE.get_at((x, y))
                if color.r == 0 and color.g == 0 and color.b == 0:
                    self.OVERLAY_SURFACE.set_at(
                        (x, y), pygame.Color(255, 250, 205, 128)
                    )

        # Draw border
        self.draw_border()

    # AI Ke liye
    def get_ai_track(self) -> pygame.Surface:
        return self.AI_SURFACE

    # Screen Pe draw kar diya
    def draw(
        self, screen: pygame.Surface, position: tuple[int, int] | pygame.Rect
    ) -> None:
        if not self.IS_MAP:
            screen.blit(self.AI_SURFACE, position)
        else:
            screen.blit(self.FOREGROUND, position)

            if self.SHOW_OVERLAY and self.OVERLAY_SURFACE is not None:
                screen.blit(self.OVERLAY_SURFACE, position)

            if self.SHOW_GRID:
                if isinstance(position, pygame.Rect):
                    grid_pos = position.topleft
                else:
                    grid_pos = position

                screen.blit(self.GRID_SURFACE, grid_pos)
