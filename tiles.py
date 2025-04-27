import pygame
import os
import csv
from main import Block, load_sprite_sheets


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = load_sprite_sheets("Terrain", "terrain.png", 96 ,96 , False)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface, offset_x, offset_y):
        print(surface)
        full_surface = surface.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
        return full_surface


class TileMap():
    def __init__(self, file_name):
        self.tile_size = 96
        self.start_y = 0
        self.start_x = 0
        self.tiles = self.load_tiles(file_name)
        self.surface = pygame.Surface((self.tile_map_w, self.tile_map_h))
        self.load_map()
    
    def draw_map(self, surface, offset_x, offset_y):
        surface.blit(self.surface, (self.tile_map_w - offset_x, self.tile_map_h - offset_y))
        return surface

    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.surface, 0, 0)

        return self.surface


    def read_cvs(self, file_name):
        tileMap_1 = []
        with open(os.path.join(file_name)) as data:
            data = csv.reader(data, delimiter=",")
            for row in data:
                tileMap_1.append(list(row))
        return tileMap_1
    
    def load_tiles(self, file_name):
        tiles = []
        map = self.read_cvs(file_name)
        x = 0
        y = 0
        block_size = 96
        for row in map:
            x = 0
            for tile in row:
                if tile == "0":
                    tiles.append(Block(x, y, block_size, 0, 0))
                elif tile == "1":
                    tiles.append(Block(x, y, block_size, 96, 0))
                elif tile == "2":
                    tiles.append(Block(x, y, block_size, 192, 0))
                elif tile == "5":
                    tiles.append(Block(x, y, block_size, 0, 96))
                elif tile == "6":
                    tiles.append(Block(x, y, block_size, 96, 96))
                elif tile == "7":
                    tiles.append(Block(x, y, block_size, 192, 96))
                    # Checks next column in csv map
                x += 1
            # Checks next row in csv map
            y += 1
        
        # Stores the size of the whole map
        self.tile_map_w = len(map[0]) * block_size
        self.tile_map_h = len(map) * block_size
        print(tiles)
        return tiles


    def get_tiles(self):
        return self.tiles





