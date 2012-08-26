import pygame, math
from camera import Camera
from light import Light
from pygame.sprite import Sprite
from pymunk.vec2d import Vec2d

class Entity(Sprite):
  def __init__(self, image_path, screen, initpos, camera):
    Sprite.__init__(self)
    self.camera = camera
    self.screen = screen
    self.rpos = Vec2d(initpos)
    self.vel = Vec2d((0,0))
    self.lights = []
    
    self.image = pygame.image.load(image_path)
    #store original size for consistent hitboxes (rotating changes image size)
    self.original_image_size = self.image.get_size() 
    self.base_image = self.image #for use in rotations
    
  def draw(self, currentCam):
    image_w, image_h = self.image.get_size()
    
    # adjust real to screen coordinates based on currentCam:
    #   screen_x = real_x - dist_realOrigin_to_screenOrigin_x
    #   screen_y = real_y - dist_realOrigin_to_screenOrigin_y
    
    sx, sy = currentCam.real_to_screen(self.rpos.x, self.rpos.y)
 
    # draw the entity to the screen coordinates
    draw_pos = self.image.get_rect().move(
        sx - image_w / 2,
        sy - image_h / 2)
    self.screen.blit(self.image, draw_pos)
  
  def update(self, time_passed, level, currentCam):
    # update the position based on the normalized velocity * speed
    # unless the entity is about to move into a solid tile
    image_w, image_h = self.original_image_size

    newrx = self.rpos.x + self.vel.x * self.speed
    new_topleft_corner = (newrx - image_w/2, self.rpos.y - image_h/2)
    new_botright_corner = (newrx + image_w/2, self.rpos.y + image_h/2)
    tiles_to_be_occupied = level.tiles_at(new_topleft_corner, new_botright_corner)
    problem_tiles = [tile for tile in tiles_to_be_occupied if not tile.attributes["movethrough"]] 
    if problem_tiles == []: 
      self.rpos.x = newrx
      
    newry = self.rpos.y + self.vel.y * self.speed
    new_topleft_corner = (self.rpos.x - image_w/2, newry - image_h/2)
    new_botright_corner = (self.rpos.x + image_w/2, newry + image_h/2)
    tiles_to_be_occupied = level.tiles_at(new_topleft_corner, new_botright_corner)
    problem_tiles = [tile for tile in tiles_to_be_occupied if not tile.attributes["movethrough"]] 
    if problem_tiles == []: 
      self.rpos.y = newry

    self.vel = Vec2d((0,0))
    
class Player(Entity):
  def __init__(self, image_path, screen, initpos, camera):
    super(Player, self).__init__(image_path, screen, initpos, camera)
    self.speed = 5
    self.base_image = pygame.transform.rotate(self.image, 180)
    self.flashlight = Light((0,0,0), self.rpos, self.rpos, 0.0, 30.0)
    self.headlight = Light((255,0,0), self.rpos, self.rpos, 0.0, 50.0)
    
    self.lights.append(self.headlight)
    self.lights.append(self.flashlight)
    
  def update(self, time_passed, level, currentCam):
    super(Player, self).update(time_passed, level, currentCam)
    
    # draw a vector between the player and the cursor
    # and rotate the player image to face it.
    # Have to use the current camera in order
    # to get the player's screen coordinates, (sx, sy)
    sx, sy = currentCam.real_to_screen(self.rpos.x, self.rpos.y)
    mouse_sx, mouse_sy = pygame.mouse.get_pos()
    mouse_rx, mouse_ry = currentCam.screen_to_real(mouse_sx, mouse_sy)

    dx = sx - mouse_sx
    dy = sy - mouse_sy
    player_to_mouse = Vec2d(dx, dy)

    self.image = pygame.transform.rotate(self.base_image, -math.degrees(player_to_mouse.angle)) 
    
    # with the entity's position updated, bring the light emitter with it
    self.flashlight.emitter_pos = self.rpos
    self.flashlight.proj_pos = Vec2d(mouse_rx, mouse_ry) 
    self.flashlight.update_surface(level)
    
    self.headlight.emitter_pos = self.rpos
    self.headlight.proj_pos = self.rpos
    self.headlight.update_surface(level)
    
    # offset the camera location to place the player
    # in the middle of the screen
    offsetX = self.rpos.x - self.camera.screen_width/2
    offsetY = self.rpos.y - self.camera.screen_height/2

    self.camera.move((offsetX, offsetY))
    
   
  def movement_handler(self, keydown):
      self.vel.x, self.vel.y = {pygame.K_w: (self.vel.x, -1),
                                pygame.K_s: (self.vel.x, 1),
                                pygame.K_a: (-1, self.vel.y),
                                pygame.K_d: (1, self.vel.y)}[keydown]
      self.vel = self.vel.normalized() 

