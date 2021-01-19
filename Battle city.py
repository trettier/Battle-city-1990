import pygame
import copy
import os
import sys
import random
import math

ch = 0
pygame.init()
SIZE_SCREEN = SIZE_LENGTH, SIZE_HEIGHT = 852, 788
screen = pygame.display.set_mode(SIZE_SCREEN)


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('start_window.png'), (1024, 896))
    screen.blit(fon, (-60, -54))
    font = pygame.font.Font(None, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(60)


def end_screen(win=False):
    if not win:
        fon = pygame.transform.scale(load_image('end.png'), (1024, 896))
    else:
        fon = pygame.transform.scale(load_image('win.png'), (1024, 896))
    screen.blit(fon, (-86, -54))
    font = pygame.font.Font(None, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(60)


def load_image(name, colorkey=None, convert=None):
    fullname = os.path.join("data", name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    if convert is not None:
        image = pygame.transform.scale(image, convert)
    return image


def modul(a, speed):
    b, c = math.fabs(a[0]), math.fabs(a[1])
    if b == 0 and c == 0:
        return [0, 0]
    if c == 0 or (b < c and b != 0):
        return [int(a[0] // b * speed), 0]
    else:
        return [0, int(a[1] // c * speed)]


# класс разметки игрового поля, если она нужна
class Board:
    def __init__(self, wigth, height):
        self.wigth = wigth
        self.height = height
        self.board = [[0] * wigth for _ in range(height)]

        self.left = 10
        self.top = 10
        self.cell_size = 64

    def render(self, screen):
        for x in range(self.height):
            for y in range(self.wigth):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255),
                                 (x * self.cell_size + self.left,
                                  y * self.cell_size + self.top,
                                  self.cell_size,
                                  self.cell_size), 1)


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(wall_sprite)
        if x1 == x2:  # вертикальная стенка
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


# класс стены
class wall(pygame.sprite.Sprite):
    image = load_image("wall_v1.png", convert=(64, 64))
    im_boom = load_image("boom_v1.png", convert=(66, 66))

    def __init__(self, x, y):
        super().__init__(wall_sprite)
        self.image = wall.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.step = 2

    def update(self):
        if self.step == 1:
            self.kill()
        if pygame.sprite.spritecollideany(self, bullet_sprite) \
                or pygame.sprite.spritecollideany(self, enemy_bullet_sprite):
            if self.step == 2:
                self.image = wall.im_boom
                self.step -= 1


# класс управляемого танка
class main_tank(pygame.sprite.Sprite):
    image11 = load_image("tank_v1.1.1.png", convert=(52, 52))
    image12 = load_image("tank_v1.1.2.png", convert=(52, 52))
    image21 = load_image("tank_v1.2.1.png", convert=(52, 52))
    image22 = load_image("tank_v1.2.2.png", convert=(52, 52))
    image31 = load_image("tank_v1.3.1.png", convert=(52, 52))
    image32 = load_image("tank_v1.3.2.png", convert=(52, 52))
    image41 = load_image("tank_v1.4.1.png", convert=(52, 52))
    image42 = load_image("tank_v1.4.2.png", convert=(52, 52))
    im_boom = load_image("boom_v1.png", convert=(66, 66))
    all_images = [
        [image11, image12], [image21, image22],
        [image31, image32], [image41, image42]
    ]

    def __init__(self, main_tank_sprite, speed):
        super().__init__(main_tank_sprite)
        self.image = main_tank.image11
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image11)
        self.rect.x = 394
        self.rect.y = 714
        self.direction = [-2, 0]
        self.all_images = {}
        self.all_images[f"[0, -{speed}]"] = main_tank.all_images[0]
        self.all_images[f"[-{speed}, 0]"] = main_tank.all_images[1]
        self.all_images[f"[0, {speed}]"] = main_tank.all_images[2]
        self.all_images[f"[{speed}, 0]"] = main_tank.all_images[3]
        self.flag = True
        self.forbidden_direction = None
        self.images = self.all_images[str(self.direction)]
        self.life = 2
        self.step = 2

    def moving(self, direction):
        if direction:
            if self.direction != direction:
                self.direction = direction
                self.images = self.all_images[str(direction)]
                self.flag = True
                if self.forbidden_direction != None:
                    self.rect = self.rect.move(self.forbidden_direction[0] * -1,
                                               self.forbidden_direction[1] * -1)
                    self.forbidden_direction = None
            self.col = pygame.sprite.spritecollideany(self, wall_sprite)

            if not self.col:
                self.rect = self.rect.move(direction)
            elif self.forbidden_direction == None:
                self.forbidden_direction = direction

            if self.flag:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.flag = not self.flag

    def update(self):
        if self.image == main_tank.im_boom:
            if self.flag:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.flag = not self.flag
        if self.life != 0:
            if pygame.sprite.spritecollideany(self, enemy_bullet_sprite):
                self.life -= 1
                self.image = main_tank.im_boom
        elif self.step == 1:
            self.kill()
            return "Game over"
        else:
            self.image = main_tank.im_boom
            self.step -= 1


# класс вражеских танков
class enemy_tank(pygame.sprite.Sprite):
    global ch
    image11 = load_image("tank_v2.1.1.png", convert=(52, 52))
    image12 = load_image("tank_v2.1.2.png", convert=(52, 52))
    image21 = load_image("tank_v2.2.1.png", convert=(52, 52))
    image22 = load_image("tank_v2.2.2.png", convert=(52, 52))
    image31 = load_image("tank_v2.3.1.png", convert=(52, 52))
    image32 = load_image("tank_v2.3.2.png", convert=(52, 52))
    image41 = load_image("tank_v2.4.1.png", convert=(52, 52))
    image42 = load_image("tank_v2.4.2.png", convert=(52, 52))
    im_boom = load_image("boom_v1.png", convert=(66, 66))
    all_images = [
        [image11, image12], [image21, image22], [image31, image32], [image41, image42]
    ]

    def __init__(self, enemy_tank_sprite, speed, coor):
        super().__init__(enemy_tank_sprite)
        self.image = enemy_tank.image11
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image11)
        self.rect.x, self.rect.y = coor
        self.direction = [-2, 0]
        self.all_images = {}
        self.all_images[f"[0, -{speed}]"] = enemy_tank.all_images[0]
        self.all_images[f"[-{speed}, 0]"] = enemy_tank.all_images[1]
        self.all_images[f"[0, {speed}]"] = enemy_tank.all_images[2]
        self.all_images[f"[{speed}, 0]"] = enemy_tank.all_images[3]
        self.flag = True
        self.forbidden_direction = None
        self.speed = speed
        self.images = self.all_images[str(self.direction)]
        self.step = 2
        self.direction_2 = [0, 0]
        self.k = 0

    def update(self, flag, rect, shot):
        if flag:
            y = ((rect[0] + rect[2] // 2) - 10) // 64
            x = ((rect[1] + rect[3] // 2) - 10) // 64
            self.x = ((self.rect[1] + self.rect[3] // 2) - 10) // 64
            self.y = ((self.rect[0] + self.rect[2] // 2) - 10) // 64
            direction = [(self.y - y) * -1, (self.x - x) * -1]
            self.direction_2 = modul(direction, self.speed)

        if self.direction_2 != [0, 0]:
            if self.direction != self.direction_2:
                self.direction = self.direction_2
                self.images = self.all_images[str(self.direction)]
                self.flag = True
                if self.forbidden_direction != None:
                    self.rect = self.rect.move(self.forbidden_direction[0] * -1,
                                               self.forbidden_direction[1] * -1)
                    self.forbidden_direction = None
            self.col = pygame.sprite.spritecollideany(self, wall_sprite)

            if not self.col:
                self.rect = self.rect.move(self.direction)
            elif self.forbidden_direction == None:
                self.forbidden_direction = self.direction

            if self.flag:
                self.image = self.images[1]
            else:
                self.image = self.images[0]
            self.flag = not self.flag

        if self.step == 1:
            self.kill()
            score.kill()

        if pygame.sprite.spritecollideany(self, bullet_sprite):
            if self.step == 2:
                self.image = enemy_tank.im_boom
                self.step -= 1

        if shot:
            self.fire()

    def fire(self):
        if self.direction_2 != [0, 0]:
            enemy_bullet(self.speed, self.direction_2, self.rect)


# класс дружественных снарядов
class main_bullet(pygame.sprite.Sprite):
    image1 = load_image("bul_v1.png", convert=(12, 16))
    image2 = load_image("bul_v2.png", convert=(16, 12))
    image3 = load_image("bul_v3.png", convert=(12, 16))
    image4 = load_image("bul_v4.png", convert=(16, 12))
    all_images = [image1, image2, image3, image4]

    def __init__(self, speed, direction, coor):
        super().__init__(bullet_sprite)
        self.all_images = {}
        self.all_images[f"[0, -{speed}]"] = main_bullet.all_images[0]
        self.all_images[f"[-{speed}, 0]"] = main_bullet.all_images[1]
        self.all_images[f"[0, {speed}]"] = main_bullet.all_images[2]
        self.all_images[f"[{speed}, 0]"] = main_bullet.all_images[3]

        self.image = self.all_images[str(direction)]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = [direction[0] * 7, direction[1] * 7]

        self.rect.x = coor[0] + 20 + direction[0] * 18
        self.rect.y = coor[1] + 20 + direction[1] * 18

    def update(self):
        if not pygame.sprite.spritecollideany(self, wall_sprite) \
                and not pygame.sprite.spritecollideany(self, enemy_tank_sprite):
            self.rect = self.rect.move(self.direction)
        else:
            self.kill()


# класс вражеских снарядов
class enemy_bullet(pygame.sprite.Sprite):
    image1 = load_image("bul_v1.png", convert=(12, 16))
    image2 = load_image("bul_v2.png", convert=(16, 12))
    image3 = load_image("bul_v3.png", convert=(12, 16))
    image4 = load_image("bul_v4.png", convert=(16, 12))
    all_images = [image1, image2, image3, image4]

    def __init__(self, speed, direction, coor):
        super().__init__(enemy_bullet_sprite)
        self.all_images = {}
        self.all_images[f"[0, -{speed}]"] = main_bullet.all_images[0]
        self.all_images[f"[-{speed}, 0]"] = main_bullet.all_images[1]
        self.all_images[f"[0, {speed}]"] = main_bullet.all_images[2]
        self.all_images[f"[{speed}, 0]"] = main_bullet.all_images[3]

        self.image = self.all_images[str(direction)]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = [direction[0] * 7, direction[1] * 7]

        self.rect.x = coor[0] + 20 + direction[0] * 18
        self.rect.y = coor[1] + 20 + direction[1] * 18

    def update(self):
        if not pygame.sprite.spritecollideany(self, wall_sprite) \
                and not pygame.sprite.spritecollideany(self, main_tank_sprite):
            self.rect = self.rect.move(self.direction)
        else:
            self.kill()


class Score():
    def __init__(self):
        self.list = 0

    def kill(self):
        self.list += 1


clock = pygame.time.Clock()
fps = 60
fps_clock = pygame.time.Clock()
speed = 2
direction = [0, -speed]
movement = None
lvl = open('data/level.txt', encoding="utf8").read().split()

main_running = True
while main_running:

    start_screen()

    BULLETEVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(BULLETEVENT, 1000)
    bul_flag = True
    ENEMYII = pygame.USEREVENT + 1
    pygame.time.set_timer(BULLETEVENT, 533)
    ene_flag = True
    ENEMYBULEV = pygame.USEREVENT + 3
    pygame.time.set_timer(ENEMYBULEV, 2000)
    enebul_flag = False
    ENEMYSPAWN = pygame.USEREVENT + 4
    pygame.time.set_timer(ENEMYSPAWN, 3198)
    spawnpoint = 0
    points = [(11, 11), (787, 11), (11, 335), (787, 340)]
    ch = 0
    ch_flag = False

    main_tank_sprite = pygame.sprite.Group()
    wall_sprite = pygame.sprite.Group()
    bullet_sprite = pygame.sprite.Group()
    enemy_bullet_sprite = pygame.sprite.Group()
    enemy_tank_sprite = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    Border(10, 10, SIZE_LENGTH - 10, 10)
    Border(10, SIZE_HEIGHT - 10, SIZE_LENGTH - 10, SIZE_HEIGHT - 10)
    Border(10, 10, 10, SIZE_HEIGHT - 10)
    Border(SIZE_LENGTH - 10, 10, SIZE_LENGTH - 10, SIZE_HEIGHT - 10)
    board = Board(13, 12)
    score = Score()
    golden = main_tank(main_tank_sprite, speed)
    for i in range(12):
        for j in range(13):
            if lvl[i][j] == "1":
                wall(j * 64 + 10, i * 64 + 10)

    for i in range(0):
        x = random.randrange(0, 12) * 64 + 10
        y = random.randrange(0, 11) * 64 + 10
        enemy_tank(enemy_tank_sprite, speed, [x, y])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.key.get_pressed()[pygame.K_a]:
                movement = [-speed, 0]
            elif pygame.key.get_pressed()[pygame.K_s]:
                movement = [0, speed]
            elif pygame.key.get_pressed()[pygame.K_w]:
                movement = [0, -speed]
            elif pygame.key.get_pressed()[pygame.K_d]:
                movement = [speed, 0]
            else:
                movement = None

            if not bul_flag:
                if event.type == BULLETEVENT:
                    bul_flag = True
            if movement:
                direction = movement
            if event.type == pygame.MOUSEBUTTONDOWN:
                if bul_flag:
                    main_bullet(speed, direction, golden.rect)
                bul_flag = False

            if event.type == ENEMYII:
                ene_flag = True

            if event.type == ENEMYBULEV:
                enebul_flag = True

            if event.type == ENEMYSPAWN:
                enemy_tank(enemy_tank_sprite, speed, points[spawnpoint])
                spawnpoint = (spawnpoint + 1) % 4

        golden.moving(movement)
        fps_clock.tick(fps)
        screen.fill((0, 0, 0))

        # board.render(screen)
        main_tank_sprite.draw(screen)
        wall_sprite.draw(screen)
        bullet_sprite.draw(screen)
        enemy_tank_sprite.draw(screen)
        enemy_bullet_sprite.draw(screen)

        wall_sprite.update()
        bullet_sprite.update()
        enemy_bullet_sprite.update()
        if golden.update():
            running = False
        enemy_tank_sprite.update(ene_flag, golden.rect, enebul_flag)
        if score.list == 5:
            print(ch)
            ch += 1
            if ch >= 1:
                ch_flag = True
                running = False
        ene_flag = False
        enebul_flag = False

        pygame.display.flip()

    main_tank_sprite.remove()
    wall_sprite.remove()
    bullet_sprite.remove()
    enemy_bullet_sprite.remove()
    enemy_tank_sprite.remove()
    if not ch:
        end_screen()
    else:
        end_screen(win=True)
pygame.quit()
