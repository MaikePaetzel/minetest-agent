
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import random
from Entity import Entity



class Sandbox:

    def __init__(self, x,y,z, dirt_size=1, tree_prob = 0.008):
        # Perlin method ? 
        self.x = x
        self.y = y
        self.z = z
        self.dirt_size = dirt_size
        self.tree_prob = tree_prob
        self.init_world()
        self.player = False

    def add_player(self,x,y,z):
        self.player = Entity(int(x), int(y), int(z))

    def init_world(self):
        self.world = np.zeros((self.x,self.y,self.z))
        

        print(self.world.shape)
        # Setting floor (dirt)
        for k in range(self.x):
            for l in range(self.z):
                for m in range(int(self.y/3),int(self.y/3)+self.dirt_size):
                    # print(k,l,m)
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
                    if random.random() <= self.tree_prob:
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

        if self.player != False:
            ax.scatter(self.player.x, self.player.z, self.player.y, c="blue", marker="s")

                        
                    

       
        

        plt.show()
