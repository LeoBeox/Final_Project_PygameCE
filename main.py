import os
from os import listdir
from os.path import isfile, join
import math
import random
import pygame
from pygame.locals import *

#Start Pygame
pygame.init()

#Window Title
pygame.display.set_caption("Fox Trot")

#Main Macros
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

def get_block(size, startX):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(startX, 0, size, size)
    surface.blit(image, (0, 0), area=rect)
     # return pygame.transform.scale2x(surface)
    return surface

class Health():
    def __init__(self, maxHealth):
        self.maxHealth = maxHealth
        self.current_health = maxHealth
        
    
    
    pass

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
        self.current_sprite_sheet = None
        self.hit = False
        self.hit_count = 0 
        self.can_move = True
        self.health = 3


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def makeHit(self):
        self.hit = True
        self.hit_count = 0
        self.can_move = True
        self.health -= 1
        self.hearts()

        if self.direction == "left":
            self.x_vel = 50
        elif self.direction == "right":
            self.x_vel = -50

    def hearts(self):
        if self.health == 0:
            print("Died")


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
        # Apply movement
        self.move(self.x_vel, self.y_vel)

        # Gravity only if not grounded (i.e., not standing on something)
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        if self.hit:
            self.hit_count += 1
            if self.hit_count > FPS:
                self.hit = False
                self.can_move = True

        self.update_sprite()


    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            sprite_sheet = "jump"
        elif self.y_vel > 1:
            sprite_sheet = "fall"
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

    def draw(self, win, offset_x, offset_y):
        try:
            win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
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

    def draw(self, win, offset_x, offset_y):
        # Debug: draw a green rectangle to see where the player should be
        # pygame.draw.rect(win, (0, 255, 0), self.rect)  # Green fill for visibility

        try:
            win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))
        except Exception as e:
            print("Error drawing sprite:", e)

        # Debug:
        # pygame.draw.rect(win, (255, 0, 0), self.rect, 2)  # draw red outline

class Block(Object):
    
    def __init__(self, x, y, size, startX):
        super().__init__(x, y, size, size, startX)  
        block = get_block(size, startX)
        if block:
            self.image.blit(block, (0, 0))
        else:
            self.image.fill((0, 255, 0))  # bright green if loading fails
        self.mask = pygame.mask.from_surface(self.image)  

class Rune(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "rune")
        self.rune = load_sprite_sheets("Traps", "Rune", width, height)
        self.image = self.rune["rune"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "rune"

    def idle(self):
        self.animation_name = "rune"

    def loop(self):
        
        sprites = self.rune[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
            
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.update()

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

    def update(self):
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)  # Update the mask


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()

    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = [i * width, j * height]
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, objects, offset_x, offset_y):
    for tile in background:
        window.blit(bg_image, tile)
   
    for obj in objects:
        obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    player.rect.y += dy
    player.update()


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
    if not player.can_move:
        return
    
    keys = pygame.key.get_pressed()

    player.x_vel = 0

    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.moveLeft(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.moveRight(PLAYER_VEL) 
        

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "rune":
            player.makeHit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("purblueBG.png")

    block_size = 96

    player = Player(100, 100, 50, 50)

    rune = Rune(100, HEIGHT - block_size - 64, 32, 64)
    rune2 = Rune(500, HEIGHT - block_size - 300, 32, 64)

    
    floor = [Block(i * block_size, HEIGHT - block_size, block_size, 0) for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    blocks = [Block(0, HEIGHT - block_size, block_size, 0)]
    objects = [*floor , Block(0, HEIGHT - block_size * 2, block_size, 0), 
               Block(block_size * 3, HEIGHT - block_size * 4, block_size, 0),
               Block(block_size * 6, HEIGHT - block_size * 6, block_size, 96),
               Block(block_size * 6, HEIGHT - block_size * 4, block_size, 192),
               rune,
               rune2]
    
    offset_x, offset_y = 0, 0
    scroll_area_width, scroll_area_height = 200, 300
    CAMERA_BOTTOM_LIMIT = -block_size + 96
    CAMERA_RIGHT_LIMIT = 1200
    CAMERA_LEFT_LIMIT = -1200

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
        rune.loop()
        rune2.loop()
        handle_movement(player, objects)

        draw(window, background, bg_image, player, objects, offset_x, offset_y)

        #Offsets X-Camera to the player so that it is centered
        target_offset_x = player.rect.x - WIDTH // 2 + player.rect.width // 2

        # Changes X-Camera so it does not go beyond right limit
        offset_x = min(target_offset_x, CAMERA_RIGHT_LIMIT)

        # Offsets Y-Camera to the player so that it is centered
        target_offset_y = player.rect.y - HEIGHT // 2 + player.rect.height // 2  

        # Changes Y-Camera so it does not go beyond ground limit
        offset_y = min(target_offset_y, CAMERA_BOTTOM_LIMIT)

            

    pygame.quit()
    quit()       
   
    pass

#Begins Main Function
if __name__ == "__main__":
    main(window)

