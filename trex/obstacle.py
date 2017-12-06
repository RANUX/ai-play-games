import pygame
import math
from game import IS_DUMPING


class Obstacle():
  file = None

  def __init__(self, x, size, horizon, color, screen):
    self.x = x
    self.y = horizon - size
    self.size = size
    self.color = color
    self.onScreen = True
    self.screen = screen
    self.distance = 0
    self.speed = 0

  def update(self, speed):
    # /* check if offscreen */
    self.onScreen = (self.x > -self.size)
    self.speed = speed
    # /* movement */
    self.x -= speed

  def draw(self):
    pygame.draw.rect(self.screen, self.color, [self.x, self.y, self.size, self.size])

  def dumpData(self, wasJump=0):
    if IS_DUMPING:
      Obstacle.dumpToFile("%d,%f,%f,%d" % (wasJump, self.distance, self.speed, self.size))

  @staticmethod
  def dumpToFile(str):
    
    if not Obstacle.file:
      Obstacle.file = open("jumpData.csv","a")
    
    Obstacle.file.write("%s\n" % str)

  @staticmethod
  def closeDumpFile():
    if Obstacle.file:
      Obstacle.file.close()

  def hits(self, dino):

    halfSize = self.size / 2
    minimumDistance = halfSize + (dino.radius) # closest before collision

    xCenter = self.x + halfSize
    yCenter = self.y + halfSize

    self.distance = math.hypot(xCenter-dino.x, yCenter-dino.y)

    return self.distance < minimumDistance