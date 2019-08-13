#!/usr/local/bin/python3

'''
This script creates a number of ants, which gradually evolve to survive and thrive in their environment.
The ants move, eat, mate, produce offspring, and die in an environment containing food and obstacles.

Ant actions:
1,2,3,4	- move up, left, down, or right
5		- propose mating with an adjacent ant. If that ant also proposes mating, then they produce offspring
  		  with a random combination of their genes
6		- eat an adjacent food
7		- die

Ant inputs:
- adjacent objects (ants, food, obstacles)
- grid location
- internal state (timers, etc)
'''

import pygame
import random

BLACK = (0,		0, 		0)
WHITE = (255, 	255, 	255)
RED =	(255,	0,		0)

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
		self.genes = b'helloworld'

	def act(self, ant):
		"""
		@brief      Causes an ant to take an action (update its state and move on the screen) given its current situation.
		
		@param      self  The object
		@param      ant   The ant that we're causing to act
		
		@return     none
		"""
		ant.rect.y += 1

def main():
	"""
	@brief      main function called from program entry point
	
	@return     None
	"""
	pygame.init()
	screen_width = 700
	screen_height = 400
	screen = pygame.display.set_mode([screen_width, screen_height])

	#list of all ant sprites in the game, managed by this "group" object
	ant_list = pygame.sprite.Group()

	#list of all sprites in the game, including foods and obstacles
	all_sprites_list = pygame.sprite.Group()

	#create some ants
	for i in range(10):
		#create an ant
		ant = Ant(Agent(), BLACK, 15, 15)
		#select a random location for the ant
		ant.rect.x = random.randrange(screen_width)
		ant.rect.y = random.randrange(screen_height)
		#add the ant to the ants & objects list
		ant_list.add(ant)
		all_sprites_list.add(ant)

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

		#ants take their actions
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
		
