import pygame as pg
import numpy as np
import math
from os import path
import time

FPS = 60
TITLE = 'Birds'
WIDTH = 1366
HEIGHT = 768
TIME_DELTA = 1
G = 6.67408e-11
img_folder = path.join(path.dirname(__file__), 'Img')
snd_folder = path.join(path.dirname(__file__), 'Snd')
font_name = pg.font.match_font('arial')
LEEWAY_TIME = 0.1
LEEWAY_ANGLE = math.pi / 90
LEEWAY_SPEED = 10
font_name = pg.font.match_font('arial')

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

pg.init()
pg.mixer.init()
win = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(TITLE)
clock = pg.time.Clock()


class Ball(pg.sprite.Sprite):
    def __init__(self, x, y, mass, radius, image):
        pg.sprite.Sprite.__init__(self)
        self.mass = mass
        self.radius = radius
        self.accel = np.array([0, 0])
        self.v = np.array([0, 0])
        self.image = pg.transform.scale(image, (radius * 2, radius * 2))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.pos = np.array([x, y])
        self.previous_contact = self.pos
        self.time_previous_contact = {}

    def update(self):
        self.pos = self.pos + self.v * TIME_DELTA
        self.v = self.v + self.accel * TIME_DELTA
        self.rect.center = (self.pos[0], self.pos[1])


class Player():
    def __init__(self, x, y, theta, size, lives, min_power, max_power, min_theta, max_theta, delta_power):
        self.x = x
        self.y = y
        self.theta = theta
        self.min_theta = min_theta
        self.max_theta = max_theta
        self.power = 0
        self.delta_theta = math.pi / 180
        self.ready = False
        self.power_time = False
        self.delta_power = delta_power
        self.direction = 0
        self.more_power = 0
        self.delay = 250
        self.last_space = pg.time.get_ticks()
        self.image = rocket
        self.image.set_colorkey(BLACK)
        self.size = size
        self.image = pg.transform.scale(self.image, (size, size))
        self.lives = lives
        self.max_power = max_power
        self.min_power = min_power

    def update(self):
        keystate = pg.key.get_pressed()
        if not self.power_time:
            if keystate[pg.K_SPACE]:
                self.power_time = True
                self.last_space = pg.time.get_ticks()
            elif keystate[pg.K_UP] and keystate[pg.K_DOWN]:
                self.direction = 0
            elif keystate[pg.K_UP]:
                self.direction = -1
                settup_snd.stop()
                settup_snd.play()
            elif keystate[pg.K_DOWN]:
                self.direction = 1
                settup_snd.stop()
                settup_snd.play()
            else:
                self.direction = 0
            self.theta += (self.delta_theta * self.direction)
            if self.theta < self.min_theta:
                self.theta = self.min_theta
            if self.theta > self.max_theta:
                self.theta = self.max_theta

        elif pg.time.get_ticks() - self.last_space > self.delay:
            if keystate[pg.K_SPACE]:
                p_ball.v = np.array([math.cos(self.theta) * self.power, math.sin(self.theta) * self.power])
                self.ready = True
                shot_snd.play()
            elif keystate[pg.K_UP] and keystate[pg.K_DOWN]:
                self.more_power = 0
            elif keystate[pg.K_UP]:
                self.more_power = -1
                settup_snd.stop()
                settup_snd.play()
            elif keystate[pg.K_DOWN]:
                self.more_power = 1
                settup_snd.stop()
                settup_snd.play()
            else:
                self.more_power = 0
            self.power += (self.delta_power * self.more_power)
            if self.power < self.min_power:
                self.power = self.min_power
            if self.power > self.max_power:
                self.power = self.max_power

    def draw(self):
        #pg.draw.line(win, BLUE, (p_ball.rect.centerx, p_ball.rect.centery), (p_ball.rect.centerx + math.cos(self.theta) * self.power, p_ball.rect.centery + math.sin(self.theta) * self.power))
        img = pg.transform.rotate(self.image, -self.theta * 180 / math.pi)
        rect = img.get_rect()
        rect.center = (self.x - math.cos(self.theta) * self.power * 10, self.y - math.sin(self.theta) * self.power * 10)
        win.blit(img, rect)


def distPoints(x1, y1, x2, y2):
    return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))


def overlap(obj1, obj2):
    return distPoints(obj1.rect.centerx, obj1.rect.centery, obj2.rect.centerx, obj2.rect.centery) <= obj1.radius + obj2.radius


def collision(obj1, obj2):
    global game_over, level
    if (obj1 == winner_ball and obj2 == win_planet) or (obj2 == winner_ball and obj1 == win_planet):
        level += 1
        win_screen()
        game_over = True
        return

    distance_between_center_of_mass = distPoints(obj1.rect.centerx, obj1.rect.centery, obj2.rect.centerx, obj2.rect.centery)
    unit_x = (obj1.pos - obj2.pos) / distance_between_center_of_mass
    unit_y = unit_x
    unit_y = unit_y[0] * -1
    v1xi = np.dot(unit_x, obj1.v)
    v1y = np.dot(unit_y, obj1.v)
    v2xi = np.dot(unit_x, obj2.v)
    v2y = np.dot(unit_y, obj2.v)

    v1xf = (v1xi * (obj1.mass - obj2.mass) + 2 * obj2.mass * v2xi) / (obj1.mass + obj2.mass)
    v2xf = (v2xi * (obj2.mass - obj1.mass) + 2 * obj1.mass * v1xi) / (obj1.mass + obj2.mass)

    obj1.v = v1xf * unit_x + v1y * unit_y
    obj2.v = v2xf * unit_x + v2y * unit_y

    if obj2 in obj1.time_previous_contact.keys():
        angle = math.acos((obj1.accel[0] * obj2.accel[1] + obj1.accel[1] * obj2.accel[0]) / math.sqrt((obj1.accel[0]**2 + obj1.accel[1]**2) * (obj2.accel[0]**2 + obj2.accel[1]**2)))
        if obj1.time_previous_contact[obj2] - pg.time.get_ticks() < LEEWAY_TIME and angle < math.pi + LEEWAY_ANGLE and angle > math.pi + LEEWAY_ANGLE:
            obj1.v -= np.dot(obj1.accel / np.linalg.norm(obj1.accel), obj1.v)
            obj2.v -= np.dot(obj2.accel / np.linalg.norm(obj2.accel), obj1.v)

            if np.linalg.norm(obj1.v) <= LEEWAY_SPEED:
                obj1.v *= 0

            if np.linalg.norm(obj2.v) <= LEEWAY_SPEED:
                obj2.v *= 0
        obj1.time_previous_contact[obj2] = pg.time.get_ticks()
    else:
        obj1.time_previous_contact[obj2] = pg.time.get_ticks()


def update():
    global game_over
    if p.ready:
        all_sprites.update()
        obj_num = 0
        list_accel = [[] for i in range(len(obj_with_mass))]
        for obj in list(obj_with_mass)[:-1:]:
            obj_num_2 = obj_num + 1
            for obj2 in list(obj_with_mass)[obj_num_2::]:
                distance_between_center_of_mass = distPoints(obj.rect.centerx, obj.rect.centery, obj2.rect.centerx, obj2.rect.centery)
                if overlap(obj, obj2):
                    collision(obj, obj2)
                    obj_num_2 += 1
                    continue
                force = ((G * obj.mass * obj2.mass) / ((obj.rect.centerx - obj2.rect.centerx)**2 + (obj.rect.centery - obj2.rect.centery)**2)**(3 / 2)) * np.array([obj2.rect.centerx - obj.rect.centerx, obj2.rect.centery - obj.rect.centery])
                list_accel[obj_num].append(force / obj.mass)
                list_accel[obj_num_2].append(force / (- obj2.mass))
                obj_num_2 += 1

            obj_num += 1
        obj_num = 0
        for obj in obj_with_mass:
            obj.accel = sum(list_accel[obj_num])
            obj_num += 1

        if p.lives <= 0:
            gg_snd.play()
            lost_screen()
            game_over = True
        if False:  # win condition
            win_screen()
            game_over = True

    if not p.ready:
        p.update()


def draw():
    win.fill(BLUE)
    win.blit(background, background_rect)

    all_sprites.draw(win)
    if not p.ready:
        p.draw()
    # for obj in obj_with_mass:
    #     pg.draw.circle(win, RED, obj.rect.center, 150)
    win.blit(cover, cover_rect)
    win.blit(restartbtn, restartbtn_rect)
    draw_lives()
    pg.display.flip()


def draw_lives():
    for i in range(p.lives - 1):
        img_rect = mini_rocket.get_rect()
        img_rect.x = WIDTH - 300 + 100 * i
        img_rect.centery = HEIGHT * 11 / 12
        win.blit(mini_rocket, img_rect)

#########
# beauty functions
###


def draw_text(surf, text, size, x, y, color):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def lost_screen():
    draw_text(win, 'You lost...', 100, WIDTH // 2, HEIGHT // 2, WHITE)
    draw_text(win, 'Press a key to continue', 25, WIDTH // 2, HEIGHT // 2 + 100, WHITE)
    pg.display.flip()
    time.sleep(4)
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
                pg.quit()
            if event.type == pg.KEYUP:
                waiting = False


def win_screen():
    global music_on
    draw_text(win, 'YOU WON!!!', 100, WIDTH // 2, HEIGHT // 2, WHITE)
    draw_text(win, 'Press a key to continue', 25, WIDTH // 2, HEIGHT // 2 + 100, WHITE)
    pg.display.flip()
    music_on = False
    pg.mixer.music.stop()
    music_on = False
    win_snd.play()
    time.sleep(4)
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                waiting = False
                pg.quit()
            if event.type == pg.KEYUP:
                waiting = False


def show_go_screen():
    win.fill(BLUE)
    win.blit(background, background_rect)
    draw_text(win, 'PLANET!', 200, WIDTH / 2, HEIGHT / 6, WHITE)
    draw_text(win, 'UP and DOWN to change your angle. ENTER to lock in', 30, WIDTH / 2, HEIGHT / 2, WHITE)
    draw_text(win, 'UP and DOWN to change you power. ENTER to FIRE', 30, WIDTH / 2, HEIGHT / 2 + 40, WHITE)
    draw_text(win, 'MAKE THE EARTH HIT MARS', 30, WIDTH / 2, HEIGHT / 2 + 40 + 40, WHITE)
    draw_text(win, 'Press a key to start (except space)', 40, WIDTH / 2, HEIGHT * 3 / 4, WHITE)
    pg.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYUP:
                waiting = False


def pause(win):
    draw_text(win, 'PAUSE', 80, WIDTH / 2, HEIGHT / 2, RED)
    draw_text(win, 'ESCAPE to continue', 22, WIDTH / 2, HEIGHT / 2 + 80, BLACK)
    pg.event.set_grab(False)
    pg.mouse.set_visible(True)
    pg.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    waiting = False


#######################
#    INITALISE GRAPHICS
#######################
background = pg.image.load(path.join(img_folder, 'background.png')).convert()
background = pg.transform.scale(background, (WIDTH, HEIGHT))
background_rect = background.get_rect()
player_img = pg.image.load(path.join(img_folder, 'planet1.png')).convert()
planet2 = pg.image.load(path.join(img_folder, 'planet2.png')).convert()
planet3 = pg.image.load(path.join(img_folder, 'planet3.png')).convert()
planet4 = pg.image.load(path.join(img_folder, 'planet4.png')).convert()
planet5 = pg.image.load(path.join(img_folder, 'planet5.png')).convert()

playbtn = pg.image.load(path.join(img_folder, 'playbtn.png')).convert()
playbtn.set_colorkey(BLACK)
restartbtn = pg.image.load(path.join(img_folder, 'restartbtn.png')).convert()
restartbtn = pg.transform.scale(restartbtn, (100, 50))
restartbtn.set_colorkey(BLACK)
restartbtn_rect = restartbtn.get_rect()
restartbtn_rect.midleft = (30, HEIGHT * 11 / 12)

pausebtn = pg.image.load(path.join(img_folder, 'pausebtn.png')).convert()
pausebtn.set_colorkey(BLACK)
rocket = pg.image.load(path.join(img_folder, 'rocket.png')).convert()
mini_rocket = pg.transform.scale(rocket, (100, 100))
mini_rocket = pg.transform.rotate(mini_rocket, 90)
mini_rocket.set_colorkey(BLACK)

cover = pg.image.load(path.join(img_folder, 'starting_screen.png')).convert()
cover = pg.transform.scale(cover, (WIDTH, HEIGHT / 6))
cover.set_colorkey(BLACK)
cover_rect = cover.get_rect()
cover_rect.bottomleft = (0, HEIGHT)

#######
# INitialise sounds
# 3

settup_snd = pg.mixer.Sound(path.join(snd_folder, 'rocketgettinginposition.wav'))
settup_snd.set_volume(0.5)

shot_snd = pg.mixer.Sound(path.join(snd_folder, 'rocketbeingshot.wav'))
shot_snd.set_volume(0.5)

win_snd = pg.mixer.Sound(path.join(snd_folder, 'winning.wav'))
win_snd.set_volume(0.5)

gg_snd = pg.mixer.Sound(path.join(snd_folder, 'gameover.wav'))
gg_snd.set_volume(0.5)

click_snd = pg.mixer.Sound(path.join(snd_folder, 'buttonclick.wav'))
click_snd.set_volume(0.5)

pg.mixer.music.load(path.join(snd_folder, 'music.wav'))
pg.mixer.music.set_volume(0.1)
pg.mixer.music.play(loops=-1)


level = 1
music_on = True
game_over = True
refresh = False
# game loop
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pg.sprite.Group()
        obj_with_mass = pg.sprite.Group()
        if level <= 1:
            p_ball = Ball(200, 300, 10000000000000, 50, player_img)
            winner_ball = p_ball
            p = Player(p_ball.pos[0], p_ball.pos[1], 0, 1.60 * p_ball.radius, 4, 0, 10, 0, math.pi * 2, 0.25)
            win_planet = Ball(500, 300, 10000000000000, 100, planet2)
            all_sprites.add(p_ball)
            obj_with_mass.add(p_ball)
            all_sprites.add(win_planet)
            obj_with_mass.add(win_planet)

        if level == 2:
            lives = p.lives
            p_ball = Ball(100, 100, 1000000, 50, planet3)
            ball1 = Ball(400, 200, 1000000, 100, player_img)
            win_planet = Ball(1000, 400, 1000000, 100, planet2)
            winner_ball = ball1

            p = Player(p_ball.pos[0], p_ball.pos[1], 0, 1.60 * p_ball.radius, lives, 5, 10, math.pi / 180 * -330, math.pi / 180 * 10, 0.25)
            all_sprites.add(p_ball)
            obj_with_mass.add(p_ball)
            all_sprites.add(ball1)
            obj_with_mass.add(ball1)
            all_sprites.add(win_planet)
            obj_with_mass.add(win_planet)
            all_sprites.add(ball1)
            obj_with_mass.add(ball1)

        if level == 3:
            lives = p.lives
            p_ball = Ball(WIDTH / 2, 100, 10000000000, 25, player_img)
            winner_ball = p_ball
            p = Player(p_ball.pos[0], p_ball.pos[1], 0, 1.60 * p_ball.radius, lives, 0, 10, 0, 0, 0.1)
            win_planet = Ball(WIDTH / 2, 650, 0.0000000000001, 25, planet2)
            ball1 = Ball(WIDTH / 2, 350, 100000000000000, 200, planet5)
            all_sprites.add(p_ball)
            obj_with_mass.add(p_ball)
            all_sprites.add(win_planet)
            obj_with_mass.add(win_planet)
            all_sprites.add(ball1)
            obj_with_mass.add(ball1)
        if not music_on:
            pg.mixer.music.stop()
            pg.mixer.music.load(path.join(snd_folder, 'music.wav'))
            pg.mixer.music.set_volume(0.1)
            pg.mixer.music.play(loops=-1)
            music_on = True
    if refresh:
        game_over = False
        lives = p.lives
        all_sprites = pg.sprite.Group()
        obj_with_mass = pg.sprite.Group()
        p_ball = Ball(300, 100, 1000000, 50, player_img)

        if level <= 1:
            p_ball = Ball(300, 100, 1000000, 50, player_img)
            winner_ball = p_ball
            p = Player(p_ball.pos[0], p_ball.pos[1], 0, 1.60 * p_ball.radius, lives, 0, 10, 0, math.pi * 2, 0.25)
            win_planet = Ball(1000, 600, 1000000, 100, planet2)
            all_sprites.add(p_ball)
            obj_with_mass.add(p_ball)
            all_sprites.add(win_planet)
            obj_with_mass.add(win_planet)

        if level == 2:
            p_ball = Ball(100, 100, 1000000, 50, planet3)
            ball1 = Ball(400, 200, 1000000, 100, player_img)
            win_planet = Ball(1000, 400, 1000000, 100, planet2)
            winner_ball = ball1

            p = Player(p_ball.pos[0], p_ball.pos[1], 0, 1.60 * p_ball.radius, lives, 5, 10, math.pi / 180 * -330, math.pi / 180 * 10, 0.25)
            all_sprites.add(p_ball)
            obj_with_mass.add(p_ball)
            all_sprites.add(ball1)
            obj_with_mass.add(ball1)
            all_sprites.add(win_planet)
            obj_with_mass.add(win_planet)
            all_sprites.add(ball1)
            obj_with_mass.add(ball1)
        if level == 3:
            p_ball = Ball(WIDTH / 2, 100, 10000000000, 25, player_img)
            winner_ball = p_ball
            p = Player(p_ball.pos[0], p_ball.pos[1], 0, 1.60 * p_ball.radius, lives, 0, 10, 0, 0, 0.1)
            win_planet = Ball(WIDTH / 2, 650, 0.0000000000001, 25, planet2)
            ball1 = Ball(WIDTH / 2, 350, 100000000000000, 200, planet5)
            all_sprites.add(p_ball)
            obj_with_mass.add(p_ball)
            all_sprites.add(win_planet)
            obj_with_mass.add(win_planet)
            all_sprites.add(ball1)
            obj_with_mass.add(ball1)

        refresh = False

    clock.tick(FPS)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pause(win)
        if event.type == pg.MOUSEBUTTONDOWN:
            pos_x, pos_y = event.pos
            if pos_x > restartbtn_rect.x and pos_x < restartbtn_rect.right and pos_y > restartbtn_rect.y and pos_y < restartbtn_rect.bottom:
                refresh = True
                p.lives -= 1
                click_snd.play()
            # if pos_x > 0 and pos_x < 50 and pos_y > 0 and pos_y < 50:
            #     print('slword')
            #     TIME_DELTA = 0.5                                               ##########################CHANGING TIME DELTA
            # if pos_x > WIDTH - 50 and pos_x < WIDTH and pos_y > HEIGHT - 50 and pos_y < HEIGHT:
            #     TIME_DELTA = 1.5
            #     print('fast')
    update()
    if level >= 4:
        game_over = True
    draw()
pg.quit()
