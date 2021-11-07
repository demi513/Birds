import pygame as pg
import numpy as np
import math

FPS = 60
TITLE = 'a title'
WIDTH = 600
HEIGHT = 480
TIME_DELTA = 1
G = 6.67408e-11

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
    def __init__(self, x, y, mass, radius):
        pg.sprite.Sprite.__init__(self)
        self.mass = mass
        self.radius = radius
        self.accel = np.array([0, 0])
        self.v = np.array([0, 0])
        self.image = pg.Surface((200, 200))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.pos = np.array([x, y])

    def update(self):
        self.pos = self.pos + self.v * TIME_DELTA
        self.v = self.v + self.accel * TIME_DELTA
        self.rect.center = (self.pos[0], self.pos[1])


class Player():
    def __init__(self, theta, power):
        self.theta = theta
        self.power = power
        self.delta_theta = math.pi / 180
        self.ready = False
        self.power_time = False
        self.delta_power = 1
        self.direction = 0
        self.more_power = 0
        self.delay = 250
        self.last_space = pg.time.get_ticks()

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
            elif keystate[pg.K_DOWN]:
                self.direction = 1
            else:
                self.direction = 0
            self.theta += (self.delta_theta * self.direction)

        elif pg.time.get_ticks() - self.last_space > self.delay:
            if keystate[pg.K_SPACE]:
                p_ball.v = np.array([math.cos(self.theta) * self.power, math.sin(self.theta) * self.power])
                self.ready = True
            elif keystate[pg.K_UP] and keystate[pg.K_DOWN]:
                self.more_power = 0
            elif keystate[pg.K_UP]:
                self.more_power = 1
            elif keystate[pg.K_DOWN]:
                self.more_power = -1
            else:
                self.more_power = 0
            self.power += (self.delta_power * self.more_power)

    def draw(self):
        pg.draw.line(win, BLUE, (p_ball.rect.centerx, p_ball.rect.centery), (p_ball.rect.centerx + math.cos(self.theta) * self.power, p_ball.rect.centery + math.sin(self.theta) * self.power))


def distPoints(x1, y1, x2, y2):
    return math.sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))


def overlap(obj1, obj2):
    return distPoints(obj1.rect.centerx, obj1.rect.centery, obj2.rect.centerx, obj2.rect.centery) < obj1.radius + obj2.radius


def collision(obj1, obj2):
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


def update():
    if p.ready:
        all_sprites.update()
        obj_num = 0
        list_accel = [[] for i in range(len(obj_with_mass))]
        for obj in list(obj_with_mass)[:-1:]:
            obj_num_2 = obj_num + 1
            for obj2 in list(obj_with_mass)[obj_num_2::]:
                distance_between_center_of_mass = distPoints(obj.rect.centerx, obj.rect.centery, obj2.rect.centerx, obj2.rect.centery)
                force = ((G * obj.mass * obj2.mass) / ((obj.rect.centerx - obj2.rect.centerx)**2 + (obj.rect.centery - obj2.rect.centery)**2)**(3 / 2)) * np.array([obj2.rect.centerx - obj.rect.centerx, obj2.rect.centery - obj.rect.centery])
                list_accel[obj_num].append(force / obj.mass)
                list_accel[obj_num_2].append(force / (- obj2.mass))
                if overlap(obj, obj2):
                    collision(obj, obj2)
                obj_num_2 += 1

            obj_num += 1
        obj_num = 0
        for obj in obj_with_mass:
            obj.accel = sum(list_accel[obj_num])
            obj_num += 1

    if not p.ready:
        p.update()


def draw():
    win.fill(BLUE)
    all_sprites.draw(win)
    p.draw()

    pg.display.flip()


#######################
#    INITALISE GRAPHICS
#######################

game_over = True
# game loop
running = True
while running:
    if game_over:
        # show_go_screen()
        game_over = False
        all_sprites = pg.sprite.Group()
        obj_with_mass = pg.sprite.Group()
        p_ball = Ball(100, 0, 10000000000, 150)
        p = Player(0, 100)
        ball2 = Ball(100, 400, 10000000000000, 150)
        ball3 = Ball(600, 400, 5000000000000, 150)
        all_sprites.add(p_ball)
        obj_with_mass.add(p_ball)
        all_sprites.add(ball2)
        obj_with_mass.add(ball2)
        all_sprites.add(ball3)
        obj_with_mass.add(ball3)
        score = 0
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    update()
    draw()
pg.quit()
