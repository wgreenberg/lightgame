import pygame, sys, os, math
from entity import Entity, Player
from level import Level
from camera import Camera
from random import randint, choice
from pygame.sprite import Sprite
from pymunk.vec2d import Vec2d

globals = { 'SCREEN_WIDTH': 1000,
            'SCREEN_HEIGHT': 1000,
            'WASD_KEYS': (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d),
            'BG_COLOR': (0, 0, 0) }

def run_game():
  
  pygame.init()
  clock = pygame.time.Clock()
  screen = pygame.display.set_mode((globals['SCREEN_WIDTH'], globals['SCREEN_HEIGHT']), 0, 32)
  
  currently_held_keys = []
  
  #debug stuff
  lvl = Level("testlevel.txt", screen) 
  playerCam = Camera((85,85), globals['SCREEN_WIDTH'], globals['SCREEN_HEIGHT'])
  originCam = Camera((0,0), globals['SCREEN_WIDTH'], globals['SCREEN_HEIGHT'])
  player = Player("resources/robodude.png", screen, (85,85), playerCam)
  currentCam = player.camera
  entities = []
  
  entities.append(player)
 
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        exit_game()
      if event.type == pygame.KEYDOWN:
        currently_held_keys.append(event.key)
      if event.type == pygame.KEYUP:
        currently_held_keys.remove(event.key)
    
    currentCam = player.camera

    for keydown in currently_held_keys:
      if keydown in globals['WASD_KEYS']:
        player.movement_handler(keydown)
      #debug stuff
      if keydown == pygame.K_1:
        currentCam = originCam
    
    time_passed = clock.tick(50)
    screen.fill(globals['BG_COLOR'])

    # debug stuff
    pygame.display.set_caption('Lightgame : %d fps' % clock.get_fps())
    corners = currentCam.get_corners()
    lvl.draw_visible_level(corners[0], corners[1])
    player.update(time_passed, lvl, currentCam)
    player.draw(currentCam)
    
    lights_per_entity = [entity.lights for entity in entities]
    all_lights = [light for lights in lights_per_entity for light in lights]
    currentCam.render_light(screen, all_lights)

    pygame.display.flip()

def exit_game():
  sys.exit()

run_game()
