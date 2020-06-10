#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dqn import *
from env import *
import tensorflow as tf
import numpy as np
import os
import random
import argparse



# Environment setting
EPISODES = 20000
MIN_REWARD = 7
# Exploration setting
epsilon = 1
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.01

# Ststs setting
AGGREGATE_STATS_EVERY = 50 # episodes


ep_rewards = [0]

# For more repectitive results
random.seed(1)
np.random.seed(1)
tf.set_random_seed(1)


# Create models folder

if not os.path.isdir('models'):
    os.makedirs('models')


max_score = 0
episode = 0


#print('init current_state', current_state)
is_game_running = True
episode_reward = 0
step = 1
action_space = ["left", "do nothing", "right"]



def ArgParse():
    """TODO: Docstring for ArgParse.
    :returns: TODO

    """
    parser = argparse.ArgumentParser(description = 'Choose mode what you want and show preview or not')
    parser.add_argument('--mode', type = str, help = 'Choose a mode between train and test(default is train)', default = 'train', dest = 'mode')
    parser.add_argument('--show', type = str, help = 'Choose show preview or not(True or False)', default = 'True', dest = 'show')
    parser.add_argument('--model', type = str, help = 'Write the model name', default = 'models/amamzingbrick____20.16max____9.86avg____0.01min__1590280037.model', dest = 'model')

    args = parser.parse_args()
    return args



def play_game(_delta_time):
    global episode
    global current_state
    global is_game_running
    global epsilon
    global max_score
    global episode_reward
    global step
    global env
    global agent
    #print("main current_state", current_state)
    if np.random.random() > epsilon:
         action = agent.get_qs(current_state)
         #print(action)
         action = np.argmax(action)
         #print("action is ", action)
    else:
        action = np.random.randint(0, ACTION_SPACE_SIZE)
    new_state, reward, is_game_running, score = env.step(action)
    #print(new_state)
    #print(is_game_running)

    episode_reward += reward
    #print(episode_reward)
    #if SHOW_PREVIEW and  episode % AGGREGATE_STATS_EVERY:
        #env.render()

    agent.update_replay_memory((current_state, action, reward, new_state, is_game_running))

    agent.train(is_game_running)

    current_state = new_state


    if score > max_score:
        max_score = score
    print('Episode %s , Score = %s, Action is %s' % (episode, score, action_space[action]))
    #print('Episode %s ,Action is %s, Reward is %s, Current score is %s, Max Score is %s' %(episode, action_space[action], reward, score, max_score))
    # print(" not run")
    
    #print("run")
   #arcade.close_window()
        # Append episode reward to a list and log stats (every given number of episodes)
    agent.tensorboard.update_stats(actions = action, steps_score = score)

    if not is_game_running:

        ep_rewards.append(episode_reward)
        if not episode % AGGREGATE_STATS_EVERY or episode == 1:
            average_reward = sum(ep_rewards[-AGGREGATE_STATS_EVERY:])/len(ep_rewards[-AGGREGATE_STATS_EVERY:])
            min_reward = min(ep_rewards[-AGGREGATE_STATS_EVERY:])
            max_reward = max(ep_rewards[-AGGREGATE_STATS_EVERY:])
            agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward, epsilon=epsilon, max_score = max_score)

            # Save model, but only when min reward is greater or equal a set value
            if average_reward >= MIN_REWARD:
                agent.model.save(f'models/{MODEL_NAME}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')

        # Decay epsilon
        if epsilon > MIN_EPSILON:
            epsilon *= EPSILON_DECAY
            epsilon = max(MIN_EPSILON, epsilon)
        episode += 1
        #print("final episode = ", episode)
        # print("first = ", episode)
        agent.tensorboard.step = episode

        episode_reward = 0
        step = 1
        current_state = env.player.get_state()
        # print(current_state)
        #print(current_state)
        is_game_running = True
def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    
    global current_state
    global epsilon
    global env
    global agent

    args = ArgParse()
    mode = args.mode

    # Make sure mode is train or test
    assert mode in ['train', 'test']

    if mode == 'test':
        epsilon = 0.1
    show_preview = args.show == str(True)
    load_model = args.model

    env = AmazingBrickEnv(show_preview)
    current_state = env.player.get_state()
    agent = DQNAgent(load_model)
    agent.tensorboard.step = episode
    if show_preview:
        arcade.open_window(SCREEN_WIDTH, SCREEN_HIGHT, 'AmazingBrick')
        arcade.set_background_color(arcade.color.WHITE)
    arcade.schedule(play_game, 1/60)
    arcade.run()
    #arcade.close_window()


if __name__ == "__main__":
    main()


