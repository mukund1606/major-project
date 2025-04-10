import pygame
from data_models import Color
from constants import TILE_SIZE
from tilemap import TILEMAP
from render.map.sprites import Spritesheet, Block, Road, Tree, Water


class MapGenerator:
    def __init__(self):
        pygame.init()
        self.road_spritesheet = Spritesheet("assets/sprites/road.png")
        self.map_width = len(TILEMAP[0]) * TILE_SIZE
        self.map_height = len(TILEMAP) * TILE_SIZE

    def generate_map_surface(self):
        """Generate a surface containing the entire map"""
        map_surface = pygame.Surface((self.map_width, self.map_height))
        map_surface.fill(Color.BLACK)

        for i, row in enumerate(TILEMAP):
            for j, column in enumerate(row):
                if column == "B":
                    block = Block(j, i, self.road_spritesheet)
                    map_surface.blit(block.image, (block.rect.x, block.rect.y))
                elif column == "W":
                    water = Water(j, i, self.road_spritesheet)
                    map_surface.blit(water.image, (water.rect.x, water.rect.y))
                elif column == "G":
                    tree = Tree(j, i, self.road_spritesheet)
                    map_surface.blit(tree.image, (tree.rect.x, tree.rect.y))
                elif column in "1za2xbC3ycw4dveLHEO":
                    road = Road(j, i, column, self.road_spritesheet)
                    map_surface.blit(road.image, (road.rect.x, road.rect.y))

        return map_surface
