import time
class Action:
    """
    This class represents atomic actions that a bot is able to execute.
    """
    def __init__(self, code, cancel, goal):
        self.code = code
        self.goal = goal
        self.cancel = cancel

        self.on_cancel = None
        self.on_goal = None

        self.next = None

        self.now = round(time.time() * 1000)


    def set_next(self, action):
        self.next = action

    def get_next(self):
        return self.next

    def set_on_cancel(self, f):
        self.on_cancel = f

    def set_on_goal(self, f):
        self.on_goal = f