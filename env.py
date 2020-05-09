#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
from queue import Queue
import numpy as np
import os

SCREEN_WIDTH = 600
HIGHEST_Y_CHECK_EVERY = 400
HIGHEST_MIN_IMPROVEMENT = 100
BAR_HEIGHT = 30
TUNNEL_OPENNESS = 130
BLOCK_SIZE = 30
PLAYER_SIZE = 26


def collide(box1, box2):
    """TODO: Docstring for collide.

    :box1: TODO
    :box2: TODO
    :returns: TODO

    """
    x01, y01, x02, y02 = box1
    x11, y11, x12, y12 = b0x2

    lx = abs((x01 + x02) / 2 - (x11 + x12) / 2)
    ly = abs((y01 + y02) / 2 - (y11 + y12) / 2)
    sax = abs(x01 - x02)
    say = abs(y01 - y02)
    sbx = abs(x11 - x12)
    sby = abs(y11 - y12)

    if lx <= (sax + sbx) / 2 and ly <= (say + sby) / 2:
        return True
    else:
        return False



class Tunnel():

    """Tunnel"""

    def __init__(self, loc_x, loc_y):
        """TODO: to be defined.

        :loc_x: TODO
        :loc_y: TODO

        """

        self.x = loc_x
        self.y = loc_y
        self.passed = False
        self.touched = False

class Block():

    """Docstring for Block. """

    def __init__(self, loc_x, loc_y, size = BLOCK_SIZE):
        """TODO: to be defined.

        :loc_x: TODO
        :loc_y: TODO
        :size: TODO

        """

        self.x = loc_x
        self.y = loc_y
        self.size = size
        self.touched = False
        self.passed = False

class Player():

    """Docstring for Player. """

    def __init__(self, starting_x, starting_y, size = PLAYER_SIZE):
        """TODO: to be defined.

        :starting_x: TODO
        :starting_y: TODO
        :size: TODO

        """
        
        self.gg = False
        self.started = False
        self.x = starting_x
        self.y = starting_y
        self.size = size
        self.vx = 0 #horizontal velocity
        self.vy = 0 #vertical velocity
        self.highest_y = 0
        self.highest_y_last_check = 0
        self.highest_y_check_count = 0

        # if AI_MODE:
            # self.ai_action = 0

    def get_state(self):
        """TODO: Docstring for get_state.
        :returns: TODO

        """
        next_tunnel = None
        next_tunnel_y = 9999
        next_block1 = None
        next_block1_x = 0
        next_block2_y = 0
        next_block2 = None
        next_block2_x = 0
        next_block2_y = 0
        bottom_tunnel = None
        bottom_y = 0

        # tunnel position
        for tunnel in tunnels.queue:
            if tunnel.y > self.y and tunnel.y < next_tunnel_y:
                next_tunnel = tunnel
                next_tunnel_y = tunnel.y

            elif tunnel.y < self.y and tunnel.y > bottom_y:
                bottom_tunnel = tunnel
                bottom_y = tunnel.y

        if next_tunnel != None:
            next_tunnel_x = next_tunnel.x
            next_tunnel_y = next_tunnel.y
        else:
            next_tunnel_x = next_tunnel_y = 0


        if bottom_tunnel != None:
            bottom_tunnel_y = bottom_tunnely
        else:
            bottom_y = 0


        # block position

        for block in block.queue:
            if block_y > bottom_y and block.y < next_tunnel_y:
                if next_block1 is None:
                    next_block1 = block
                    next_block1_x = next_block1.x
                    next_block1_y = next_block.y
                else:
                    next_block2 = block
                    next_block2_x = next_block2.x
                    next_block2_y = next_block.y

        state = np.array([
            self.x - self.size / 2 - next_tunnel_x + TUNNEL_OPENNESS / 2,
            next_tunnel_x + TUNNEL_OPENNESS / 2 - self.x - self.size / 2,
            next_tunnel_y - self.y - BAR_HEIGHT / 2 - self.size / 2,

            next_block1_x - self.x,
            next_block1_y - self.y,
            next_block2_x - self.x,
            next_block2_y - self.y,
            self.y- self.size / 2 - bottom_y - BAR_HEIGHT / 2,
            self.vx, self.vy])

        return state

    def update(self):
        """TODO: Docstring for update.
        :returns: TODO

        """
        global score
        next_tunnel = None
        next_block = None
        delta_reward = 0  # 0.1

        state = get_state()

        self.highest_y_check_count += 1
        if self.highest_y_check_count > HIGHEST_Y_CHECK_EVERY:
            if self.highest_y - self.highest_y_last_check < HIGHEST_MIN_IMPROVEMENT:
                self.gg = True
            self.highest_y_last_check = self.highest_y
            self.highest_y_check_count = 0

        if not self.gg:
            # make sure palyer cant out of the screen
            if self.x < self.size / 2:
                self.x = self.size / 2
            elif self.x > SCREEN_WIDTH - self.size / 2:
                self.x = SCREEN_WIDTH - self.size / 2

            for block in blocks.queue:
                if collide((block.x, block.y, block.x + block.size),(self.x, self.y, self.x + self.size, self.y + self.size)):
                    block.touched = True
                    self.gg = True

                    if not block.passed and next_block is None:
                        next_block = block

            if next_block != None:

                if self.y - self.size > next_block.y and not next_block.passed:
                    next_block.passed = True

                    delta_reward += 0
                    # score += 1

            for tunnel in tunnels.queue:
                tunnel_full = (0, tunnel.y - BAR_HEIGHT / 2, SCREEN_WIDTH, tunnel.y + BAR_HEIGHT / 2)
                tunnel_space = (tunnel.x - TUNNEL_OPENNESS / 2 + self.size, tunnel.y - BAR_HEIGHT / 2,
                                tunnel.x + TUNNEL_OPENNESS / 2 - self.size, tunnel.y + BAR_HEIGHT / 2)

                player = (self.x - self.size / 2, self.y - self.size / 2, self.x + self.size / 2, self.y + self.size / 2)
                if collide(tunnel_full, player):
                    if not collide(tunnel_space, player):
                        self.vx = self.vy = 0
                        tunnel.touched = True
                        self.gg = True

                if tunnel.passed == False and next_tunnel is None:
                    next_tunnel = tunnel

            if len(tunnel.queue) > 0:
                if self.y - self.size > next_tunnel.y and not next_tunnel.passed:
                    next_tunnel.passed = True
                    score += 1
                    delta_reward += 1
        

        self.x += self.vx
        self.y += self.vy

        if self.y > self.highest.y:
            self.highest_y = self.y

        if self.started:
            self.vy = -GRAVITY

        return state, delta_reward









        
        
        


