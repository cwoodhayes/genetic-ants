#!/usr/local/bin/python3

'''
This script creates a number of ants, which gradually evolve to survive and thrive in their environment.
The ants move, eat, mate, produce offspring, and die in an environment containing food and obstacles.

Ant movement:
any combo of dx=1, -1 and dy=1, -1

Ant actions:
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
import random, math
import numpy as np

BLACK = (0,		0, 		0)
GREY =	(150,	150,	150)
WHITE = (255, 	255, 	255)
RED =	(255,	0,		0)

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 400
MATING_PERIOD = 200	#period in turns
MATING_DELAY = 200 #delay until ant matures enough to mate with other ants

class Ant(pygame.sprite.Sprite):
	##
	## @brief      Constructs the ant
	##
	## @param      self    The object
	## @param      agent   The agent controlling the ant
	## @param      game    The game object describing various game state items
	## @param      init_x  The initial x position of the ant
	## @param      init_y  The initial y position of the ant
	## @param      width   The width of the ant
	## @param      height  The height of the ant on screen
	##
	def __init__(self, agent, game, init_x, init_y, width=15, height=15):

		super().__init__()
		self.agent = agent

		#make the generic square that represents this ant
		self.image = pygame.Surface((width, height))
		print(agent.get_color())
		self.image.fill(agent.get_color())

		#initialize the object position
		self.rect = self.image.get_rect()
		self.rect.x = init_x
		self.rect.y = init_y

		#initialize the game object
		self.game = game

		#add the ant to the relevant object lists
		self.id = len(game.ant_list)
		print('Ant {} spawning at ({},{}).'.format(self.id, init_x, init_y))
		print(self.agent.genes)
		self.game.ant_list.add(self)
		self.game.all_sprites_list.add(self)

		#initialize previous movement
		self.prev_dx = 0
		self.prev_dy = 0

		#prev action
		self.prev_action = 0

		#ant's can't mate til they're a bit older
		self.prev_mating_turn = MATING_DELAY

	##
	## @brief      Called once per tick to perform an action and update the
	##             ant's location on screen
	##
	## @param      self  The object
	##
	## @return     none
	##
	def update(self):
		self.agent.act(self)

	##
	## @brief      Interact with another ant with whom you've collided
	##
	## @param      self       The object
	## @param      other_ant  The other ant
	##
	## @return     none
	##
	def interact(self, other_ant):
		self.attempt_mate(other_ant)

	def attempt_mate(self, other_ant):
		if self.game.turn_count - self.prev_mating_turn > MATING_PERIOD and \
				self.game.turn_count - other_ant.prev_mating_turn > MATING_PERIOD:
			child_genes = self.agent.mate(other_ant.agent.genes)
			#if the mating produced a viable offspring (otherwise is None), make a new ant and spawn it nearby
			if child_genes is None:
				pass
			else:
				child_spawn_angle = random.uniform(0, math.pi)
				child = Ant(Agent(child_genes), self.game,
					#spawn the child 20 units away at some random angle
					self.rect.x + 20*math.sin(child_spawn_angle), 
					self.rect.y + 20*math.cos(child_spawn_angle))

				#reset the mating timer
				self.prev_mating_turn = self.game.turn_count
				other_ant.prev_mating_turn = self.game.turn_count
				print('{} + {} -> {}'.format(self.id, other_ant.id, child.id))

class Agent:
	"""
	@brief      Class for an agent. Each ant has an agent that tells it what to
	            do. The agents have 'genes' which determine what kind of actions
	            they take.
	"""
	movement_weights = np.array([1,1,5,5])	#see act()

	##
	## @brief      Constructs the object.
	##
	## @param      self   The object
	## @param      genes  The genes of the agent
	##
	def __init__(self, genes=None):
		if genes is None:
			self.genes = (np.random.rand(4,4) - .5)*2
		else:
			self.genes = genes
		self.prev_dy = 0
		self.prev_dx = 0
		self.movement_inputs = np.empty((1,4))
		self.weighted_movement_inputs = np.empty((1,4))
		self.movement_outputs = np.empty((1,2))

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

		init_x = ant.rect.x
		init_y = ant.rect.y
		#use current position and velocity, plus genetic preference, to determine movement.
		self.movement_inputs = np.array([ant.rect.x/SCREEN_WIDTH, ant.rect.y/SCREEN_HEIGHT, self.prev_dx, self.prev_dy])
		np.multiply(self.movement_inputs, Agent.movement_weights, out=self.weighted_movement_inputs)
		#generate movement outputs between 0 and 1
		self.movement_outputs = np.matmul(self.movement_inputs, self.genes[0:4,0:2]) / Agent.movement_weights.sum() + .5

		#pick a number between 0 and 1. If it is above the normalized movement_output, then we set dx to 1.
		#if it is below movement_output, we set to 0. This allows genes to set a preference on movement,
		#but not to entirely determine it, or else ants get stuck.
		dx = 1 if random.random() > self.movement_outputs[0] else -1
		dy = 1 if random.random() > self.movement_outputs[1] else -1

		#list of ants that we collide with this turn
		ant_collisions = []

		#complete x movement action
		ant.rect.x += dx
		if ant.rect.left < 0 or ant.rect.right > SCREEN_WIDTH:
			#undo if that took us off the screen
			ant.rect.x -= dx
		else:
			#collisions with ants
			ant_collisions.extend(pygame.sprite.spritecollide(ant, ant.game.ant_list, False))
			#collision with walls
			wall_collisions = pygame.sprite.spritecollide(ant, ant.game.wall_list, False)

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
			ant_collisions.extend(pygame.sprite.spritecollide(ant, ant.game.ant_list, False))
			#collision with walls
			wall_collisions = pygame.sprite.spritecollide(ant, ant.game.wall_list, False)

			#prevent us from moving into an obstacle
			for wall in wall_collisions:
				if dy > 0:
					ant.rect.bottom = wall.rect.top
				else:
					ant.rect.top = wall.rect.bottom

		#resolve ant collisions
		for other_ant in ant_collisions:
			#spritecollide is dumb and collides you with yourself
			if ant is not other_ant:
				ant.interact(other_ant)

		#save this iteration's movement results
		self.prev_dx = ant.rect.x - init_x
		self.prev_dy = ant.rect.y - init_y

	def mate(self, genes):
		"""
		@brief      Produces offspring genes given this agent's genes and another set of genes. For now, offspring
					occurs no matter what.
		
		@param      genes  The genes to mate with
		
		@return     genes of the new offspring.
		"""

		offspring_genes = np.copy(self.genes)
		#generate offspring's genes through random combination of my genes and their genes
		with np.nditer([offspring_genes, genes], op_flags=[['readwrite'], ['readonly']]) as it:
			for mine, theirs in it:
				mine[...] = mine if (random.randrange(2) == 0) else theirs

		return offspring_genes

	def get_color(self):
		"""
		Somewhat arbitrarily assigns this ant a color from its genes.
		"""
		return ((self.genes[0:3,0]/2)+.5)*255


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

class Game:
	def __init__(self):
		self.turn_count = 0
		self.ant_list = pygame.sprite.Group()
		self.wall_list = pygame.sprite.Group()
		#list of all sprites in the game, including foods, ants, and obstacles
		self.all_sprites_list = pygame.sprite.Group()

def main():
	"""
	@brief      main function called from program entry point
	
	@return     None
	"""
	pygame.init()
	screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

	#initialize the game object
	game = Game()

	#create some ants
	for i in range(10):
		#create an ant
		ant = Ant(Agent(),
					#store references to the game object
					game,
					#select a random location for the ant
					random.randrange(SCREEN_WIDTH), random.randrange(SCREEN_HEIGHT))

	#create some obstacles
	for i in range(15):
		#create a randomly sized obstacle
		wall = Wall(BLACK, random.betavariate(2,20)*SCREEN_WIDTH, random.betavariate(2,20)*SCREEN_HEIGHT)
		#select a random location for the ant
		wall.rect.x = random.randrange(SCREEN_WIDTH)
		wall.rect.y = random.randrange(SCREEN_HEIGHT)
		#add the wall to the wall and objects lists
		game.wall_list.add(wall)
		game.all_sprites_list.add(wall)

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
		game.ant_list.update()

		#draw all the sprites
		game.all_sprites_list.draw(screen)

		#limit to 60fps
		clock.tick(60)
		game.turn_count += 1

		#update the display with what we've drawn
		pygame.display.flip()

	pygame.quit()


if __name__ == '__main__':
	"""
	Program entry point
	"""
	main()
		
