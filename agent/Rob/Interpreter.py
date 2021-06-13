from Rob import Action
import threading
import time

class DummyInterpreter :
    """
        Description :
        ----------
        This provisionary class builds scripted behaviours out of atomic actions.
        It is merely a test instance.

        Attributes :
        ----------
        stack : list 
            stack of actions
        active : Action
            current action
        pause : float
            thread waiting time

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
            This function will take care of the 

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
