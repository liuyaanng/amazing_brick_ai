#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dqn import *
from env import *
import tensorflow as tf
import numpy as np
import os
import random
from tqdm import tqdm
import arcade


# Environment setting
EPISODES = 200
MIN_REWARD = 0
# Exploration setting
epsilon = 1
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.01

# Ststs setting
AGGREGATE_STATS_EVERY = 50 # episodes
SHOW_PREVIEW = False


env = AmazingBrickEnv()
ep_rewards = [0]

# For more repectitive results
random.seed(1)
np.random.seed(1)
tf.set_random_seed(1)


# Create models folder

if not os.path.isdir('models'):
    os.makedirs('models')

agent = DQNAgent()

arcade.schedule(env.step, 1/60)
arcade.run()
# for episode in tqdm(range(1, EPISODES + 1), ascii=True, unit="episode"):
    # agent.tensorboard.step = episode

    # episode_reward = 0
    # step = 1
    # current_state = env.reset()
    # print(current_state)
    # is_game_running = True


    # while is_game_running:
        # if np.random.random() > epsilon:
            # action = np.argmax(agent.get_qs(current_state))
        # else:
            # action = np.random.randint(0, env.ACTION_SPACE_SIZE)
        # new_state, reward, is_game_running = env.step(action)
        # print(new_state)

        # episode_reward += reward
        # print(episode_reward)
        # if SHOW_PREVIEW and not episode % AGGREGATE_STATS_EVERY:
            # env.render()

        # agent.update_replay_memory((current_state, action, reward, new_state, is_game_running))

        # agent.train(is_game_running, step)

        # current_state = new_state

        # step += 1


        # # Append episode reward to a list and log stats (every given number of episodes)
    # ep_rewards.append(episode_reward)
    # if not episode % AGGREGATE_STATS_EVERY or episode == 1:
        # average_reward = sum(ep_rewards[-AGGREGATE_STATS_EVERY:])/len(ep_rewards[-AGGREGATE_STATS_EVERY:])
        # min_reward = min(ep_rewards[-AGGREGATE_STATS_EVERY:])
        # max_reward = max(ep_rewards[-AGGREGATE_STATS_EVERY:])
        # agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward, epsilon=epsilon)

        # # Save model, but only when min reward is greater or equal a set value
        # if min_reward >= MIN_REWARD:
            # agent.model.save(f'models/{MODEL_NAME}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')

    # # Decay epsilon
    # if epsilon > MIN_EPSILON:
        # epsilon *= EPSILON_DECAY
        # epsilon = max(MIN_EPSILON, epsilon)


