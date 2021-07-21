from miney import lua
import time
import datetime
import miney
import logging as log
from enum import Enum
from math import isclose
import textwrap
from dataclasses import dataclass
import sys
sys.path.append("/home/nrg/potsdam/embagent/minetest-agent/droidlet/")
from typing import Any, Optional


import agent.Rob.lua_actions as la
from droidlet.interpreter.task import Task

import threading


class Result(Enum):
    RUNNING = 0
    SUCCESS = 1
    FAIL = 2
    TIMEOUT = 3


class Compass(Enum):
    N = 0
    E = 1
    S = 2
    W = 3


def orientation_2_deltas(orientation):
    d_x = 0.0
    d_z = 0.0
    if orientation == Compass.N.value: # away from sun
        d_x = 1.0
    elif orientation == Compass.E.value: # left in direction of the sun
        d_z = -1.0
    elif orientation == Compass.S.value: # towards sun
        d_x = -1.0
    elif orientation == Compass.W.value: # right in direction of the sun
        d_z = 1.0

    return d_x, d_z


class LuaRunRef:
    def __init__(self, npc_id, lua_command, max_time=1.0, lua_check=False, check_pause=0.5):
        self.npc_id = npc_id
        self.lua_command = lua_command
        self.max_time = max_time
        self.lua_check = lua_check
        self.check_pause = check_pause

    def as_task(self, agent):
        return LuaRun(agent, self.npc_id, self.lua_command, self.max_time, self.lua_check, self.check_pause)


class LuaRun(Task):
    def __init__(self, agent, npc_id, lua_command, max_time=1.0, lua_check=False, check_pause=0.5):
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
        print(f"LuaRun.run_checks: commencing result checks at {datetime.datetime.now()}")
        print(textwrap.indent(self.lua_check, prefix=">>> "))
        result = None
        try:
            result = lua_runner.run(self.lua_check)
        except miney.LuaResultTimeout:
            print(f"LuaRun.run_checks: result check timed out after {self.max_time}s at {datetime.datetime.now()}")
            return 3
        print(f"LuaRun.run_checks: check produced: {result}")
        if result != 0:
            return result

    def run_command(self, lua_runner):
        """
        Sends this lua snippet to be executed ingame
        """
        print(textwrap.indent(self.lua_command, prefix=">>> "))
        print(f"atomic_actions.LuaRun.run_command: attempting execution at {datetime.datetime.now()}")
        try:
            lua_runner.run(
                self.lua_command, timeout=self.max_time if self.max_time > 0 else None
            )
        except miney.LuaResultTimeout:
            log.exception(
                f"Execution timed out after {self.max_time}s at {datetime.datetime.now()}"
            )
            return False
        print(f"atomic_actions.LuaRun.run_command: finished execution at {datetime.datetime.now()}")
        return True

    def step(self, agent):
        print("LuaRun.step: Calling LuaRun.step")
        if self.finished:
            return

        if not self.started:
            import uuid
            print("LuaRun.step: Sending command")
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


class SleepRef:
    def __init__(self, how_long):
        self.how_long = how_long

    def as_task(self, agent):
        return Sleep(agent, self.how_long)


class Sleep(Task):
    def __init__(self, agent, how_long):
        self.how_long = how_long
        super().__init__(agent)

    def step(self, agent):
        print("Sleep.step: Calling Sleep.step")
        if self.finished:
            return
        time.sleep(self.how_long)
        self.finished = True


class NodeSetRef:
    def __init__(self, target_pos, node_type):
        self.target_pos = target_pos
        self.node_type = node_type

    def as_task(self, agent):
        return NodeSet(agent, self.target_pos, self.node_type)


class NodeSet(Task):
    def __init__(self, agent, target_pos, node_type):
        self.target_pos = target_pos
        self.node_type = node_type
        super().__init__(agent)

    def step(self, agent):
        print("NodeSet.step: Calling NodeSet.step")
        if self.finished:
            return
        print("NodeSet.step: Calling mt.node.set with args", self.target_pos, self.node_type)
        agent.world.mt.node.set(self.target_pos, self.node_type)
        self.finished = True


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

    def __init__(self, *,  agent, npc_id, steps):
        self.steps = tuple(steps)
        self._step_index = 0
        super().__init__(agent)

    def step(self, agent):
        print("atomic_actions.AtomicAction.step: calling task.step")
        if self.finished:
            return

        if self._step_index == len(self.steps):
            self.finished = True
            return

        agent.memory.add_tick()
        self.add_child_task(self.steps[self._step_index].as_task(agent))
        self._step_index += 1

    @classmethod
    def from_move(cls, agent, move_action, bot_state, world):
        d = 0
        if move_action.direction == "left": # 90° counter-clockwise
            d = -1
        elif move_action.direction == "right": # 90° clockwise
            d = 1
        elif move_action.direction == "backward": # 180° clockwise
            d = 2

        # update the brains orientation and get deltas
        new_orientation = (world.bot_orientation.value + d) % 4
        world.bot_orientation = Compass(new_orientation)
        d_x, d_z = orientation_2_deltas(new_orientation)

        # build the move action
        bot_pos = bot_state.position
        lua_bot_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_pos['x'],
            y=bot_pos['y'],
            z=bot_pos['z'])
        move_check = la.lua_move_check.format(target=lua_bot_pos)

        lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_pos['x'] + d_x * move_action.distance or 1,
            y=bot_pos['y'],
            z=bot_pos['z'] + d_z * move_action.distance or 1)
        move = la.lua_move.format(target=lua_target_pos)
        move_command = LuaRunRef(npc_id=bot_state.bot_id, lua_command=move, max_time=60.0, lua_check=move_check, check_pause=1.0, )

        # build turn action to stay consistent with compass
        # looking one block further in walking direction
        lua_look_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_pos['x'] + d_x * (move_action.distance  or 1) + d_x,
            y=bot_pos['y'],
            z=bot_pos['z'] + d_z * (move_action.distance  or 1) + d_z
        )

        turn = la.lua_turn.format(target=lua_look_pos)
        turn_command = LuaRunRef(npc_id=bot_state.bot_id, lua_command=turn, )

        steps = [turn_command, move_command]
        return cls(agent=agent, npc_id=bot_state.bot_id, steps=steps)

    @classmethod
    def from_turn(cls, agent, turn_action, bot_state, world):
        d = 0
        if turn_action.direction == "left": # 90° counter-clockwise
            d = -1
        elif turn_action.direction == "right": # 90° clockwise
            d = 1
        elif turn_action.direction == "backward": # 180° clockwise
            d = 2

        # update the brains orientation and get deltas
        new_orientation = (world.bot_orientation.value + d) % 4
        world.bot_orientation = Compass(new_orientation)
        d_x, d_z = orientation_2_deltas(new_orientation)

        # update the bots ingame orientation
        bot_pos = bot_state.position
        lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_pos['x'] + d_x,
            y=bot_pos['y'],
            z=bot_pos['z'] + d_z)

        turn = la.lua_turn.format(target=lua_target_pos)
        turn_command = LuaRunRef(npc_id=bot_state.bot_id, lua_command=turn)
        steps = [turn_command]
        return cls(agent=agent, npc_id=bot_state.bot_id, steps=steps)

    @classmethod
    def from_place_block(cls, agent, place_block_action, bot_state, world):
        dx, dz = orientation_2_deltas(world.bot_orientation.value)

        # find the floor block in front of the bot
        bot_pos = bot_state.position
        target_pos = {
            'x' : bot_pos['x'] + dx,
            'y' : bot_pos['y'] - 3.0, # minus bot height
            'z' : bot_pos['z'] + dz
        }
        # find the highest position to place a new block
        check_node = world.mt.node.get(target_pos)
        while check_node['name'] != 'air':
            target_pos['y'] += 1.0
            check_node = world.mt.node.get(target_pos)

        # bascially cheat for now
        #self.bot.mt.node.set(target_pos, 'default:' + str(type))

        steps = [NodeSetRef(target_pos, 'default:' + str(place_block_action.type))]
        return cls(agent=agent, npc_id=bot_state.bot_id, steps=steps)

    @classmethod
    def from_destroy_block(cls, agent, destroy_block_action, bot_state, world):
        dx, dz = orientation_2_deltas(world.bot_orientation.value)

        # find floor block in front of bot
        bot_pos = bot_state.position
        target_pos = {
            'x' : bot_pos['x'] + dx,
            'y' : bot_pos['y'] - 3.0, # minus bot height
            'z' : bot_pos['z'] + dz
        }

        if destroy_block_action.height: # find block at specified height
            target_pos['y'] += destroy_block_action.height
        else: # find the highest block to destroy
            check_node = world.mt.node.get(target_pos)
            while check_node['name'] != 'air':
                target_pos['y'] += 1.0
                check_node = world.mt.node.get(target_pos)
            target_pos['y'] -= 1.0

        # TODO: check if theres air already or
        # if we are digging into ground
        # -> throw an error

        # make it look like rob is mining
        # bascially cheat for now

        steps = [
            LuaRunRef(npc_id=bot_state.bot_id, lua_command=la.lua_toggle_mining.format(npc_id=bot_state.bot_id)),
            SleepRef(.5),
            NodeSetRef(target_pos, "air"),
            LuaRunRef(npc_id=bot_state.bot_id, lua_command=la.lua_toggle_mining.format(npc_id=bot_state.bot_id)),
        ]
        return cls(agent=agent, npc_id=bot_state.bot_id, steps=steps)

    @classmethod
    def come_here(cls, agent, bot_state, world):
        steps = [
            LuaRunRef(
                npc_id=bot_state.bot_id,
                lua_command=la.lua_come_here,
                max_time=60.0,
                lua_check=la.lua_come_here_check,
                check_pause=0.5
            )
        ]
        return cls(agent=agent, npc_id=bot_state.bot_id, steps=steps)