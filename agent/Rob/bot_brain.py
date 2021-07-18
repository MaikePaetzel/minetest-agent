import logging as log
import miney
<<<<<<< HEAD
import agent.Rob.atomic_actions as aa
import agent.Rob.lua_actions as la
import agent.Rob.bot_controller as bc
=======
import atomic_actions as aa
import lua_actions as la
import bot_controller as bc
from math import isclose
>>>>>>> d03024e52777fcd58b6467d38e69fddb05e204bc

class DemoBrain:
    """
    Description :
    ----------
    This class runs scripted behaviours on the bot object.
    """

    def __init__(self, controller=bc.BotController()):
        self.bot = controller

    def process(self, request):
        """
        Behaviours are executed from stack meaning
        the last ones that are added will be 
        will be executed first.
        """
        self.bot.mt.time_of_day = 0.7
        try:
            print("Attempting to execute command:")
            exec("self." + str(request))
            return True
        except Exception as e:
            print("self." + str(request))
            print("could not be executed as python call. Check for missing or wrong parameters)")
            log.exception(e)
            return False

    def run_lua(self, code):
        return self.bot.lua_runner.run(code)

    #################################################
    #define more complex behaviours

    def Move(self, direction, distance):
        distance = float(distance)
        delta_x = 0.0
        delta_z = 0.0
        if direction == "forward": # towards sun
            delta_x = distance
        elif direction == "backward": # away from sun
            delta_x = -distance
        elif direction == "right": # right in direction of the sun
            delta_z = distance
        elif direction == "left": # left in direction of the sun
            delta_z = -distance

        bot_pos = self.run_lua(la.lua_get_position.format(npc_id=self.bot.id))
        lua_bot_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_pos['x'],
            y=bot_pos['y'],
            z=bot_pos['z'])
        move_check = la.lua_move_check.format(target=lua_bot_pos)

        lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_pos['x'] + delta_x,
            y=bot_pos['y'],
            z=bot_pos['z'] + delta_z)
        move = la.lua_move.format(target=lua_target_pos)

        move_action = aa.AtomicAction(
            self.bot.lua_runner,
            self.bot.id,
            move,
            60.0,
            move_check,
            1.0)

        self.bot.add_action(move_action)
        self.bot.start_execution()

    #################################################
    def Turn(self, direction):
        delta_x = 0.0
        delta_z = 0.0
        if direction == "forward": # towards sun
            delta_x = 1.0
        elif direction == "backward": # away from sun
            delta_x = -1.0
        elif direction == "right": # right in direction of the sun
            delta_z = 1.0
        elif direction == "left": # left in direction of the sun
            delta_z = -1.0
        
        bot_pos = self.run_lua(la.lua_get_position.format(npc_id=self.bot.id))
        lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_pos['x'] + delta_x,
            y=bot_pos['y'],
            z=bot_pos['z'] + delta_z)
        
        turn = la.lua_turn.format(target=lua_target_pos)
        turn_action = aa.AtomicAction(self.bot.lua_runner, self.bot.id, turn)

        self.bot.add_action(turn_action)
        self.bot.start_execution()

    #################################################
    def ComeHere(self):
        come = aa.AtomicAction(
            self.bot.lua_runner,
            self.bot.id,
            la.lua_come_here,
            60.0,
            la.lua_come_here_check,
            0.5)

        self.bot.add_action(come)
        self.bot.start_execution()

    #################################################
    def PlaceBlock(self, type):
        bot_yaw = self.run_lua(la.lua_get_yaw.format(npc_id=self.bot.id))

        delta_x = 0.0
        delta_z = 0.0
        
        TOL = 1.57 # a bit less than pi/2
        if isclose(bot_yaw, 0.0, rel_tol= TOL): # towards sun
            delta_x = 1.0
        elif isclose(bot_yaw, 3.1415, rel_tol= TOL): # away from sun
            delta_x = -1.0
        elif isclose(bot_yaw, 4.7123, rel_tol= TOL): # right in direction of the sun
            delta_z = 1.0
        elif isclose(bot_yaw, 1.5707, rel_tol= TOL): # left in direction of the sun
            delta_z = -1.0

        # find the floor block in front of the bot
        bot_pos = self.run_lua(la.lua_get_position.format(npc_id=self.bot.id))
        lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_pos['x'] + delta_x,
            y=bot_pos['y'],
            z=bot_pos['z'] + delta_z)
        
        # find the highest position to place a new block
        height = bot_pos['y']-1.0
        while self.run_lua(la.lua_get_node.format(pos=lua_target_pos)):
            height += 1.0
            lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
                x=bot_pos['x'] + delta_x,
                y=height,
                z=bot_pos['z'] + delta_z)

        place = la.lua_place_block.format(target=lua_target_pos, block=str(type))
        place_action = aa.AtomicAction(self.bot.lua_runner, self.bot.id, place)

        self.bot.add_action(place_action)
        self.bot.start_execution()

    #################################################
    def DestroyBlock(self, height):
        pass
