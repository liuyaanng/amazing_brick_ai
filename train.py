#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dqn import *
from env import *
import tensorflow as tf
import numpy as np
import os
import random



# Environment setting
EPISODES = 20000

# Exploration setting
epsilon = 1
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.01

# Ststs setting
AGGREGATE_STATS_EVERY = 50 # episodes
SHOW_PREVIEW = False
env = AmazingBrickEnv()


# For more repectitive results
random.seed(1)
np.random.seed(1)
tf.set_random_seed(1)


# Create models folder

if not os.path.isdir('models'):
    os.makedirs('models')

agent = DQNAgent()


