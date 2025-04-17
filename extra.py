#  if not self.on_ground:
#             if self.y_vel < 0:
#                 sprite_sheet = "jump"
#             elif self.y_vel > 1:
#                 sprite_sheet = "fall"
#             else:
#                 sprite_sheet = "jump"
#         elif self.x_vel != 0:
#             sprite_sheet = "run"
#         else:
#             sprite_sheet = "idle"

#         sprite_sheet_name = f"{sprite_sheet}_{self.direction}"

#         # Reset animation if state changed
#         if sprite_sheet_name != self.current_sprite_sheet:
#             self.animation_count = 0
#             self.current_sprite_sheet = sprite_sheet_name

#         sprites = self.SPRITES.get(sprite_sheet_name)
#         if not sprites or len(sprites) == 0:
#             print(f"[ERROR] No sprites for {sprite_sheet_name}")
#             self.sprite = pygame.Surface((self.rect.width, self.rect.height))
#             return

#         # Calculate frame index safely
#         self.animation_count += 1
#         max_count = len(sprites) * self.ANIMATION_DELAY

#         if self.animation_count >= max_count:
#             self.animation_count = 0  # Loop animation when it reaches end

#         sprite_index = self.animation_count // self.ANIMATION_DELAY
#         sprite_index = min(sprite_index, len(sprites) - 1)  # Clamp for safety

#         # Set the sprite
#         print(f"[DEBUG] Sheet: {sprite_sheet_name}, Frame: {sprite_index}/{len(sprites)}, Anim Count: {self.animation_count}")


#         self.sprite = sprites[sprite_index]
#         self.update()