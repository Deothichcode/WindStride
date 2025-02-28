import pygame
from pygame.locals import*

pygame.init()

screen_with = 1000
screen_height = 800

screen = pygame.display.set_mode((screen_with,screen_height))
pygame.display.set_caption('Wind Stride')

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
pygame.quit()