import pygame, math, numpy
from pymunk import Vec2d

class Camera():

  def __init__(self, init_pos, screenwidth, screenheight):
    self.rxpos = init_pos[0]
    self.rypos = init_pos[1]
    self.screen_width = screenwidth
    self.screen_height = screenheight
    self.shadow_mask = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
    
  def move(self, newpos):
    # move the camera to a new coordinate position
    self.rxpos = newpos[0]
    self.rypos = newpos[1]
    
  def get_corners(self):
    # return the top left and bottom right corner coordinates
    topleft = (self.rxpos, self.rypos)
    botright = (self.rxpos + self.screen_width,
                self.rypos + self.screen_height)
    
    return (topleft, botright)
  
  # real_to_screen: given a pair of real world coordinates, return
  # their position in this camera's vision grid
  def real_to_screen(self, rx, ry):
    top_left_corner = self.get_corners()[0]
    sx = rx - top_left_corner[0]
    sy = ry - top_left_corner[1]
    
    return (sx, sy)
    
  # screen_to_real: given a pair of coordinates referring to this
  # camera's vision grid, return their real world analogue
  def screen_to_real(self, sx, sy):
    top_left_corner = self.get_corners()[0]
    rx = sx + top_left_corner[0]
    ry = sy + top_left_corner[1]
    
    return (rx, ry)
   
 
  def render_light(self, screen, list_of_lights):
    screen_width, screen_height = self.screen_width, self.screen_height
    
    # fill screen with darkness, full alpha
    self.shadow_mask.fill((1,1,1,255)) 
    
    # for every light that's visible on screen, subtract that alpha value
    # from the darkness
    for light in list_of_lights:
      # offset the center by the rotated surface's dimensions
      realwidth = light.alpha_surface.get_rect().width
      realheight = light.alpha_surface.get_rect().height
      xoffset_pos = light.proj_pos.x - realwidth/2
      yoffset_pos = light.proj_pos.y - realheight/2

      # get the screen position of the surface
      light_spos = self.real_to_screen(xoffset_pos, yoffset_pos)
      
      self.shadow_mask.blit(light.alpha_surface, light_spos, None, pygame.BLEND_RGBA_SUB)
          
      self.shadow_mask.blit(light.color_surface, light_spos, None, pygame.BLEND_RGB_ADD)
      
    # given the camera's visibility, remove unseeable light by adding full
    # alpha to non-visible areas
      for r_polygon in light.polylist:
        s_polygon = map(lambda p: self.real_to_screen(p[0], p[1]), r_polygon)
        pygame.draw.polygon(self.shadow_mask, (1,1,1,255), s_polygon, 0)
        
    # Finally, blit the light layer onto the screen
    screen.blit(self.shadow_mask, (0,0))
        
