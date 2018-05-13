#coding:utf-8
import pygame
import os
import sys
import random
from stable_sprite import *

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

class Bullet(pygame.sprite.Sprite):
	def __init__(self,img_name,x,y,direction):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load(img_name).convert()
		self.image.set_colorkey(white)
		self.image = pygame.transform.rotate(self.image, direction)
		self.rect = self.image.get_rect()
		self.rect.left = x
		self.rect.top = y
		self.speed = 4
		self.change_x = 0
		self.change_y = 0
		self.direction = direction
		if direction == 90:
			self.change_x = -self.speed
			self.rect.top -= 3
		elif direction == 180:
			self.change_y = self.speed
			self.rect.left -= 3
		elif direction == 270:
			self.change_x = self.speed
			self.rect.top -= 3
		elif direction == 0:
			self.change_y = -self.speed
			self.rect.left -= 3
	
	def explode(self):
		if self.direction == 90 or self.direction == 270:
			x = self.rect.left + 4
			y = self.rect.top + 3
		elif self.direction == 180 or self.direction == 0:
			x = self.rect.left + 3
			y = self.rect.top + 4
		g_explosion_list.add(Explosion(x,y,1))

	def update(self):
		if self.change_x != 0 and self.change_y != 0:
			print "error at class Player update"
			sys.exit()
		self.rect.left += self.change_x
		self.rect.top += self.change_y
		collide_walls = pygame.sprite.spritecollide(self, g_wall_list, False)
		collide_bricks = pygame.sprite.spritecollide(self, g_brick_list, False)
		if collide_walls or collide_bricks:
			self.explode()
			self.kill()
		# 去掉附近的Brick
		extra_brick_poss = []
		for brick in collide_bricks:
			if self.direction == 90 or self.direction == 270:
				extra_brick_poss.append((brick.rect.left, brick.rect.top + 10))
				extra_brick_poss.append((brick.rect.left, brick.rect.top - 10))
			elif self.direction == 180 or self.direction == 0:
				extra_brick_poss.append((brick.rect.left + 10 ,brick.rect.top))
				extra_brick_poss.append((brick.rect.left - 10 ,brick.rect.top))
			brick.kill()
		for brick in g_brick_list:
			for extra_brick_pos in extra_brick_poss:
				if brick.rect.left == extra_brick_pos[0] and brick.rect.top == extra_brick_pos[1]:
					brick.kill()

class PlayerBullet(Bullet):
	def __init__(self,x,y,direction,power=1):
		Bullet.__init__(self,"images/Bullet_yellow.png",x,y,direction)
		self.power = power

	def update(self):
		Bullet.update(self)
		if not self.alive():
			return
		collide_stones = pygame.sprite.spritecollide(self, g_stone_list, False)
		if collide_stones:
			self.explode()
			self.kill()
			if self.power == 2:
				for stone in collide_stones:
					stone.kill()
			return
		collide_enamys = pygame.sprite.spritecollide(self, g_enamy_list, False)
		if collide_enamys:
			self.explode()
			self.kill()
			for enamy in collide_enamys:
				enamy.crashed()
			return 
		collide_enamy_bullets = pygame.sprite.spritecollide(self, g_enamy_bullet_list, False)
		if collide_enamy_bullets:
			self.explode()
			self.kill()
			for enamy_bullet in collide_enamy_bullets:
				enamy_bullet.explode()
				enamy_bullet.kill()
			return

class EnamyBullet(Bullet):
	def __init__(self,x,y,direction):
		Bullet.__init__(self,"images/Bullet_red.png",x,y,direction)

	def update(self):
		Bullet.update(self)
		if not self.alive():
			return
		collide_stones = pygame.sprite.spritecollide(self, g_stone_list, False)
		if collide_stones:
			self.explode()
			self.kill()
			return
		collide_player1s = pygame.sprite.spritecollide(self, g_player1_list, False)
		if collide_player1s:
			self.explode()
			self.kill()
			for player1 in collide_player1s:
				if not player1.protected:
					player1.crashed()
			return 
		collide_player1_bullets = pygame.sprite.spritecollide(self, g_player1_bullet_list, False)
		if collide_player1_bullets:
			self.explode()
			self.kill()
			for player1_bullet in collide_player1_bullets:
				player1_bullet.explode()
				player1_bullet.kill()
			return

class Tank(pygame.sprite.Sprite):
	def __init__(self,img_name,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image_bak = pygame.image.load(img_name).convert()
		self.image = self.image_bak
		self.image.set_colorkey(white)
		self.rect = self.image.get_rect()
		self.rect.top = y
		self.rect.left = x
		self.change_x = 0
		self.change_y = 0
		self.direction = 0
		self.speed = 2
		self.max_bullet_num = 1

	def changeface(self,img_name):
		self.image_bak = pygame.image.load(img_name).convert()
		self.image_bak.set_colorkey(white)
		self.image = self.image_bak
		self.image = pygame.transform.rotate(self.image_bak, self.direction)

	def changespeed(self,x,y):
		'''
			x,y至少有一个为零
		'''
		if self.change_x == 0 and x != 0:
			# 修正self.rect.top
			if self.rect.top%10 >= 5:
				self.rect.top = (self.rect.top/10+1)*10
			else:
				self.rect.top = (self.rect.top/10)*10
		if self.change_y == 0 and y != 0:
			# 修正self.rect.left
			if self.rect.left%10 >= 5:
				self.rect.left = (self.rect.left/10+1)*10
			else:
				self.rect.left = (self.rect.left/10)*10
		self.change_x = x * self.speed
		self.change_y = y * self.speed
		if x < 0:
			self.direction = 90
		elif x > 0:
			self.direction = 270
		if y > 0:
			self.direction = 180
		elif y < 0:
			self.direction = 0
		self.image = pygame.transform.rotate(self.image_bak, self.direction)

	def explode(self):
		x = self.rect.left + 20
		y = self.rect.top + 20
		g_explosion_list.add(Explosion(x,y,2))

	def crashed(self):
		self.explode()
		self.kill()

class Player(Tank):
	def __init__(self,x,y,bullets):
		Tank.__init__(self,"images/Our1.png",x,y)
		self.speed = 2
		self.max_bullet_num = 1
		self.life = 3
		self.power = 1
		self.bullets = bullets
		self.protected_time = -1
		self.protected = False

	def set_protected(self, time):
		self.protected = True
		self.protected_time = time
		self.changeface("images/Our1_protected.png")

	def fire(self):
		x = self.rect.left + 20
		y = self.rect.top + 20
		if self.direction == 90:
			x -= 20
		elif self.direction == 270:
			x += 20
		elif self.direction == 180:
			y += 20
		elif self.direction == 0:
			y -= 20
		if len(self.bullets) < self.max_bullet_num:
			if self.power > 1:
				self.bullets.add(PlayerBullet(x,y,self.direction,2))
			else:
				self.bullets.add(PlayerBullet(x,y,self.direction,1))

	def reset(self,x,y):	
		self.rect.left = x
		self.rect.top = y
		self.power = 1
		self.changeface("images/Our1.png")

	def update(self):
		if self.protected_time >= 0:
			self.protected_time -= 1
			if self.protected_time == 0:
				self.protected = False
				self.changeface("images/Our%d.png" % self.power)	
		if self.change_x != 0 and self.change_y != 0:
			print "error at class Player update"
			sys.exit()
		old_x=self.rect.left
		old_y=self.rect.top
		new_x=old_x+self.change_x
		new_y=old_y+self.change_y
		self.rect.left = new_x
		self.rect.top = new_y
		collide_walls = pygame.sprite.spritecollide(self, g_wall_list, False)
		collide_bricks = pygame.sprite.spritecollide(self, g_brick_list, False)
		collide_stones = pygame.sprite.spritecollide(self, g_stone_list, False)
		collide_waters = pygame.sprite.spritecollide(self, g_water_list, False)
		collide_enamys = pygame.sprite.spritecollide(self, g_enamy_list, False)
		if collide_walls or collide_bricks or collide_stones or collide_waters or collide_enamys:
			self.rect.left = old_x
			self.rect.top = old_y

class Enamy(Tank):
	def __init__(self,img_name,x,y):
		Tank.__init__(self,img_name,x,y)
		self.speed = 2
		self.max_bullet_num = 2
		self.prize = 0

	def fire(self):
		x = self.rect.left + 20
		y = self.rect.top + 20
		if self.direction == 90:
			x -= 20
		elif self.direction == 270:
			x += 20
		elif self.direction == 180:
			y += 20
		elif self.direction == 0:
			y -= 20
		if len(g_enamy_bullet_list) < self.max_bullet_num:
			g_enamy_bullet_list.add(EnamyBullet(x,y,self.direction))

	def crashed(self):
		if self.prize:
			g_prize_list.add(Prize(self.prize))
		Tank.crashed(self)

	def set_prize(self, prize):
		self.prize = prize

	def update(self):
		if self.change_x != 0 and self.change_y != 0:
			print "error at class Tank update"
			sys.exit()
		old_x=self.rect.left
		old_y=self.rect.top
		new_x=old_x+self.change_x
		new_y=old_y+self.change_y
		self.rect.left = new_x
		self.rect.top = new_y
		collide_walls = pygame.sprite.spritecollide(self, g_wall_list, False)
		collide_bricks = pygame.sprite.spritecollide(self, g_brick_list, False)
		collide_stones = pygame.sprite.spritecollide(self, g_stone_list, False)
		collide_waters = pygame.sprite.spritecollide(self, g_water_list, False)
		collide_enamys = pygame.sprite.spritecollide(self, g_enamy_list, False)
		collide_player1 = pygame.sprite.spritecollide(self, g_player1_list, False)
		if collide_walls or collide_bricks or collide_stones or collide_waters or collide_enamys or collide_player1:
			self.rect.left = old_x
			self.rect.top = old_y

class Enamy1(Enamy):
	def __init__(self,x,y):
		Enamy.__init__(self,"images/Enamy1.png",x,y)
		self.speed = 2
		self.max_bullet_num = 2
	
	def update(self):
		i = random.randint(1,40)
		if i == 1:
			self.changespeed(1,0)
		elif i == 2:
			self.changespeed(-1,0)
		elif i == 3:
			self.changespeed(0,1)
		elif i == 4:
			self.changespeed(0,-1)
		if random.randint(1,20) == 1:
			self.fire()
		Enamy.update(self)

class Enamy2(Enamy):
	def __init__(self,x,y):
		Enamy.__init__(self,"images/Enamy2.png",x,y)
		self.speed = 4
		self.max_bullet_num = 2

	def update(self):
		i = random.randint(1,40)
		if i == 1:
			self.changespeed(1,0)
		elif i == 2:
			self.changespeed(-1,0)
		elif i == 3:
			self.changespeed(0,1)
		elif i == 4:
			self.changespeed(0,-1)
		if random.randint(1,20) == 1:
			self.fire()
		Enamy.update(self)

class Enamy3(Enamy):
	def __init__(self,x,y):
		self.life = 3
		Enamy.__init__(self,"images/Enamy3_%d.png"%self.life,x,y)
		self.speed = 2
		self.max_bullet_num = 2
	
	def update(self):
		i = random.randint(1,40)
		if i == 1:
			self.changespeed(1,0)
		elif i == 2:
			self.changespeed(-1,0)
		elif i == 3:
			self.changespeed(0,1)
		elif i == 4:
			self.changespeed(0,-1)
		if random.randint(1,20) == 1:
			self.fire()
		Enamy.update(self)

	def crashed(self):
		self.life -= 1
		if self.prize:
			g_prize_list.add(Prize(self.prize))
			self.prize = 0
		if self.life != 0:
			self.changeface("images/Enamy3_%d.png"%self.life)
		else:
			self.explode()
			self.kill()
