import pygame, sys, os, math
from tile import Tile
from pygame.sprite import Sprite

TILE_DIMENSION = 32

class Level():
  
  # Level constructor:
  # takes the secreen and a file-path to the text file
  # which contains the level
  def __init__(self, level_path, screen):
    Tile.load_images()
    self.screen = screen
    self.level_path = level_path
    self.tiles = self.parse_level() #2D array containing tile codes (ints)
    
  # parse_level:
  # Given the file path for the level text file,
  # return a 2D array containing all tiles. Coordinates
  # of each tile are positioned at their top left corner
  def parse_level(self):
    level_file = open(self.level_path)
    map_so_far = []
    x = 0
    y = 0
    for line in level_file:
      x = 0
      map_row = []
      for char in list(line.strip()):
        this_tile = Tile(self.screen, x, y, char, TILE_DIMENSION)
        map_row.append(this_tile)    
        x = x+TILE_DIMENSION
      map_so_far.append(map_row)
      y = y+TILE_DIMENSION
    
    level_file.close()
    return map_so_far
  
  def tile_at(self, coordinates):
    x = naturalize(coordinates[0]/TILE_DIMENSION)
    y = naturalize(coordinates[1]/TILE_DIMENSION)
    
    if y < len(self.tiles):
      if x < len(self.tiles[y]):
        return self.tiles[y][x]
      
    return -1
  
  def tiles_at(self, box_top_left_corner, box_bot_right_corner):
    x_lower_bound = naturalize(box_top_left_corner[0]/TILE_DIMENSION )
    x_upper_bound = naturalize(box_bot_right_corner[0]/TILE_DIMENSION +1)
    y_lower_bound = naturalize(box_top_left_corner[1]/TILE_DIMENSION )
    y_upper_bound = naturalize(box_bot_right_corner[1]/TILE_DIMENSION +1)
    tiles = []
    
    for row in self.tiles[y_lower_bound:y_upper_bound]:
      for tile in row[x_lower_bound:x_upper_bound]:
        #tile.image = pygame.image.load("resources/robodude.png")
        tiles.append(tile)
        
    return tiles
  
  # draw_visible_level:
  # Given dimensions/location of a camera, select subset of
  # tiles which belong on screen and draw them.
  # DESCRIPTION: each tile is TILE_DIMENSIONxTILE_DIMENSIONpx, so for a tile at idexes [m][n],
  # that's m*TILE_DIMENSION pixels from the left of the real origin,
  # and n*TILE_DIMENSION pixels from the top of the real origin. So,
  # given that our screen is looking at pixels from
  # cam_top_left_corner to cam_bot_right_corner, find the
  # index bounds of the subset
  # NOTE: this method should be generalized to return
  #       a subset of tiles within a radius of an object
  def draw_visible_level(self, cam_top_left_corner, cam_bot_right_corner):
    x_lower_bound = naturalize(cam_top_left_corner[0]/TILE_DIMENSION)
    x_upper_bound = naturalize(cam_bot_right_corner[0]/TILE_DIMENSION + 1)
    y_lower_bound = naturalize(cam_top_left_corner[1]/TILE_DIMENSION)
    y_upper_bound = naturalize(cam_bot_right_corner[1]/TILE_DIMENSION + 1)
    #print("{0} {1} {2} {3}".format(x_lower_bound, x_upper_bound, y_lower_bound, y_upper_bound))
    for row in self.tiles[y_lower_bound:y_upper_bound]:
      for tile in row[x_lower_bound:x_upper_bound]:
        tile.draw_tile(cam_top_left_corner[0], cam_top_left_corner[1])
        
# Naturalizes a number. Duh.
def naturalize(num):
  if num > 0:
    return int(num)
  return 0
