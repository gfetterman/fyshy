import itertools as it
import os
import random
import sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

SCORE_HEIGHT_OFFSET = 32
SCORE_FONT_SIZE = 24
END_SPLASH_FONT_SIZE = 36
END_SPLASH_PLAYER_OFFSET = 100

WIN_FLASHES = 5
WIN_FLASH_DURATION = 500 # ms
LOSE_SCREEN_DURATION = 2000 # ms

FPS = 30

BLACK = (0, 0, 0)
XKCD_CRIMSON = (140, 0, 15)
XKCD_BABY_BLUE = (162, 207, 254)
XKCD_CERULEAN = (4, 133, 209)
BG_COLOR = XKCD_BABY_BLUE
INVERT_BG_COLOR = XKCD_CERULEAN
LOSE_SCREEN_COLOR = XKCD_CRIMSON

KEY_DX2DY2 = {pygame.K_UP: (0, -1),
              pygame.K_DOWN: (0, 1),
              pygame.K_LEFT: (-1, 0),
              pygame.K_RIGHT: (1, 0)}
LEFT = -1
RIGHT = 1
# gameplay constant parameters

INITIAL_DIRECTION = LEFT
INITIAL_X = WINDOW_WIDTH // 2
INITIAL_Y = WINDOW_HEIGHT // 2

PLAYER_MAX_SPEED = 3
PLAYER_ACCELERATION = 1.5
ENEMY_SPEED_RANGE = (2, 5)

MAX_ENEMY_FISH = 16
ALLOWED_OVERLAP = 0.8
ENEMY_SIZES = (0.25, 0.5, 0.75, 1.25, 1.75, 2.25, 3.25, 4.5)
SIZE_UP_THRESHOLDS = {4: 1.5, 8: 2, 16: 3, 32: 4}
BASE_SCORE = 100
WIN_SIZE = 32

# icons

WINDOW_ICON_IMG = 'imgs/fish_window_icon.png'
PLAYER_FISH_IMG = 'imgs/fish.png'
PLAYER_FISH_WIGGLE_IMG = 'imgs/fish_tail_wiggle.png'
ENEMY_FISH_IMG = 'imgs/other_fish.png'
ENEMY_FISH_WIGGLE_IMG = 'imgs/enemy_fish_tail_wiggle.png'
DEAD_FISH_IMG = 'imgs/fish_dead.png'

ENEMY_FRAME_STRETCH = 3

class Fish:
    def __init__(self,
                 icons,
                 x=INITIAL_X,
                 y=INITIAL_Y,
                 direction=INITIAL_DIRECTION,
                 max_speed=PLAYER_MAX_SPEED,
                 acceleration=PLAYER_ACCELERATION):
        self.direction = direction
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.acceleration = acceleration
        self.base_icons = icons
        self.base_width, self.base_height = icons[0].get_rect().size
        self.set_icons(icons)
        self.max_speed = max_speed
        self.impulses = {key: False for key in KEY_DX2DY2}
        self.fish_eaten = 0
        self.score = 0

    def set_icons(self, icons):
        flipped = [pygame.transform.flip(icon, True, False) for icon in icons]
        self.icons = icons if self.direction == LEFT else flipped
        self.flipped_icons = flipped if self.direction == LEFT else icons
        self.width, self.height = icons[0].get_rect().size
        self.half_width = self.width // 2
        self.half_height = self.height // 2
        self.curr_icon_idx = 0    @property
    def tail_x(self):
        return self.x - (self.half_width * self.direction)

    @property
    def curr_icon(self):
        return self.icons[self.curr_icon_idx]
    @property
    def top_left(self):
        return (round(self.x - self.half_width),
                round(self.y - self.half_height))

    @property
    def hitbox(self):
        return (self.x - self.half_width * ALLOWED_OVERLAP,
                self.x + self.half_width * ALLOWED_OVERLAP,
                self.y - self.half_height * ALLOWED_OVERLAP,
                self.y + self.half_height * ALLOWED_OVERLAP)
    def update_location(self):
        dx2 = sum(KEY_DX2DY2[key][0] * self.acceleration
                  for key, pressed in self.impulses.items() if pressed)
        dy2 = sum(KEY_DX2DY2[key][1] * self.acceleration
                  for key, pressed in self.impulses.items() if pressed)
        drag_x = self.dx * abs(self.dx) / 30
        drag_y = self.dy * abs(self.dy) / 30
        self.dx = max(min((self.dx + dx2 - drag_x), self.max_speed),
                      -self.max_speed)
        self.dy = max(min((self.dy + dy2 - drag_y), self.max_speed),
                      -self.max_speed)
        self.x = max(min((self.x + self.dx), WINDOW_WIDTH), 0)
        self.y = max(min((self.y + self.dy), WINDOW_HEIGHT), 0)
        if ((dx2 > 0 and self.direction == LEFT) or
            (dx2 < 0 and self.direction == RIGHT)):
            self.direction = LEFT if self.direction == RIGHT else RIGHT
            self.icons, self.flipped_icons = self.flipped_icons, self.icons
        if dx2:
            self.curr_icon_idx = (self.curr_icon_idx + 1) % len(self.icons)

    def eat(self, fish):
        self.fish_eaten += 1
        self.score += fish.score
        if self.fish_eaten in SIZE_UP_THRESHOLDS:
            size_up_proportion = SIZE_UP_THRESHOLDS[self.fish_eaten]
            new_width = int(self.base_width * size_up_proportion)
            new_height = int(self.base_height * size_up_proportion)
            new_icons = [pygame.transform.smoothscale(icon,
                                                      (new_width, new_height))
                         for icon in self.base_icons]
            self.set_icons(new_icons)
class EnemyFish(Fish):
    def __init__(self, icons, x, y, direction, max_speed, size):
        icons = list(it.chain.from_iterable(it.repeat(icon, ENEMY_FRAME_STRETCH)
                                            for icon in icons))
        super().__init__(icons, x, y, direction, max_speed)
        self.size = size
        self.score = size * BASE_SCORE
        self.curr_frame_idx = random.randrange(len(icons))

    def update_location(self):
        self.x = self.x + self.direction * self.max_speed
        self.curr_icon_idx = (self.curr_icon_idx + 1) % len(self.icons)
def overlap(first, second):
    return (first[0] <= second[1] and first[1] >= second[0])
def hitbox_overlap(first, second):
    first_left, first_right, first_bottom, first_top = first.hitbox
    second_left, second_right, second_bottom, second_top = second.hitbox
    return (overlap((first_left, first_right), (second_left, second_right)) and
            overlap((first_bottom, first_top), (second_bottom, second_top)))
def overlap_edges(fish):
    return ((fish.direction == LEFT and fish.tail_x <= 0) or
            (fish.direction == RIGHT and fish.tail_x >= WINDOW_WIDTH))
def handle_collisions(player_fish, other_fish):
    to_remove = []
    for fish_idx, fish in enumerate(other_fish):
        if hitbox_overlap(player_fish, fish):
            if fish.width >= player_fish.width:
                return False
            else:
                to_remove.append(fish_idx)
                player_fish.eat(fish)
        elif overlap_edges(fish):
            to_remove.append(fish_idx)
    for fish_idx in reversed(to_remove):
        other_fish.pop(fish_idx)
    return True
def draw_pond(display_surface, player_fish, other_fish):
    display_surface.fill(BG_COLOR)
    max_x = display_surface.get_width()
    for fish in other_fish + [player_fish]:
        display_surface.blit(fish.curr_icon, fish.top_left)

def draw_score(display_surface, player_fish):
    font = pygame.font.Font(None, SCORE_FONT_SIZE)
    text_surface = font.render(str(int(player_fish.score)), True, BLACK)
    loc = (display_surface.get_width() // 2, SCORE_HEIGHT_OFFSET)
    display_surface.blit(text_surface, text_surface.get_rect(center=loc))
def win_screen(display_surface, player_fish):
    curr_color, next_color = BG_COLOR, INVERT_BG_COLOR
    for _ in range(WIN_FLASHES):
        curr_color, next_color = next_color, curr_color
        display_surface.fill(curr_color)
        player_fish.x = display_surface.get_width() // 2
        player_fish.y = (display_surface.get_height() // 2 -
                         END_SPLASH_PLAYER_OFFSET)
        display_surface.blit(player_fish.curr_icon, player_fish.top_left)
        font = pygame.font.Font(None, END_SPLASH_FONT_SIZE)
        text_surface = font.render('You won!', True, next_color)
        loc = (display_surface.get_width() // 2,
               display_surface.get_height() // 2)
        display_surface.blit(text_surface, text_surface.get_rect(center=loc))
        pygame.display.update()
        pygame.time.wait(WIN_FLASH_DURATION)

def lose_screen(display_surface):
    display_surface.fill(LOSE_SCREEN_COLOR)
    x = display_surface.get_width() // 2
    y = display_surface.get_height() // 2 - END_SPLASH_PLAYER_OFFSET
    dead_fish = Fish([pygame.image.load(DEAD_FISH_IMG)], x, y)
    display_surface.blit(dead_fish.curr_icon, dead_fish.top_left)
    font = pygame.font.Font(None, END_SPLASH_FONT_SIZE)
    text_surface = font.render('You got eaten', True, BLACK)
    loc = (display_surface.get_width() // 2, display_surface.get_height() // 2)
    display_surface.blit(text_surface, text_surface.get_rect(center=loc))
    pygame.display.update()
    pygame.time.wait(LOSE_SCREEN_DURATION)

def spawn_enemy_fish(prototypes):
    size = random.choice(ENEMY_SIZES)
    width, height = (int(size * dim) for dim in prototypes[0].get_rect().size)
    direction = random.choice((LEFT, RIGHT))
    x = WINDOW_WIDTH if direction == LEFT else 0
    x -= direction * width // 2
    y = random.randrange(WINDOW_HEIGHT)
    speed = random.uniform(*ENEMY_SPEED_RANGE)
    icons = [pygame.transform.smoothscale(icon, (width, height))
             for icon in prototypes]
    return EnemyFish(icons, x, y, direction, speed, size)

def repopulate_enemy_fish(enemy_fish, prototypes, count=MAX_ENEMY_FISH):
    return (enemy_fish + [spawn_enemy_fish(prototypes)
                          for _ in range(len(enemy_fish), count)])

def main():
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_icon(pygame.image.load(WINDOW_ICON_IMG))
    player_prototypes = [pygame.image.load(PLAYER_FISH_IMG),
                         pygame.image.load(PLAYER_FISH_WIGGLE_IMG)]
    enemy_prototypes = [pygame.image.load(ENEMY_FISH_IMG),
                        pygame.image.load(ENEMY_FISH_WIGGLE_IMG)]
    player_fish = Fish(player_prototypes)
    enemy_fish = repopulate_enemy_fish([], enemy_prototypes)
    pygame.display.set_caption('Fishpy')
    frame_clock = pygame.time.Clock()
    while True:
        if player_fish.fish_eaten >= WIN_SIZE:
            win_screen(display_surface, player_fish)
            player_fish = Fish(player_prototypes)
            enemy_fish = repopulate_enemy_fish([], enemy_prototypes)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in KEY_DX2DY2:
                    player_fish.impulses[event.key] = True
            elif event.type == pygame.KEYUP:
                if event.key in KEY_DX2DY2:
                    player_fish.impulses[event.key] = False
        for fish in enemy_fish + [player_fish]:
            fish.update_location()
        survived = handle_collisions(player_fish, enemy_fish)
        if not survived:
            lose_screen(display_surface)
            player_fish = Fish(player_prototypes)
            enemy_fish = []
        enemy_fish = repopulate_enemy_fish(enemy_fish, enemy_prototypes)
        draw_pond(display_surface, player_fish, enemy_fish)
        draw_score(display_surface, player_fish)
        pygame.display.update()
        frame_clock.tick(FPS)

if __name__ == '__main__':
    main()
