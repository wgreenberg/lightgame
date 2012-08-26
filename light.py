import pygame, math
from pygame.sprite import Sprite
from pymunk.vec2d import Vec2d

class Light():
  HEIGHT = 100.5 # height lights are held from the ground
  PRESET_SURFACE_WIDTH = 200
  PRESET_SURFACE_LENGTH = 200
  MIN_DEFLECTION_ANGLE = 20.0
  MIN_WIDTH = 60.0
  MIN_LENGTH = 60.0
  MAX_LENGTH = 600.0

  def __init__(self, color, emitter_pos, projection_pos, direction, aperture_angle):
    self.emitter_pos = Vec2d(emitter_pos) # position of the emitter (flashlight)
    self.proj_pos = Vec2d(projection_pos) # center of the light ellipse
    self.direction = direction
    self.aperture_angle = aperture_angle
    self.deflection_angle = self.get_deflection_angle()
    
    # for the light surface, begin with a preset size, create the mask,
    # and then scale from there
    self.base_alpha_surface = pygame.Surface((self.PRESET_SURFACE_WIDTH, self.PRESET_SURFACE_LENGTH), pygame.SRCALPHA)
    self.alpha_surface = pygame.Surface((self.PRESET_SURFACE_WIDTH, self.PRESET_SURFACE_LENGTH), pygame.SRCALPHA)
    self.set_alpha_surface_mask()

    self.base_color_surface = pygame.Surface((self.PRESET_SURFACE_WIDTH, self.PRESET_SURFACE_LENGTH), pygame.SRCALPHA)
    self.color_surface = pygame.Surface((self.PRESET_SURFACE_WIDTH, self.PRESET_SURFACE_LENGTH), pygame.SRCALPHA)
    self.set_color_surface_mask(color)
    
    self.l_width, self.l_length = 100,100
    self.polylist = []
    
    
    
  # get_projection_dimensions: calculate and return the dimensions of the
  # light "image" (the ellipse which represents the unhindered projection)
  def get_projection_dimensions(self):
    # get the length
    d1 = self.HEIGHT * math.tan(math.radians(90.0 - (self.deflection_angle + self.aperture_angle/2.0)))
    d2 = self.HEIGHT * math.tan(math.radians(90.0 - (self.deflection_angle - self.aperture_angle/2.0)))
    length = abs(d2 - d1)
    if length < self.MIN_LENGTH:
      length = self.MIN_LENGTH
    if length > self.MAX_LENGTH:
      length = self.MAX_LENGTH
    
    # get the width
    emit_to_proj = self.emitter_pos - self.proj_pos
    flashlight_to_proj = math.sqrt((emit_to_proj.length)**2 + (self.HEIGHT)**2)
    width = 2.0 * math.tan(math.radians(self.aperture_angle/2.0)) * flashlight_to_proj
    width = abs(width)
    if width < self.MIN_WIDTH:
      width = self.MIN_WIDTH
      
    if math.degrees(self.deflection_angle) < abs(self.MIN_DEFLECTION_ANGLE):
      width, length = self.MIN_WIDTH, self.MIN_LENGTH
    
    return (int(width), int(length))
    
  # get_deflection_angle: given the current emitter/projection positions,
  # calculate and return the deflection angle, which represents the angle
  # between the light source and the horizontal
  def get_deflection_angle(self):
    emit_to_proj = self.emitter_pos - self.proj_pos
    d = emit_to_proj.length
    
    theta = math.atan2(self.HEIGHT, d)
    if theta<0:
      deflection = (180*(theta + (math.pi*2))/math.pi)
    else:
      deflection = (180*(theta)/math.pi)
    
    return deflection
  
  # given a list of opaque shadows, paint the appropriate shadows
  # on the surfaces
  def get_polygon_list(self, level):
    tiles = self.get_opaque_tiles(level)

    pointlist = []
    for tile in tiles:
      pointlist.append(self.get_shadow_points(tile))
      
    return pointlist 
  
  # return a list of Tiles which are in the projection area, and
  # which light does not go through
  def get_opaque_tiles(self, level):
    realwidth = self.alpha_surface.get_rect().width
    realheight = self.alpha_surface.get_rect().height
    right_edge_pos = self.proj_pos.x + realwidth/2
    bot_edge_pos = self.proj_pos.y + realheight/2
    offset_pos = (self.proj_pos[0] - realwidth/2, self.proj_pos[1] - realheight/2)
    
    # set corners for tiles_at()
    proj_top_left = offset_pos
    proj_bot_right = (right_edge_pos, bot_edge_pos)
    
    tiles_in_projection_area = level.tiles_at(proj_top_left, proj_bot_right)
    opaque_tiles = [tile for tile in tiles_in_projection_area if not tile.attributes["shinethrough"]]
    
    return opaque_tiles
  
  # given the location of the emitter, as well as another point and 
  # a distance, return the point on the line formed by the emitter
  # position and p2, which is dist away from the emitter
  def trace_point(self, p2, dist):
    x1, y1 = self.emitter_pos.x, self.emitter_pos.y
    x2, y2 = p2.x, p2.y
    theta = math.atan2((y2-y1),(x2-x1))    
    if theta<0:
      d= (180*(theta+(math.pi*2))/math.pi)
    else:
      d= (180*(theta)/math.pi)
    dx = math.cos(math.radians(d))
    dy = math.sin(math.radians(d))                
    
    return (x2 + dx*dist, y2 + dy*dist)

  # given a tile, return a list of points which forms the polygon
  # that represents the shadow formed by shining the light from
  # the emitter position onto the tile
  def get_shadow_points(self, tile):
    # define light->tile directions in terms of coordinates, which 
    # follow this convention:
    #  nw: (-1, 1)  | n: (0, 1)  | ne: (1, 1)
    #   w: (0, -1)  |  TILE POS  |  e: (0, 1)
    #  sw: (-1, -1) | s: (0, -1) | se: (-1, 1)
    southwest, west, northwest, south, center, north, southeast, east, northeast = [(ew, ns) for ew in (-1, 0, 1) for ns in (-1, 0, 1)] 
    dir_to_tile = tile.direction_from(self)

    # get the 'real' dimensions of the rotated light surface
    rot_height = self.alpha_surface.get_rect().height
    rot_width = self.alpha_surface.get_rect().width

    # grab the biggest dimension, as it will be used as the
    # far edge of the shadow polygon
    if rot_height > rot_width:
      trace_to_dim = rot_height
    else:
      trace_to_dim = rot_width
    
    # based on the direction from light->til, store points for
    # the shadow polygon
    pointlist = []
    if dir_to_tile == north:
      pointlist.append(self.trace_point(tile.topleft, trace_to_dim))
      pointlist.append(self.trace_point(tile.topright, trace_to_dim))
      pointlist= pointlist + [(tile.topleft.x, tile.topleft.y), (tile.topright.x,tile.topright.y)][::-1]
    if dir_to_tile == south:
      pointlist.append(self.trace_point(tile.botleft, trace_to_dim))
      pointlist.append(self.trace_point(tile.botright, trace_to_dim))
      pointlist = pointlist + [(tile.botleft.x, tile.botleft.y), (tile.botright.x, tile.botright.y)][::-1]
    if dir_to_tile == east:
      pointlist.append(self.trace_point(tile.topright, trace_to_dim))
      pointlist.append(self.trace_point(tile.botright, trace_to_dim))
      pointlist = pointlist + [(tile.topright.x, tile.topright.y), (tile.botright.x, tile.botright.y)][::-1]
    if dir_to_tile == west:
      pointlist.append(self.trace_point(tile.topleft, trace_to_dim))
      pointlist.append(self.trace_point(tile.botleft, trace_to_dim))
      pointlist = pointlist + [(tile.topleft.x, tile.topleft.y), (tile.botleft.x, tile.botleft.y)][::-1]
    if dir_to_tile == northeast:
      pointlist.append(self.trace_point(tile.topleft, trace_to_dim))
      pointlist.append(self.trace_point(tile.botright, trace_to_dim))
      pointlist = pointlist + [(tile.topleft.x, tile.topleft.y), (tile.topright.x, tile.topright.y), (tile.botright.x, tile.botright.y)][::-1]
    if dir_to_tile == northwest:
      pointlist.append(self.trace_point(tile.topright, trace_to_dim))
      pointlist.append(self.trace_point(tile.botleft, trace_to_dim))
      pointlist = pointlist + [(tile.topright.x, tile.topright.y), (tile.topleft.x, tile.topleft.y), (tile.botleft.x, tile.botleft.y)][::-1]
    if dir_to_tile == southeast:
      pointlist.append(self.trace_point(tile.topright, trace_to_dim))
      pointlist.append(self.trace_point(tile.botleft, trace_to_dim))
      pointlist = pointlist + [(tile.topright.x, tile.topright.y), (tile.botright.x, tile.botright.y), (tile.botleft.x, tile.botleft.y)][::-1]
    if dir_to_tile == southwest:
      pointlist.append(self.trace_point(tile.topleft, trace_to_dim))
      pointlist.append(self.trace_point(tile.botright, trace_to_dim))
      pointlist = pointlist + [(tile.topleft.x, tile.topleft.y), (tile.botleft.x, tile.botleft.y), (tile.botright.x, tile.botright.y)][::-1]
    
    return pointlist
  
  # maps (x, y) pairs to values from [0, 1] for use in making
  # gradient masks. Presently just uses the linear distance
  # from the center of the surface
  def channel_scaling_coeff(self, x, y):
    center = self.PRESET_SURFACE_WIDTH/2
    coeff = math.sqrt((x-center)**2 + (y-center)**2)/center
    if(coeff > 1):
      coeff = 1
    return coeff
  
  def set_alpha_surface_mask(self):
    self.base_alpha_surface.fill((0,0,0))
    mask = pygame.surfarray.pixels_alpha(self.base_alpha_surface)
    size = self.PRESET_SURFACE_WIDTH
    
    for x in range(size):
      for y in range(size):
        mask[x][y] = 255 * (1 - self.channel_scaling_coeff(x, y))
        
  def set_color_surface_mask(self, color):
    self.base_color_surface.fill(color)
    mask = pygame.surfarray.pixels3d(self.base_color_surface)
    size = self.PRESET_SURFACE_WIDTH
    
    for x in range(size):
      for y in range(size):
        coeff = self.channel_scaling_coeff(x, y)
        mask[x][y] = [color[0] * (1-coeff), color[1] * (1-coeff), color[2] * (1-coeff)]
        
  # update_surface: given the current light state, along with the current
  # level, redraw the light shape 
  def update_surface(self, level):
    self.deflection_angle = self.get_deflection_angle()
    self.l_width, self.l_length = self.get_projection_dimensions()
    self.direction = -(self.proj_pos-self.emitter_pos ).get_angle_degrees() + 90.0
    self.polylist = self.get_polygon_list(level)
    
    del self.alpha_surface
    self.alpha_surface = pygame.Surface((self.l_width, self.l_length), pygame.SRCALPHA)
    pygame.transform.scale(self.base_alpha_surface, (self.l_width, self.l_length), self.alpha_surface)
    self.alpha_surface = pygame.transform.rotate(self.alpha_surface, self.direction)

    del self.color_surface
    self.color_surface = pygame.Surface((self.l_width, self.l_length), pygame.SRCALPHA)
    pygame.transform.scale(self.base_color_surface, (self.l_width, self.l_length), self.color_surface)
    self.color_surface = pygame.transform.rotate(self.color_surface, self.direction)
    
