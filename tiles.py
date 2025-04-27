import pygame
import os
import csv


class Tile(pygame.sprite.Sprite):
    tile_image = None
    
    def __init__(self, x, y, size, startX, startY):
        super().__init__()
        self.rect = pygame.Rect(x, y, size, size)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)

        if Tile.tile_image is None:
            path = os.path.join("assets", "Terrain", "Terrain.png")
            Tile.tile_image = pygame.image.load(path).convert_alpha()
        
        tile_surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
        rect = pygame.Rect(startX, startY, size, size)
        tile_surface.blit(Tile.tile_image, (0, 0), area=rect)

        self.image.blit(tile_surface, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


    def draw(self, surface, offset_x, offset_y):
        surface.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class TileMap():
    def __init__(self, file_name):
        self.tile_size = 96
        self.start_y = 0
        self.start_x = 0
        self.tiles = self.load_tiles(file_name)
    
    def draw_map(self, surface, offset_x, offset_y):
        # Draws only the visible tiles by checking offset to see if its in current view.
        for tile in self.tiles:
            if (tile.rect.x - offset_x > -self.tile_size and
                tile.rect.x - offset_x < surface.get_width() and
                tile.rect.y - offset_y > -self.tile_size and
                tile.rect.y - offset_y < surface.get_height()):

                tile.draw(surface, offset_x, offset_y)

        return surface

    def read_csv(self, file_name):
        tileMap_1 = []
        with open(os.path.join(file_name)) as data:
            data = csv.reader(data, delimiter=",")
            for row in data:
                tileMap_1.append(list(row))
        return tileMap_1
    
    def load_tiles(self, file_name):
        tiles = []
        csv_map = self.read_csv(file_name)
        block_size = self.tile_size

        y = 0

        for row in csv_map:
            x = 0
            for tile in row:
                if tile == "-1":
                    pass
                elif tile == "0":
                    tiles.append(Tile(x * block_size, y * block_size, block_size, 0, 0))
                elif tile == "1":
                    tiles.append(Tile(x * block_size, y * block_size, block_size, 96, 0))
                elif tile == "2":
                    tiles.append(Tile(x * block_size, y * block_size, block_size, 192, 0))
                elif tile == "5":
                    tiles.append(Tile(x * block_size, y * block_size, block_size, 0, 96))
                elif tile == "6":
                    tiles.append(Tile(x * block_size, y * block_size, block_size, 96, 96))
                elif tile == "7":
                    tiles.append(Tile(x * block_size, y * block_size, block_size, 192, 96))
                    # Checks next column in csv map
                x += 1
            # Checks next row in csv map
            y += 1
        
        # Stores the size of the whole map
        self.tile_map_w = len(csv_map[0]) * block_size
        self.tile_map_h = len(csv_map) * block_size
        return tiles


    def get_tiles(self):
        return self.tiles





