#coding:utf-8
import pygame
import os
import random

global g_player1_bullet_list 
global g_enamy_bullet_list 
global g_player1_list 
global g_enamy_list 
global g_explosion_list 
global g_prize_list 
global g_brick_list 
global g_stone_list 
global g_grass_list 
global g_water_list 
global g_wall_list 
global g_home_list 
global g_rewards

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
orange = (255,128,0)

class Wall(pygame.sprite.Sprite):
	def __init__(self,x,y,width,height):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([width, height])
		self.image.fill(blue)
		self.rect = self.image.get_rect()
		self.rect.left = x
		self.rect.top = y
         
class Brick(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([10,10])
		self.image.fill(orange)
		pygame.draw.line(self.image, white, [0,0], [10,0])
		if (x+y)%20 == 0:
			pygame.draw.line(self.image, white, [9,0], [9,10])
		self.rect = self.image.get_rect()
		self.rect.left = x
		self.rect.top = y

class Block(pygame.sprite.Sprite):
	def __init__(self,img_name,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img_name).convert()
		self.image.set_colorkey(white)
		self.rect = self.image.get_rect()
		self.rect.left = x
		self.rect.top = y

def Stone(x,y):
		return Block("images/Stone.png",x,y)

def Water(x,y):
		return Block("images/Water.png",x,y)

def Grass(x,y):
		return Block("images/Grass.png",x,y)

class Explosion(pygame.sprite.Sprite):
	def __init__(self,x,y,size=1):
		pygame.sprite.Sprite.__init__(self)
		self.size = size
		self.seq = 1
		self.image = pygame.image.load(self.get_next_img()).convert()
		self.image.set_colorkey(white)
		self.rect = self.image.get_rect()
		if self.size == 1:
			self.rect.left = x - 10
			self.rect.top = y - 10
		elif self.size == 2:
			self.rect.left = x - 20
			self.rect.top = y - 20

	def get_next_img(self):
		img_name = 'images/explosion/explosion%d-%d.png' % (self.size, self.seq)
		if not os.path.exists(img_name):
			self.kill()
			return None
		self.seq += 2
		return img_name

	def update(self):
		img_name = self.get_next_img()
		if img_name:
			self.image = pygame.image.load(img_name).convert()
			self.image.set_colorkey(white)

class Prize(pygame.sprite.Sprite):
	def __init__(self,prize_i):
		pygame.sprite.Sprite.__init__(self)
		self.prize_i = prize_i
		prize_img_name = "images/prize/prize%d.png" % prize_i
		self.image = pygame.image.load(prize_img_name).convert()
		self.image.set_colorkey(white)
		self.rect = self.image.get_rect()
		self.rect.left = 10 + random.randint(0, 480)
		self.rect.top = 10 + random.randint(0, 480)

	def update(self):
		collide_player1 = pygame.sprite.spritecollide(self, g_player1_list, False)
		if collide_player1:
			if len(collide_player1) != 1:
				print "error at class Prize update"
				sys.exit()
			player1 = collide_player1[0]
			g_rewards.append((player1,self.prize_i))
			self.kill()

class Home(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([40,40])
		self.image.fill(green)
		self.rect = self.image.get_rect()
		self.rect.left = x
		self.rect.top = y

	def update(self):
		collide_bullets1 = pygame.sprite.spritecollide(self, g_player1_bullet_list, False)
		collide_bullets3 = pygame.sprite.spritecollide(self, g_enamy_bullet_list, False)
		if collide_bullets1 or collide_bullets3:
			print 'Game Over'
