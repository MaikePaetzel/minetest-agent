import logging as log
from enum import Enum
import lua_actions as la

class Brain:
    """
    Description :
    ----------
    This class runs scripted behaviours on the bot object.
    """

    class Compass(Enum):
        N = 0
        E = 1
        S = 2
        W = 3

    def __init__(self, controller):
        self.bot = controller
        # initialize orientation to north
        self.orientation = self.Compass.N
        self.run_lua(la.lua_init_compass.format(npc_id=self.bot.id))
        self.run_lua(la.lua_lock_daytime)

    def process(self, request):
        """
        Behaviours are executed from stack meaning
        the last ones that are added will be 
        will be executed first.
        """
        try:
            print("Attempting to execute command:")
            exec("self." + str(request))
            return True
        except Exception as e:
            print("self." + str(request))
            print("could not be executed as python call. Check for missing or wrong parameters)")
            log.exception(e)
            return False

    #################################################
    # Helper Functions
    #################################################

    def run_lua(self, code):
        return self.bot.lua_runner.run(code)

    def get_bot_yaw(self):
        return self.run_lua(la.lua_get_yaw.format(npc_id=self.bot.id))

    def get_bot_position(self):
        return self.run_lua(la.lua_get_position.format(npc_id=self.bot.id))

    def orientation_2_deltas(self, orientation):
        d_x = 0.0
        d_z = 0.0
        if orientation == self.Compass.N.value: # away from sun
            d_x = 1.0
        elif orientation == self.Compass.E.value: # left in direction of the sun
            d_z = -1.0
        elif orientation == self.Compass.S.value: # towards sun
            d_x = -1.0
        elif orientation == self.Compass.W.value: # right in direction of the sun
            d_z = 1.0
        
        return d_x, d_z
