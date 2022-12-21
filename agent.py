import pygame
import torch
import random
import numpy
from collections import deque
from game import FlappyBirdGameAI
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


def train():
    sum_reward = 0
    plot_times = []
    plot_mean_times = []
    total_time = 0
    record = 0
    agent = Agent()
    game = FlappyBirdGameAI()
    while True:
        # get old state
        state_old = get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, game_over, time, score = game.play_step(final_move)
        state_new = get_state(game)

        sum_reward += reward

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        # memory
        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            # train long memory, plot result
            game.reset()
            agent.number_of_games += 1
            agent.train_long_memory()

            if time > record:
                record = time
                agent.model.save()

            print("Game: ", agent.number_of_games, "Time: ", time, "Record: ", record, "Score: ", score, "Reward: ", sum_reward)
            sum_reward = 0

            plot_times.append(time)
            total_time += time
            mean_times = total_time / agent.number_of_games
            plot_mean_times.append(mean_times)
            plot(plot_times, plot_mean_times)


def get_state(game):
    bird_rect = pygame.Rect((68, 48), game.bird_rect.center)
    bird_rect1 = pygame.Rect((68, 48), game.bird_rect.center)
    bird_rect2 = pygame.Rect((68, 48), game.bird_rect.center)
    bird_rect1.centery -= 12
    bird_rect2.centery += 0.4

    pipes = game.pipe_list

    state = [
        # Dying when jumping
        (bird_rect1.bottom >= 900) or
        (bird_rect1.top <= -100) or
        (game.check_collision(pipes, bird_rect1)),

        # Dying when doing nothing
        (bird_rect2.bottom >= 900) or
        (bird_rect2.top <= -100) or
        (game.check_collision(pipes, bird_rect2)),

        game.bird_movement,

        game.dist,

        game.pipe_space,

        game.space_mid[0],
        game.space_mid[1],

        bird_rect.x,
        bird_rect.y
    ]

    return numpy.array(state, dtype=int)


class Agent:

    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(9, 256, 2)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        self.epsilon = 80 - self.number_of_games
        final_move = [0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 1)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            if torch.cuda.is_available():
                state0 = state0.cuda()
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


if __name__ == "__main__":
    train()
