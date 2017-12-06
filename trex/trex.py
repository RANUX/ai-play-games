import pygame
WHITE = (255, 255, 255)

class Trex:
  def __init__(self, x, y, radius, screen):
    self.x = x
    self.y = y
    self.yVelocity = 0
    self.speed = 1
    self.onGround = True
    self.screen = screen
    self.radius = radius

  def jump(self):
    self.yVelocity = -(self.radius * 0.7)

  def draw(self):
    pygame.draw.ellipse(self.screen,WHITE,[self.x, self.y, self.radius, self.radius],2)

  def update(self, platform):
    bottom = self.y + self.radius*2        # bottom pixel of circle
    nextBottom = bottom + self.yVelocity # calculate next frame's bottom

    if bottom <= platform and nextBottom >= platform:
      self.yVelocity = 0                  # reset velocity
      self.y = platform - self.radius     # don't go past platform
      self.onGround = True
    elif (platform - bottom) > 1:
      self.yVelocity += self.speed        # increase velocity
      self.onGround = False

    # movement
    self.y += self.yVelocity