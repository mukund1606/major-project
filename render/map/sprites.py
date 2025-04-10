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
    def __init__(self, x: int, y: int, spritesheet: Spritesheet):
        self._layer = BLOCK_LAYER

        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(Color.WHITE)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class Water(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, spritesheet: Spritesheet):
        self._layer = BLOCK_LAYER

        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(Color.BLUE)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class Tree(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, spritesheet: Spritesheet):
        self._layer = BLOCK_LAYER

        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(Color.GREEN)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y


class Road(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, tile_type: str, spritesheet: Spritesheet):
        self._layer = ROAD_LAYER

        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE

        self.visible = True  # Normal roads are visible
        self.is_underground = tile_type == "U"

        if tile_type == "1":  # 80 * 160
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = spritesheet.get_sprite(0, 0, self.width, self.height)

        elif tile_type == "z":  # 80 * 160
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = spritesheet.get_sprite(80, 0, self.width, self.height)

        elif tile_type == "a":  # 80 * 160
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = spritesheet.get_sprite(342, 176, self.width, self.height)

        elif tile_type == "2":  # 160 * 80
            self.width = 2 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = spritesheet.get_sprite(0, 166, self.width, self.height)

        elif tile_type == "x":  # 160 * 80
            self.width = 2 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = spritesheet.get_sprite(0, 244, self.width, self.height)

        elif tile_type == "b":  # 160 * 80
            self.width = 2 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = spritesheet.get_sprite(439, 176, self.width, self.height)

        elif tile_type == "C":  # 160 * 160
            self.width = 2 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = spritesheet.get_sprite(169, 179, self.width, self.height)

        elif tile_type == "3":  # 160 * 240
            self.width = 2 * TILE_SIZE
            self.height = 3 * TILE_SIZE
            self.image = spritesheet.get_sprite(3, 338, self.width, self.height)

        elif tile_type == "y":  # 160 * 240
            self.width = 2 * TILE_SIZE
            self.height = 3 * TILE_SIZE
            self.image = spritesheet.get_sprite(171, 342, self.width, self.height)

        elif tile_type == "c":  # 160 * 80
            self.width = 2 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = spritesheet.get_sprite(337, 343, self.width, self.height)

        elif tile_type == "w":  # 320 * 80
            self.width = 4 * TILE_SIZE
            self.height = TILE_SIZE
            self.image = spritesheet.get_sprite(338, 431, self.width, self.height)

        elif tile_type == "4":  # 240 * 160
            self.width = 3 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = spritesheet.get_sprite(0, 586, self.width, self.height)

        elif tile_type == "d":  # 240 * 160
            self.width = 3 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = spritesheet.get_sprite(247, 585, self.width, self.height)

        elif tile_type == "v":  # 80 * 160
            self.width = TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = spritesheet.get_sprite(493, 513, self.width, self.height)

        elif tile_type == "e":  # 80 * 320
            self.width = TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = spritesheet.get_sprite(671, 430, self.width, self.height)

        elif tile_type == "L":  # 640 * 160
            self.width = 8 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = spritesheet.get_sprite(167, 1, self.width, self.height)

        elif tile_type == "H":  # 800 * 320
            self.width = 10 * TILE_SIZE
            self.height = 4 * TILE_SIZE
            self.image = spritesheet.get_sprite(5, 757, self.width, self.height)

        elif tile_type == "E":  # 560 * 560
            self.width = 7 * TILE_SIZE
            self.height = 7 * TILE_SIZE
            self.image = spritesheet.get_sprite(858, 20, self.width, self.height)

        elif tile_type == "O":  # 320 * 160
            self.width = 4 * TILE_SIZE
            self.height = 2 * TILE_SIZE
            self.image = spritesheet.get_sprite(817, 603, self.width, self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
