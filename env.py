#!/usr/bin/env python
# -*- coding: utf-8 -*-
import arcade
import time
import random
from queue import Queue
import numpy as np
import os
from cfg import *
def collide(box1, box2):
    """TODO: Docstring for collide.

    :box1: TODO
    :box2: TODO
    :returns: TODO

    """
    x01, y01, x02, y02 = box1
    x11, y11, x12, y12 = box2

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

        :loc_x: Tunnel space / 2
        :loc_y: Tunnel space / 2

        """

        self.x = loc_x
        self.y = loc_y
        self.passed = False
        self.touched = False

class Block():

    """Docstring for Block. """

    def __init__(self, loc_x, loc_y, size = BLOCK_SIZE):
        """TODO: to be defined.

        :loc_x: the center of a circle
        :loc_y: the center of a circle
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

        :starting_x: The center of player circle
        :starting_y: The center of player circle
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
        
        self.useless_action_num = 0

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
        next_block1_y = 0
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
            bottom_tunnel_y = bottom_tunnel
        else:
            bottom_y = 0


        # block position

        for block in blocks.queue:
            if block.y > bottom_y and block.y < next_tunnel_y:
                if next_block1 is None:
                    next_block1 = block
                    next_block1_x = next_block1.x
                    next_block1_y = next_block1.y
                else:
                    next_block2 = block
                    next_block2_x = next_block2.x
                    next_block2_y = next_block2.y

        state = np.array([
            # the distance between 
            # player left and next tunnel left
            self.x - self.size / 2 - next_tunnel_x + TUNNEL_OPENNESS / 2,
            # player right and next tunnel right
            next_tunnel_x + TUNNEL_OPENNESS / 2 - self.x - self.size / 2,
            # player top and next tunnel bottom
            next_tunnel_y - self.y - BAR_HEIGHT / 2 - self.size / 2,
            # player botton and last tunnel top
            self.y - self.size / 2 - bottom_y - BAR_HEIGHT / 2,
            
            next_block2_y - self.y - BLOCK_SIZE / 2 - self.size / 2,
            next_block1_y - self.y - BLOCK_SIZE / 2 - self.size / 2,
            self.y - next_block2_y - BLOCK_SIZE / 2 - self.size / 2,
            self.y - next_block1_y - BLOCK_SIZE / 2 - self.size / 2,

            next_block2_x - self.x - BLOCK_SIZE / 2 - self.size / 2,
            next_block1_x - self.x - BLOCK_SIZE / 2 - self.size / 2,
            self.x - next_block2_x - BLOCK_SIZE / 2 - self.size / 2,
            self.x - next_block1_x - BLOCK_SIZE / 2 - self.size / 2,
            # x distance of block1 and player
            next_block1_x - self.x,
            # y distance of block1 and player
            next_block1_y - self.y,
            # x distance of block2 and player
            next_block2_x - self.x,
            # y distance of block2 and player
            next_block2_y - self.y,
            self.vx, self.vy])
        state = state.reshape(3,3,2)

        return state

    def update(self):
        """TODO: Docstring for update.
        :returns: TODO

        """
        global score
        next_tunnel = None
        next_block = None
        delta_reward = 0  # 0.1

        state = self.get_state()
        #print(state.shape)
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
                if collide((block.x + block.size / 2, block.y - block.size / 2, block.x + block.size / 2, block.y + block.size / 2),(self.x - self.size / 2, self.y - self.size / 2, self.x + self.size / 2, self.y + self.size / 2)):
                    block.touched = True
                    self.gg = True

                    if not block.passed and next_block is None:
                        next_block = block

            if next_block != None:
                if self.y - self.size > next_block.y and not next_block.passed:
                    next_block.passed = True

                    delta_reward += 0
                    # score += 1
            # print("length of tunnels:",len(tunnels.queue))
            
            # if len(tunnels.queue):
                # print("tunnels queue:", tunnels.queue[0])
            for tunnel in tunnels.queue:
                tunnel_full = (0, tunnel.y - BAR_HEIGHT / 2, SCREEN_WIDTH, tunnel.y + BAR_HEIGHT / 2)
                tunnel_space = (tunnel.x - TUNNEL_OPENNESS / 2 + self.size / 2, tunnel.y - BAR_HEIGHT / 2,
                                tunnel.x + TUNNEL_OPENNESS / 2 - self.size / 2, tunnel.y + BAR_HEIGHT / 2)

                player = (self.x - self.size / 2, self.y - self.size / 2, self.x + self.size / 2, self.y + self.size / 2)
                if collide(tunnel_full, player):
                    if not collide(tunnel_space, player):
                        self.vx = self.vy = 0
                        tunnel.touched = True
                        self.gg = True
                # print(tunnel.passed)
                # print(next_tunnel)
                if tunnel.passed == False and next_tunnel is None:
                    next_tunnel = tunnel

            if next_tunnel != None:
                # print(self.y)
                # print(next_tunnel)
                if self.y - self.size > next_tunnel.y and not next_tunnel.passed:
                    next_tunnel.passed = True
                    score += 1
                    delta_reward += 1
                    self.useless_action_num = 0
        # print(self.useless_action_num)
        if self.useless_action_num > NO_OP_MAX:
            self.gg = True
        self.x += self.vx
        self.y += self.vy

        if self.y > self.highest_y:
            self.highest_y = self.y

        if self.started:
            self.vy = -GRAVITY

        return state, delta_reward, bool(1-self.gg)

    def action(self, choice):
        """TODO: Docstring for action.

        :choice: TODO
        :returns: TODO

        """
        AI_MODE = False
        if AI_MODE:
            self.ai_action = choice
        if choice == 0:
            self.started = True
            self.vx = -BOOST_H
            self.vy = BOOST_V
        if choice == 2:
            self.started = True
            self.vx = BOOST_H
            self.vy = BOOST_V

        self.useless_action_num += 1



class AmazingBrickEnv():

    """Docstring for AmazingBrickEnv. """
    
    ACTION_SPACE_SIZE = 3

    def reset(self):
        """TODO: Docstring for reset.
        :returns: TODO

        """
        global score
        
        global tunnels
        global blocks
        self.game_height = 0
        score = 0
        
        self.frames = 0
        self.player = Player(SCREEN_WIDTH / 2, 20)
        self.next_tunnel_y = TUNNEL_SPACE
        self.is_game_running = True
        AI_MODE = False
        tunnels = Queue()
        blocks = Queue()
        

        return self.player.get_state()


    def __init__(self):
        """TODO: to be defined. """
        self.reset()
        self.e = 0 # the currnet episode

        
    def step(self, action):
        """TODO: Docstring for step.

        :action: TODO
        :returns: TODO

        """
        global tunnels
        global blocks
        # action = random.randint(0,2)
        # action = 1
        self.player.action(action)
        self.observation, reward , is_game_running= self.player.update()
        # print(self.observation, reward)
        #print("score:", score)
        
        # if player out of the view, game over
        if self.player.y < self.game_height:
            self.player.gg = True
        changed = False
        print("position is (%s, %s)" %(self.player.x, self.player.y))
    
        if self.player.y - SCREEN_HIGHT / 2 > self.game_height:
            self.game_height = self.player.y - SCREEN_HIGHT / 2
            changed = True
            # print("game_height: ", self.game_height)
        if changed:
            self.game_height = int(self.game_height)
            arcade.set_viewport(0, SCREEN_WIDTH, self.game_height, SCREEN_HIGHT + self.game_height)



        new_tunnel_needed = True
        if len(tunnels.queue) > 0:
            if tunnels.queue[-1].y  + TUNNEL_SPACE > SCREEN_HIGHT + self.game_height:
                new_tunnel_needed = False
            if tunnels.queue[0].y + 100 < self.game_height:
                tunnels.get()
        if len(blocks.queue) > 0:
            if blocks.queue[0].y + 100 < self.game_height:
                blocks.get()


        while new_tunnel_needed:
            new_tunnel = Tunnel(SCREEN_WIDTH / 2 + random.randint(-100, 100), self.next_tunnel_y)
            new_block_1 = Block(SCREEN_WIDTH / 2 + random.randint(-random.randint(0, 150), random.randint(0,150)), self.next_tunnel_y + TUNNEL_SPACE / 3)
            new_block_2 = Block(SCREEN_WIDTH / 2 + random.randint(-random.randint(0, 150), random.randint(0,150)), self.next_tunnel_y + 2 * TUNNEL_SPACE / 3)
            tunnels.put(new_tunnel)
            blocks.put(new_block_1)
            blocks.put(new_block_2)

            self.next_tunnel_y += TUNNEL_SPACE

            if self.next_tunnel_y > self.game_height + SCREEN_HIGHT:
                new_tunnel_needed = False


        if self.player.gg:
            #tunnels.queue.clear()
            #blocks.queue.clear()
            # print("bugs", len(tunnels.queue),len(blocks.queue))
            # time.sleep(0.3)
            print("game terimnaled")
            self.reset()
            arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HIGHT)
        
        
        #print("start render")
 
        # if SHOW_PREVIEW:
        self.render()
        #image = arcade.get_image(0, 0, width = int(SCREEN_WIDTH), height = int(SCREEN_HIGHT) )
        # image.save('test.png')
        return self.observation, reward, is_game_running, score
    def render(self):
        arcade.start_render()
        # arcade.draw_circle_filled(300,200,26,arcade.color.GREEN)
        print("into render")
        player_x = self.player.x + self.player.size / 2
        player_y = self.player.y + self.player.size / 2
        print(player_x, player_y)
        arcade.draw_circle_filled(np.random.randint(0, 800), player_y, self.player.size / 2, arcade.color.BLACK) 
        #print(self.player.x + self.player.size / 2, self.player.y + self.player.size / 2)
 #       arcade.draw_circle_filled(self.player.x + self.player.size / 2, self.player.y + self.player.size / 2, self.player.size / 2, arcade.color.BLACK)
 #      arcade.draw_circle_filled(100, self.player.y + self.player.size / 2, self.player.size / 2, arcade.color.BLACK)

        # if blocks.queue:
            # for block in blocks.queue:
                # #print(block.x, block.y)
                # arcade.draw_circle_filled(block.x, block.y, block.size / 2, arcade.color.RED)
        # if tunnels.queue:
            # for tunnel in tunnels.queue:
                # # print(tunnel.y + BAR_HEIGHT / 2, tunnel.y - BAR_HEIGHT / 2)
                # arcade.draw_lrtb_rectangle_filled(0, tunnel.x - TUNNEL_OPENNESS / 2, tunnel.y + BAR_HEIGHT / 2, tunnel.y - BAR_HEIGHT / 2, arcade.color.GREEN)
                # arcade.draw_lrtb_rectangle_filled(tunnel.x + TUNNEL_OPENNESS / 2, SCREEN_WIDTH, tunnel.y + BAR_HEIGHT / 2, tunnel.y - BAR_HEIGHT / 2, arcade.color.GREEN)

# def main():
    # ENV = AmazingBrickEnv()

    # arcade.open_window(SCREEN_WIDTH, SCREEN_HIGHT, 'AmazingBrick')
    # arcade.set_background_color(arcade.color.WHITE)

    # arcade.schedule(ENV.step, 1/ 60)

    # arcade.run()

    # arcade.close_window()


# if __name__ == "__main__":
    # main()

