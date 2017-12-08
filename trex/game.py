#!/usr/bin/env python3

import pygame, sys
import random
import math
from pygame import Surface, Color, QUIT
from trex import *
from obstacle import *
import noise
import numpy
import pickle
from spritesheets import *

# constants
WIN_WIDTH = 800
WIN_HEIGHT = 200
DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
BACKGROUND_COLOR = (66, 66, 66)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
IS_DUMPING = False
OBSTACLE_INITSPEED = 4
OBSTACLE_MAXSIZE = 50
IS_NN_ACTIVE = True

# global vars
clock = None
screen = None
frameCount = 0
dino = None
bg = None
horizon = 0
obstacles = None
obstacleSpeed = 0
gameOver = False
score = 0
font = None
dumpObstacleData = True
nn = None

# sprites
sp_n = 0
FPS = 120
frames = FPS / 12
strips = []
image = None

def setup():
    global clock, screen, bg, horizon, dino, font, nn, strips, image
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(DISPLAY)
    strips.append(SpriteStripAnim('./assets/200-offline-sprite.png', (927,0,44,54), 2, 0, True, frames))
    strips.append(SpriteStripAnim('./assets/200-offline-sprite.png', (1015,0,44,54), 1, 0, False, frames))
    strips[sp_n].iter()
    image = strips[sp_n].next()
    font = pygame.font.Font(None, 30)
    pygame.display.set_caption("T-Rex game")
    bg = Surface((WIN_WIDTH,WIN_HEIGHT))
    bg.fill(BACKGROUND_COLOR)
    restart()
    horizon = WIN_HEIGHT - 40
    radius = 20
    dino = Trex(radius * 2, horizon-radius*2, radius, screen)

    if IS_NN_ACTIVE:
        nn = pickle.load(open( "nn.bin", "rb" ))

def restart():
  global gameOver, obstacles, obstacleSpeed, score, sp_n
  gameOver = False
  obstacleSpeed = OBSTACLE_INITSPEED
  obstacles = []
  score = 0
  sp_n = 0

def drawHorizon():
    pygame.draw.line(screen, WHITE, [0, horizon], [WIN_WIDTH, horizon], 2)


def handleLevel():
    global obstacleSpeed, score, strips, image

    if frameCount % (math.floor(obstacleSpeed)*9) == 0:
      rnd = noise.pnoise1(random.randint(1, math.floor((frameCount*3)/4))/frameCount)

      if rnd > 0.45 and not gameOver:
          newObstacle()

          # dump randomly with without jump
          if dumpObstacleData:
              obstacles[len(obstacles)-1].dumpData()

      if frameCount % 120 == 0:
          obstacleSpeed *= 1.05

    if not gameOver:
      score += 1

def handleObstacles():
    global gameOver, sp_n
    for obstacle in obstacles:
      obstacle.draw()

      if not gameOver:
        obstacle.update(obstacleSpeed)

        if (obstacle.hits(dino)):
          sp_n = 1
          gameOver = True


        if not obstacle.onScreen:
          obstacles.pop()

def newObstacle():
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    size = random.randint(0, 30) + 20
    
    obstacle = Obstacle(WIN_WIDTH+size, size, horizon, color, screen)
    obstacles.insert(0, obstacle)

def keyPressed(e):
    if (e.key == pygame.K_UP or e.key == pygame.K_SPACE) and dino.onGround and not gameOver:

      if dumpObstacleData:
        obstacles[len(obstacles)-1].dumpData(1)
      
      dino.jump()
    
    if e.key == pygame.K_F5:
      restart()

def drawHUD():
    scoreText = font.render("Score: %d" % score, True, WHITE)
    screen.blit(scoreText, [5, 5])

    if gameOver:
      gameOverText = font.render("Game Over Bro! ;(", True, WHITE)
      restrtText = font.render("Press F5 to restart.", True, WHITE)
      screen.blit(gameOverText, [(WIN_WIDTH-gameOverText.get_width())/2, WIN_HEIGHT/4])
      screen.blit(restrtText, [(WIN_WIDTH-restrtText.get_width())/2, WIN_HEIGHT/3+10])

def update():
    global frameCount, gameOver, image

    for e in pygame.event.get():
      if e.type == QUIT:
          Obstacle.closeDumpFile()
          pygame.quit()
          sys.exit()
      if e.type == pygame.KEYDOWN:
          keyPressed(e)

    if (len(obstacles) > 1 and nn):
        obst = obstacles[len(obstacles)-1]
        inputs = numpy.asfarray([obst.distance, obst.speed, obst.size])
        # normalize values
        inputs[0] = inputs[0] / WIN_WIDTH + 0.01
        inputs[1] = inputs[1] / obstacleSpeed - 0.01
        inputs[2] = inputs[2] / OBSTACLE_MAXSIZE + 0.01
        output = nn.query(inputs)
        if output > 0.7 and dino.onGround:
            dino.jump()

    clock.tick(FPS)
    frameCount += 1

    screen.blit(bg, (0,0))
    drawHorizon()
    handleLevel()
    handleObstacles()
    if not gameOver:
      dino.update(horizon)
    
    dino.draw(image)
    drawHUD()
    try:
      image = strips[sp_n].next()
    except StopIteration:
      pass

def main():
    setup()

    while 1:
      update()
      pygame.display.update()
      

if __name__ == "__main__":
    main()