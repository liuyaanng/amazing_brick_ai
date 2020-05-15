#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tensorflow as tf
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Activation, Flatten
from keras.optimizers import Adam
from keras.callbacks import TensorBoard
from collections import deque
import time
import random

from env import *
from cfg import *

LOAD_MODEL = None
# Own Tensorboard class
class ModifiedTensorBoard(TensorBoard):

    # Overriding init to set initial step and writer (we want one log file for all .fit() calls)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.writer = tf.summary.FileWriter(self.log_dir)

    # Overriding this method to stop creating default log writer
    def set_model(self, model):
        pass

    # Overrided, saves logs with our step number
    # (otherwise every .fit() will start writing from 0th step)
    def on_epoch_end(self, epoch, logs=None):
        self.update_stats(**logs)

    # Overrided
    # We train for one batch only, no need to save anything at epoch end
    def on_batch_end(self, batch, logs=None):
        pass

    # Overrided, so won't close writer
    def on_train_end(self, _):
        pass

    # Custom method for saving own metrics
    # Creates writer, writes custom metrics and closes writer
    def update_stats(self, **stats):
        self._write_logs(stats, self.step)


class DQNAgent:

    """Docstring for DQNAgent. """

    def __init__(self):
        """TODO: to be defined. """

        # Main model
        self.model = self.create_model()

        # Target model
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        # An array with last n steps of training
        self.replay_memory = deque(maxlen = REPLAY_MEMORY_SIZE)

        # Custom tensorboard object
        self.tensorboard = ModifiedTensorBoard(log_dir="logs/{}-{}".format(MODEL_NAME, int(time.time())))

        # Used to count when to update target network with main network's weights
        self.target_update_counter = 0


    def create_model(self):
        """TODO: Docstring for create_model.
        :returns: TODO

        """
        if LOAD_MODEL is not None:
            print(f"Loading {LOAD_MODEL}")
            model = load_model(LOAD_MODEL)
            print(f"Model {LOAD_MODEL} loaded")
        else:
            model = Sequential()

            model.add(Conv2D(500, (2, 2), input_shape=OBSERVATION_SPACE_VALUES))
            model.add(Activation('relu'))
            model.add(MaxPooling2D(pool_size = (1, 1)))
            # model.add(Dropout(0.2))
            

            model.add(Conv2D(500, (2, 2)))
            model.add(Activation('relu'))
            model.add(MaxPooling2D(pool_size = (2, 2)))
            # model.add(Dropout(0.2))


            model.add(Flatten())
            model.add(Dense(64))


            model.add(Dense(3, activation = 'linear'))
            model.compile(loss='mse', optimizer=Adam(lr=0.001), metrics=['accuracy'])

        return model

    def update_replay_memory(self, transition):
        """TODO: (current_state, action, reward, new_state, is_game_running)
        :returns: TODO

        """
        self.replay_memory.append(transition)

    def get_qs(self, state):
        """Queries main network for A values given current observatin space.

        :state: TODO
        :returns: TODO

        """
        return self.model.predict(np.array(state).reshape(-1, *state.shape))[0]

    def train(self, terminal_state, step):
        """TODO: Docstring for trian.

        :terminal_state: TODO
        :step: TODO
        :returns: TODO

        """
        if (len(self.replay_memory)) < MIN_REPLAY_MEMORY_SIZE:
            return

        minibatch = random.sample(self.replay_memory, MINIBATCH_SIZE)


        current_states = np.array([transition[0] for transition in minibatch])
        current_qs_list = self.model.predict(current_states)


        new_current_states = np.array([transition[3] for transition in minibatch])
        future_qs_list = self.target_model.predict(new_current_states)



        X = []
        y = []


        # Now we need to enumerate our batchs
        for index, (current_state, action, reward, new_current_state, is_game_running) in enumerate(minibatch):
            if not is_game_running:
                new_q = reward
            else:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + DISCOUNT * max_future_q

            # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            # and append to training data
            X.append(current_state)
            y.append(current_qs)


        # Fit all samples as one bathc, log only on termianl state
        self.model.fit(np.array(X), np.array(y), batch_size = MINIBATCH_SIZE, verbose=0, shuffle=False, callbacks=[self.tensorboard] if not terminal_state else None)
        
        # updating to determine if we want to update target_model yet
        if not terminal_state:
            self.target_update_counter += 1

        if self.target_update_counter >  UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0


