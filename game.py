import sys

import numpy
import pygame
import random

pygame.init()

SPAWN_PIPE = pygame.USEREVENT
SCREEN_WIDTH = 576
SCREEN_HEIGHT = 1024
FPS = 60
BIRD_CENTER = (100, 256)


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 5
    return pipes


class FlappyBirdGameAI:

    def __init__(self):
        self.frame_iteration = 0
        self.bird_movement = 0
        self.gravity = 0.4
        self.score = 0
        self.space_mid = (0, 0)
        self.dist = 1000
        self.pipe_space = 0
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()

        self.background = pygame.image.load("resources/sprites/background-day.png").convert()
        self.background = pygame.transform.scale2x(self.background)

        self.bird = pygame.image.load("resources/sprites/bluebird-mid-flap.png").convert_alpha()
        self.bird = pygame.transform.scale2x(self.bird)
        self.bird_rect = self.bird.get_rect(center=BIRD_CENTER)

        self.floor_base = pygame.image.load("resources/sprites/base.png").convert()
        self.floor_base = pygame.transform.scale2x(self.floor_base)
        self.floor_x_pos = 0

        self.pipe_surface = pygame.image.load("resources/sprites/pipe-green.png")
        self.pipe_surface = pygame.transform.scale2x(self.pipe_surface)
        self.pipe_list = []
        self.pipe_height = [400, 600, 800]
        self.pipe_spaces = [225, 250, 275, 300, 325, 350]

        pygame.time.set_timer(SPAWN_PIPE, 1200)

        self.flap_sound = pygame.mixer.Sound("resources/audio/wing.wav")
        self.die_sound = pygame.mixer.Sound("resources/audio/die.wav")

        self.game_active = True

        self.reset()

    def reset(self):
        self.frame_iteration = 0

        self.bird_movement = 0

        self.score = 0

        self.space_mid = (0, 0)

        self.dist = 1000

        self.pipe_space = 0

        self.bird_rect = self.bird.get_rect(center=BIRD_CENTER)

        self.floor_x_pos = 0

        self.bird_rect.center = BIRD_CENTER

        self.pipe_list.clear()

    def play_step(self, action):
        self.frame_iteration += 1
        self.display.blit(self.background, (0, 0))
        game_over = self.check_collision(self.pipe_list, self.bird_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == SPAWN_PIPE and not game_over:
                self.pipe_list.extend(self.create_pipe())

        self._move(action)

        self.bird_movement += self.gravity
        self.bird_rect.centery += self.bird_movement

        self.display.blit(self.bird, self.bird_rect)

        self.pipe_list = move_pipes(self.pipe_list)
        self.draw_pipes(self.pipe_list)

        reward = 0

        self.space_mid = (0, 0)
        pipe_before = None
        old_pipe_mid_pos = None
        for pipe in self.pipe_list:
            pipe_mid_pos = pipe.centerx
            if pipe_mid_pos <= self.bird_rect.centerx < pipe_mid_pos + 0.01 and not old_pipe_mid_pos == pipe_mid_pos:
                self.score += 1
                reward += (2 * self.score)
                old_pipe_mid_pos = pipe_mid_pos
            if pipe_before is not None:
                self.pipe_space = pipe_before.top - pipe.bottom
                self.space_mid = (pipe.centerx, ((100 + pipe.bottom)/2))
                self.space_mid = (self.space_mid[0], self.space_mid[1] + self.pipe_space)
            pipe_before = pipe
        if self.space_mid != (0, 0):
            self.dist = pygame.math.Vector2(self.bird_rect.center).distance_to(self.space_mid)
            dist_reward = ((300 - self.dist) / 1000)
        else:
            dist_reward = 0
        if dist_reward < 0:
            dist_reward = 0
        if game_over:
            reward = reward - 10
            reward = reward + dist_reward
            reward = reward + (0.2 * (self.score + 1))
            return reward, game_over, self.frame_iteration, self.score
        else:
            reward = reward + (0.2 * (self.score + 1))
            #reward = reward + dist_reward

        self.update_ui()
        self.clock.tick(FPS)
        return reward, game_over, self.frame_iteration, self.score

    def _move(self, action):
        if numpy.array_equal(action, [0, 1]):
            self.bird_movement = 0
            self.bird_movement -= 12

    def check_collision(self, pipes, bird_rect):
        for pipe in pipes:
            if bird_rect.colliderect(pipe):
                return True

        if bird_rect.top <= -100 or bird_rect.bottom >= 900:
            return True
        return False

    def game_floor(self):
        self.display.blit(self.floor_base, (self.floor_x_pos, 900))
        self.display.blit(self.floor_base, (self.floor_x_pos + SCREEN_WIDTH, 900))

    def create_pipe(self):
        random_pipe_pos_top = random.choice(self.pipe_height)
        random_pipe_space = random.choice(self.pipe_spaces)
        top_pipe = self.pipe_surface.get_rect(midbottom=(700, random_pipe_pos_top - random_pipe_space))
        bottom_pipe = self.pipe_surface.get_rect(midtop=(700, random_pipe_pos_top))
        return bottom_pipe, top_pipe

    def draw_pipes(self, pipes):
        for pipe in pipes:
            if pipe.bottom >= SCREEN_HEIGHT:
                self.display.blit(self.pipe_surface, pipe)
            else:
                flipped_pipe = pygame.transform.flip(self.pipe_surface, False, True)
                self.display.blit(flipped_pipe, pipe)

    def update_ui(self):
        self.floor_x_pos -= 1
        self.game_floor()
        if self.floor_x_pos <= -SCREEN_WIDTH:
            self.floor_x_pos = 0

        pygame.display.update()
