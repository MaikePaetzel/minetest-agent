from dataclasses import dataclass
from traceback import TracebackException
from typing import Any, Dict
import textwrap

import queue
import sys
sys.path.append("/home/nrg/potsdam/embagent/minetest-agent/droidlet/")

import logging

from agents.core import BaseAgent
from droidlet.memory.sql_memory import AgentMemory
import agent.Rob.lua_actions as la
import miney
import configparser
from dialog_manager.rasa_dm.actions import actions
from agent.Rob import atomic_actions
import time


class Robo(BaseAgent):
    def __init__(self, action_input_queue: queue.Queue, world: "MinetestWorld"=None, opts=None):
        self.action_input_queue = action_input_queue
        self.world = world
        self.last_task_memid = None
        self.pos = (0, 0, 0)
        super(Robo, self).__init__(opts)

    def init_memory(self):
        self.memory = AgentMemory()

    def init_perception(self):
        self.perception_modules = {}
        self.perception_modules['heuristic'] = HeuristicPerception(self)

    def init_controller(self):
        pass

    def perceive(self):
        self.world.step() # update world state
        #for perception_module in self.perception_modules.values():
        #    perception_module.perceive()

    def controller_step(self):
        # need to get incoming dialogue actions and work out what to do with them
        try:
            action = self.action_input_queue.get_nowait()
        except:
            return

        print("droidlet_agent.Robo.controller_step: action from action_input_queue", action)

        if action is None:
            return

        if isinstance(action, actions.Stop):
            while self.memory.task_stack_peek():
                self.memory.task_stack_pop()
        else:
            bot_state = self.world.get_state()
            try:
                try:
                    if isinstance(action, actions.ComeHere):
                        atomic_action = atomic_actions.AtomicAction.come_here(self, bot_state, self.world)
                    elif isinstance(action, actions.Move):
                        atomic_action = atomic_actions.AtomicAction.from_move(self, action, bot_state, self.world)
                    elif isinstance(action, actions.DestroyBlock):
                        atomic_action = atomic_actions.AtomicAction.from_destroy_block(self, action, bot_state, self.world)
                    elif isinstance(action, actions.PlaceBlock):
                        atomic_action = atomic_actions.AtomicAction.from_place_block(self, action, bot_state, self.world)
                    elif isinstance(action, actions.Turn):
                        atomic_action = atomic_actions.AtomicAction.from_turn(self, action, bot_state, self.world)
                    else:
                        return
                except:
                    print("droidlet_agent.Robo.controller_step: error handling action from rasa", action)
                    return

                print("droidlet_agent.Robo.controller_step: pushing action to task stack", atomic_action)
                pushed = self.memory.task_stack_push(atomic_action)
                pushed.get_update_status({"prio": 1})

            except Exception as e:
                import traceback
                traceback.print_exc()
                #print(e)
                return

    def task_step(self, sleep_time=5):
        while (
            self.memory.task_stack_peek() and self.memory.task_stack_peek().task.check_finished()
        ):
            print("droidlet_agent.Robo.task_step: removing finished task from stack")
            self.memory.task_stack_pop()

        # do nothing if there's no task
        if self.memory.task_stack_peek() is None:
            #print("droidlet_agent.Robo.task_step: nothing to do")
            return

        # If something to do, step the topmost task
        task_mem = self.memory.task_stack_peek()
        print("droidlet_agent.Robo.task_step: stepping with task", task_mem)
        if task_mem.memid != self.last_task_memid:
            self.last_task_memid = task_mem.memid
        task_mem.task.step(self)
        self.memory.task_stack_update_task(task_mem.memid, task_mem.task)

    def handle_exception(self, e):
        import traceback
        print(e)
        traceback.print_last()
        pass

    def send_chat(self, chat):
        pass

    def step(self):
        #print("Agent step perceiving")
        self.perceive()
        self.memory.update(self)
        # maybe place tasks on the stack, based on memory/perception
        self.controller_step()
        # step topmost task on stack
        self.task_step()
        self.count += 1


@dataclass
class BotState:
    bot_id: str
    position: Dict[str, int]
    orientation_to_sun: float
    inventory: Dict[str, int]
    nearby_blocks_grid: Dict[Any, Any]
    yaw: Any
    compass_orientation: Any


from enum import Enum
class State(Enum):
    NOEXIST = 0
    IDLE = 1
    RUNNING = 2


class MinetestWorld:
    def __init__(self, server, playername, password, port, opts=None, spec=None):
        # interact via miney etc
        #self.bot_id = bot_id
        self.mt = miney.Minetest(server, playername, password, port)
        self.lua_runner = miney.Lua(self.mt)

        config = configparser.ConfigParser()

        config.read("/home/nrg/potsdam/embagent/minetest-agent/agent/Rob/newnpc.conf")
        config = config['NPC']

        player = self.mt.player[0]
        bot_id = config['ID']

        self.id = bot_id
        if config.getboolean('SPAWN_ON_PLAYER'):
            pos = player.position
            pos_vector = tuple([pos['x'], pos['y']+1, pos['z']])
        else:
            pos = [float(i) for i in config['SPAWN_POSITION'].split()]
            pos_vector = tuple([pos[0], pos[1]+1, pos[2]])

        yaw = float(config['YAW'])
        modname = config['MOD_NAME']
        ownername = config['OWNER_NAME']

        add_rob = f"""
        local ref = {{
            id = "{bot_id}",
            pos = vector.new{pos_vector},
            yaw = {yaw},
            name = "{modname}",
            owner = "{ownername}",
        }}
        npcf:add_npc(ref)
        """

        # testing if rob already exists
        test_rob = f"""
        local e = npcf:get_luaentity(\"{bot_id}\")
            if e then
                return true
            else
                return false
            end
        """

        for i in range(3):
            if self.lua_runner.run(test_rob):
                self.state = State.IDLE
                print("droidlet_agent.MinetestWorld.__init__: rob is initialized")
                break
            print(f"droidlet_agent.MinetestWorld.__init__: {i+1}. try to initialize Rob")
            self.lua_runner.run(add_rob)
            # TODO: sleep for max time or just await ingame result
            time.sleep(10)

        if not self.lua_runner.run(test_rob):
            # TODO: raise exceptions
            print("droidlet_agent.MinetestWorld.__init__: Initializing Rob FAILED")

        self.lua_runner.run(la.lua_init_compass.format(npc_id=bot_id))
        self.bot_orientation = atomic_actions.Compass.N

    def step(self):
        self.run_lua("return minetest.set_timeofday(0.5)", do_print=False)

    def run_lua(self, lua, do_print=True):
        if do_print:
            print("droidlet_agent.MinetestWorld.run_lua: running lua")
            print(textwrap.indent(lua, prefix=">>> "))
        return self.lua_runner.run(lua)

    def get_state(self):
        position = self.run_lua(la.lua_get_position.format(npc_id=self.id))
        orientation_to_sun = self.run_lua(la.lua_get_orientation_to_sun.format(npc_id=self.id))
        yaw = self.run_lua(la.lua_get_yaw.format(npc_id=self.id))
        inventory = {}
        #nearby_blocks_grid = self.run_lua(la.lua_get_nodes(npc_id=self.bot_id))
        rval = BotState(
            self.id,
            position,
            orientation_to_sun,
            inventory,
            None, #nearby_blocks_grid
            yaw,
            self.bot_orientation
        )
        print("droidlet_agent.MinetestWorld.get_state: bot state", rval)
        return rval

    def handle_exception(self, e):
        import traceback
        traceback.print_last()
        pass


# heuristic_perception.py
class HeuristicPerception:
    def __init__(self, agent):
        self.agent = agent

    def perceive(self):
        # get the n x n x n grid of blocks
        pass


def run(q):
    pass