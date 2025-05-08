import os
from os import listdir
from os.path import isfile, join
import math
import random
import pygame
from pygame.locals import *
from tiles import *

#Start Pygame
pygame.init()

#Window Title
pygame.display.set_caption("Goblin Trot")

#Main Macros
BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800
CANVAS_WIDTH, CANVAS_HEIGHT = 4800, 1200
FPS = 60
PLAYER_VEL = 5

# Sets window display size
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Gets the flipped version of sprites that have a direction (ie. left or right)
def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

# Loads the sprite sheets from the given directory and returns a dictionary of sprites
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

        # Adds the sprites with the proper direction for easier calling.
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    
    return all_sprites

# Gets the block from the terrain sprite sheet, returns a surface with the block image.
def get_block(size, startX, startY):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(startX, startY, size, size)
    surface.blit(image, (0, 0), area=rect)
    return surface

# Handles health display and damage for player and enemies. 
class Health:
    def __init__(self, x, y, maxHealth, entity=None):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.max_health = maxHealth
        self.current_health = maxHealth
        self.sprites = load_sprite_sheets("Utility", "Health", 32, 32, False)
        self.sprite_name = "life"
        self.frame = self.current_health
        self.entity = entity
        self.fixed_pos = True
        self.offset_x = 40   # For un-fixed positions v
        self.offset_y = -50

    # Handles damage and returns alive value as boolean  
    def take_damage(self, damage):
        self.current_health = max(0, self.current_health - damage)
        return self.current_health <= 0
    
    # Updates the health display position based on the entity's position, except for when fixed_pos is True
    def update(self):
        if self.entity and not self.fixed_pos:
            self.rect.x = self.entity.rect.x + self.offset_x
            self.rect.y = self.entity.rect.y + self.offset_y


    # Draws the health display on the canvas and determines which frame to display based on current health
    def draw(self, canvas, offset_x=0, offset_y=0):
        
        frame_index = self.max_health - self.current_health

        if frame_index >= len(self.sprites[self.sprite_name]):
            frame_index = len(self.sprites[self.sprite_name]) - 1

        sprite = self.sprites[self.sprite_name][frame_index]
        
        if self.fixed_pos:
            canvas.blit(sprite, (self.rect.x, self.rect.y))
        else:
            canvas.blit(sprite, (self.rect.x - offset_x, self.rect.y - offset_y))

# Handles the player character, as well as health, movement, animation, and some collision detection.       
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
        self.hit = False
        self.hit_count = 0 
        self.can_move = True
        self.is_alive = True
        self.max_health = 3
        self.health_display = Health(925, 20, self.max_health, self)
        self.health_display.fixed_pos = True


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def makeHit(self):
        self.hit = True
        self.hit_count = 0
        
        is_dead = self.health_display.take_damage(1)

        if is_dead:
            self.is_alive = False
            
        if self.direction == "left":
            self.x_vel = 30
        elif self.direction == "right":
            self.x_vel = -30

        self.can_move = False

    def moveLeft(self, vel):
        if not self.can_move:
            return
        
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def moveRight(self, vel):
        if not self.can_move:
            return
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def jump(self, jump_vel):
        if not self.can_move:
            return

        if self.jump_count < 2:
            self.y_vel = jump_vel
            self.animation_count = 0
            self.jump_count += 1
            self.on_ground = False  # No longer on the ground after jumping

    def loop(self, FPS):
        # Apply movement
        self.move(self.x_vel, self.y_vel)

        # Gravity only if not on ground
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.fall_count += 1

        if self.hit:
            self.hit_count += 1
            if self.hit_count > FPS:
                self.hit = False
                self.can_move = True

        self.health_display.update()

        # print(self.y_vel) # Debug
        self.update_sprite()


    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.y_vel *= -1

    def update_sprite(self):

        sprite_sheet = "idle"

        if self.is_alive == False:
            sprite_sheet = "dead" 
            self.can_move = False
        elif self.hit:
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

    def draw(self, canvas, offset_x, offset_y):
        try:
            canvas.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
            self.health_display.draw(canvas, offset_x, offset_y)
        except Exception as e:
            print("Error drawing sprite:", e)

# Handles the enemey character, as well as health, movement, animation, and some collision detection.
class Enemy(pygame.sprite.Sprite):
    
    ANIMATION_DELAY = 5
    
    def __init__(self, x, y, width, height, patrol_distance=200):
        super().__init__()
        self.name = "enemy"
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 2  # Default patrol speed
        self.fall_count = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.sprite = None
        self.sprites = load_sprite_sheets("Enemies", "EvilWizard", 32, 32, True)
        self.hit = False
        self.hit_count = 0
        self.can_move = True
        self.is_alive = True
        self.max_health = 3
        self.health_display = Health(x, y-20, self.max_health, self)
        self.health_display.fixed_pos = False
        
        # Patrol variables
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.patrol_right_bound = x + patrol_distance
        self.patrol_left_bound = x

    def move(self, dx):
        self.rect.x += dx

    def makeHit(self):
        self.hit = True
        self.hit_count = 0

        is_dead = self.health_display.take_damage(1)

        if is_dead:
            self.is_alive = False

        self.can_move = False

    def moveLeft(self, vel):
        if not self.can_move:
            return

        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def moveRight(self, vel):  
        if not self.can_move:
            return
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def patrol(self):
        # Patrol back and forth within bounds
        if self.rect.x >= self.patrol_right_bound:
            self.direction = "left"
            self.x_vel = -abs(self.x_vel)  # Ensure negative velocity
            self.animation_count = 0
        elif self.rect.x <= self.patrol_left_bound:
            self.direction = "right"
            self.x_vel = abs(self.x_vel)  # Ensure positive velocity
            self.animation_count = 0

    def loop(self, FPS):
        # Handle patrol movement if alive and can move
        if self.is_alive and self.can_move:
            self.patrol()
            self.move(self.x_vel)

        # Reset hit state after delay
        if self.hit:
            self.hit_count += 1
            if self.hit_count > FPS:
                self.hit = False
                self.can_move = True

        self.health_display.update()
        
        self.update_sprite()


    def update_sprite(self):
        sprite_sheet = "moving"  # Default animation

        if not self.is_alive:
            sprite_sheet = "dead"
            self.can_move = False
        elif self.hit:
            sprite_sheet = "hit"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.sprites[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)

        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, canvas, offset_x, offset_y):
        try:
            canvas.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
            self.health_display.draw(canvas, offset_x, offset_y)
        except Exception as e:
            print("Error drawing enemy sprite:", e)

# Class for game objects, such as blocks and runes (Kinda replaced with tile and tilemap, but still works for game end and rune)
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

# Class for blocks in the game.
class Block(Object):
    
    def __init__(self, x, y, size, startX, startY):
        super().__init__(x, y, size, size)  
        block = get_block(size, startX, startY)
        if block:
            self.image.blit(block, (0, 0))
        else:
            self.image.fill((0, 255, 0))  # bright green just in case loading fails
        self.mask = pygame.mask.from_surface(self.image)  

# Class for Rune Traps in the game
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

# Draws Everything onto the screen
def draw(canvas, window, background, bg_image, player, objects, enemies, tilemap, offset_x, offset_y):
    canvas.fill((0, 0, 0, 0))

    for tile in background:
        canvas.blit(bg_image, tile)

    tilemap.draw_map(canvas, offset_x, offset_y)



    for obj in objects:
        if obj not in tilemap.get_tiles():
            obj.draw(canvas, offset_x, offset_y)

    for enemy in enemies:
        enemy.draw(canvas, offset_x, offset_y)

    player.draw(canvas, offset_x, offset_y)

    window.blit(canvas, (0, 0))

    

    pygame.display.update()

def handle_vertical_collision(player, objects, tilemap, dy):
    collided_objects = []
    player.rect.y += dy
    player.update()


    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):

            horizontal_overlap = min(player.rect.right - obj.rect.left,
                                    obj.rect.right - player.rect.left)
            if horizontal_overlap > 10:

                if dy > 0:  # Player is falling
                    player.rect.bottom = obj.rect.top
                    player.landed()  # Reset jump count and set player on ground
                elif dy < 0:  # Player is jumping upwards
                    player.rect.top = obj.rect.bottom
                    player.hit_head()  # Handle hitting the ceiling
                
            collided_objects.append(obj)

    for tile in tilemap.tiles:
        if pygame.sprite.collide_mask(player, tile):

            horizontal_overlap = min(player.rect.right - tile.rect.left,
                                    tile.rect.right - player.rect.left)
            
            if horizontal_overlap > 10:
                if dy > 0:  # Player is falling
                    player.rect.bottom = tile.rect.top
                    player.landed()  # Reset jump count and set player on ground
                elif dy < 0:  # Player is jumping upwards
                    player.rect.top = tile.rect.bottom
                    player.hit_head()  # Handle hitting the ceiling
            
            collided_objects.append(tile)

    return collided_objects

# Handles the collisions between the player and the enemies.
def handle_enemy_collisions(player, enemies):

    for enemy in enemies:
        if enemy.is_alive and pygame.sprite.collide_mask(player, enemy):
            # Checks if the player rect is coliding with enemy rect.
            player_bottom = player.rect.bottom
            enemy_top = enemy.rect.top
            vertical_tolerance = 25 # Leniance
            
            if (abs(player_bottom - enemy_top) < vertical_tolerance and player.y_vel > 0):
                # Enemy gets hit.
                enemy.makeHit()
                # Make the player bounce slightly
                player.y_vel = -8
            else:
                # Player gets hit.
                player.makeHit()


def collide(player, objects, tilemap, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if player.rect.colliderect(obj.rect):
                collided_object = obj
                break

    for tile in tilemap.tiles:
        if pygame.sprite.collide_mask(player, tile):
            if player.rect.colliderect(tile.rect):
                collided_object = tile
                break


    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_movement(player, objects, tilemap):
    keys = pygame.key.get_pressed()

    player.x_vel = 0

    if player.can_move:
        collide_left = collide(player, objects, tilemap, -PLAYER_VEL * 2)
        collide_right = collide(player, objects, tilemap, PLAYER_VEL * 2)

        if keys[pygame.K_LEFT] and not collide_left:
            player.moveLeft(PLAYER_VEL)
        if keys[pygame.K_RIGHT] and not collide_right:
            player.moveRight(PLAYER_VEL) 
    else:
            
        collide_left = collide(player, objects, tilemap, PLAYER_VEL * 2)
        collide_right = collide(player, objects, tilemap, PLAYER_VEL * 2)
        

    vertical_collide = handle_vertical_collision(player, objects, tilemap, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if type(obj) == Tile:
            break
        if obj and obj.name == "rune":
            player.makeHit()
        elif obj and obj.name == "enemy":
            player.makeHit()


# Main Function that handles everything that happens, including window, time, sprites, and logic.
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("purblueBG.png")

    block_size = 96

    player = Player(45, 1650, 50, 50)
    JUMP_VEL = -6

    # Runes
    rune = Rune(3 * block_size + 15, 17 * block_size + 20, 32, 64)
    rune2 = Rune(500, HEIGHT - block_size - 300, 32, 64)
    rune3 = Rune(46 * block_size + 15, 10 * block_size + 30, 32, 64)
    rune4 = Rune(45 * block_size + 15, 10 * block_size + 30, 32, 64)
    rune5 = Rune(24 * block_size, 8 * block_size, 32, 64)
    rune6 = Rune(25 * block_size, 15.25 * block_size, 32, 64)
    rune7 = Rune(30 * block_size, 5 * block_size, 32, 64)
    rune8 = Rune(40 * block_size, -1 * block_size, 32, 64)
    rune9 = Rune(41 * block_size, 8 * block_size, 32, 64)
    rune10 = Rune(44 * block_size, 13 * block_size + 15, 32, 64)

    # Enemies
    enemy1 = Enemy(8 * block_size, 12.4 * block_size, 32, 32, 5.25 * block_size)
    enemy2 = Enemy(28 * block_size, 8.4 * block_size, 32, 32, 6.25 * block_size)
    enemy3 = Enemy(35 * block_size, 16.4 * block_size, 32, 32, 3.25 * block_size)
    enemy4 = Enemy(38 * block_size, 12.4 * block_size, 32, 32, 4.25 * block_size)
    
    objects = [rune, rune2, rune3, rune4, rune5, rune6, rune7, rune8, rune9, rune10]
    enemies = [enemy1, enemy2, enemy3, enemy4]
    
    canvas = pygame.surface.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))

    offset_x, offset_y = 0, 0
    tilemap = TileMap('GoblinBroMap1.csv')

    CAMERA_BOTTOM_LIMIT = 1100
    CAMERA_RIGHT_LIMIT = 3800
    CAMERA_LEFT_LIMIT = 0

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump(JUMP_VEL)
        player.loop(FPS)
        
        for rune in objects:
            rune.loop()

        for enemy in enemies:
            enemy.loop(FPS)

        handle_movement(player, objects, tilemap)
        handle_enemy_collisions(player, enemies)
        
        draw(canvas, window, background, bg_image, player, objects, enemies, tilemap, offset_x, offset_y)

        #Offsets X-Camera to the player so that it is centered
        target_offset_x = player.rect.x - WIDTH // 2 + player.rect.width // 2

        offset_x += (target_offset_x - offset_x) * 0.15 # Smoothness 

        # Changes X-Camera so it does not go beyond right limit
        offset_x = max(CAMERA_LEFT_LIMIT, min(target_offset_x, CAMERA_RIGHT_LIMIT))

        # Offsets Y-Camera to the player so that it is centered
        target_offset_y = player.rect.y - HEIGHT // 2 + player.rect.height // 2  

        offset_y += (target_offset_y - offset_y) * 0.15 # Smoothness 

        # Changes Y-Camera so it does not go beyond ground limit
        offset_y = min(target_offset_y, CAMERA_BOTTOM_LIMIT)

            

    pygame.quit()
    quit()       
   
    pass

#Begins Main Function
if __name__ == "__main__":
    main(window)

