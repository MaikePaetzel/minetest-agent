import time
import datetime
import miney
import logging as log
from enum import Enum
from math import isclose

import sys
sys.path.append("/home/nrg/potsdam/embagent/minetest-agent/droidlet/")


import agent.Rob.lua_actions as la
from droidlet.interpreter.task import Task

import threading


class Result(Enum):
    RUNNING = 0
    SUCCESS = 1
    FAIL = 2
    TIMEOUT = 3


class AtomicAction(Task):
    """
    This class holds lua code of atomic actions that a bot is able to execute.
    It can be run by calling class objects like a function.

    lua_runner   -  sends lua code off to be executed ingame
    npc_id       -  npc that is supposed to execute the command
    lua_command  -  behaviour to be executed
    max_time     -  max time for lua_command to finish ingame
                    must be > 0.0
    lua_check    -  lua code to check whether game state eventually changed as expected
                    if this is None the execution will return after max_time
    check_pause  -  pause between result checks
    """

    def __init__(self, *,  agent, npc_id, lua_command, max_time=1.0, lua_check=False, check_pause=0.5):
        self.started = False
        LUA_BASE = (
            f"local npc = npcf:get_luaentity(\"{npc_id}\")"
            "\n"
            "local move_obj = npcf.movement.getControl(npc)"
        )
        assert lua_command
        self.lua_command = LUA_BASE + lua_command

        if lua_check:
            self.lua_check = LUA_BASE + lua_check
            assert check_pause > 0.0
            self.check_pause = check_pause
        else:
            self.lua_check = None

        if max_time:
            assert max_time >= 0.0
            self.max_time = max_time

        super().__init__(agent)

    def run_checks(self, lua_runner):
        """
        Sends this lua snippet to be executed ingame
        """
        print(self.lua_check)
        print(f"Commencing result checks at {datetime.datetime.now()}")
        result = None
        try:
            result = lua_runner.run(self.lua_check)
        except miney.LuaResultTimeout:
            log.exception(
                f"Result check timed out after {self.max_time}s at {datetime.datetime.now()}"
            )
            return 3
        print(f"Check produced: {result}")
        if result != 0:
            return result

    def run_command(self, lua_runner):
        """
        Sends this lua snippet to be executed ingame
        """
        print(self.lua_command)
        print(f"Attempting execution at {datetime.datetime.now()}")
        try:
            lua_runner.run(
                self.lua_command, timeout=self.max_time if self.max_time > 0 else None
            )
        except miney.LuaResultTimeout:
            log.exception(
                f"Execution timed out after {self.max_time}s at {datetime.datetime.now()}"
            )
            return False
        print(f"Finished execution at {datetime.datetime.now()}")
        return True

    def step(self, agent):
        print("Calling task.step")
        if self.finished:
            return

        if not self.started:
            import uuid
            print("Sending command")
            print(self.lua_command)
            self.run_command(agent.world.lua_runner)
            #agent.world.lua_runner.mt.send({"lua": self.lua_command, "id": str(uuid.uuid4())})
            #agent.world.lua_runner.mt.receive()
            self.started = True
            return

        if self.started and self.lua_check is not None:
            if self.run_checks(agent.world.lua_runner):
                self.finished = True
        else:
            self.finished = True

    @classmethod
    def from_move(cls, agent, move_action, bot_state, world):
        distance = move_action.distance
        delta_x = 0.0
        delta_z = 0.0
        if move_action.direction == "forward":  # towards sun
            delta_x = distance
        elif move_action.direction == "backward":  # away from sun
            delta_x = -distance
        elif move_action.direction == "right":  # right in direction of the sun
            delta_z = distance
        elif move_action.direction == "left":  # left in direction of the sun
            delta_z = -distance

        # bot_pos = self.run_lua(la.lua_get_position.format(npc_id=self.bot.id))
        lua_bot_pos = "{{x={x}, y={y}, z={z}}}".format(**bot_state.position)
        move_check = la.lua_move_check.format(target=lua_bot_pos)

        lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_state.position["x"] + delta_x,
            y=bot_state.position["y"],
            z=bot_state.position["z"] + delta_z,
        )
        move = la.lua_move.format(target=lua_target_pos)

        return cls(agent=agent, npc_id=bot_state.bot_id, lua_command=move, max_time=60.0, lua_check=move_check, check_pause=1.0, )

    @classmethod
    def from_turn(cls, agent, turn_action, bot_state, world):
        delta_x = 0.0
        delta_z = 0.0
        if turn_action.direction == "forward":  # towards sun
            delta_x = 1.0
        elif turn_action.direction == "backward":  # away from sun
            delta_x = -1.0
        elif turn_action.direction == "right":  # right in direction of the sun
            delta_z = 1.0
        elif turn_action.direction == "left":  # left in direction of the sun
            delta_z = -1.0

        # bot_pos = self.run_lua(la.lua_get_position.format(npc_id=self.bot.id))
        lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_state.position["x"] + delta_x,
            y=bot_state.position["y"],
            z=bot_state.position["z"] + delta_z,
        )

        turn = la.lua_turn.format(target=lua_target_pos)
        return cls(agent=agent, npc_id=bot_state.bot_id, lua_command=turn, )

    @classmethod
    def from_place_block(cls, agent, place_block_action, bot_state, world):

        delta_x = 0.0
        delta_z = 0.0

        TOL = 1.57 # a bit less than pi/2
        if isclose(bot_state.orientation_to_sun, 0.0, rel_tol=TOL): # towards sun
            delta_x = 1.0
        elif isclose(bot_state.orientation_to_sun, 3.1415, rel_tol=TOL): # away from sun
            delta_x = -1.0
        elif isclose(bot_state.orientation_to_sun, 4.7123, rel_tol=TOL): # right in direction of the sun
            delta_z = 1.0
        elif isclose(bot_state.orientation_to_sun, 1.5707, rel_tol=TOL): # left in direction of the sun
            delta_z = -1.0

        target_x = bot_state.position['x'] + delta_x
        target_y = bot_state.position['y']
        target_z = bot_state.position['z'] + delta_z

        # find the floor block in front of the bot
        lua_target_pos = f"{{x={target_x}, y={target_y}, z={target_z}}}"

        # find the highest position to place a new block

        # TODO use the grids from perception

        height = target_y-1.0
        while agent.world.run_lua(la.lua_get_node.format(pos=lua_target_pos)):
            height += 1.0
            lua_target_pos = f"{{x={target_x}, y={height}, z={target_z}}}"

        place = la.lua_place_block.format(target=lua_target_pos, block=place_block_action.type)
        return cls(agent=agent, npc_id=bot_state.bot_id, lua_command=place, )

    @classmethod
    def come_here(cls, agent, bot_state, world):
        return cls(
            agent=agent,
            npc_id=bot_state.bot_id,
            lua_command=la.lua_come_here,
            max_time=60.0,
            lua_check=la.lua_come_here_check,
            check_pause=0.5
        )