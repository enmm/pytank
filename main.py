#!/usr/bin/python
#coding:utf-8
import pygame
import random

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
orange = (255,128,0)

pygame.init()
offset = (10,10)
screen = pygame.display.set_mode([630+offset[0], 530+offset[1]])
pygame.display.set_caption('PyTank')
screen.fill(black)

# 供多个文件使用的全局变量
g_player1_bullet_list = pygame.sprite.RenderPlain()
g_enamy_bullet_list = pygame.sprite.RenderPlain()
g_player1_list = pygame.sprite.RenderPlain()
g_enamy_list = pygame.sprite.RenderPlain()
g_explosion_list = pygame.sprite.RenderPlain()
g_prize_list = pygame.sprite.RenderPlain()
g_brick_list = pygame.sprite.RenderPlain()
g_stone_list = pygame.sprite.RenderPlain()
g_grass_list = pygame.sprite.RenderPlain()
g_water_list = pygame.sprite.RenderPlain()
g_wall_list = pygame.sprite.RenderPlain()
g_home_list = pygame.sprite.RenderPlain()
g_rewards = []

# 将全局变量导入到相应模块
import movable_sprite
movable_sprite.g_player1_bullet_list = g_player1_bullet_list
movable_sprite.g_enamy_bullet_list = g_enamy_bullet_list
movable_sprite.g_player1_list = g_player1_list
movable_sprite.g_enamy_list = g_enamy_list
movable_sprite.g_explosion_list = g_explosion_list
movable_sprite.g_prize_list = g_prize_list
movable_sprite.g_brick_list = g_brick_list
movable_sprite.g_stone_list = g_stone_list
movable_sprite.g_grass_list = g_grass_list
movable_sprite.g_water_list = g_water_list
movable_sprite.g_wall_list = g_wall_list
movable_sprite.g_home_list = g_home_list
movable_sprite.g_rewards = g_rewards
import stable_sprite
stable_sprite.g_player1_bullet_list = g_player1_bullet_list
stable_sprite.g_enamy_bullet_list = g_enamy_bullet_list
stable_sprite.g_player1_list = g_player1_list
stable_sprite.g_enamy_list = g_enamy_list
stable_sprite.g_explosion_list = g_explosion_list
stable_sprite.g_prize_list = g_prize_list
stable_sprite.g_brick_list = g_brick_list
stable_sprite.g_stone_list = g_stone_list
stable_sprite.g_grass_list = g_grass_list
stable_sprite.g_water_list = g_water_list
stable_sprite.g_wall_list = g_wall_list
stable_sprite.g_home_list = g_home_list
stable_sprite.g_rewards = g_rewards
from movable_sprite import *
from stable_sprite import *

# 添加家
home = Home(250,490)
g_home_list.add(home)
# 添加墙壁
wall=Wall(0,0,10,540)
g_wall_list.add(wall)
wall=Wall(10,0,530,10)
g_wall_list.add(wall)
wall=Wall(10,530,530,10)
g_wall_list.add(wall)
wall=Wall(530,10,10,520)
g_wall_list.add(wall)

player1 = None

# 敌人队列
#enamy_queue = [str(random.randint(1,3)) for i in range(20)]
enamy_queue = []

# 敌人的出生地点
positions = [(10,10),(250,10),(490,10)]
positions.reverse()

freezing_time = -1
home_protected_time = -1
home_left,home_top,home_right,home_bottom = (210,450,330,530)

# 需要全局变量g_brick_list,g_stone_list,g_home_list,g_player1_list,g_enamy_list,home_{ltrb}
def protected_home():
	for brick in g_brick_list:
		x,y = brick.rect.left,brick.rect.top
		if x<home_left or x>=home_right or y>=home_bottom or y<home_top:
			continue
		brick.kill()
	for x in range(home_left,home_right,20):
		for y in range(home_top,home_bottom,20):
			stone = Stone(x,y)
			collide_home = pygame.sprite.spritecollide(stone, g_home_list, False)
			collide_player1 = pygame.sprite.spritecollide(stone, g_player1_list, False)
			collide_enamy = pygame.sprite.spritecollide(stone, g_enamy_list, False)
			if collide_home or collide_player1 or collide_enamy:
				pass
			else:
				g_stone_list.add(stone)

# 需要全局变量g_stone_list,g_brick_list,g_home_list,g_player1_list,g_enamy_list,home_{ltrb}
def reset_home():
	for stone in g_stone_list:
		x,y = stone.rect.left,stone.rect.top
		if x<home_left or x>=home_right or y>=home_bottom or y<home_top:
			continue
		stone.kill()
	for x in range(home_left,home_right,10):
		for y in range(home_top,home_bottom,10):
			brick = Brick(x,y)
			collide_home = pygame.sprite.spritecollide(brick, g_home_list, False)
			collide_player1 = pygame.sprite.spritecollide(brick, g_player1_list, False)
			collide_enamy = pygame.sprite.spritecollide(brick, g_enamy_list, False)
			if collide_home or collide_player1 or collide_enamy:
				pass
			else:
				g_brick_list.add(brick)

# 需要全局变量g_rewards,g_enamy_list,freezing_time,home_protected_time
def take_reward():
	global freezing_time, home_protected_time
	while g_rewards:
		player,reward = g_rewards.pop()
		if reward == 1:
			player.life += 1
		elif reward == 2:
			player.max_bullet_num = 2
			if player.power < 3:
				player.power += 1
				player.changeface("images/Our%d.png" % player.power)
		elif reward == 3:
			freezing_time = 200
		elif reward == 4:
			home_protected_time = 200
			protected_home()
		elif reward == 5:
			player.set_protected(400)
		elif reward == 6:
			for enamy in g_enamy_list:
				enamy.explode()
				enamy.kill()
		else:
			print 'error at take_reward'
			sys.exit()

# 需要全局参数screen,enamy_queue,player1
def paint_enamy_queue():
	panel = pygame.Surface([90, 530])
	panel.fill(blue)
	# 将所有未出场的Enamy绘制到panel上
	for i in range(len(enamy_queue)):
		font = pygame.font.Font(None, 50)
		text = font.render(enamy_queue[i], True, white)
		panel.blit(text, [(i/10)*40+15, (i%10)*35+10])
	# 将player1的生命等信息绘制到panel上
	font = pygame.font.Font(None, 40)
	text = font.render('LIFE:%d' % player1.life, True, white)
	panel.blit(text, [0, 400])
	# 将panel镶嵌到screen的特定坐标上
	screen.blit(panel, [545, 5])

# 需要全局参数：enamy_queue,positions,g_enamy_list,g_player1_list
def add_enamy():
	n = enamy_queue.pop()
	enamy = None
	x,y = positions.pop()
	if n == '1':
		enamy = Enamy1(x,y)
	elif n == '2':
		enamy = Enamy2(x,y)
	elif n == '3':
		enamy = Enamy3(x,y)
#if len(enamy_queue) == 15:
	enamy.set_prize(random.randint(1,6))
	collide_enamys = pygame.sprite.spritecollide(enamy, g_enamy_list, False)
	collide_player1 = pygame.sprite.spritecollide(enamy, g_player1_list, False)
	if collide_enamys or collide_player1:
		enamy_queue.append(n)
		positions.append((x,y))
	else:
		g_enamy_list.add(enamy)
		positions.insert(0,(x,y))

# 需要全局参数：player1,g_player1_list
def reborn():
	global player1
	if player1:
		if player1.life > 1:
			player1.life -= 1
			player1.reset(160+offset[0],480+offset[1])
			g_player1_list.add(player1)
		else:
			print 'Game Over'
	else:
		player1 = Player(160+offset[0],480+offset[1],g_player1_bullet_list)
		g_player1_list.add(player1)

# 需要全局参数：enamy_queue,g_brick_list,g_stone_list,g_grass_list,g_water_list
def load_stage(stage):
	fd = open("stage/%d.map" % stage)
	fd.seek(3)
	data = []
	for line in fd.readlines():
		data.append(line.split())
	for row in range(len(data)):
		for col in range(len(data[row])):
			if data[row][col] == '1':
				g_brick_list.add(Brick(offset[0]+col*10,offset[1]+row*10))
			if data[row][col] == '2':
				g_stone_list.add(Stone(offset[0]+col*10,offset[1]+row*10))
			if data[row][col] == '3':
				g_grass_list.add(Grass(offset[0]+col*10,offset[1]+row*10))
			if data[row][col] == '4':
				g_water_list.add(Water(offset[0]+col*10,offset[1]+row*10))
	fd = open("stage/%d.queue" % stage)
	global enamy_queue
	enamy_queue = fd.readlines()[0].split()
	enamy_queue.reverse()

load_stage(8)
	
clock = pygame.time.Clock()
done = False

player1_direction_stack = []
player1_firing = False

while done == False:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done=True
 
		if event.type == pygame.KEYDOWN:
			if event.key == ord('a'):
				player1_direction_stack.append((-1,0))
			if event.key == ord('d'):
				player1_direction_stack.append((1,0))
			if event.key == ord('w'):
				player1_direction_stack.append((0,-1))
			if event.key == ord('s'):
				player1_direction_stack.append((0,1))
			if event.key == ord('j'):
				player1_firing = True
                 
		if event.type == pygame.KEYUP:
			if event.key == ord('a'):
				player1_direction_stack.remove((-1,0))
			if event.key == ord('d'):
				player1_direction_stack.remove((1,0))
			if event.key == ord('w'):
				player1_direction_stack.remove((0,-1))
			if event.key == ord('s'):
				player1_direction_stack.remove((0,1))
			if event.key == ord('j'):
				player1_firing = False
                 
	screen.fill(black)
	# 添加必要的Tank
	if len(g_player1_list) == 0:
		reborn()
	if len(g_enamy_list) < 6 and len(enamy_queue) > 0:
		add_enamy()
	# 控制Player1的下一步动作
	if player1_direction_stack:
		x,y = player1_direction_stack[len(player1_direction_stack)-1]
		player1.changespeed(x,y)
	else:
		player1.changespeed(0,0)
	if player1_firing:
		player1.fire()
	#g_player1_bullet_list.update(g_player2_list)
	g_player1_bullet_list.update()
	g_player1_bullet_list.draw(screen)
	g_enamy_bullet_list.update()
	g_enamy_bullet_list.draw(screen)
	g_player1_list.update()
	g_player1_list.draw(screen)
	if freezing_time >= 0:
		freezing_time -= 1
	else:
		g_enamy_list.update()
	if home_protected_time >= 0:
		home_protected_time -= 1
		if home_protected_time == 0:
			reset_home()
	g_enamy_list.draw(screen)
	g_wall_list.draw(screen)
	g_brick_list.draw(screen)
	g_stone_list.draw(screen)
	g_water_list.draw(screen)
	g_grass_list.draw(screen)
	g_explosion_list.update()
	g_explosion_list.draw(screen)
	g_prize_list.update()
	g_prize_list.draw(screen)
	g_home_list.update()
	g_home_list.draw(screen)
	take_reward()
	paint_enamy_queue()

	pygame.display.flip()
	clock.tick(40)
             
pygame.quit()
