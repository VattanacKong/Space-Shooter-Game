import pygame
import os

assets = "D:\TUX\Space Invaders (2)\Space Invaders"

#this script cut a long explosion picture into smaller pieces to display as explosion animation
EXPLOSION_SHEET = pygame.image.load(os.path.join(assets,"assets", "explosion_blue.png"))

FRAME_WIDTH = EXPLOSION_SHEET.get_width() /24  
FRAME_HEIGHT = EXPLOSION_SHEET.get_height()

for i in range(24):
    x = i  * FRAME_WIDTH
    y = 0
    piece = EXPLOSION_SHEET.subsurface((x, y, FRAME_WIDTH, FRAME_HEIGHT))
    pygame.image.save(piece, os.path.join('D:\TUX\Space Invaders (2)\Space Invaders/assets\explosion',f"explosion_{i}.png"))