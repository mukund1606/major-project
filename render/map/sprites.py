import pygame

from data_models import Color
from constants import TILE_SIZE, BLOCK_LAYER, ROAD_LAYER


class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(Color.GREEN)
        return sprite


class Block(pygame.sprite.Sprite):
    def __init__(
        self,
        x: int,
        y: int,
        tile_type: str,
        building_spritesheet: Spritesheet,
        boundary_spritesheet: Spritesheet,
    ):
        self._layer = BLOCK_LAYER

        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE

        if tile_type == "B":
            self.width = TILE_SIZE
            self.height = TILE_SIZE
            self.image = pygame.Surface([self.width, self.height])
            self.image.fill(Color.BLACK)

        elif tile_type == "h":
            self.width = 4 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(0, 11, self.width, self.height)

        elif tile_type == "<":
            self.width = 4 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                806, 351, self.width, self.height
            )

        elif tile_type == ">":
            self.width = 4 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                806, 433, self.width, self.height
            )

        elif tile_type == "p":
            self.width = 10 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                1, 351, self.width, self.height
            )

        elif tile_type == "!":
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                1045, 520, self.width, self.height
            )

        elif tile_type == "t":
            self.width = 4 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                1, 522, self.width, self.height
            )

        elif tile_type == "$":
            self.width = 4 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                1, 1502, self.width, self.height
            )

        elif tile_type == "@":
            self.width = 4 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                328, 1502, self.width, self.height
            )

        elif tile_type == "m":
            self.width = 8 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                593, 5, self.width, self.height
            )

        elif tile_type == "W":
            self.width = 8 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                2, 1684, self.width, self.height
            )

        elif tile_type == "Z":
            self.width = 8 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                653, 851, self.width, self.height
            )

        elif tile_type == "n":
            self.width = 3 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                1497, 3, self.width, self.height
            )

        elif tile_type == "I":
            self.width = TILE_SIZE
            self.height = TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                648, 1178, self.width, self.height
            )

        elif tile_type == "q":
            self.width = 2 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                1240, 5, self.width, self.height
            )

        elif tile_type == "r":
            self.width = 5 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                1240, 216, self.width, self.height
            )

        elif tile_type == "s":
            self.width = 2 * TILE_SIZE
            self.height = 1 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                1240, 386, self.width, self.height
            )

        elif tile_type == "R":
            self.width = 8 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                1, 850, self.width, self.height
            )

        elif tile_type == "A":
            self.width = 8 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                0, 1174, self.width, self.height
            )

        elif tile_type == "F":
            self.width = 8 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                366, 521, self.width, self.height
            )

        elif tile_type == "l":
            self.width = 10 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = boundary_spritesheet.get_sprite(
                5, 1075, self.width, self.height
            )

        elif tile_type == "g":
            self.width = 8 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = boundary_spritesheet.get_sprite(
                7, 391, self.width, self.height
            )

        elif tile_type == "M":
            self.width = 8 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = boundary_spritesheet.get_sprite(
                775, 1, self.width, self.height
            )

        elif tile_type == "Q":
            self.width = 8 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = boundary_spritesheet.get_sprite(
                845, 721, self.width, self.height
            )

        elif tile_type == "T":
            self.width = 10 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = boundary_spritesheet.get_sprite(
                666, 392, self.width, self.height
            )

        elif tile_type == "*":
            self.width = 10 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = boundary_spritesheet.get_sprite(
                5, 722, self.width, self.height
            )

        elif tile_type == "/":
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                339, 2, self.width, self.height
            )

        elif tile_type == "|":
            self.width = 2 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                429, 2, self.width, self.height
            )

        elif tile_type == "#":
            self.width = TILE_SIZE
            self.height = TILE_SIZE
            self.image = building_spritesheet.get_sprite(
                429, 86, self.width, self.height
            )

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class Tree(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, boundary_spritesheet: Spritesheet):
        self._layer = BLOCK_LAYER

        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.image = boundary_spritesheet.get_sprite(0, 92, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class Road(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, tile_type: str, road_spritesheet: Spritesheet):
        self._layer = ROAD_LAYER

        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE

        self.visible = True  # Normal roads are visible
        self.is_underground = tile_type == "U"

        if tile_type == "1":
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(0, 0, self.width, self.height)

        elif tile_type == "z":
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(80, 0, self.width, self.height)

        elif tile_type == "a":
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(342, 176, self.width, self.height)

        elif tile_type == "2":
            self.width = 2 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = road_spritesheet.get_sprite(0, 166, self.width, self.height)

        elif tile_type == "x":
            self.width = 2 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = road_spritesheet.get_sprite(0, 244, self.width, self.height)

        elif tile_type == "b":
            self.width = 2 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = road_spritesheet.get_sprite(439, 176, self.width, self.height)

        elif tile_type == "C":
            self.width = 2 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(169, 179, self.width, self.height)

        elif tile_type == "3":
            self.width = 2 * TILE_SIZE
            self.height = 3 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(3, 338, self.width, self.height)

        elif tile_type == "y":
            self.width = 2 * TILE_SIZE
            self.height = 3 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(171, 342, self.width, self.height)

        elif tile_type == "c":
            self.width = 2 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = road_spritesheet.get_sprite(337, 343, self.width, self.height)

        elif tile_type == "w":
            self.width = 4 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = road_spritesheet.get_sprite(338, 431, self.width, self.height)

        elif tile_type == "4":
            self.width = 3 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(0, 586, self.width, self.height)

        elif tile_type == "d":
            self.width = 3 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(247, 585, self.width, self.height)

        elif tile_type == "v":
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(493, 513, self.width, self.height)

        elif tile_type == "e":
            self.width = TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(671, 430, self.width, self.height)

        elif tile_type == "L":
            self.width = 8 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(167, 1, self.width, self.height)

        elif tile_type == "H":
            self.width = 10 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(5, 757, self.width, self.height)

        elif tile_type == "E":
            self.width = 7 * TILE_SIZE
            self.height = 7 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(858, 20, self.width, self.height)

        elif tile_type == "O":
            self.width = 4 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(817, 603, self.width, self.height)

        elif tile_type == "f":
            self.width = 2 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = road_spritesheet.get_sprite(1, 1094, self.width, self.height)

        elif tile_type == "+":
            self.width = TILE_SIZE
            self.height = TILE_SIZE
            self.image = road_spritesheet.get_sprite(1, 1094, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
