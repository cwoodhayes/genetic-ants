#!/usr/local/bin/python3

'''
This script creates a number of ants, which gradually evolve to survive and thrive in their environment.
The ants move, eat, mate, produce offspring, and die in an environment containing food and obstacles.

Ant actions:
1,2,3,4	- move up, left, down, or right
5		- propose mating with a colliding ant. If that ant also proposes mating, then they produce offspring
  		  with a random combination of their genes
6		- eat a colliding food
7		- die

todo:
8		- attack a colliding ant. The ants' genes determines who wins the fight and kills the other.
9		- befriend a colliding ant. The ants then share food (todo--determine this mechanism) and protect each other

Ant inputs:
- colliding objects (ants, food, obstacles)
- grid location
- internal state (timers, etc)
'''

import pygame
import random
import numpy as np

BLACK = (0,		0, 		0)
GREY =	(150,	150,	150)
WHITE = (255, 	255, 	255)
RED =	(255,	0,		0)

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 400

class Ant(pygame.sprite.Sprite):
	''' 
	Class for an ant. it learns stuff
	'''
	def __init__(self, agent, color, width, height):
		"""
		Agent -- the agent which makes decisions as to the ant's movement
		color -- ant color
		width -- ant width
		height - ant height
		"""

		super().__init__()
		self.agent = agent

		#make the generic square that represents this ant
		self.image = pygame.Surface((width, height))
		self.image.fill(color)

		#initialize the object position
		self.rect = self.image.get_rect()

		#initialize the collision lists
		self.ant_list = None
		self.wall_list = None

	def update(self):
		"""
		@brief      Called once a tick to update the ant's position on the screen.
		
		@param      self  The object
		
		@return     None
		"""
		self.agent.act(self)

class Agent:
	"""
	@brief      Class for an agent. Each ant has an agent that tells it what to do.
				The agents have 'genes' which determine what kind of actions they take.
	"""
	def __init__(self):
		self.genes = np.random.rand(4,4) - .5

	def act(self, ant):
		"""
		@brief      Causes an ant to take an action (update its state and move
		            on the screen) given its current situation.
		
		@param      self             The object
		@param      ant              The ant that we're causing to act
		@param      ant_collisions   The ants we've collided with
		@param      wall_collisions  The walls we've collided with
		
		@return     none
		"""
		'''
		movement phase inputs:
		[gridx, gridy]
		outputs: []

		action phase inputs:
		[gridx, gridy, collideant, collidewall]
		'''
		movement_inputs = np.array([[ant.rect.x/SCREEN_WIDTH], [ant.rect.y/SCREEN_HEIGHT]])
		#generate movement decisions
		movement_outputs = np.matmul(self.genes[0:2,0:2], movement_inputs)

		dx = movement_outputs[0]
		dy = movement_outputs[1]

		#complete x movement action
		ant.rect.x += dx
		if ant.rect.left < 0 or ant.rect.right > SCREEN_WIDTH:
			#undo if that took us off the screen
			ant.rect.x -= dx
		else:
			#collisions with ants
			ant_collisions = pygame.sprite.spritecollide(ant, ant.ant_list, False)
			#collision with walls
			wall_collisions = pygame.sprite.spritecollide(ant, ant.wall_list, False)

			#prevent us from moving into an obstacle
			for wall in wall_collisions:
				if dx > 0:
					#moving right, so align our right edge with the left edge of the wall
					ant.rect.right = wall.rect.left
				else:
					#moving left, so do the opposite
					ant.rect.left = wall.rect.right

		#complete y movement action
		ant.rect.y += dy
		if ant.rect.top < 0 or ant.rect.bottom > SCREEN_HEIGHT:
			#undo that if it's taking us off the screen
			ant.rect.y -= dy
		else:
			#collisions with ants
			ant_collisions = pygame.sprite.spritecollide(ant, ant.ant_list, False)
			#collision with walls
			wall_collisions = pygame.sprite.spritecollide(ant, ant.wall_list, False)

			#prevent us from moving into an obstacle
			for wall in wall_collisions:
				if dy > 0:
					ant.rect.bottom = wall.rect.top
				else:
					ant.rect.top = wall.rect.bottom

class Wall(pygame.sprite.Sprite):
	"""
	@brief      an obstacle that prevents the ant from passing through it
	"""
	def __init__(self, color, width, height):
		"""
		color -- wall color
		width -- wall width
		height - wall height
		"""

		super().__init__()

		#make the generic square that represents this ant
		self.image = pygame.Surface((width, height))
		self.image.fill(color)

		#initialize the object position
		self.rect = self.image.get_rect()

def main():
	"""
	@brief      main function called from program entry point
	
	@return     None
	"""
	pygame.init()
	screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

	#list of all ant sprites in the game, managed by this "group" object
	ant_list = pygame.sprite.Group()
	wall_list = pygame.sprite.Group()

	#list of all sprites in the game, including foods and obstacles
	all_sprites_list = pygame.sprite.Group()

	#create some ants
	for i in range(10):
		#create an ant
		ant = Ant(Agent(), GREY, 15, 15)
		#select a random location for the ant
		ant.rect.x = random.randrange(SCREEN_WIDTH)
		ant.rect.y = random.randrange(SCREEN_HEIGHT)
		#add the ant to the ants & objects list, and store references to these lists in the ant
		ant.ant_list = ant_list
		ant.wall_list = wall_list
		ant_list.add(ant)
		all_sprites_list.add(ant)

	#create some obstacles
	for i in range(15):
		#create a randomly sized obstacle
		wall = Wall(BLACK, random.betavariate(2,20)*SCREEN_WIDTH, random.betavariate(2,20)*SCREEN_HEIGHT)
		#select a random location for the ant
		wall.rect.x = random.randrange(SCREEN_WIDTH)
		wall.rect.y = random.randrange(SCREEN_HEIGHT)
		#add the wall to the wall and objects lists
		wall_list.add(wall)
		all_sprites_list.add(wall)

	#loop until user hits the close button
	done = False
	clock = pygame.time.Clock()

	# ----------------------- MAIN PROGRAM LOOP ---------------------
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				done = True

		#clear the screen
		screen.fill(WHITE)

		#ants take their move actions
		ant_list.update()

		#draw all the sprites
		all_sprites_list.draw(screen)

		#limit to 60fps
		clock.tick(60)

		#update the display with what we've drawn
		pygame.display.flip()

	pygame.quit()


if __name__ == '__main__':
	"""
	Program entry point
	"""
	main()
		
