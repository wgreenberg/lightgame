import pygame, sys, os, math
from random import randint, choice
from pygame.sprite import Sprite
from pymunk.vec2d import Vec2d

globals = { 'SCREEN_WIDTH': 600,
            'SCREEN_HEIGHT': 600,
            'WASD_KEYS': (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d),
            'BG_COLOR': (255, 255, 0) }

def run_game():
  
  pygame.init()
  clock = pygame.time.Clock()
  screen = pygame.display.set_mode((globals['SCREEN_WIDTH'], globals['SCREEN_HEIGHT']), 0, 32)
  
  currently_held_keys = []
  
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        exit_game()
      if event.type == pygame.KEYDOWN:
        if event.key in globals['WASD_KEYS']:
          currently_held_keys.append(event.key)
      if event.type == pygame.KEYUP:
        if event.key in globals['WASD_KEYS']:
          currently_held_keys.remove(event.key)
    
    screen.fill(globals['BG_COLOR'])
    pygame.display.flip()

def exit_game():
  sys.exit()

run_game()