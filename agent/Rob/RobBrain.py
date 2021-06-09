from Rob import Action
import threading
import time

class RobBrain :
    """
        Desciption :
        ----------
        Dummy brain of the NPC, will just execute the action that we gave to the stack
        Manage action to provide sequence task management.

        Attributes :
        ----------
        stack : list 
            Stack of Action
        active : Action
            Current Action
        pause : float
            Thread waiting time

        WARNING
        ----------
        Thread unsing, might be dangerous (infinite loop etc) + performance issues

    """

    def __init__(self):
        self.stack = []
        self.active = None
        # Thread refresh rate
        self.pause = 2
        # Starting threaded loop
        self.stop = False
        threading.Thread(target=self.loop).start()

        

    def loop(self):
        """
            This function will create an infinite loop (have to be used threaded, at least imagined this way)
            that will execute part "code" of an "Action"

        """
        print('Starting infinite loop -> Ctrl-C to Cancel...\n')
        while True:
            
            if self.active == None:
                if len(self.stack) != 0:
                    self.active = self.stack.pop(0)
                    self.active.code(self.active)
            else :
                if self.active.goal(self.active):
                    if self.active.on_goal != None:
                       self.active.on_goal(self.active)
                
                    if self.active.next != None :
                        self.active =self.active.next
                    else :
                        self.active = None 

                elif self.active.cancel(self.active) :
                    if self.active.on_cancel != None :
                        self.active.on_cancel(self.active)

                
                    
            time.sleep(self.pause)

    def addAction(self, action):
        self.stack.append(action)

    def clear(self):
        self.stack.clear()

    def skip(self):
        self.active = None
        # if we consider "skip" action that skip an entiere block
        # self.active = self.active.next
