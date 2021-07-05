# from tensorforce import Agent
import tensorforce
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import random
import math

# tensorforce.tensorforce.Environment

class Env(tensorforce.Environment):
    def __init__(self,x,y,z,
                rand_obj = False,
                rand_init_pos=False, 
                obj=None, 
                reward_snow_ball=0.5, 
                dirt_size=1, 
                tree_prob = 0.008, 
                x_p=None,y_p=None,z_p=None,
                hole_prob = 0.0,
                seed = None
                
                
                ):
        super().__init__()


        # terrain generation
        self.x = x
        self.y = y
        self.z = z
        self.dirt_size = dirt_size
        self.tree_prob = tree_prob
        self.hole_prob = hole_prob

        
        # random thingy
        self.rand_obj = rand_obj
        self.rand_init_pos = rand_init_pos
        self.seed = seed

        if seed is not None:
            np.seed(seed)

        if rand_obj :
            self.obj = (np.random.randint(0, x), 4, np.random.randint(0, z))
        else :
            if obj is None:
                raise Exception('obj is not defined')
            self.obj = obj

        if rand_init_pos:
            self.ox_p = np.random.randint(0, x)
            self.oy_p = 4
            self.oz_p = np.random.randint(0, z)
        else : 
            if x_p is None or y_p is None or z_p is None :
                raise Exception('Init position is not defined')
            self.ox_p= x_p
            self.oy_p= y_p
            self.oz_p= z_p

        self.previous_reward = 0
        self.reward_snow_ball = reward_snow_ball 


    def states(self):
        return dict(
            world = dict(
                shape = (self.x,self.y,self.z,),
                type = 'float'
            ),
            agent = dict(
                shape=(3,),
                type = 'float'
            ),
            objective = dict(
                shape= (3,),
                type = 'float'
            )
        )

    def actions(self):
        return dict(type='int', num_values=4) # 0-3

    # Optional: should only be defined if environment has a natural fixed
    # maximum episode length; otherwise specify maximum number of training
    # timesteps via Environment.create(..., max_episode_timesteps=???)
    def max_episode_timesteps(self):
        return super().max_episode_timesteps()

    # Optional additional steps to close environment
    def close(self):
        super().close()

    def reset(self):
        self.init_world()
        state = dict(
            world = self.world, 
            agent=(self.x_p,self.y_p,self.z_p),
            objective = self.obj
        )
        return state

    def execute(self, actions):

        def compute_reward(pos,obj, previous_d):
            ret = math.sqrt(
                (pos[0] - obj[0])**2 +
                (pos[1] - obj[1])**2 +
                (pos[2] - obj[2])**2
            )
            if ret >= previous_d :
                return -10 ,ret
            else :
                return 10,ret

        reward = 0
        if actions == 0:
            if self.x_p +1 < self.x :
                if self.world[self.x_p+1][self.y_p][self.z_p] == 0:
                    self.x_p +=1
                    if self.world[self.x_p][self.y_p-1][self.z_p] == 0:
                        self.y_p -=1
                else :
                    if self.world[self.x_p+1][self.y_p+1][self.z_p] == 0:
                        self.x_p +=1
                        self.y_p +=1
            else :
                reward = -100

        if actions == 1:
            if self.x_p -1 >= 0 :
                if self.world[self.x_p-1][self.y_p][self.z_p] == 0:
                    self.x_p -=1
                    if self.world[self.x_p][self.y_p-1][self.z_p] == 0:
                        self.y_p -=1
                else :
                    if self.world[self.x_p-1][self.y_p+1][self.z_p] == 0:
                        self.x_p -=1
                        self.y_p +=1
            else :
                reward = -100

        if actions == 2:
            if self.z_p +1 < self.z :
                if self.world[self.x_p][self.y_p][self.z_p+1] == 0:
                    self.z_p +=1
                    if self.world[self.x_p][self.y_p-1][self.z_p] == 0:
                        self.y_p -=1
                else :
                    if self.world[self.x_p][self.y_p+1][self.z_p+1] == 0:
                        self.z_p +=1
                        self.y_p +=1
            else :
                reward = -100

        if actions == 3:
            if self.z_p -1 >= 0 :
                if self.world[self.x_p][self.y_p][self.z_p-1] == 0:
                    self.z_p -=1
                    if self.world[self.x_p][self.y_p-1][self.z_p] == 0:
                        self.y_p -=1
                else :
                    if self.world[self.x_p][self.y_p+1][self.z_p-1] == 0:
                        self.z_p -=1
                        self.y_p +=1
            else :
                reward = -100
                    
        
        next_state = dict(
            world = self.world, 
            agent=(self.x_p,self.y_p,self.z_p),
            objective = self.obj
        )
        
        if (self.x_p,self.y_p,self.z_p) == self.obj:
            terminal = True
            reward = 1000
        else :
            terminal = False
            r,ret = compute_reward((self.x_p,self.y_p,self.z_p),self.obj, self.previous_d)
            reward += r
            self.previous_d =ret


        if self.previous_reward < 0 and reward <0:
            reward += self.previous_reward * self.reward_snow_ball
        if self.previous_reward > 0 and reward >0:
            reward += self.previous_reward * self.reward_snow_ball
        self.previous_reward =reward
        return next_state, terminal, reward




    def init_world(self):
        if self.rand_init_pos:
            self.ox_p = np.random.randint(0, self.x)
            self.oy_p = 4
            self.oz_p = np.random.randint(0, self.z)
        else :
            self.x_p= self.ox_p
            self.y_p= self.oy_p
            self.z_p= self.oz_p

        if self.rand_obj :
            self.obj = (np.random.randint(0, self.x), 4, np.random.randint(0, self.z))


        self.previous_d = math.sqrt(
                (self.x_p - self.obj[0])**2 +
                (self.y_p - self.obj[1])**2 +
                (self.z_p - self.obj[2])**2
            )


        self.world = np.zeros((self.x,self.y,self.z))
        # print(self.world.shape)
        # Setting floor (dirt)
        for k in range(self.x):
            for l in range(self.z):
                for m in range(int(self.y/3),int(self.y/3)+self.dirt_size):
                    # print(k,l,m)
                    if np.random.random() > self.hole_prob :
                        self.world[k][m][l] = 1

        # Setting stone 
        for k in range(self.x):
            for l in range(self.z):
                for m in range(int(self.y/3)):
                    if self.world[k][m][l] != 1:
                        self.world[k][m][l] = 2

        # Adding trees
        for k in range(self.x):
            for l in range(self.z):
                    if np.random.random() <= self.tree_prob:
                        for i in range(int(self.y/3)):
                            self.world[k][int(self.y/3)+self.dirt_size+i][l] = 3 


    def outputMap(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        for x in range(self.x):
            for y in range(self.y):
                for z in range(self.z):
                    if self.world[x][y][z] == 1 :
                        ax.scatter(x, z, y, c="green", marker="s") # The output is made on purpose, to fit to minetest world
                    elif self.world[x][y][z] == 2 :
                        ax.scatter(x, z, y, c="grey", marker="s")
                    elif self.world[x][y][z] == 3 :
                        ax.scatter(x, z, y, c="brown", marker="s")

        # if self.player != False:
        ax.scatter(self.x_p, self.z_p, self.y_p, c="blue", marker="s")
        ax.set_xlim(0, self.x); ax.set_ylim(0, self.z); ax.set_zlim(0, self.y)
        plt.show()

             