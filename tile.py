import pygame, sys, os, math
from pymunk.vec2d import Vec2d
from pygame.sprite import Sprite

#Tile attributes:
#  movethrough: [true/false] player can move through it
#  shinethrough: [true/false] light can shine through it 
#  drawbelow: [true/false] light/player 'move' on top of it
#  visible: [true/false] appears on scren

types = { "wall": {"movethrough": False,
                   "shinethrough": False,
                   "drawbelow": False,
                   "visible": True },
          "floor": {"movethrough": True,
                    "shinethrough": True,
                    "drawbelow": True,
                    "visible": True } 
         }

char_to_type = { "#": "wall",
                 ".": "floor" }

images = { "wall": "resources/wall.png",
           "blank": "resources/blank.png",
           "floor": "resources/floor.png" }

class Tile(Sprite):
  @staticmethod  
  def load_images():
    for key in images:
      images[key] = pygame.image.load(images[key]).convert()
 
  def __init__(self, screen, rxpos, rypos, tile_character, tile_dim):
    Sprite.__init__(self)
    self.screen = screen
    self.rxpos = rxpos
    self.rypos = rypos
    self.tile_type = char_to_type[tile_character]
    self.attributes = types[self.tile_type]
    self.image = images[self.tile_type]
    self.dimension = tile_dim
    self.topleft = Vec2d(self.rxpos, self.rypos)
    self.topright = Vec2d(self.rxpos + self.dimension, self.rypos)
    self.botleft = Vec2d(self.rxpos, self.rypos + self.dimension)
    self.botright = Vec2d(self.rxpos + self.dimension, self.rypos + self.dimension)
    self.corners = [self.topleft, self.topright, self.botleft, self.botright]

    # debug
    self.dbflag = False

  def debug_paint_tile(self):
    self.dbflag = True
    self.image = images["blank"]
    
  #Given the (dx, dy) of the real origin to the camera origin,
  #draw the tile onto screen coordinates
  def draw_tile(self, xoffset, yoffset):
    sx = self.rxpos - xoffset
    sy = self.rypos - yoffset
    draw_pos = self.image.get_rect().move(sx, sy)
    self.screen.blit(self.image, draw_pos)
    if self.dbflag:
      self.image = images[self.tile_type]
      self.dbflag = False

  # given an emitter, return the tuple which describes
  # the direction from the EMITTER to the TILE
  def direction_from(self, light):
    epos = light.emitter_pos
     
    # ew = -1 if west, 0 if neither, 1 if east
    # ns = -1 if south, 0 if neither, 1 if north
    if epos.x < self.topleft.x:
      ew = -1
    elif epos.x > self.botright.x:
      ew = 1
    else:
      ew = 0
      
    if epos.y > self.botright.y:
      ns = -1
    elif epos.y < self.topleft.y:
      ns = 1
    else:
      ns = 0
      
    return (ew, ns)
