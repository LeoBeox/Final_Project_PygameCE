import os
from os import listdir
from os.path import isfile, join
import math
import random
import pygame
from pygame.locals import *

pygame.init()

pygame.display.set_caption("Platformer")

BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range (sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))


        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0, 0), area=rect)
     # return pygame.transform.scale2x(surface)
    return surface



class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacter", "GoblinBro", 32, 32, True)
    ANIMATION_DELAY = 5
    
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.gravity_enabled = True
        self.on_ground = False  # New flag to check if on the ground
        self.current_sprite_sheet = None


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def moveLeft(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def moveRight(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def jump(self):
        if self.jump_count < 2:
            self.y_vel = -self.GRAVITY * 8
            self.animation_count = 0
            self.jump_count += 1
            self.on_ground = False  # No longer on the ground after jumping

    def loop(self, FPS):
        if self.gravity_enabled:
            self.move(self.x_vel, self.y_vel)
            if not self.on_ground:
                self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
                self.fall_count += 1
            else:
                self.y_vel = 0
        else:
            self.move(self.x_vel, 0)
        
        # If no collision happened yet and player is not on floor, they're falling
        if self.y_vel > 0 and not self.on_ground:
            self.on_ground = False  # ensures state resets correctly mid-air
            
        self.update_sprite()

    def landed(self):
        if not self.on_ground:
            self.fall_count = 0
            self.y_vel = 0
            self.jump_count = 0
            self.on_ground = True  # Player is on the ground after landing
    
    def hit_head(self):
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if not self.on_ground:
            if self.y_vel < 0:
                sprite_sheet = "jump"
            elif self.y_vel > 1:
                sprite_sheet = "fall"
            else:
                sprite_sheet = "jump"
        elif self.x_vel != 0:
            sprite_sheet = "run"
        else:
            sprite_sheet = "idle"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        
        # print(f"[DEBUG] Sheet: {sprite_sheet_name}, Frame: {sprite_index}/{len(sprites)}, Anim Count: {self.animation_count}, Y_Vel: {self.y_vel}")
        
        self.sprite = sprites[sprite_index]

        self.animation_count += 1

        self.update()






    def update(self):
        self.rect.topleft = (self.rect.x, self.rect.y)  # Set the position of the rect based on x and y coordinates
        self.mask = pygame.mask.from_surface(self.sprite)  # Update the mask

    def draw(self, win, offset_x):
        try:
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        except Exception as e:
            print("Error drawing sprite:", e)

class Object(pygame.sprite.Sprite):

    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        # Debug: draw a green rectangle to see where the player should be
        # pygame.draw.rect(win, (0, 255, 0), self.rect)  # Green fill for visibility

        try:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        except Exception as e:
            print("Error drawing sprite:", e)

        # Debug:
        # pygame.draw.rect(win, (255, 0, 0), self.rect, 2)  # draw red outline

class Block(Object):
    
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)  
        block = get_block(size)
        if block:
            self.image.blit(block, (0, 0))
        else:
            self.image.fill((0, 255, 0))  # bright green if loading fails
        self.mask = pygame.mask.from_surface(self.image)  



def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()

    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)
   
    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:  # Player is falling
                player.rect.bottom = obj.rect.top
                player.landed()  # Reset jump count and set player on ground
            elif dy < 0:  # Player is jumping upwards
                player.rect.top = obj.rect.bottom
                player.hit_head()  # Handle hitting the ceiling
            
            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if player.rect.colliderect(obj.rect):
                collided_object = obj
                break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_movement(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0

    collide_left = collide(player, objects, -PLAYER_VEL)
    collide_right = collide(player, objects, PLAYER_VEL)

    if keys[pygame.K_LEFT] and not collide_left:
        player.moveLeft(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.moveRight(PLAYER_VEL) 
        

    handle_vertical_collision(player, objects, player.y_vel)



def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("purblueBG.png")

    player = Player(100, 100, 50, 50)

    block_size = 96
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    blocks = [Block(0, HEIGHT - block_size, block_size)]
    objects = [*floor , Block(0, HEIGHT - block_size * 2, block_size), 
               Block(block_size * 3, HEIGHT - block_size * 4, block_size)]
    
    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()
        player.loop(FPS)
        handle_movement(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (
            player.rect.right - offset_x <= scroll_area_width and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()       
   
    pass

if __name__ == "__main__":
    main(window)

