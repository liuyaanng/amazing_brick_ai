#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dqn import *
from env import *
import tensorflow as tf
import numpy as np
import os
import random
from tqdm import tqdm


# Environment setting
EPISODES = 20000
MIN_REWARD = 0.5
# Exploration setting
epsilon = 1
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.01

# Ststs setting
AGGREGATE_STATS_EVERY = 50 # episodes


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

max_score = 0
arcade.open_window(SCREEN_WIDTH, SCREEN_HIGHT, 'AmazingBrick')
arcade.set_background_color(arcade.color.WHITE)
episode = 0

def main(_delta_time):
    global max_score
    global episode
    global epsilon
    # print("first = ", episode)
    agent.tensorboard.step = episode

    episode_reward = 0
    step = 1
    current_state = env.player.get_state()
    # print(current_state)
    #print(current_state)
    is_game_running = True

    while is_game_running:
        if np.random.random() > epsilon:
            action = np.argmax(agent.get_qs(current_state))
        else:
            action = np.random.randint(0, env.ACTION_SPACE_SIZE)
        new_state, reward, is_game_running, score = env.step(action)
        #print(new_state)
        #print(is_game_running)
        
        episode_reward += reward
        #print(episode_reward)
        #if SHOW_PREVIEW and  episode % AGGREGATE_STATS_EVERY:
 #           env.render()
            #pass

        agent.update_replay_memory((current_state, action, reward, new_state, is_game_running))

        agent.train(is_game_running, step)

        current_state = new_state

        step += 1

        if score > max_score:
            max_score = score

        print('Episode %s ,Current score is %s, Max Score is %s' %(episode,score, max_score))
    # print(" not run")
    
    #print("run")
   #arcade.close_window()
        # Append episode reward to a list and log stats (every given number of episodes)
    ep_rewards.append(episode_reward)
    if not episode % AGGREGATE_STATS_EVERY or episode == 1:
        average_reward = sum(ep_rewards[-AGGREGATE_STATS_EVERY:])/len(ep_rewards[-AGGREGATE_STATS_EVERY:])
        min_reward = min(ep_rewards[-AGGREGATE_STATS_EVERY:])
        max_reward = max(ep_rewards[-AGGREGATE_STATS_EVERY:])
        agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward, epsilon=epsilon)

        # Save model, but only when min reward is greater or equal a set value
        if min_reward >= MIN_REWARD:
            agent.model.save(f'models/{MODEL_NAME}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')

    # Decay epsilon
    if epsilon > MIN_EPSILON:
        epsilon *= EPSILON_DECAY
        epsilon = max(MIN_EPSILON, epsilon)
    episode += 1
    print("final episode = ", episode)

arcade.schedule(main, 1/60)
arcade.run()
arcade.close_window()


