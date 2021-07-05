

class Entity:
    def __init__(self, x, y, z):
        self.x =x
        self.y = y
        self.z = z
        self.yaw = 1

        self.inventory = [0,0,0]
        self.id_inv = 0


    def action(self,id_action, world):
        if id_action == 0:
            self.move_up(world)
        elif id_action == 1:
            self.move_down(world)
        elif id_action == 2:
            self.move_right(world)
        elif id_action == 3:
            self.move_left(world)
        elif id_action == 4:
            self.watch_up(world)
        elif id_action == 5:
            self.watch_mid(world)
        elif id_action == 6:
            self.watch_down(world)
        elif id_action == 7:
            self.rotate_inventory(world)
        elif id_action == 8:
            self.place_up(world)
        elif id_action == 9:
            self.place_down(world)
        elif id_action == 10:
            self.place_right(world)
        elif id_action == 11:
            self.place_left(world)


    def move_up(self,world):
        if self.x+1 < world.x :
            self.x +=1

    def move_down(self,world):
        if self.x-1 >=0:
            self.x -=1

    def move_right(self,world):
        if self.z+1 <= world.z :
            self.z +=1
    
    def move_left(self,world):
        if self.z-1 >= 0 :
            self.y -=1



    def watch_up(self,world):
        self.yaw = 1

    def watch_mid(self,world):
        self.yaw = 0

    def watch_down(self,world):
        self.yaw = -1

    def rotate_inventory(self,world):
        self.id += 1
        if self.id_inv >= len(self.inventory):
            self.id_inv = 0

  

    def place_up(self, world):
        if self.inventory[self.id_inv] > 0:
            if world.world[self.x+1][self.y+self.yaw][self.z] == 0:
                if self.id_inv == 0 :
                    block = 1
                elif self.id_inv == 1:
                    block = 2
                elif self.id_inv == 2:
                    block = 3
                world.world[self.x+1][self.y+self.yaw][self.z] = block

    def place_down(self, world):
        if self.inventory[self.id_inv] > 0:
            if world.world[self.x-1][self.y+self.yaw][self.z] == 0:
                if self.id_inv == 0 :
                    block = 1
                elif self.id_inv == 1:
                    block = 2
                elif self.id_inv == 2:
                    block = 3
                world.world[self.x-1][self.y+self.yaw][self.z] = block

    
    def place_right(self, world):
        if self.inventory[self.id_inv] > 0:
            if world.world[self.x][self.y+self.yaw][self.z+1] == 0:
                if self.id_inv == 0 :
                    block = 1
                elif self.id_inv == 1:
                    block = 2
                elif self.id_inv == 2:
                    block = 3
                world.world[self.x][self.y+self.yaw][self.z+1] = block


    def place_left(self, world):
        if self.inventory[self.id_inv] > 0:
            if world.world[self.x][self.y+self.yaw][self.z-1] == 0:
                if self.id_inv == 0 :
                    block = 1
                elif self.id_inv == 1:
                    block = 2
                elif self.id_inv == 2:
                    block = 3
                world.world[self.x][self.y+self.yaw][self.z-1] = block


    