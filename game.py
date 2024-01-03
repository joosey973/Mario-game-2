import os
import sys

import pygame

pygame.font.init()

LEVEL_COUNT = 1


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class MainWindow:
    def __init__(self):
        self.cell_size = 50
        self.width, self.height = 500, 500
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.fon = pygame.transform.scale(load_image("fon.jpg", colorkey=-1), (self.width, self.height))
        self.font = pygame.font.Font(None, 30)
        self.text_rendered = self.font.render("Играть", 1, pygame.Color("black"))
        self.text_collide = self.text_rendered.get_rect()
        self.text_collide.x, self.text_collide.y = (10, self.cell_size)

    def main_window_running(self):
        flag_to_start_game = True
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEMOTION:
                    pos = event.pos
                    if pos[0] in range(self.text_collide.x, self.text_collide.x + self.text_collide.size[0] + 1) and \
                            pos[1] in range(self.text_collide.y, self.text_collide.y + self.text_collide.size[1] + 1):
                        self.text_rendered = self.font.render("Играть", 1, pygame.Color("grey"))
                        flag_to_start_game = True
                    else:
                        self.text_rendered = self.font.render("Играть", 1, pygame.Color("black"))
                        flag_to_start_game = False
                if event.type == pygame.MOUSEBUTTONDOWN and flag_to_start_game:
                    return True
            self.screen.blit(self.fon, (0, 0))
            self.screen.blit(self.text_rendered, (self.text_collide.x, self.text_collide.y))
            pygame.display.update()


class HeroMove(pygame.sprite.Sprite):
    def __init__(self, cell_size, update_tilemap, hero_pos, ind_of_portal, screen, tilemap, *all_sprites):
        super().__init__(*all_sprites)
        self.cell_size = cell_size
        self.hero_pos = hero_pos
        self.ind_of_portal = ind_of_portal
        self.tilemap = tilemap
        self.screen = screen
        self.update_tilemap = update_tilemap
        self.image = load_image("mar.png", colorkey=-1)
        self.rect = self.image.get_rect()
        self.rect.x = self.hero_pos[1] * self.cell_size + self.cell_size // 3.7
        self.rect.y = self.hero_pos[0] * self.cell_size + self.cell_size // 8
        self.d = self.cell_size

    def update_hero_pos(self):
        self.ind_of_portal = tuple((i, j) for i in range(len(self.tilemap)) for j in range(len(self.tilemap[0]))
                                   if self.tilemap[i][j] == "@")[0]
        hero_pos = tuple((i, j) for i in range(len(self.tilemap)) for j in range(len(self.tilemap[0])) if self.tilemap[i][j] == "_")[0]
        self.rect.x = hero_pos[1] * self.cell_size + self.cell_size // 3.7
        self.rect.y = hero_pos[0] * self.cell_size + self.cell_size // 8

    def update(self, *args, **kwargs):
        global LEVEL_COUNT
        if args:
            key = args[0]
            try:
                if self.rect.x // self.cell_size == self.ind_of_portal[1] and self.rect.y // self.cell_size == self.ind_of_portal[0]:
                    LEVEL_COUNT += 1
                    self.tilemap = self.update_tilemap()
                    self.update_hero_pos()
                if key[pygame.K_DOWN] and (self.tilemap[(self.rect.y + self.cell_size) // self.cell_size]
                                           [self.rect.x // self.cell_size]) != '#':
                    if self.rect.y + self.d <= self.screen.get_height():
                        self.rect.top += self.d
                elif key[pygame.K_UP] and (self.tilemap[(self.rect.y - self.cell_size) // self.cell_size]
                                           [self.rect.x // self.cell_size]) != '#':
                    if self.rect.y - self.d >= 0:
                        self.rect.top -= self.d
                elif key[pygame.K_LEFT] and (self.tilemap[self.rect.y // self.cell_size]
                                             [(self.rect.x - self.cell_size) // self.cell_size]) != '#':
                    if self.rect.x - self.d >= 0:
                        self.rect.left -= self.d
                elif key[pygame.K_RIGHT] and (self.tilemap[self.rect.y // self.cell_size]
                                              [(self.rect.x + self.cell_size) // self.cell_size]) != '#':
                    if self.rect.x + self.d <= self.screen.get_width():
                        self.rect.right += self.d
            except IndexError:
                return


class Game:
    def __init__(self):
        self.tilemap = self.update_tilemap()
        self.screen = pygame.display.set_mode((500, 500))
        self.fps = pygame.time.Clock()
        self.cell_size = 50
        self.all_sprites = pygame.sprite.Group()
        self.fps = pygame.time.Clock()

    def render(self, scr):
        for x_coord in range(self.screen.get_width() // self.cell_size):
            for y_coord in range(self.screen.get_height() // self.cell_size):
                self.screen.blit(load_image("grass.png", -1), (x_coord * self.cell_size,
                                                               y_coord * self.cell_size, self.cell_size,
                                                               self.cell_size))
                if self.tilemap[y_coord][x_coord] == '#':
                    self.screen.blit(load_image("box.png", -1), (x_coord * self.cell_size,
                                                                 y_coord * self.cell_size, self.cell_size,
                                                                 self.cell_size))
                elif self.tilemap[y_coord][x_coord] == "@":
                    self.screen.blit(pygame.transform.scale(load_image("portal.jpg", -1), (self.cell_size, self.cell_size)),
                                     (x_coord * self.cell_size, y_coord * self.cell_size, self.cell_size, self.cell_size))

    def update_tilemap(self):
        try:
            self.tilemap = list(map(lambda x: " ".join(x.strip()).split(),
                                    open(rf"maps/tilemap_{LEVEL_COUNT}.txt", "r", encoding="utf-8").readlines()))
            return self.tilemap
        except FileNotFoundError:
            print("Такого уровня ещё нет. Ждите обновления.")
            sys.exit()

    def run(self):
        self.render(self.screen)
        # finding index of portal
        ind_of_portal = tuple((i, j) for i in range(len(self.tilemap)) for j in range(len(self.tilemap[0])) if self.tilemap[i][j] == "@")[0]
        hero_pos = tuple((i, j) for i in range(len(self.tilemap)) for j in range(len(self.tilemap[0])) if self.tilemap[i][j] == "_")[0]
        HeroMove(self.cell_size, self.update_tilemap, hero_pos, ind_of_portal, self.screen, self.tilemap, self.all_sprites)
        while True:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                key = pygame.key.get_pressed()
                self.all_sprites.update(key)
            self.render(self.screen)
            self.all_sprites.draw(self.screen)
            self.fps.tick(60)
            pygame.display.update()


flag = MainWindow().main_window_running()
if flag:
    Game().run()
